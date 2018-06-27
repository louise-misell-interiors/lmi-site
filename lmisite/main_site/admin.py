from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import *


class ProjectBeforeImageInline(admin.TabularInline):
    model = ProjectBeforeImage
    extra = 3


class ProjectAfterImageInline(admin.TabularInline):
    model = ProjectAfterImage
    extra = 3


class ProjectAdmin(admin.ModelAdmin):
    inlines = [ProjectBeforeImageInline, ProjectAfterImageInline]


class ServiceSummarryInline(admin.TabularInline):
    model = ServiceSummary
    extra = 3


class ServiceAdmin(admin.ModelAdmin):
    inlines = [ServiceSummarryInline]


class AboutImageInline(admin.TabularInline):
    model = AboutSectionImage
    extra = 3


class AboutAdmin(admin.ModelAdmin):
    inlines = [AboutImageInline]


admin.site.register(SiteConfig, SingletonModelAdmin)
admin.site.register(MainSliderImage)
admin.site.register(Testimonial)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(AboutSection, AboutAdmin)
