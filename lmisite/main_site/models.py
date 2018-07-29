from PIL import Image as Img
import io
from django.db import models
from solo.models import SingletonModel
from phonenumber_field.modelfields import PhoneNumberField
from django.core.files.uploadedfile import InMemoryUploadedFile
from ckeditor_uploader.fields import RichTextUploadingField


def compress_img(image, new_width=1500):
    img = Img.open(io.BytesIO(image.read()))
    img.thumbnail((new_width, new_width * image.height / image.width), Img.ANTIALIAS)
    output = io.BytesIO()
    if img.mode == 'RGBA':
        background = Img.new("RGB", image.size, (255, 255, 255))
        background.paste(image, image.split()[-1])
        image = background
    img.save(output, format='JPEG', quality=80, optimise=True)
    output.seek(0)
    return InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % image.name.split('.')[0], 'image/jpeg',
                                len(output.getvalue()), None)


class SiteConfig(SingletonModel):
    instagram_url = models.URLField(default="", blank=True)
    pintrest_url = models.URLField(default="", blank=True)
    facebook_url = models.URLField(default="", blank=True)
    linkedin_url = models.URLField(default="", blank=True)
    houzz_url = models.URLField(default="", blank=True)

    email = models.EmailField(default="", blank=True)
    mobile = PhoneNumberField(blank=True)
    phone = PhoneNumberField(blank=True)
    address = models.TextField(default="", blank=True)

    privacy_policy = models.FileField(blank=True)
    terms_and_conditions = models.FileField(blank=True)

    image_slider_speed = models.PositiveIntegerField(default=5000, verbose_name="Home page image slider speed (ms)")
    testimonials_slider_speed = \
        models.PositiveIntegerField(default=10000, verbose_name="Home page testimonials slider speed (ms)")


class MainSliderImage(models.Model):
    name = models.CharField(max_length=255, default="", blank=True)
    image = models.ImageField(blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        if self.image:
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
    icon = models.CharField(max_length=255)
    description = models.TextField()
    price = models.CharField(max_length=255, default="", blank=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    class Meta:
        ordering = ['order']

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
    breif = models.TextField()
    outcome = models.TextField()
    image = models.ImageField(blank=True)
    image_alt_text = models.CharField(max_length=255, blank=True)
    photography_credits = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        if self.image:
            self.image = compress_img(self.image)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProjectBeforeImage(models.Model):
    project = models.ForeignKey(Project, related_name='before_images', on_delete=models.CASCADE)
    image = models.ImageField(blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        if self.image:
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
        if self.image:
            self.image = compress_img(self.image)
        super().save(*args, **kwargs)


class AboutSection(models.Model):
    draft = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    heading = models.CharField(max_length=255, default="", blank=True)
    text = models.TextField()
    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class AboutSectionImage(models.Model):
    section = models.ForeignKey(AboutSection, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        if self.image:
            self.image = compress_img(self.image)
        super().save(*args, **kwargs)


class Testimonial(models.Model):
    draft = models.BooleanField(default=False)
    text = models.TextField()
    image = models.ImageField(blank=True)
    image_alt_text = models.CharField(max_length=255, blank=True)
    client = models.CharField(max_length=255)
    featured = models.BooleanField(default=False, verbose_name="Featured on home page")
    not_on_testimonials = models.BooleanField(default=False, verbose_name="Not displayed on testimonials page")
    order = models.PositiveIntegerField(default=0, blank=True, null=False)
    related_project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        if self.image:
            self.image = compress_img(self.image)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.client


class DesignInsiderPost(models.Model):
    draft = models.BooleanField(default=False)
    title = models.CharField(max_length=255)
    date = models.DateField()
    image = models.ImageField(blank=True)
    summary = models.TextField(blank=True)
    content = RichTextUploadingField(blank=True)

    class Meta:
        get_latest_by = ['-date']
        ordering = ['-date']

    def save(self, *args, **kwargs):
        if self.image:
            self.image = compress_img(self.image)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
