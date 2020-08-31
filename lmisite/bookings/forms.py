from django import forms
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from .models import *
from . import views


class AuthWidget(forms.Widget):
    template_name = 'bookings/auth_button_widget.html'

    def render(self, name, value, attrs=None, **kwargs):
        is_signed_in = False

        creds = views.get_credentials()
        if creds is not None and creds.scopes == views.SCOPES:
            is_signed_in = True

        context = {
            'is_signed_in': is_signed_in
        }
        return mark_safe(render_to_string(self.template_name, context))


class ConfigForm(forms.ModelForm):
    auth = forms.Field(widget=AuthWidget, required=False)

    def save(self, commit=True):
        return super().save(commit=commit)

    class Meta:
        fields = ['auth', 'booking_notice']
        model = Config
