from .models import SiteConfig
from . import instagram


def config_processor(request):
    config = SiteConfig.objects.first()

    instagram_feed = instagram.get_user_feed()[:10]
    return {'config': config, 'instagram': instagram_feed}
