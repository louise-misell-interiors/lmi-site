from django.db import models
from solo.models import SingletonModel
from phonenumber_field.modelfields import PhoneNumberField


class SiteConfig(SingletonModel):
    instagram_url = models.URLField(default="", blank=True)
    pintrest_url = models.URLField(default="", blank=True)
    facebook_url = models.URLField(default="", blank=True)
    linkedin_url = models.URLField(default="", blank=True)
    houzz_url = models.URLField(default="", blank=True)

    calendly_url = models.CharField(max_length=255, blank=True)

    email = models.EmailField(default="", blank=True)
    mobile = PhoneNumberField(blank=True)
    phone = PhoneNumberField(blank=True)
    address = models.TextField(default="", blank=True)


class MainSliderImage(models.Model):
    name = models.CharField(max_length=255, default="", blank=True)
    image = models.ImageField()

    def __str__(self):
        return self.name


class Testimonial(models.Model):
    text = models.TextField()
    image = models.ImageField()
    client = models.CharField(max_length=255)
    featured = models.BooleanField(default=False)

    def __str__(self):
        return self.client


class Service(models.Model):
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

    def __str__(self):
        return self.name


class ServiceSummary(models.Model):
    class Meta:
        verbose_name_plural = "Serivce Summaries"

    service = models.ForeignKey(Service, related_name="service_summaries", on_delete=models.CASCADE)
    text = models.CharField(max_length=255)


class Project(models.Model):
    name = models.CharField(max_length=255)
    breif = models.TextField()
    outcome = models.TextField()

    def __str__(self):
        return self.name


class ProjectBeforeImage(models.Model):
    project = models.ForeignKey(Project, related_name='before_images', on_delete=models.CASCADE)
    image = models.ImageField()


class ProjectAfterImage(models.Model):
    project = models.ForeignKey(Project, related_name='after_images', on_delete=models.CASCADE)
    image = models.ImageField()


class AboutSection(models.Model):
    name = models.CharField(max_length=255)
    heading = models.CharField(max_length=255, default="", blank=True)
    text = models.TextField()

    def __str__(self):
        return self.name


class AboutSectionImage(models.Model):
    section = models.ForeignKey(AboutSection, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField()
