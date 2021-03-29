from . import models
from . import views
import requests
import requests.exceptions


def get_user_feed():
    creds = views.get_fb_credentials()
    if creds is None:
        return []

    config = models.SiteConfig.objects.first()
    if config.facebook_page_id is None or config.facebook_page_id == "":
        return []

    try:
        r = requests.get(f"https://graph.facebook.com/v3.3/{config.facebook_page_id}?fields=instagram_business_account"
                         f"{{name,media{{media_type,media_url,permalink,caption}}}}", params={"access_token": creds}, timeout=3)
    except requests.exceptions.Timeout:
        return []
    if r.status_code != 200:
        return []
    media = r.json().get("instagram_business_account", {}).get("media", {}).get("data", [])

    media = list(filter(lambda m: m["media_type"] in ("IMAGE", "CAROUSEL_ALBUM"), media))

    return media
