from django import forms
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from . import models
from . import views
import requests
from phonenumber_field.formfields import PhoneNumberField


class ContactForm(forms.Form):
    first_name = forms.CharField(label='Your first name', widget=forms.TextInput(attrs={'placeholder': 'Your first name'}))
    last_name = forms.CharField(label='Your last name', widget=forms.TextInput(attrs={'placeholder': 'Your last name'}))
    your_email = forms.EmailField(label='Your email', widget=forms.EmailInput(attrs={'placeholder': 'Your email'}))
    your_phone = PhoneNumberField(label='Your phone', widget=forms.TextInput(attrs={'placeholder': 'Your phone'}))
    message = forms.CharField(label='Your message', widget=forms.Textarea(attrs={'placeholder': 'Your message'}))
    source = forms.CharField(
        required=False,
        label='Where did you hear about me?',
        widget=forms.TextInput(attrs={'placeholder': 'Where did you hear about me?'})
    )
    newsletter = forms.BooleanField(required=False, label='Click here to be signed up to my newsletter', label_suffix="")


class NewsletterForm(forms.Form):
    first_name = forms.CharField(label='Your first name', widget=forms.TextInput(attrs={'placeholder': 'Your first name'}))
    last_name = forms.CharField(label='Your last name', widget=forms.TextInput(attrs={'placeholder': 'Your last name'}))
    email = forms.EmailField(label='Your email', widget=forms.EmailInput(attrs={'placeholder': 'Your email'}))


class FbAuthWidget(forms.Widget):
    template_name = 'main_site/fb_auth_button_widget.html'

    def render(self, name, value, attrs=None, **kwargs):
        is_signed_in = False

        creds = views.get_fb_credentials()
        if creds is not None:
            is_signed_in = True

        context = {
            'is_signed_in': is_signed_in
        }
        return mark_safe(render_to_string(self.template_name, context))


class NewsletterAuthWidget(forms.Widget):
    template_name = 'main_site/newsletter_auth_button_widget.html'

    def render(self, name, value, attrs=None, **kwargs):
        is_signed_in = False

        creds = views.get_newsletter_credentials()
        if creds is not None:
            is_signed_in = True

        context = {
            'is_signed_in': is_signed_in
        }
        return mark_safe(render_to_string(self.template_name, context))


class PageWidget(forms.Widget):
    template_name = 'main_site/fb_page_widget.html'

    def render(self, name, value, attrs: dict=None, **kwargs):
        is_signed_in = False

        creds = views.get_fb_credentials()
        if creds is not None:
            is_signed_in = True

        choices = []
        if is_signed_in:
            accounts = requests.get("https://graph.facebook.com/v3.3/me/accounts", params={"access_token": creds})
            accounts.raise_for_status()
            accounts = accounts.json()["data"]
            choices = list(map(lambda a: {"id": a["id"], "name": a["name"]}, accounts))

        context = {
            'is_signed_in': is_signed_in,
            'name': name,
            'value': value,
            'values': choices,
            'attrs': " ".join(map(lambda a: f"{a[0]}={a[1]}", attrs.items()))
        }
        return mark_safe(render_to_string(self.template_name, context))


class NewsletterGroupWidget(forms.Widget):
    template_name = 'main_site/newsletter_group_widget.html'

    def render(self, name, value, attrs: dict=None, **kwargs):
        is_signed_in = False

        creds = views.get_newsletter_credentials()
        if creds is not None:
            is_signed_in = True

        choices = []
        if is_signed_in:
            lists = requests.get(f"{creds['endpoint']}/3.0/lists", headers={
                "Authorization": f"OAuth {creds['token']}"
            })
            lists.raise_for_status()
            lists = lists.json()["lists"]
            choices = list(map(lambda a: {"id": a["id"], "name": a["name"]}, lists))

        context = {
            'is_signed_in': is_signed_in,
            'name': name,
            'value': value,
            'values': choices,
            'attrs': " ".join(map(lambda a: f"{a[0]}={a[1]}", attrs.items()))
        }
        return mark_safe(render_to_string(self.template_name, context))


class ConfigForm(forms.ModelForm):
    fb_auth = forms.Field(widget=FbAuthWidget, required=False)
    newsletter_auth = forms.Field(widget=NewsletterAuthWidget, required=False)

    def save(self, commit=True):
        return super().save(commit=commit)

    class Meta:
        fields = ('fb_auth', 'facebook_page_id', 'newsletter_auth', 'newsletter_group_id',
                  'instagram_url', 'twitter_url', 'facebook_url', 'pintrest_url', 'linkedin_url', 'homify_url',
                  'houzz_url', 'bark_url', 'email', 'notification_email', 'mobile', 'phone', 'address',
                  'privacy_policy', 'terms_and_conditions', 'image_slider_speed', 'testimonials_slider_speed',
                  'price_range',
                  'home_title', 'home_subtitle', 'home_description', 'home_about_text', 'home_about_cta',
                  'home_help_text', 'home_help_image', 'home_help_cta', 'home_testimonials_cta',
                  'about_title', 'about_header_image', 'about_image_2', 'about_description', 'about_mission_statement',
                  'about_text', 'about_text_2', 'about_cta', 'about_testimonials_cta',
                  'resources_title', 'resources_image', 'resources_description', 'resources_text',
                  'portfolio_title', 'portfolio_header_image', 'portfolio_description', 'portfolio_text',
                  'blog_title', 'blog_header_image', 'blog_description', 'blog_text',
                  'services_title', 'services_header_image', 'services_description', 'services_text',
                  'services_cta', 'services_testimonials_cta',
                  'online_design_title', 'online_design_header_image', 'online_design_description',
                  'online_design_text', 'online_design_button_text',
                  'design_for_diversity_title', 'design_for_diversity_header_image', 'design_for_diversity_description',
                  'designer_in_a_box_title', 'designer_in_a_box_header_image', 'designer_in_a_box_description',
                  'designer_in_a_box_content',
                  'contact_title', 'contact_header_image', 'contact_description', 'contact_text_1', 'contact_text_2',
                  'contact_testimonials_cta', 'contact_form_image',
                  'testimonials_title', 'testimonials_header_image', 'testimonials_description', 'testimonials_text',
                  'booking_title', 'booking_header_image',
                  'apple_merchantid')
        widgets = {
            "facebook_page_id": PageWidget,
            "newsletter_group_id": NewsletterGroupWidget
        }
        model = models.SiteConfig
