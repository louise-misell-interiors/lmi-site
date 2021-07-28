from django.contrib import admin
from solo.admin import SingletonModelAdmin
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from .models import *
from .forms import *


class ProjectBeforeImageInline(SortableInlineAdminMixin, admin.TabularInline):
    model = ProjectBeforeImage
    extra = 3


class ProjectAfterImageInline(SortableInlineAdminMixin, admin.TabularInline):
    model = ProjectAfterImage
    extra = 3


class ProjectItemInline(SortableInlineAdminMixin, admin.StackedInline):
    model = ProjectItem
    fields = (
        ('type',),
        ('image', 'image_alt_text', 'hover_image', 'hover_image_alt_text',),
        ('text',),
        ('width', 'height',),
    )
    extra = 3


@admin.register(Project)
class ProjectAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = [ProjectItemInline]


class ServiceSummaryInline(SortableInlineAdminMixin, admin.TabularInline):
    model = ServiceSummary
    extra = 3


class ServiceButtonInline(admin.TabularInline):
    model = ServiceButton
    extra = 1


@admin.register(Service)
class ServiceAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = [ServiceSummaryInline, ServiceButtonInline]


@admin.register(ServiceGroup)
class ServiceAdmin(admin.ModelAdmin):
    pass


class OnlineDesignStepButtonInline(admin.TabularInline):
    model = OnlineDesignStepButton
    extra = 1


@admin.register(OnlineDesignStep)
class OnlineDesignStepAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = [OnlineDesignStepButtonInline]


@admin.register(Testimonial)
class TestimonialAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


@admin.register(Resource)
class ResourceAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


@admin.register(MainSliderImage)
class MainSliderImageAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


@admin.register(SiteConfig)
class SiteConfigAdmin(SingletonModelAdmin):
    form = ConfigForm


class DesignInsiderPostRelatedInline(SortableInlineAdminMixin, admin.TabularInline):
    fk_name = 'post'
    model = DesignInsiderPostRelated
    extra = 3


@admin.register(DesignInsiderPost)
class DesignInsiderPostAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = [DesignInsiderPostRelatedInline]


@admin.register(ShortPost)
class ShortPostAdmin(admin.ModelAdmin):
    pass


@admin.register(NewsletterEntry)
class NewsletterEntryAdmin(admin.ModelAdmin):
    pass


class QuizVariableInline(admin.TabularInline):
    exclude = ["id"]
    model = QuizVariables
    extra = 3


class QuizStepInline(SortableInlineAdminMixin, admin.StackedInline):
    exclude = ["id"]
    model = QuizStep
    extra = 3
    show_change_link = True


class QuizResultInline(SortableInlineAdminMixin, admin.StackedInline):
    exclude = ["id"]
    model = QuizResult
    extra = 3


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    inlines = [QuizVariableInline, QuizStepInline, QuizResultInline]
    readonly_fields = ["id"]


class QuizStepAnswerInline(SortableInlineAdminMixin, admin.StackedInline):
    exclude = ["id"]
    model = QuizStepAnswer
    extra = 3


@admin.register(QuizStep)
class QuizStepAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = [QuizStepAnswerInline]
    exclude = ["id"]


class ProductImageInline(SortableInlineAdminMixin, admin.StackedInline):
    exclude = ["id"]
    model = ProductImage
    extra = 3


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    exclude = ["id"]


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


class BasketItemInline(admin.StackedInline):
    exclude = ["id"]
    model = BasketItem
    extra = 0


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    inlines = [BasketItemInline]
    exclude = ["id"]


class PostageServiceTypeInline(SortableInlineAdminMixin, admin.StackedInline):
    exclude = ["id"]
    model = PostageServiceType
    extra = 3


@admin.register(PostageService)
class PostageServiceAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = [PostageServiceTypeInline]


admin.site.site_header = "Louise Misell Interiors"
admin.site.site_title = "Louise Misell Interiors"
admin.site.index_title = "Home"
