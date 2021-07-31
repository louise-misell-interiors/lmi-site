import json

import bookings.models as booking_models
import django.utils.xmlutils
import google_auth_oauthlib.flow
import requests
from django.contrib.syndication.views import Feed
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.utils import feedgenerator, timezone
from django.utils.encoding import iri_to_uri
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required

from . import forms
from .models import *

FB_CLIENT_SECRETS_FILE = "facebook_client_secret.json"
FB_SCOPES = ['instagram_basic', 'pages_show_list']
NEWSLETTER_CLIENT_SECRETS_FILE = "mailchimp_client_secret.json"


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def index(request):
    slider_imgs = MainSliderImage.objects.all()
    testimonials = Testimonial.objects.filter(featured_on=Testimonial.HOME_PAGE)
    projects = Project.objects.filter(draft=False)[:4]
    services = Service.objects.filter(type=Service.MAIN)
    if not request.user.is_superuser:
        testimonials = testimonials.filter(draft=False)
        services = services.filter(draft=False)
    return render(request, "main_site/index.html",
                  {"testimonial": testimonials.first(), "slider_imgs": slider_imgs, "projects": projects,
                   "services": services})


def page_not_found(request, exception=None):
    r = render(request, "main_site/404.html")
    r.status_code = 404
    return r


def config(request):
    return render(request, "main_site/config.js", content_type="application/javascript")


def apple_merchantid(request):
    config = SiteConfig.objects.first()
    return HttpResponse(config.apple_merchantid, content_type='text/plain')


def handle_newsletter(request):
    form = forms.NewsletterForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data['email']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']

        config = SiteConfig.objects.first()
        creds = get_newsletter_credentials()
        entry = NewsletterEntry()

        if creds is not None and config.newsletter_group_id:
            member = requests.post(f"{creds['endpoint']}/3.0/lists/{config.newsletter_group_id}/members/", headers={
                "Authorization": f"OAuth {creds['token']}"
            }, json={
                "email_address": email,
                "status": "pending",
                "ip_signup": get_client_ip(request),
                "source": "Website",
                "merge_fields": {
                    "FNAME": first_name,
                    "LNAME": last_name
                }
            })
            if member.status_code == 200:
                data = member.json()
                entry.mailchimp_id = data.get("id", "")

        entry.first_name = first_name
        entry.last_name = last_name
        entry.email = email
        entry.save()
    return form


def design_insider(request):
    posts = DesignInsiderPost.objects.all()
    if not request.user.is_staff:
        posts = posts.filter(draft=False)

    short_posts = ShortPost.objects.all()
    if not request.user.is_staff:
        short_posts = short_posts.filter(draft=False)

    if request.method == "POST":
        form = handle_newsletter(request)
        return render(request, "main_site/design_insider.html",
                      {"posts": posts, "short_posts": short_posts, "form": form, "sent": True})
    else:
        form = forms.NewsletterForm()

    return render(request, "main_site/design_insider.html",
                  {"posts": posts, "short_posts": short_posts, "form": form})


def design_insider_post(request, id):
    post = get_object_or_404(DesignInsiderPost, id=id)

    short_posts = ShortPost.objects.all()
    if not request.user.is_staff:
        short_posts = short_posts.filter(draft=False)

    if request.method == "POST":
        form = handle_newsletter(request)
        return render(request, "main_site/design_insider_post.html",
                      {"post": post, "short_posts": short_posts, "form": form, "sent": True})
    else:
        form = forms.NewsletterForm()

    return render(
        request, "main_site/design_insider_post.html", {
            "post": post,
            "short_posts": short_posts,
            "form": form
        })


class DesignInsiderFeedType(feedgenerator.Rss201rev2Feed):
    def rss_attributes(self):
        return {
            'version': self._version,
            'xmlns:atom': 'http://www.w3.org/2005/Atom',
            'xmlns:media': 'http://search.yahoo.com/mrss/',
            'xmlns:content': 'http://purl.org/rss/1.0/modules/content/',
        }

    def add_item_elements(self, handler: django.utils.xmlutils.SimplerXMLGenerator, item: dict):
        super().add_item_elements(handler, item)
        handler.addQuickElement('content:encoded', item.get('content'))
        image = item.get("image")
        if image:
            handler.startElement('media:content', {
                "url": image.get("image"),
                "medium": "image",
                "isDefault": "true",
            })
            handler.addQuickElement("media:description", image.get("alt"))
            handler.endElement('media:content')


class DesignInsiderFeed(Feed):
    feed_type = DesignInsiderFeedType
    title = "Louise Misell Interiors blog"
    author_name = "Louise Misell"
    author_email = "louise@louisemisellinteriors.co.uk"
    item_author_name = "Louise Misell"
    item_author_email = "louise@louisemisellinteriors.co.uk"
    description = "Updates and posts from Louise Misell Interiors"
    request = None
    site = None

    def add_domain(self, url):
        protocol = 'https' if self.request.is_secure() else 'http'
        if url.startswith('//'):
            url = '%s:%s' % (protocol, url)
        elif not url.startswith(('http://', 'https://', 'mailto:')):
            url = iri_to_uri('%s://%s%s' % (protocol, self.site.domain, url))
        return url

    def get_context_data(self, **kwargs):
        self.request = kwargs.get("request")
        self.site = kwargs.get("site")
        return {}

    def link(self):
        return reverse('design_insider')

    def feed_url(self):
        return reverse('design_insider_rss')

    def feed_copyright(self):
        now = timezone.now()
        return f"Copyright Louise Misell Interiors {now.year}"

    def item_copyright(self):
        now = timezone.now()
        return f"Copyright Louise Misell Interiors {now.year}"

    def items(self):
        return DesignInsiderPost.objects.all().filter(draft=False)

    def item_title(self, item: DesignInsiderPost):
        return item.title

    def item_description(self, item: DesignInsiderPost):
        return item.summarize

    def item_pubdate(self, item: DesignInsiderPost):
        return timezone.datetime(item.date.year, item.date.month, item.date.day, 0, 0, 0)

    def item_link(self, item: DesignInsiderPost):
        return reverse('design_insider_post', kwargs={"id": item.id})

    def item_extra_kwargs(self, item: DesignInsiderPost):
        return {
            "content": item.content,
            "image": {
                "image": self.add_domain(item.image.url),
                "alt": item.image_alt
            }
        }


def about(request):
    testimonials = Testimonial.objects.filter(featured_on=Testimonial.ABOUT_PAGE)
    if not request.user.is_staff:
        testimonials = testimonials.filter(draft=False)
    return render(request, "main_site/about.html", {"testimonial": testimonials.first()})


def resources(request):
    resources = Resource.objects.all()

    if request.method == "POST":
        form = handle_newsletter(request)
    else:
        form = forms.NewsletterForm()

    return render(request, "main_site/resources.html", {
        "form": form,
        "resources": resources
    })


def portfolio(request):
    projects = Project.objects.all()
    if not request.user.is_staff:
        projects = projects.filter(draft=False)
    return render(request, "main_site/portfolio.html", {"projects": projects})


def project(request, id):
    project = get_object_or_404(Project, id=id)
    projects = Project.objects.filter(~Q(id=id))
    if not request.user.is_staff:
        projects = projects.filter(draft=False)
    return render(request, "main_site/project.html", {"project": project, "projects": projects})


def services(request):
    services = Service.objects.all()

    testimonials = Testimonial.objects.filter(featured_on=Testimonial.SERVICES_PAGE)
    if not request.user.is_staff:
        services = services.filter(draft=False)
        testimonials = testimonials.filter(draft=False)

    services = list(services)
    services_render = []
    last_group = None
    for i, service in enumerate(services):
        next_i = i + 1
        next_service = services[next_i] if next_i < len(services) else None
        services_render.append({
            "service": service,
            "group": service.group if service.group != last_group else None,
            "last_group": (
                    next_service.group != service.group and (service.group is not None)
            ) if next_service else (service.group is not None)
        })
        last_group = service.group

    return render(request, "main_site/services.html", {"services": services_render, "testimonial": testimonials.first()})


def online_design(request):
    steps = OnlineDesignStep.objects.all()
    testimonials = Testimonial.objects.filter(featured_on=Testimonial.ONLINE_DESIGN_PAGE)
    if not request.user.is_staff:
        steps = steps.filter(draft=False)
        testimonials = testimonials.filter(draft=False)
    return render(request, "main_site/online_design.html", {"steps": steps, "testimonial": testimonials.first()})


def diversity_for_design(request):
    testimonials = Testimonial.objects.filter(featured_on=Testimonial.DESIGN_FOR_DIVERSITY)
    if not request.user.is_staff:
        testimonials = testimonials.filter(draft=False)

    return render(request, "main_site/diversity_for_design.html", {"testimonial": testimonials.first()})


@staff_member_required
def designer_in_a_box(request):
    return render(request, "main_site/designer_in_a_box.html")


def testimonials(request):
    testimonials = Testimonial.objects.filter(not_on_testimonials=False)
    if not request.user.is_staff:
        testimonials = testimonials.filter(draft=False)
    return render(request, "main_site/testimonials.html", {"testimonials": testimonials})


def contact(request):
    testimonials = Testimonial.objects.filter(featured_on=Testimonial.CONTACT_PAGE)
    if not request.user.is_staff:
        testimonials = testimonials.filter(draft=False)

    booking_config = booking_models.Config.objects.first()
    booking_notice = booking_config.booking_notice if booking_config else None

    if request.method == 'POST':
        form = forms.ContactForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['your_email']
            phone = form.cleaned_data['your_phone']
            message = form.cleaned_data['message']
            newsletter = form.cleaned_data['newsletter']
            source = form.cleaned_data['source']

            config = SiteConfig.objects.first()
            email_msg = EmailMultiAlternatives(
                subject=f"{first_name} has sent a message on your website",
                body=f"Name: {first_name} {last_name}\r\n"
                     f"Email: {email}\r\n"
                     f"Phone: {phone}\r\n"
                     f"Source: {source}\r\n\r\n"
                     f"---\r\n\r\n{message}",
                to=[config.email],
                reply_to=[email]
            )
            email_msg.send()

            matching_customers = booking_models.Customer.objects.filter(email=email)
            if len(matching_customers) > 0:
                customer = matching_customers.first()
            else:
                customer = booking_models.Customer()
                customer.email = email

                creds = get_newsletter_credentials()
                if creds is not None and config.newsletter_group_id:
                    member = requests.put(
                        f"{creds['endpoint']}/3.0/lists/{config.newsletter_group_id}/members/",
                        headers={
                           "Authorization": f"OAuth {creds['token']}"
                        }, json={
                            "email_address": email,
                            "status_if_new": "subscribed" if newsletter else "unsubscribed",
                            "source": "Website",
                            "ip_signup": get_client_ip(request),
                            "merge_fields": {
                                "FNAME": first_name,
                                "LNAME": last_name,
                            }
                        }
                    )
                    if member.status_code == 200:
                        data = member.json()
                        customer.mailchimp_id = data.get("id", "")

            customer.first_name = first_name
            customer.last_name = last_name
            customer.phone = phone
            customer.source = source

            customer.full_clean()
            customer.save()

            return render(request, "main_site/contact.html",
                          {'form': form, 'sent': True, "testimonial": testimonials.first()})
    else:
        form = forms.ContactForm()

    return render(request, "main_site/contact.html", {
        'form': form,
        'sent': False,
        "testimonial": testimonials.first(),
        "booking_notice": booking_notice,
    })


def booking(request, id):
    return render(request, "main_site/booking.html", {"booking_id": id})


def quiz(request, id):
    quiz = get_object_or_404(Quiz, id=id)

    return render(request, "main_site/quiz.html", {
        "quiz": quiz
    })


@login_required
def account_profile(request):
    return render(request, "registration/profile.html", {})


def fb_authorise(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        FB_CLIENT_SECRETS_FILE, scopes=FB_SCOPES)

    uri = request.build_absolute_uri(reverse('fb_oauth'))
    if not settings.DEBUG:
        uri = uri.replace("http://", "https://")
    flow.redirect_uri = uri

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent',
        include_granted_scopes='true')

    request.session['state'] = state
    request.session['redirect'] = request.META.get('HTTP_REFERER')

    return redirect(authorization_url)


def fb_oauth(request):
    state = request.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        FB_CLIENT_SECRETS_FILE, scopes=FB_SCOPES, state=state)
    uri = request.build_absolute_uri(reverse('fb_oauth'))
    if not settings.DEBUG:
        uri = uri.replace("http://", "https://")
    flow.redirect_uri = uri

    token = flow.fetch_token(code=request.GET.get("code"))

    config = SiteConfig.objects.first()
    config.facebook_token = fb_credentials_to_json(token)
    config.save()

    return redirect(request.session['redirect'])


def fb_deauthorise(request):
    credentials = get_fb_credentials()

    if credentials is not None:
        requests.delete('https://graph.facebook.com/v3.3/{user-id}/permissions',
                        params={'access_token': credentials})

        config = SiteConfig.objects.first()
        config.facebook_token = ""
        config.save()

    return redirect(request.META.get('HTTP_REFERER'))


def fb_credentials_to_json(credentials):
    return json.dumps({'token': credentials['access_token']})


def get_fb_credentials():
    config = SiteConfig.objects.first()
    if config is None:
        return None
    try:
        data = json.loads(config.facebook_token)
        return data['token']
    except json.JSONDecodeError:
        return None


def newsletter_authorise(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(NEWSLETTER_CLIENT_SECRETS_FILE, scopes=[])

    uri = request.build_absolute_uri(reverse('newsletter_oauth'))
    if not settings.DEBUG:
        uri = uri.replace("http://", "https://")
    flow.redirect_uri = uri

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent',
        include_granted_scopes='true')

    request.session['state'] = state
    request.session['redirect'] = request.META.get('HTTP_REFERER')

    return redirect(authorization_url)


def newsletter_oauth(request):
    state = request.session['state']

    flow = \
        google_auth_oauthlib.flow.Flow.from_client_secrets_file(NEWSLETTER_CLIENT_SECRETS_FILE, scopes=[], state=state)
    uri = request.build_absolute_uri(reverse('newsletter_oauth'))
    if not settings.DEBUG:
        uri = uri.replace("http://", "https://")
    flow.redirect_uri = uri

    token = flow.fetch_token(code=request.GET.get("code"))

    config = SiteConfig.objects.first()
    config.newsletter_credentials = newsletter_credentials_to_json(token)
    config.save()

    return redirect(request.session['redirect'])


def newsletter_deauthorise(request):
    credentials = get_newsletter_credentials()

    if credentials is not None:
        config = SiteConfig.objects.first()
        config.newsletter_credentials = ""
        config.save()

    return redirect(request.META.get('HTTP_REFERER'))


def newsletter_credentials_to_json(credentials):
    return json.dumps({'token': credentials['access_token']})


def get_newsletter_credentials():
    config = SiteConfig.objects.first()
    if config is None:
        return None
    try:
        data = json.loads(config.newsletter_credentials)
        token = data["token"]

        r = requests.get("https://login.mailchimp.com/oauth2/metadata", headers={
            "Authorization": f"OAuth {token}"
        })
        r.raise_for_status()
        data = r.json()

        return {
            "token": token,
            "endpoint": data["api_endpoint"]
        }
    except json.JSONDecodeError:
        return None


class BrandGoogleManufacturerFeedType(feedgenerator.Rss201rev2Feed):
    def rss_attributes(self):
        return {
            'version': self._version,
            'xmlns:g': 'http://base.google.com/ns/1.0',
        }

    def add_item_elements(self, handler: django.utils.xmlutils.SimplerXMLGenerator, item: dict):
        super().add_item_elements(handler, item)
        handler.addQuickElement('g:id', item["g_id"])
        handler.addQuickElement('g:brand', item["g_brand"])
        handler.addQuickElement('g:title', item["g_name"])
        handler.addQuickElement('g:gtin', item["g_gtin"])
        handler.addQuickElement('g:description', item["g_description"])
        handler.addQuickElement('g:product_page_url', item["g_product_page_url"])
        handler.addQuickElement('g:product_line', item["g_title"])
        handler.addQuickElement('g:product_name', item["g_subtitle"])
        handler.addQuickElement('g:suggested_retail_price', item["g_price"])

        if len(item["g_images"]) >= 1:
            handler.addQuickElement('g:image_link', item["g_images"][0])
            for img in item["g_images"][1:]:
                handler.addQuickElement('g:additional_image_link', img)


class BrandGoogleManufacturerFeed(Feed):
    feed_type = BrandGoogleManufacturerFeedType

    def get_object(self, request, id):
        return get_object_or_404(Brand, id=id)

    def title(self, obj: Brand):
        return obj.name

    def link(self):
        return reverse('index')

    def feed_url(self, obj: Brand):
        return reverse('shop_brand_feed', kwargs={"id": obj.id})

    def feed_copyright(self):
        now = timezone.now()
        return f"Copyright Louise Misell Interiors {now.year}"

    def item_copyright(self):
        now = timezone.now()
        return f"Copyright Louise Misell Interiors {now.year}"

    def items(self, obj: Brand):
        return obj.products.all()

    def item_title(self, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.description_text

    def item_link(self, item: Product):
        return reverse('shop_product', kwargs={"id": item.id})

    def item_guid(self, item: Product):
        return str(item.id)

    def item_extra_kwargs(self, item: Product):
        return {
            "g_id": str(item.id),
            "g_brand": str(item.brand.name),
            "g_name": str(item.name),
            "g_title": str(item.title),
            "g_subtitle": str(item.subtitle),
            "g_gtin": str(item.gtin),
            "g_description": str(item.description_text),
            "g_price": f"GBP {item.price}",
            "g_product_page_url": settings.EXTERNAL_URL_BASE + reverse('shop_product', kwargs={"id": item.id}),
            "g_images": [settings.EXTERNAL_URL_BASE + i.image.url for i in item.images.all()]
        }
