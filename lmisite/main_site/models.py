from PIL import Image as Img
import io
from django.db import models
from solo.models import SingletonModel
from phonenumber_field.modelfields import PhoneNumberField
from django.core.files.uploadedfile import UploadedFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from ckeditor_uploader.fields import RichTextUploadingField


def compress_img(image, new_width=1500):
    if bool(image) and image.file is not None and isinstance(image.file, UploadedFile):
        img = Img.open(io.BytesIO(image.read()))
        img.thumbnail((new_width, new_width * image.height / image.width), Img.ANTIALIAS)
        output = io.BytesIO()
        if img.mode == 'RGBA':
            background = Img.new("RGB", image.size, (255, 255, 255))
            background.paste(img, img.split()[-1])
            img = background
        img.save(output, format='JPEG', quality=80, optimise=True)
        output.seek(0)
        return InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % image.name.split('.')[0], 'image/jpeg',
                                    len(output.getvalue()), None)
    else:
        return image


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
    home_about_text = models.TextField(blank=True)
    home_help_text = models.TextField(blank=True, verbose_name="Home how can I help text")

    about_title = models.CharField(max_length=255, blank=True)
    about_description = models.TextField(blank=True)
    about_mission_statement = models.TextField(blank=True)
    about_text = RichTextUploadingField(blank=True)

    portfolio_title = models.CharField(max_length=255, blank=True)
    portfolio_description = models.TextField(blank=True)
    portfolio_text = models.TextField(blank=True)

    blog_title = models.CharField(max_length=255, blank=True)
    blog_description = models.TextField(blank=True)
    blog_text = models.TextField(blank=True)

    services_title = models.CharField(max_length=255, blank=True)
    services_description = models.TextField(blank=True)
    services_text = models.TextField(blank=True)

    contact_title = models.CharField(max_length=255, blank=True)
    contact_description = models.TextField(blank=True)
    contact_text_1 = models.TextField(blank=True)
    contact_text_2 = models.TextField(blank=True)

    testimonials_title = models.CharField(max_length=255, blank=True)
    testimonials_description = models.TextField(blank=True)
    testimonials_text = models.TextField(blank=True)


class MainSliderImage(models.Model):
    name = models.CharField(max_length=255, default="", blank=True)
    image = models.ImageField(blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        self.image = compress_img(self.image)
        super().save(*args, **kwargs)

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
    description = models.TextField(blank=True)
    price = models.CharField(max_length=255, default="", blank=True)
    button_text = models.CharField(max_length=255, default="", blank=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        self.image = compress_img(self.image)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ServiceSummary(models.Model):
    class Meta:
        verbose_name_plural = "Serivce Summaries"
        ordering = ['order']

    service = models.ForeignKey(Service, related_name="service_summaries", on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0, blank=True, null=False)


class Project(models.Model):
    draft = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    area = models.CharField(max_length=255, blank=True)
    breif = models.TextField()
    outcome = models.TextField()
    image = models.ImageField(blank=True)
    image_alt_text = models.CharField(max_length=255, blank=True)
    photography_credits = models.TextField(blank=True)
    meta_description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        self.image = compress_img(self.image)
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
        self.image = compress_img(self.image)
        self.hover_image = compress_img(self.hover_image)
        super().save(*args, **kwargs)


class ProjectBeforeImage(models.Model):
    project = models.ForeignKey(Project, related_name='before_images', on_delete=models.CASCADE)
    image = models.ImageField(blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        self.image = compress_img(self.image)
        super().save(*args, **kwargs)


class ProjectAfterImage(models.Model):
    project = models.ForeignKey(Project, related_name='after_images', on_delete=models.CASCADE)
    image = models.ImageField(blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        self.image = compress_img(self.image)
        super().save(*args, **kwargs)


class Testimonial(models.Model):
    HOME_PAGE = 'H'
    ABOUT_PAGE = 'H'
    FEATURED_ON = (
        ('', '---'),
        (HOME_PAGE, 'Home page'),
        (ABOUT_PAGE, 'About page'),
    )

    draft = models.BooleanField(default=False)
    text = models.TextField()
    image = models.ImageField(blank=True)
    client = models.CharField(max_length=255)
    featured_on = models.CharField(blank=True, null=True, choices=FEATURED_ON)
    not_on_testimonials = models.BooleanField(default=False, verbose_name="Not displayed on testimonials page")
    order = models.PositiveIntegerField(default=0, blank=True, null=False)
    related_project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        self.image = compress_img(self.image)
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
        self.image = compress_img(self.image)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


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
    google_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Newsletter entries"

    def __str__(self):
        return self.google_id
