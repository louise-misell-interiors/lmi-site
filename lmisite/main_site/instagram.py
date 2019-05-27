from . import models
from . import views
import requests


def get_user_feed():
    creds = views.get_credentials()
    if creds is None:
        return []

    config = models.SiteConfig.objects.first()
    if config.facebook_page_id is None or config.facebook_page_id == "":
        return []

    r = requests.get(f"https://graph.facebook.com/v3.3/{config.facebook_page_id}?fields=instagram_business_account"
                     f"{{name,media{{media_type,media_url,permalink,caption}}}}", params={"access_token": creds})
    r.raise_for_status()
    media = r.json()["instagram_business_account"]["media"]["data"]

    media = list(filter(lambda m: m["media_type"] == "IMAGE", media))

    return media
