import dataclasses
import datetime

import base64
import secrets
import decimal
from PIL import Image as Img
import io
import readtime
import nltk.data
import string
import uuid
import typing
import ast
import gtin.validator
import django_countries.fields
import pytz
from bs4 import BeautifulSoup
from django.conf import settings
from django.db import models
from solo.models import SingletonModel
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile, InMemoryUploadedFile
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')


def compress_img(image, new_width=1500):
    if bool(image) and image.file is not None and isinstance(image.file, UploadedFile):
        img = Img.open(io.BytesIO(image.read()))
        img.thumbnail((new_width, new_width * image.height / image.width), Img.BICUBIC)
        output = io.BytesIO()
        output_webp = io.BytesIO()
        if img.mode == 'RGBA':
            background = Img.new("RGB", image.size, (255, 255, 255))
            background.paste(img, img.split()[-1])
            img = background
        img.save(output, format='JPEG', quality=80, optimise=True)
        img.save(output_webp, format='WebP')
        image.save("%s.webp" % image.name.split('.')[0], ContentFile(output_webp.getvalue()), save=True)
        image.save("%s.jpg" % image.name.split('.')[0], ContentFile(output.getvalue()), save=True)


class SiteConfig(SingletonModel):
    facebook_token = models.TextField(blank=True, default="")
    facebook_page_id = models.CharField(max_length=255, blank=True, default="")

    instagram_token = models.TextField(blank=True, default="")
    instagram_token_expires = models.DateTimeField(blank=True, null=True)

    newsletter_credentials = models.TextField(blank=True, default="")
    newsletter_group_id = models.CharField(max_length=255, blank=True, default="")

    instagram_url = models.URLField(default="", blank=True)
    twitter_url = models.URLField(default="", blank=True)
    pintrest_url = models.URLField(default="", blank=True)
    facebook_url = models.URLField(default="", blank=True)
    linkedin_url = models.URLField(default="", blank=True)
    houzz_url = models.URLField(default="", blank=True)
    homify_url = models.URLField(default="", blank=True)
    bark_url = models.URLField(default="", blank=True)

    email = models.EmailField(default="", blank=True)
    email_shop = models.EmailField(default="", blank=True)
    notification_email = models.EmailField(default="", blank=True)
    mobile = PhoneNumberField(blank=True)
    phone = PhoneNumberField(blank=True)
    address = models.TextField(default="", blank=True)

    privacy_policy = models.FileField(blank=True)
    terms_and_conditions = models.FileField(blank=True)
    shop_terms_and_conditions = models.FileField(blank=True)

    image_slider_speed = models.PositiveIntegerField(default=5000, verbose_name="Home page image slider speed (ms)")

    price_range = models.CharField(max_length=255, blank=True)

    home_title = models.CharField(max_length=255, blank=True)
    home_description = models.TextField(blank=True)
    home_subtitle = models.CharField(max_length=255, blank=True)
    home_about_text = RichTextUploadingField(blank=True)
    home_about_cta = models.CharField(max_length=255, blank=True)
    home_about_cta_link = models.URLField(blank=True)
    home_help_text = RichTextUploadingField(blank=True, verbose_name="Home how can I help text")
    home_help_image = models.ImageField(blank=True, verbose_name="Home how can I help background image")
    home_help_cta = models.CharField(max_length=255, blank=True)
    home_help_cta_link = models.URLField(blank=True)
    home_testimonials_cta = models.CharField(max_length=255, blank=True)
    home_testimonials_cta_link = models.URLField(blank=True)
    home_slider_text = models.TextField(blank=True)

    about_title = models.CharField(max_length=255, blank=True)
    about_header = models.CharField(max_length=255, blank=True)
    about_header_image = models.ImageField(blank=True)
    about_why_header = models.CharField(max_length=255, blank=True)
    about_why_header_image = models.ImageField(blank=True)
    about_headshot_image = models.ImageField(blank=True)
    about_description = models.TextField(blank=True)
    about_mission_statement = RichTextUploadingField(blank=True)
    about_text = RichTextUploadingField(blank=True)
    about_text_2 = RichTextUploadingField(blank=True)
    about_top_cta = models.CharField(max_length=255, blank=True)
    about_top_cta_link = models.URLField(blank=True)
    about_cta = models.CharField(max_length=255, blank=True)
    about_cta_link = models.URLField(blank=True)
    about_testimonials_cta = models.CharField(max_length=255, blank=True)
    about_testimonials_cta_link = models.URLField(blank=True)

    resources_title = models.CharField(max_length=255, blank=True)
    resources_image = models.ImageField(blank=True)
    resources_bio_image = models.ImageField(blank=True)
    resources_description = models.TextField(blank=True)
    resources_text = RichTextUploadingField(blank=True)

    portfolio_title = models.CharField(max_length=255, blank=True)
    portfolio_header = models.CharField(max_length=255, blank=True)
    portfolio_header_image = models.ImageField(blank=True)
    portfolio_description = models.TextField(blank=True)
    portfolio_text = RichTextUploadingField(blank=True)

    blog_title = models.CharField(max_length=255, blank=True)
    blog_header = models.CharField(max_length=255, blank=True)
    blog_header_image = models.ImageField(blank=True)
    blog_sidebar_image = models.ImageField(blank=True)
    blog_description = models.TextField(blank=True)
    blog_text = RichTextUploadingField(blank=True)

    services_title = models.CharField(max_length=255, blank=True)
    services_header = models.CharField(max_length=255, blank=True)
    services_header_image = models.ImageField(blank=True)
    services_description = models.TextField(blank=True)
    services_text = RichTextUploadingField(blank=True)
    services_cta = models.CharField(max_length=255, blank=True)
    services_cta_link = models.URLField(blank=True)
    services_testimonials_cta = models.CharField(max_length=255, blank=True)
    services_testimonials_cta_link = models.URLField(blank=True)

    online_design_title = models.CharField(max_length=255, blank=True)
    online_design_header_image = models.ImageField(blank=True)
    online_design_description = models.TextField(blank=True)
    online_design_button_text = models.CharField(max_length=255, blank=True)
    online_design_text = RichTextUploadingField(blank=True)

    design_for_diversity_title = models.CharField(max_length=255, blank=True)
    design_for_diversity_header_image = models.ImageField(blank=True)
    design_for_diversity_description = models.TextField(blank=True)

    designer_in_a_box_title = models.CharField(max_length=255, blank=True)
    designer_in_a_box_header_image = models.ImageField(blank=True)
    designer_in_a_box_description = models.TextField(blank=True)
    designer_in_a_box_content = RichTextUploadingField(blank=True)

    contact_title = models.CharField(max_length=255, blank=True)
    contact_header = models.CharField(max_length=255, blank=True)
    contact_header_image = models.ImageField(blank=True)
    contact_form_image = models.ImageField(blank=True)
    contact_description = models.TextField(blank=True)
    contact_text_1 = RichTextUploadingField(blank=True)
    contact_text_2 = RichTextUploadingField(blank=True)
    contact_form_text = RichTextUploadingField(blank=True)
    contact_submitted_texts = RichTextUploadingField(blank=True)
    contact_testimonials_cta = models.CharField(max_length=255, blank=True)
    contact_cta = models.CharField(max_length=255, blank=True)
    contact_cta_link = models.URLField(blank=True)

    testimonials_title = models.CharField(max_length=255, blank=True)
    testimonials_header = models.CharField(max_length=255, blank=True)
    testimonials_header_image = models.ImageField(blank=True)
    testimonials_description = models.TextField(blank=True)
    testimonials_text = RichTextUploadingField(blank=True)

    booking_title = models.CharField(max_length=255, blank=True)
    booking_cta = models.CharField(max_length=255, blank=True)
    booking_header_image = models.ImageField(blank=True)

    basket_header_image = models.ImageField(blank=True)

    apple_merchantid = models.TextField(blank=True, null=True)

    banner_text = RichTextField(blank=True, null=True)
    banner_link = models.URLField(blank=True, null=True)
    banner_enabled = models.BooleanField(blank=True)

    shop_title = models.CharField(max_length=255, blank=True)
    shop_header_image = models.ImageField(blank=True)
    shop_description = models.TextField(blank=True)
    shop_text = RichTextField(blank=True)

    faq_title = models.CharField(max_length=255, blank=True)
    faq_header = models.CharField(max_length=255, blank=True)
    faq_header_image = models.ImageField(blank=True)
    faq_description = models.TextField(blank=True)
    faq_cta = models.CharField(max_length=255, blank=True)
    faq_cta_link = models.URLField(blank=True)

    @property
    def address_nl(self):
        return self.address.replace("\r\n", "\n").replace("\n", "\\n")


class MainSliderImage(models.Model):
    name = models.CharField(max_length=255, default="", blank=True)
    image = models.ImageField(blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    url = models.URLField(default="", blank=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        compress_img(self.image)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Resource(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField()
    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = RichTextUploadingField()
    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    class Meta:
        verbose_name_plural = "FAQs"
        verbose_name = "FAQ"
        ordering = ['order']

    def __str__(self):
        return self.question


class ServiceGroup(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    draft = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    HOME_PAGE = 'M'
    SERVICES_PAGE = 'O'
    TYPES = (
        (HOME_PAGE, "Home page"),
        (SERVICES_PAGE, "Services page")
    )
    type = models.CharField(max_length=1, choices=TYPES, default=SERVICES_PAGE)
    image = models.ImageField(blank=True)
    home_page_image = models.ImageField(blank=True)
    home_cta = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    price = models.CharField(max_length=255, default="", blank=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=False)
    group = models.ForeignKey(ServiceGroup, on_delete=models.PROTECT, blank=True, null=True)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        compress_img(self.image)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ServiceButton(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='buttons')
    button_text = models.CharField(max_length=255, default="", blank=True)
    button_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.button_text


class ServiceSummary(models.Model):
    class Meta:
        verbose_name_plural = "Service Summaries"
        ordering = ['order']

    service = models.ForeignKey(Service, related_name="service_summaries", on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0, blank=True, null=False)


class OnlineDesignStep(models.Model):
    draft = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    image = models.ImageField(blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        compress_img(self.image)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class OnlineDesignStepButton(models.Model):
    step = models.ForeignKey(OnlineDesignStep, on_delete=models.CASCADE, related_name='buttons')
    button_text = models.CharField(max_length=255, default="", blank=True)
    button_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.button_text


class Project(models.Model):
    draft = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    area = models.CharField(max_length=255, blank=True)
    breif = models.TextField()
    outcome = models.TextField()
    image = models.ImageField(blank=True)
    image_alt_text = models.CharField(max_length=255, blank=True)
    header_image = models.ImageField(blank=True)
    photography_credits = models.TextField(blank=True)
    meta_description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        compress_img(self.image)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProjectItem(models.Model):
    project = models.ForeignKey(Project, related_name='items', on_delete=models.CASCADE)
    TEXT = 'T'
    IMAGE = 'I'
    TYPES = (
        (TEXT, "Text"),
        (IMAGE, "Image")
    )
    type = models.CharField(max_length=1, choices=TYPES, default=TEXT)
    image = models.ImageField(blank=True)
    image_alt_text = models.CharField(max_length=255, blank=True)
    hover_image = models.ImageField(blank=True)
    hover_image_alt_text = models.CharField(max_length=255, blank=True)
    text = models.TextField(blank=True)
    width = models.PositiveIntegerField(default=1)
    height = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        compress_img(self.image)
        compress_img(self.hover_image)
        super().save(*args, **kwargs)


class ProjectBeforeImage(models.Model):
    project = models.ForeignKey(Project, related_name='before_images', on_delete=models.CASCADE)
    image = models.ImageField(blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        compress_img(self.image)
        super().save(*args, **kwargs)


class ProjectAfterImage(models.Model):
    project = models.ForeignKey(Project, related_name='after_images', on_delete=models.CASCADE)
    image = models.ImageField(blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        compress_img(self.image)
        super().save(*args, **kwargs)


class Testimonial(models.Model):
    HOME_PAGE = 'H'
    ABOUT_PAGE = 'A'
    SERVICES_PAGE = 'S'
    CONTACT_PAGE = 'C'
    ONLINE_DESIGN_PAGE = 'O'
    DESIGN_FOR_DIVERSITY = 'D'
    FEATURED_ON = (
        ('', '---'),
        (HOME_PAGE, 'Home page'),
        (ABOUT_PAGE, 'About page'),
        (SERVICES_PAGE, 'Services page'),
        (CONTACT_PAGE, 'Contact page'),
        (ONLINE_DESIGN_PAGE, 'Online design page'),
        (DESIGN_FOR_DIVERSITY, 'Design for Diversity page'),
    )

    LIGHT = "L"
    DARK = "D"
    IMAGE = "I"
    STYLE = (
        (LIGHT, "Light"),
        (DARK, "Dark"),
        (IMAGE, "Image")
    )

    draft = models.BooleanField(default=False)
    text = models.TextField()
    image = models.ImageField(blank=True)
    client = models.CharField(max_length=255)
    featured_on = models.CharField(blank=True, null=True, choices=FEATURED_ON, max_length=1)
    style = models.CharField(choices=STYLE, max_length=1)
    not_on_testimonials = models.BooleanField(default=False, verbose_name="Not displayed on testimonials page")
    order = models.PositiveIntegerField(default=0, blank=True, null=False)
    related_project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        compress_img(self.image)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.client


class DesignInsiderPost(models.Model):
    draft = models.BooleanField(default=False)
    title = models.CharField(max_length=255)
    date = models.DateField()
    image = models.ImageField(blank=True)
    image_alt = models.CharField(verbose_name="Image alt text", max_length=255, blank=True)
    summary = models.TextField(blank=True)
    content = RichTextUploadingField(blank=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        compress_img(self.image)
        super().save(*args, **kwargs)

    @property
    def summarize(self):
        if len(self.summary.strip()):
            return self.summary

        soup = BeautifulSoup(self.content)
        for script in soup(["script", "style"]):
            script.extract()  # rip it out
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        tokens = sent_detector.tokenize(text)

        target_len = 400
        out = ""
        for token in tokens:
            if len(token) + len(out) > target_len:
                break
            out = f"{out} {token}"

        return out

    @property
    def read_time(self):
        try:
            return str(readtime.of_html(self.content))
        except Exception:
            return ""

    def __str__(self):
        return self.title


class DesignInsiderPostRelated(models.Model):
    post = models.ForeignKey(DesignInsiderPost, on_delete=models.CASCADE, related_name='related_posts')
    related_post = models.ForeignKey(DesignInsiderPost, on_delete=models.CASCADE, related_name='relatee_posts')
    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return str(self.related_post)


class ShortPost(models.Model):
    draft = models.BooleanField(default=False)
    title = models.CharField(max_length=255)
    date = models.DateField()
    content = RichTextUploadingField(blank=True)

    class Meta:
        get_latest_by = ['-date']
        ordering = ['-date']

    def __str__(self):
        return self.title


class ContactFormQuestion(models.Model):
    TYPE_ONE_LINE = "T"
    TYPE_MULTI_LINE = "M"
    TYPE_SELECT = "S"
    TYPE_MULTI_SELECT = "U"

    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    question = models.CharField(max_length=255)
    required = models.BooleanField()

    TYPES = (
        (TYPE_ONE_LINE, "One Line"),
        (TYPE_MULTI_LINE, "Multi-line"),
        (TYPE_SELECT, "Select"),
        (TYPE_MULTI_SELECT, "Multi-select"),
    )

    question_type = models.CharField(max_length=1, choices=TYPES)

    def __str__(self):
        return self.question

    class Meta:
        ordering = ['order']


class ContactFormQuestionOption(models.Model):
    question = models.ForeignKey(ContactFormQuestion, on_delete=models.CASCADE, related_name='options')
    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    option = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.question.question} - {self.option}"

    class Meta:
        ordering = ['order']


class NewsletterEntry(models.Model):
    mailchimp_id = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()

    class Meta:
        verbose_name_plural = "Newsletter entries"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


def validate_variable_name(value):
    if len(value) < 1:
        raise ValidationError("Variable name too short")
    if value[0] in string.digits:
        raise ValidationError("Variable cannot start with digit")

    valid_chars = string.ascii_letters + string.digits + "_"
    if any(c not in valid_chars for c in value):
        raise ValidationError("Variable contains invalid characters")


def validate_exec(value):
    try:
        ast.parse(value, mode='exec')
    except SyntaxError as e:
        raise ValidationError(f"Syntax error: {e.msg}")


def validate_eval(value):
    try:
        ast.parse(value, mode='eval')
    except SyntaxError as e:
        raise ValidationError(f"Syntax error: {e.msg}")


class Quiz(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    draft = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    intro_text = models.TextField()
    result_header = RichTextField(blank=True, null=True)
    result_save_to_email = RichTextField(blank=True, null=True)
    results_email_subject = models.CharField(max_length=255)
    results_email_header_background = models.ImageField(blank=True)
    results_email_header_logo = models.ImageField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class QuizVariables(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='variables')
    name = models.CharField(max_length=255, validators=[validate_variable_name])
    initial_value = models.TextField(validators=[validate_eval])

    def __str__(self):
        return self.name


class QuizStep(models.Model):
    STYLE_MOODBOARD = "mb"
    STYLE_IMAGE_GRID = "ig"
    STYLE_RADIO = "rb"
    STYLES = (
        (STYLE_RADIO, "Multiple choice / radio button"),
        (STYLE_MOODBOARD, "Image moodboard"),
        (STYLE_IMAGE_GRID, "Image grid"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.PositiveIntegerField(default=0, blank=True, null=False)
    max_choices = models.PositiveIntegerField(default=0, blank=True, null=False)
    style = models.CharField(max_length=2, choices=STYLES)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="steps")
    question_text = RichTextField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{str(self.quiz)}: step #{int(self.order)}"


class QuizStepAnswer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    step = models.ForeignKey(QuizStep, on_delete=models.CASCADE, related_name="answers")
    order = models.PositiveIntegerField(default=0, blank=True, null=False)
    text = RichTextField(blank=True, null=True)
    alt_text = models.TextField(blank=True, null=True)
    image = models.ImageField(blank=True, null=True)
    effect = models.TextField(blank=True, null=True, validators=[validate_exec])

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{str(self.step)}: answer #{int(self.order)}"


class QuizResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='results')
    order = models.PositiveIntegerField(default=0, blank=True, null=False)
    condition = models.TextField(blank=True, null=True, validators=[validate_eval])
    text = RichTextUploadingField()
    image = models.ImageField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    link_text = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{str(self.quiz)}: result #{int(self.order)}"


class QuizSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    current_step = models.ForeignKey(QuizStep, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)

    @property
    def result(self) -> typing.Optional[QuizResult]:
        variables = {}
        for variable in self.quiz.variables.all():
            variables[variable.name] = eval(variable.initial_value, {}, {})

        for answer in self.answers.order_by('answer__step__order').all():
            if answer.answer.effect:
                exec(answer.answer.effect, {}, variables)

        for result in self.quiz.results.all():
            if bool(eval(result.condition, {}, variables)):
                return result

        return None


class QuizSessionStepAnswer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(QuizSession, on_delete=models.CASCADE, related_name="answers")
    answer = models.ForeignKey(QuizStepAnswer, on_delete=models.CASCADE)


class PostageService(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    despatch_monday = models.BooleanField(blank=True, verbose_name="Despatch Monday")
    despatch_tuesday = models.BooleanField(blank=True, verbose_name="Despatch Tuesday")
    despatch_wednesday = models.BooleanField(blank=True, verbose_name="Despatch Wednesday")
    despatch_thursday = models.BooleanField(blank=True, verbose_name="Despatch Thursday")
    despatch_friday = models.BooleanField(blank=True, verbose_name="Despatch Friday")
    despatch_saturday = models.BooleanField(blank=True, verbose_name="Despatch Saturday")
    despatch_sunday = models.BooleanField(blank=True, verbose_name="Despatch Sunday")
    country = django_countries.fields.CountryField()
    cutoff_time = models.TimeField()
    timezone = models.CharField(max_length=255, default="Europe/London")
    handling_time_min = models.PositiveSmallIntegerField(verbose_name="Minimum handling time (days)")
    handling_time_max = models.PositiveSmallIntegerField(verbose_name="Maximum handling time (days)")
    transit_time_min = models.PositiveSmallIntegerField(verbose_name="Minimum transit time (days)")
    transit_time_max = models.PositiveSmallIntegerField(verbose_name="Maximum transit time (days)")
    order = models.PositiveIntegerField(default=0, blank=True, null=False)
    rm_service_code = models.CharField(max_length=255, blank=True, null=True, verbose_name="Royal Mail service code")

    class Meta:
        ordering = ['order']

    # Maximum volume of the postage service, in millilitres
    @property
    def max_volume(self):
        return self.types.annotate(
            volume=models.F('max_width') * models.F('max_height') * models.F('max_depth')
        ).aggregate(max_vol=models.Max('volume'))["max_vol"]

    @property
    def despatch_days_str(self):
        out = []

        if self.despatch_monday:
            out.append("Monday")
        if self.despatch_tuesday:
            out.append("Tuesday")
        if self.despatch_wednesday:
            out.append("Wednesday")
        if self.despatch_thursday:
            out.append("Thursday")
        if self.despatch_friday:
            out.append("Friday")
        if self.despatch_saturday:
            out.append("Saturday")
        if self.despatch_sunday:
            out.append("Sunday")

        return out

    @property
    def cutoff_time_utc_str(self):
        tz = pytz.timezone(self.timezone)
        cutoff_datetime = datetime.datetime.combine(datetime.datetime.now(), self.cutoff_time)
        cutoff_datetime_local = tz.localize(cutoff_datetime)
        offset_secs = cutoff_datetime_local.utcoffset().seconds
        offset_mins = offset_secs // 60
        offset_hours = offset_mins // 60
        offset_mins -= offset_hours * 60
        return f'{cutoff_datetime_local.strftime("%H:%M:%S")}{"+" if offset_hours >0 else "-"}{abs(offset_hours):0>2}:{offset_mins:0>2}'

    def delivery_time_range(self, timestamp=None, products=None):
        if not timestamp:
            timestamp = datetime.datetime.utcnow()

        if not timestamp.tzinfo:
            tz = pytz.timezone(self.timezone)
            timestamp = tz.fromutc(timestamp)

        back_order_days = 0

        if products is not None:
            back_ordered_products = list(filter(lambda p: p.back_ordered_days, products))
            if back_ordered_products:
                back_order_days = max(map(lambda p: p.back_ordered_days, back_ordered_products))

        despatch_days = [
            self.despatch_monday, self.despatch_tuesday, self.despatch_wednesday, self.despatch_thursday,
            self.despatch_friday, self.despatch_saturday, self.despatch_sunday,
        ]
        weekday = timestamp.weekday()

        past_cutoff = timestamp.time() > self.cutoff_time
        if past_cutoff:
            weekday += 1
            if weekday == 7:
                weekday = 0

        despatch_days = despatch_days[weekday:] + despatch_days[:weekday]
        next_despatch = next(filter(lambda d: d[1], enumerate(despatch_days)), None)
        if next_despatch is None:
            return None
        despatch_offset = next_despatch[0]
        despatch_offset = max(back_order_days, despatch_offset)
        handling_time_min = max(self.handling_time_min, despatch_offset)
        handling_time_max = max(self.handling_time_max, despatch_offset)

        times = handling_time_min + self.transit_time_min, handling_time_max + self.transit_time_max

        if past_cutoff:
            times = times[0] + 1, times[1] + 1

        return times

    @staticmethod
    def format_delivery_time_range(time_range):
        if time_range:
            if time_range[0] == time_range[1]:
                if time_range[0] == 1:
                    return "tomorrow"
                else:
                    return f"within {time_range[0]} days"
            else:
                return f"within {time_range[0]} to {time_range[1]} days"
        else:
            return None

    def formatted_delivery_time_range(self, timestamp=None, products=None):
        time_range = self.delivery_time_range(timestamp=timestamp, products=products)
        return self.format_delivery_time_range(time_range)

    def __str__(self):
        return self.name


class PostageServiceType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(PostageService, on_delete=models.CASCADE, related_name="types")
    name = models.CharField(max_length=255)
    max_weight = models.DecimalField(max_digits=9, decimal_places=4, default=0, verbose_name="Max weight (kg)")
    max_width = models.DecimalField(max_digits=9, decimal_places=2, default=0, verbose_name="Max width (cm)")
    max_height = models.DecimalField(max_digits=9, decimal_places=2, default=0, verbose_name="Max height (cm)")
    max_depth = models.DecimalField(max_digits=9, decimal_places=2, default=0, verbose_name="Max depth (cm)")
    price = models.DecimalField(max_digits=9, decimal_places=2)
    order = models.PositiveIntegerField(default=0, blank=True, null=False)
    rm_package_format_id = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Royal Mail package format identifier")

    class Meta:
        ordering = ['order']

    # Maximum volume of the postage method type, in millilitres
    @property
    def max_volume(self):
        return self.max_width * self.max_height * self.max_depth

    def __str__(self):
        return f"{self.service.name}: {self.name}"


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    header_image = models.ImageField(blank=True)
    image = models.ImageField(blank=True)
    description = RichTextField()
    draft = models.BooleanField(blank=True, default=False)
    noindex = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Brand(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    logo = models.ImageField(blank=True, null=True)

    def __str__(self):
        return self.name


def validate_gtin(value):
    if not gtin.validator.is_valid_GTIN(value):
        raise ValidationError("Not a valid GTIN")


class Product(models.Model):
    BACK_ORDER = "https://schema.org/BackOrder"
    DISCONTINUED = "https://schema.org/Discontinued"
    IN_STOCK = "https://schema.org/InStock"
    IN_STORE_ONLY = "https://schema.org/InStoryOnly"
    LIMITED_AVAILABILITY = "https://schema.org/LimitedAvailability"
    ONLINE_ONLY = "https://schema.org/OnlineOnly"
    OUT_OF_STOCK = "https://schema.org/OutOfStock"
    PRE_ORDER = "https://schema.org/PreOrdre"
    PRE_SALE = "https://schema.org/PreSale"
    SOLD_OUT = "https://schema.org/SoldOut"

    AVAILABILITY = (
        (BACK_ORDER, "Back order"),
        (DISCONTINUED, "Discontinued"),
        (IN_STOCK, "In stock"),
        (IN_STORE_ONLY, "In store only"),
        (LIMITED_AVAILABILITY, "Limited availability"),
        (ONLINE_ONLY, "Online only"),
        (OUT_OF_STOCK, "Out of stock"),
        (PRE_ORDER, "Pre order"),
        (PRE_SALE, "Pre sale"),
        (SOLD_OUT, "Sold out"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name="products", blank=True, null=True)
    name = models.CharField(max_length=255)
    noindex = models.BooleanField(blank=True, default=False)
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    description = RichTextField()
    extended_description = RichTextField(blank=True, null=True)
    header_image = models.ImageField(blank=True, null=True)
    gtin = models.CharField(max_length=255, validators=[validate_gtin], verbose_name="GTIN", blank=True, null=True)
    mpn = models.CharField(max_length=255, blank=True, null=True, verbose_name="Manufacturer part number")
    price = models.DecimalField(max_digits=9, decimal_places=2)
    availability = models.CharField(max_length=255, choices=AVAILABILITY)
    back_ordered_days = models.PositiveIntegerField(blank=True, null=True)
    draft = models.BooleanField(blank=True)
    weight = models.DecimalField(max_digits=9, decimal_places=4, default=0, verbose_name="Unit weight (kg)")
    width = models.DecimalField(max_digits=9, decimal_places=2, default=0, verbose_name="Unit width (cm)")
    height = models.DecimalField(max_digits=9, decimal_places=2, default=0, verbose_name="Unit height (cm)")
    depth = models.DecimalField(max_digits=9, decimal_places=2, default=0, verbose_name="Unit depth (cm)")
    delivery_info = RichTextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    class Meta:
        ordering = ['order']

    # Volume of one item, in millilitres
    @property
    def volume(self):
        return self.width * self.height * self.depth

    @property
    def all_postage_options(self):
        dims = [self.width, self.height, self.depth]
        return PostageServiceType.objects.filter(max_weight__gte=self.weight).filter(
            models.Q(max_width__gte=dims[0],  max_height__gte=dims[1], max_depth__gte=dims[2]) |
            models.Q(max_width__gte=dims[0],  max_depth__gte=dims[1],  max_height__gte=dims[2]) |
            models.Q(max_height__gte=dims[0], max_width__gte=dims[1],  max_depth__gte=dims[2]) |
            models.Q(max_height__gte=dims[0], max_depth__gte=dims[1],  max_width__gte=dims[2]) |
            models.Q(max_depth__gte=dims[0],  max_width__gte=dims[1],  max_height__gte=dims[2]) |
            models.Q(max_depth__gte=dims[0],  max_height__gte=dims[1], max_width__gte=dims[2])
        )

    @property
    def possible_postage_options(self):
        out = []
        options = self.all_postage_options
        services = {}
        for option in options:
            if option.service.id not in services:
                services[option.service.id] = []
            services[option.service.id].append(option)

        for options in services.values():
            out.append(options[0])

        return out

    __description_text = None

    def __str__(self):
        return f"{str(self.brand)}: {self.name}"

    @property
    def description_text(self):
        if self.__description_text:
            return self.__description_text

        soup = BeautifulSoup(self.description)
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()

        self.__description_text = text

        return text


class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField()
    alt = models.TextField()
    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    class Meta:
        ordering = ['order']


@dataclasses.dataclass
class PostageBin:
    service_type: PostageServiceType
    weight_grams: int
    items: typing.List[Product]


@dataclasses.dataclass
class PostageOption:
    service: PostageService
    description: str
    price: decimal.Decimal
    bins: typing.List[PostageBin]

    def to_json(self):
        return {
            "id": str(self.service.id),
            "description": self.description,
            "price": int(round(self.price * 100)),
            "bins": [{
                "service": str(bin.service_type.id),
                "items": [str(item.id) for item in bin.items],
                "weight": bin.weight_grams
            } for bin in self.bins]
        }

    @classmethod
    def from_json(cls, data):
        service = PostageService.objects.get(id=data["id"])
        return cls(
            service=service,
            description=data["description"],
            price=decimal.Decimal(data["price"]) / decimal.Decimal(100),
            bins=[PostageBin(
                service_type=PostageServiceType.objects.get(id=bin_data["service"]),
                weight_grams=bin_data["weight"],
                items=[Product.objects.get(id=item) for item in bin_data["items"]]
            ) for bin_data in data["bins"]]
        )


def get_basket_id():
    return base64.b32encode(secrets.token_bytes(5)).decode()


class Basket(models.Model):
    STATE_CREATION = "C"
    STATE_PAID = "P"

    STATES = (
        (STATE_CREATION, "Creation"),
        (STATE_PAID, "Paid"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    postage_service = models.ForeignKey(PostageService, on_delete=models.SET_NULL, blank=True, null=True)
    postage_service_bins = models.JSONField(blank=True, null=True)
    postage_address = models.ForeignKey('PostalAddress', on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField( blank=True, null=True)
    phone = PhoneNumberField(blank=True, null=True)
    state = models.CharField(max_length=1, choices=STATES, default=STATE_CREATION)
    payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    reference = models.CharField(max_length=64, default=get_basket_id)
    completed_date = models.DateTimeField(blank=True, null=True)
    rm_order_id = models.JSONField(max_length=255, blank=True, null=True, verbose_name="Royal Mail order ID")

    @property
    def disp_reference(self):
        return "-".join(self.reference[i:i+3] for i in range(0, len(self.reference), 3))

    def __str__(self):
        return self.disp_reference

    @property
    def item_quantity(self):
        return self.items.aggregate(models.Sum('quantity'))["quantity__sum"] or 0

    @property
    def items_total(self):
        return self.items.aggregate(
            total=models.Sum(models.F('product__price') * models.F('quantity'), output_field=models.DecimalField())
        )["total"] or decimal.Decimal(0)

    @property
    def can_checkout(self):
        return bool(len(self.items.all()))

    @property
    def postage_service_bins_obj(self):
        return PostageOption.from_json(self.postage_service_bins)

    def possible_postage_options(self, country: str) -> typing.List[PostageOption]:
        @dataclasses.dataclass
        class Item:
            id: uuid.UUID
            service_types: typing.List[PostageServiceType]
            product: Product

        services = {}
        all_item_ids = set()

        for item in self.items.all():
            postage_options = item.product.all_postage_options
            seen_services = set()
            for option in postage_options:
                if option.service.country.code == country:
                    if option.service.id in seen_services:
                        continue

                    seen_services.add(option.service.id)
                    if option.service not in services:
                        services[option.service] = []

                    service_types = list(filter(lambda o: o.service.id == option.service.id, postage_options))

                    for _ in range(item.quantity):
                        item_id = uuid.uuid4()
                        all_item_ids.add(item_id)
                        services[option.service].append(Item(
                            id=item_id,
                            service_types=service_types,
                            product=item.product
                        ))

        @dataclasses.dataclass
        class Bin:
            max_vol: decimal.Decimal
            max_weight: decimal.Decimal
            service_type: PostageServiceType
            service_types: typing.List[PostageServiceType]
            items: list

            @property
            def cur_vol(self):
                return sum(map(lambda i: i.product.volume, self.items))

            @property
            def cur_weight(self):
                return sum(map(lambda i: i.product.weight, self.items))

            def insert(self, extra_item: Item):
                if self.cur_vol + extra_item.product.volume < self.max_vol and \
                        self.cur_weight + extra_item.product.weight < self.max_weight and \
                        any(s in self.service_types for s in extra_item.service_types):
                    self.items.append(extra_item)
                    self.service_types = list(filter(lambda t: t in extra_item.service_types, self.service_types))
                    return True

                for poss_new_service in self.service_types:
                    if poss_new_service in extra_item.service_types:
                        if self.cur_vol + extra_item.product.volume < poss_new_service.max_volume and \
                                self.cur_weight + extra_item.product.weight < poss_new_service.max_weight:
                            self.service_type = poss_new_service
                            self.items.append(extra_item)
                            self.service_types.remove(poss_new_service)
                            self.service_types = list(
                                filter(lambda t: t in extra_item.service_types, self.service_types)
                            )
                            self.max_vol = poss_new_service.max_volume
                            self.max_weight = poss_new_service.max_weight
                            return True

        @dataclasses.dataclass
        class ServiceOption:
            service: PostageService
            items: typing.List[Item]
            bins: typing.List[Bin]

        services = services.items()
        service_options = []

        for i, (service, items) in enumerate(services):
            bins = []
            for item in items:
                found = False

                for poss_bin in bins:
                    if poss_bin.insert(item):
                        found = True
                        break

                if not found:
                    bins.append(Bin(
                        item.service_types[0].max_volume,
                        item.service_types[0].max_weight,
                        item.service_types[0],
                        item.service_types[1:],
                        [item]
                    ))

            service_options.append(ServiceOption(
                service=service,
                items=items,
                bins=bins
            ))

        out_options = []

        for service_option in service_options:
            if all(i in all_item_ids for i in map(lambda i: i.id, service_option.items)):
                delivery_time_range = service_option.service.formatted_delivery_time_range(
                    products=list(map(lambda i: i.product, service_option.items))
                )
                if delivery_time_range:
                    desc = f"Arrives {delivery_time_range}"
                else:
                    desc = "Delivery estimate unavailable"

                out_bins = []
                price = decimal.Decimal(0)
                for in_bin in service_option.bins:
                    out_bins.append(PostageBin(
                        service_type=in_bin.service_type,
                        items=list(map(lambda i: i.product, in_bin.items)),
                        weight_grams=int(round(in_bin.cur_weight * 1000)),
                    ))
                    price += in_bin.service_type.price

                out_options.append(PostageOption(
                    service=service_option.service,
                    description=desc,
                    bins=out_bins,
                    price=price
                ))

        return out_options


class BasketItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="baskets")
    quantity = models.PositiveIntegerField(default=0)

    @property
    def total_price(self):
        return self.product.price * self.quantity


class PostalAddress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    address_line3 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255)
    region = models.CharField(max_length=255, blank=True, null=True)
    post_code = models.CharField(max_length=255, blank=True, null=True)
    country = django_countries.fields.CountryField(blank_label="")
    delivery_notes = models.TextField(blank=True, null=True)

    @property
    def as_formatted_address(self):
        out = self.address_line1
        if self.address_line2:
            out += f"\r\n{self.address_line2}"
        if self.address_line3:
            out += f"\r\n{self.address_line3}"
        out += f"\r\n{self.city}"
        if self.region:
            out += f"\r\n{self.region}"
        if self.post_code:
            out += f"\r\n{self.post_code}"
        out += f"\r\n{self.country.name}"

        return out
