from django.contrib import admin
from solo.admin import SingletonModelAdmin
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from .models import *


class ProjectBeforeImageInline(SortableInlineAdminMixin, admin.TabularInline):
    model = ProjectBeforeImage
    extra = 3


class ProjectAfterImageInline(SortableInlineAdminMixin, admin.TabularInline):
    model = ProjectAfterImage
    extra = 3


@admin.register(Project)
class ProjectAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = [ProjectBeforeImageInline, ProjectAfterImageInline]


class ServiceSummaryInline(SortableInlineAdminMixin, admin.TabularInline):
    model = ServiceSummary
    extra = 3


@admin.register(Service)
class ServiceAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = [ServiceSummaryInline]


class AboutImageInline(SortableInlineAdminMixin, admin.TabularInline):
    model = AboutSectionImage
    extra = 3


@admin.register(AboutSection)
class AboutAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = [AboutImageInline]


@admin.register(Testimonial)
class TestimonialAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


@admin.register(MainSliderImage)
class MainSliderImageAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


@admin.register(SiteConfig)
class SiteConfigAdmin(SingletonModelAdmin):
    pass


@admin.register(DesignInsiderPost)
class DesignInsiderPostAdmin(admin.ModelAdmin):
    pass


@admin.register(ShortPost)
class ShortPostAdmin(admin.ModelAdmin):
    pass


@admin.register(NewsletterEntry)
class NewsletterEntryAdmin(admin.ModelAdmin):
    pass


admin.site.site_header = "Louise Misell Interiors"
admin.site.site_title = "Louise Misell Interiors"
admin.site.index_title = "Home"
