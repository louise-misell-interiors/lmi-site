from .models import SiteConfig
from . import instagram, shop
from django.conf import settings


def config_processor(request):
    config = SiteConfig.objects.first()
    basket = shop.get_basket(request, create=False)

    instagram_feed = instagram.get_user_feed()[:12]
    return {
        "config": config,
        "instagram": instagram_feed,
        "basket": basket,
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY
    }
