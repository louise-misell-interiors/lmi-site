import copy
import json
import uuid

import requests

import stripe
import bookings.views
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone

from . import forms
from .models import *


def shop_category(request, id):
    category_obj = get_object_or_404(Category, id=id)
    items = category_obj.products.order_by('order')

    return render(request, "main_site/category.html", {
        "category": category_obj,
        "items": items
    })


def shop_product(request, id):
    product_obj = get_object_or_404(Product, id=id)

    return render(request, "main_site/product.html", {
        "product": product_obj
    })


def get_basket(request, create=True, complete=False):
    if complete:
        return Basket.objects.filter(id=request.session["basket_id"]).first()

    if "basket_id" in request.session:
        basket = Basket.objects.filter(id=request.session["basket_id"], state=Basket.STATE_CREATION).first()
    else:
        basket = None

    if not basket and create:
        basket = Basket(
            user=request.user if request.user.is_authenticated else None
        )
        basket.save()
        request.session["basket_id"] = str(basket.id)

    return basket


@require_POST
def shop_product_add(request, id):
    product_obj = get_object_or_404(Product, id=id)

    try:
        quantity = int(request.POST.get("quantity"))
    except ValueError:
        return HttpResponse(status=400)

    basket = get_basket(request)
    basket_item, _ = BasketItem.objects.get_or_create(
        basket=basket,
        product=product_obj
    )
    basket_item.quantity += quantity
    basket_item.save()
    request.session["added_to_basket"] = str(product_obj.id)

    return redirect('shop_basket')


def shop_basket(request):
    basket = get_basket(request)

    return render(request, "main_site/basket.html", {
        "basket": basket
    })


def shop_basket_details(request):
    basket = get_basket(request, create=False)
    if not basket:
        return redirect('shop_basket')

    postage_address = basket.postage_address if basket.postage_address else PostalAddress()
    details = {
        "name": basket.name,
        "email": basket.email,
        "phone": basket.phone,
    }

    if request.method == "POST":
        form = forms.PostalAddressForm(request.POST, prefix="addr", instance=postage_address)
        details_form = forms.PersonalDetailsForm(request.POST, prefix="details", initial=details)
        form.full_clean()
        details_form.full_clean()

        if form.is_valid() and details_form.is_valid():
            form.instance.name = details_form.cleaned_data['name']
            form.save()
            basket.postage_address = form.instance
            basket.name = details_form.cleaned_data['name']
            basket.phone = details_form.cleaned_data['phone']
            basket.email = details_form.cleaned_data['email']
            basket.save()

            return redirect('shop_basket_payment')
    else:
        form = forms.PostalAddressForm(prefix="addr", instance=postage_address)
        details_form = forms.PersonalDetailsForm(prefix="details", initial=details)

    return render(request, "main_site/basket_details.html", {
        "basket": basket,
        "details_form": details_form,
        "form": form
    })


def shop_basket_payment(request):
    basket = get_basket(request, create=False)
    if not basket or not basket.postage_address:
        return redirect('shop_basket')

    postage_options = basket.possible_postage_options(basket.postage_address.country)

    can_deliver = bool(len(postage_options))

    return render(request, "main_site/basket_payment.html", {
        "basket": basket,
        "postage_options": postage_options,
        "can_deliver": can_deliver
    })


def shop_basket_complete(request):
    basket = get_basket(request, complete=True)
    if not basket or not basket.completed_date or not basket.postage_service:
        return redirect('shop_basket')

    delivery_time_range = basket.postage_service.formatted_delivery_time_range(timestamp=basket.completed_date)

    return render(request, "main_site/basket_complete.html", {
        "basket": basket,
        "delivery_time_range": delivery_time_range
    })


@require_POST
def shop_basket_update_quantity(request):
    basket = get_basket(request, create=False)
    if not basket:
        return redirect('shop_basket')

    basket_item = get_object_or_404(BasketItem, id=request.POST.get("id"), basket=basket)

    action = request.POST.get("action")
    if action == "update" or action == "update_js":
        try:
            new_quantity = int(request.POST.get("quantity"))
        except ValueError:
            return HttpResponse(status=400)

        basket_item.quantity = new_quantity
        basket_item.save()
    elif action == "remove" or action == "remove_js":
        basket_item.delete()

    if action == "update_js" or action == "remove_js":
        return render(request, "main_site/basket_fragment.html", {
            "basket": basket
        })

    return redirect('shop_basket')


@require_POST
def shop_basket_calculate_postage(request):
    basket = get_basket(request, create=False)
    if not basket:
        return HttpResponse(status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    country = data.get("address", {}).get("country")
    if not country:
        return HttpResponse(status=400)

    postage_options = basket.possible_postage_options(country)

    return HttpResponse(json.dumps({
        "options": list(map(lambda option: {
            "id": str(option.service.id),
            "label": option.service.name,
            "detail": option.description,
            "amount": int(round(option.price * 100))
        }, postage_options))
    }))


@require_POST
def shop_basket_payment_intent(request):
    basket = get_basket(request, create=False)
    if not basket:
        return HttpResponse(status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    postage_option_id = data.get("postage_option", {})
    if not postage_option_id:
        return HttpResponse(status=400)
    try:
        postage_option_id = uuid.UUID(postage_option_id)
    except ValueError:
        return HttpResponse(status=400)

    customer_name = data.get("name", None)
    customer_email = data.get("email", None)
    customer_phone = data.get("phone", None)
    customer_address = data.get("address", None)

    if customer_name:
        basket.name = customer_name
    if customer_email:
        basket.email = customer_email
    if customer_phone:
        basket.phone = customer_phone

    if customer_address:
        postage_address = basket.postage_address if basket.postage_address else PostalAddress()
        postage_address.name = customer_address.get("recipient")
        address_lines = iter(customer_address.get("addressLine", []))
        postage_address.address_line1 = next(address_lines, None)
        postage_address.address_line2 = next(address_lines, None)
        postage_address.address_line3 = next(address_lines, None)
        postage_address.city = customer_address.get("city")
        postage_address.region = customer_address.get("region")
        postage_address.post_code = customer_address.get("postalCode")
        postage_address.country = customer_address.get("country")

        if not postage_address.name or not postage_address.address_line1 or not postage_address.city\
                or not postage_address.country:
            return HttpResponse(status=400)

        postage_address.save()
        basket.postage_address = postage_address

    basket.save()

    postage_options = basket.possible_postage_options(basket.postage_address.country)

    postage_option = next(filter(lambda o: o.service.id == postage_option_id, postage_options), None)
    if not postage_option:
        return HttpResponse(status=400)

    if not basket.postage_service or postage_option.service.id != basket.postage_service.id \
            or not basket.payment_intent_id:
        if basket.payment_intent_id:
            stripe.PaymentIntent.cancel(basket.payment_intent_id)
            basket.payment_intent_id = None
            basket.save()

        amount = basket.items_total + postage_option.price

        payment_intent = stripe.PaymentIntent.create(
            amount=int(round(amount * 100)),
            currency='gbp',
            payment_method_types=['card'],
            metadata={
                'basket': basket.id
            },
            shipping={
                "name": basket.name,
                "address": {
                    "line1": basket.postage_address.address_line1,
                    "line2": basket.postage_address.address_line2,
                    "city": basket.postage_address.city,
                    "state": basket.postage_address.region,
                    "country": basket.postage_address.country,
                    "postal_code": basket.postage_address.post_code,
                },
                "carrier": postage_option.service.name,
                "phone": basket.phone.as_e164,
            },
            payment_method_options={
                "card": {
                    "request_three_d_secure": "any"
                }
            }
        )
        basket.payment_intent_id = payment_intent.id
        basket.postage_service = postage_option.service
        basket.postage_service_bins = postage_option.to_json()
        basket.save()
    else:
        payment_intent = stripe.PaymentIntent.retrieve(basket.payment_intent_id)

    return HttpResponse(json.dumps({
        "client_secret": payment_intent.client_secret
    }))


def send_stripe_receipt(charge):
    config = SiteConfig.objects.first()

    if not charge.billing_details.email:
        return

    if charge.receipt_number:
        subject = f"Your Louise Misell Interiors receipt - {charge.receipt_number}"
    else:
        subject = "Your Louise Misell Interiors receipt"

    context = {
        "charge": charge,
        "amount": decimal.Decimal(charge.amount) / decimal.Decimal(100),
        "date": datetime.datetime.utcfromtimestamp(charge.created)
    }

    email_msg = EmailMultiAlternatives(
        subject=subject,
        body=render_to_string("bookings/receipt_txt.html", context),
        to=[charge.billing_details.email],
        reply_to=[f"Louise Misell Interiors <{config.email}>"]
    )
    email_msg.attach_alternative(render_to_string("bookings/receipt.html", context), "text/html")
    email_msg.send()


def stripe_webhook(request):
    try:
        event = stripe.Event.construct_from(
            json.loads(request.body), stripe.api_key
        )
    except ValueError:
        return HttpResponse(status=400)

    bookings.views.stripe_webhook(event)

    obj = event.data.object
    if obj.object == "payment_intent":
        basket = Basket.objects.filter(state=Basket.STATE_CREATION, payment_intent_id=obj.id).first()
        if basket and obj.status == "succeeded":
            basket.state = basket.STATE_PAID
            basket.completed_date = timezone.now()
            basket.save()
            order_succeeded(basket)
    elif obj.object == "charge":
        if event.type == "charge.succeeded":
            send_stripe_receipt(obj)

    return HttpResponse(status=200)


def order_succeeded(basket: Basket):
    config = SiteConfig.objects.first()

    make_rm_order(basket)

    payment_intent = stripe.PaymentIntent.retrieve(basket.payment_intent_id)
    amount = decimal.Decimal(payment_intent.amount) / decimal.Decimal(100)

    items_text = []
    for item in basket.items.all():
        item_text = f"ID: {item.product.id}\r\n" \
                    f"Brand ID: {item.product.brand.id}\r\n" \
                    f"Name: {item.product.name}\r\n" \
                    f"GTIN: {item.product.gtin}\r\n" \
                    f"MPN: {item.product.mpn}\r\n" \
                    f"Quantity: {item.quantity}"
        items_text.append(item_text)

    items_text = "\r\n---\r\n".join(items_text)
    items_text = f"--- BEGIN ITEMS ---\r\n{items_text}\r\n--- END ITEMS ---"

    recipient_address = "--- BEGIN DELIVERY ADDRESS ---\r\n" \
                        f"ID: {basket.postage_address.id}\r\n" \
                        f"Name: {basket.postage_address.name}\r\n" \
                        f"Line 1: {basket.postage_address.address_line1}\r\n" \
                        f"Line 2: {basket.postage_address.address_line2}\r\n" \
                        f"Line 3: {basket.postage_address.address_line3}\r\n" \
                        f"City: {basket.postage_address.city}\r\n" \
                        f"County: {basket.postage_address.region}\r\n" \
                        f"Postcode: {basket.postage_address.post_code}\r\n" \
                        f"Country: {basket.postage_address.country.code}\r\n" \
                        "--- END DELIVERY ADDRESS ---"

    customer = "--- BEGIN CUSTOMER ---\r\n" \
               f"Name: {basket.name}\r\n" \
               f"Email: {basket.email}\r\n" \
               f"Phone: {basket.phone.as_e164}\r\n" \
               "--- END CUSTOMER ---"

    summary = "--- BEGIN SUMMARY ---\r\n" \
              f"ID: {basket.id}\r\n" \
              f"Date: {basket.completed_date}\r\n" \
              f"Total amount: {amount} {payment_intent.currency.upper()}\r\n" \
              "--- END SUMMARY ---"

    body = f"{summary}\r\n\r\n{customer}\r\n\r\n{recipient_address}\r\n\r\n{items_text}"

    email_msg = EmailMessage(
        subject=f"New shop order - {basket.id}",
        body=body,
        to=[config.notification_email],
        reply_to=[f"{basket.name} <{basket.email}>"]
    )
    email_msg.send()


def make_rm_order(basket: Basket):
    if settings.RM_API_KEY:
        postage_option = PostageOption.from_json(basket.postage_service_bins)
        subtotal = basket.items_total

        address = {
            "fullName": basket.postage_address.name,
            "addressLine1": basket.postage_address.address_line1,
            "addressLine2": basket.postage_address.address_line2,
            "addressLine3": basket.postage_address.address_line3,
            "city": basket.postage_address.city,
            "county": basket.postage_address.region,
            "postcode": basket.postage_address.post_code,
            "countryCode": basket.postage_address.country.code,
        }

        order = {
            "orderReference": None,
            "recipient": {
                "address": address,
                "phoneNumber": basket.phone.as_e164,
                "emailAddress": basket.email,
                "addressBookReference": str(basket.postage_address.id),
            },
            "billing": {
                "address": address,
                "phoneNumber": basket.phone.as_e164,
                "emailAddress": basket.email,
            },
            "packages": None,
            "orderDate": basket.completed_date.isoformat(),
            "specialInstructions": basket.postage_address.delivery_notes,
            "subtotal": str(subtotal),
            "shippingCostCharged": str(postage_option.price),
            "total": str(subtotal + postage_option.price),
            "currencyCode": "GBP",
            "postageDetails": {
                "serviceCode": postage_option.service.rm_service_code,
                "sendNotificationsTo": "recipient",
                "receiveEmailNotifications": True,
                "receiveSmsNotifications": True,
            }
        }

        orders = []
        for i, postage_bin in enumerate(postage_option.bins):
            new_order = copy.copy(order)
            new_order["orderReference"] = f"{basket.id};{i}"
            new_order["packages"] = [{
                "weightInGrams": postage_bin.weight_grams,
                "packageFormatIdentifier": postage_bin.service_type.rm_package_format_id
                if postage_bin.service_type.rm_package_format_id else "undefined",
                "contents": [next(
                    {
                        "name": product.name,
                        "SKU": str(product.id),
                        "quantity": len(list(filter(lambda p: p.id == pid, postage_bin.items))),
                        "unitValue": str(product.price),
                        "unitWeightInGrams": int(round(product.weight * 1000)),
                        "customsDeclarationCategory": "saleOfGoods",
                    } for product in postage_bin.items if product.id == pid
                ) for pid in set(map(lambda p: p.id, postage_bin.items))]
            }]
            orders.append(new_order)

        r = requests.post("https://api.parcel.royalmail.com/api/v1/orders", headers={
            "Authorization": f"Bearer {settings.RM_API_KEY}",
        }, json={
            "items": orders
        })
        r.raise_for_status()

        basket.rm_order_id = list(map(lambda o: o["orderIdentifier"], r.json()["createdOrders"]))
        basket.save()
