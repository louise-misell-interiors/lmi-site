from PIL import Image as Img
import io
import readtime
import nltk.data
from bs4 import BeautifulSoup
from django.db import models
from solo.models import SingletonModel
from phonenumber_field.modelfields import PhoneNumberField
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile, InMemoryUploadedFile
from ckeditor_uploader.fields import RichTextUploadingField

sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')


def compress_img(image, new_width=1500):
    if bool(image) and image.file is not None and isinstance(image.file, UploadedFile):
        img = Img.open(io.BytesIO(image.read()))
        img.thumbnail((new_width, new_width * image.height / image.width), Img.ANTIALIAS)
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
    notification_email = models.EmailField(default="", blank=True)
    mobile = PhoneNumberField(blank=True)
    phone = PhoneNumberField(blank=True)
    address = models.TextField(default="", blank=True)

    privacy_policy = models.FileField(blank=True)
    terms_and_conditions = models.FileField(blank=True)

    image_slider_speed = models.PositiveIntegerField(default=5000, verbose_name="Home page image slider speed (ms)")
    testimonials_slider_speed = \
        models.PositiveIntegerField(default=10000, verbose_name="Home page testimonials slider speed (ms)")

    price_range = models.CharField(max_length=255, blank=True)

    home_title = models.CharField(max_length=255, blank=True)
    home_description = models.TextField(blank=True)
    home_subtitle = models.CharField(max_length=255, blank=True)
    home_about_text = RichTextUploadingField(blank=True)
    home_about_cta = models.CharField(max_length=255, blank=True)
    home_help_text = RichTextUploadingField(blank=True, verbose_name="Home how can I help text")
    home_help_image = models.ImageField(blank=True, verbose_name="Home how can I help background image")
    home_help_cta = models.CharField(max_length=255, blank=True)
    home_testimonials_cta = models.CharField(max_length=255, blank=True)

    about_title = models.CharField(max_length=255, blank=True)
    about_header_image = models.ImageField(blank=True)
    about_image_2 = models.ImageField(blank=True)
    about_description = models.TextField(blank=True)
    about_mission_statement = RichTextUploadingField(blank=True)
    about_text = RichTextUploadingField(blank=True)
    about_text_2 = RichTextUploadingField(blank=True)
    about_cta = models.CharField(max_length=255, blank=True)
    about_testimonials_cta = models.CharField(max_length=255, blank=True)

    resources_title = models.CharField(max_length=255, blank=True)
    resources_image = models.ImageField(blank=True)
    resources_description = models.TextField(blank=True)
    resources_text = RichTextUploadingField(blank=True)

    portfolio_title = models.CharField(max_length=255, blank=True)
    portfolio_header_image = models.ImageField(blank=True)
    portfolio_description = models.TextField(blank=True)
    portfolio_text = RichTextUploadingField(blank=True)

    blog_title = models.CharField(max_length=255, blank=True)
    blog_header_image = models.ImageField(blank=True)
    blog_description = models.TextField(blank=True)
    blog_text = RichTextUploadingField(blank=True)

    services_title = models.CharField(max_length=255, blank=True)
    services_header_image = models.ImageField(blank=True)
    services_description = models.TextField(blank=True)
    services_text = RichTextUploadingField(blank=True)
    services_cta = models.CharField(max_length=255, blank=True)
    services_testimonials_cta = models.CharField(max_length=255, blank=True)

    online_design_title = models.CharField(max_length=255, blank=True)
    online_design_header_image = models.ImageField(blank=True)
    online_design_description = models.TextField(blank=True)
    online_design_button_text = models.CharField(max_length=255, blank=True)
    online_design_text = RichTextUploadingField(blank=True)

    design_for_diversity_title = models.CharField(max_length=255, blank=True)
    design_for_diversity_header_image = models.ImageField(blank=True)
    design_for_diversity_description = models.TextField(blank=True)

    contact_title = models.CharField(max_length=255, blank=True)
    contact_header_image = models.ImageField(blank=True)
    contact_form_image = models.ImageField(blank=True)
    contact_description = models.TextField(blank=True)
    contact_text_1 = RichTextUploadingField(blank=True)
    contact_text_2 = RichTextUploadingField(blank=True)
    contact_testimonials_cta = models.CharField(max_length=255, blank=True)

    testimonials_title = models.CharField(max_length=255, blank=True)
    testimonials_header_image = models.ImageField(blank=True)
    testimonials_description = models.TextField(blank=True)
    testimonials_text = RichTextUploadingField(blank=True)

    booking_title = models.CharField(max_length=255, blank=True)
    booking_header_image = models.ImageField(blank=True)

    apple_merchantid = models.TextField(blank=True, null=True)


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


class ServiceGroup(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    draft = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    MAIN = 'M'
    OTHER = 'O'
    TYPES = (
        (MAIN, "Main"),
        (OTHER, "Other")
    )
    type = models.CharField(max_length=1, choices=TYPES, default=MAIN)
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
        verbose_name_plural = "Serivce Summaries"
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


class NewsletterEntry(models.Model):
    mailchimp_id = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()

    class Meta:
        verbose_name_plural = "Newsletter entries"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
