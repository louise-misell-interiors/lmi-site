from django import forms
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from . import models
from . import views
import requests
from phonenumber_field.formfields import PhoneNumberField


class ContactForm(forms.Form):
    your_name = forms.CharField(label='Your name', widget=forms.TextInput(attrs={'placeholder': 'Your name'}))
    your_email = forms.EmailField(label='Your email', widget=forms.EmailInput(attrs={'placeholder': 'Your email'}))
    your_phone = PhoneNumberField(label='Your phone', widget=forms.TextInput(attrs={'placeholder': 'Your phone'}))
    message = forms.CharField(label='Your message', widget=forms.Textarea(attrs={'placeholder': 'Your message'}))


class NewsletterForm(forms.Form):
    name = forms.CharField(label='Your name', widget=forms.TextInput(attrs={'placeholder': 'Your name'}))
    email = forms.EmailField(label='Your email', widget=forms.EmailInput(attrs={'placeholder': 'Your email'}))


class AuthWidget(forms.Widget):
    template_name = 'main_site/auth_button_widget.html'

    def render(self, name, value, attrs=None, **kwargs):
        is_signed_in = False

        creds = views.get_credentials()
        if creds is not None:
            is_signed_in = True

        context = {
            'is_signed_in': is_signed_in
        }
        return mark_safe(render_to_string(self.template_name, context))


class PageWidget(forms.Widget):
    template_name = 'main_site/page_widget.html'

    def render(self, name, value, attrs: dict=None, **kwargs):
        is_signed_in = False

        creds = views.get_credentials()
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


class ConfigForm(forms.ModelForm):
    auth = forms.Field(widget=AuthWidget, required=False)

    def save(self, commit=True):
        return super().save(commit=commit)

    class Meta:
        fields = ('auth', 'facebook_page_id', 'instagram_url', 'twitter_url', 'facebook_url', 'pintrest_url',
                  'linkedin_url', 'homify_url', 'houzz_url', 'bark_url', 'email', 'mobile', 'phone', 'address',
                  'privacy_policy', 'terms_and_conditions', 'image_slider_speed', 'testimonials_slider_speed',
                  'price_range',
                  'home_title', 'home_subtitle', 'home_description', 'home_text',
                  'about_title', 'about_description',
                  'portfolio_title', 'portfolio_description', 'portfolio_text',
                  'blog_title', 'blog_description', 'blog_text',
                  'services_title', 'services_description', 'services_text',
                  'contact_title', 'contact_description',
                  'testimonials_title', 'testimonials_description', 'testimonials_text')
        widgets = {
            "facebook_page_id": PageWidget
        }
        model = models.SiteConfig
