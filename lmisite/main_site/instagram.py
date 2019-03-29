import requests
import hashlib
import json

BASE_URL = 'https://www.instagram.com/'
QUERY_MEDIA = BASE_URL + 'graphql/query/?query_hash=f2405b236d85e8296cf30347c9f08c2a&variables={0}'
QUERY_MEDIA_VARS = '{{"id":"{0}","first":50,"after":"{1}"}}'


def get_shared_data(user):
    user_page = requests.get(user, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0"
    })
    shared_data = json.loads(user_page.text.split("window._sharedData = ")[1].split(";</script>")[0])
    return shared_data


def get_ig_gis(rhx_gis, params):
    data = rhx_gis + ":" + params
    return hashlib.md5(data.encode('utf-8')).hexdigest()


def get_user_data(user_id, rhx_gis):
    params = QUERY_MEDIA_VARS.format(user_id, '')

    resp = requests.get(QUERY_MEDIA.format(params), headers={
        "X-Instagram-GIS": get_ig_gis(rhx_gis, params),
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0"
    })
    return resp.json()


def get_user_feed(user):
    shared_data = get_shared_data(user)
    rhx_gis = shared_data['rhx_gis']
    user_id = shared_data['entry_data']['ProfilePage'][0]['graphql']['user']["id"]

    resp = get_user_data(user_id, rhx_gis)
    nodes = [n for n in (n['node'] for n in resp['data']['user']['edge_owner_to_timeline_media']['edges'])
             if not n['is_video']]

    return nodes
