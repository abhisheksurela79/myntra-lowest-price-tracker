import json
import requests


def fetched_header():
    url = "https://www.myntra.com/beacon/user-data"
    payload = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    raw_cookies = response.cookies
    cookies = {'_abck': raw_cookies['_abck'], '_pv': raw_cookies['_pv'],
               '_xsrf': raw_cookies['_xsrf'], 'ak_bmsc': raw_cookies['ak_bmsc'], 'at': raw_cookies['at'],
               'bc': raw_cookies['bc'], 'bm_sz': raw_cookies['bm_sz'], 'dp': raw_cookies['dp'],
               'lt_session': raw_cookies['lt_session'], 'lt_timeout': raw_cookies['lt_timeout'],
               'microsessid': raw_cookies['microsessid'], 'user_session': raw_cookies['user_session'],
               'utm_track_v1': raw_cookies['utm_track_v1'], 'utrid': raw_cookies['utrid'],
               'akaas_myntra_SegmentationLabel': raw_cookies['akaas_myntra_SegmentationLabel']}

    return {"payload": payload, "headers": headers, "cookies": cookies}

