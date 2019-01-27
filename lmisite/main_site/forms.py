from django import forms
from phonenumber_field.formfields import PhoneNumberField


class ContactForm(forms.Form):
    your_name = forms.CharField(label='Your name', widget=forms.TextInput(attrs={'placeholder': 'Your name'}))
    your_email = forms.EmailField(label='Your email', widget=forms.EmailInput(attrs={'placeholder': 'Your email'}))
    your_phone = PhoneNumberField(label='Your phone', widget=forms.TextInput(attrs={'placeholder': 'Your phone'}))
    message = forms.CharField(label='Your message', widget=forms.Textarea(attrs={'placeholder': 'Your message'}))


class NewsletterForm(forms.Form):
    email = forms.EmailField(label='Your email', widget=forms.EmailInput(attrs={'placeholder': 'Your email'}))
