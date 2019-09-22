from .models import SiteConfig


def config_processor(request):
    config = SiteConfig.objects.first()
    return {"config": config}
