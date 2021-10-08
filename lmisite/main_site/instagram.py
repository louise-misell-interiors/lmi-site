from . import views
import requests
import requests.exceptions


def get_user_feed():
    creds = views.get_instagram_credentials()
    if creds is None:
        return []

    try:
        r = requests.get(
            "https://graph.instagram.com/me/media", params={
                "access_token": creds,
                "fields": "id,caption,media_url,permalink,media_type"
            }, timeout=3
        )
    except requests.exceptions.Timeout:
        return []
    except requests.exceptions.ConnectionError:
        return []
    if r.status_code != 200:
        return []
    media = r.json().get("data", [])

    media = list(filter(lambda m: m["media_type"] in ("IMAGE", "CAROUSEL_ALBUM"), media))

    return media
