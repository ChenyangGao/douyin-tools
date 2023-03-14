#!/usr/bin/env python3
# coding: utf-8

__all__ = ["check_if_logged", "get_userid", "get_live_info"]

import requests

from json import loads
from urllib.parse import unquote

from .cookies import cookie_list_to_cookiejar
from .text import text_within


HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7', 
    'accept-encoding': 'gzip, deflate, br', 
    'accept-language': 'zh-CN,zh;q=0.9,und;q=0.8', 
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36', 
    'cookie': '__ac_nonce=', 
}


def check_if_logged(cookies):
    # NOTE: 这个接口还可以检测直播间是否存在、是否在播等等，但需要已登录的 cookies
    if not cookies:
        return False
    url = 'https://live.douyin.com/webcast/room/chat/'
    if isinstance(cookies, str):
        resp = requests.get(url, headers={"cookie": cookies})
    else:
        if isinstance(cookies, list):
            cookies = cookie_list_to_cookiejar(cookies)
        resp = requests.get(url, cookies=cookies)
    return resp.json()['status_code'] != 20003


def _get_a_room_id():
    url = "https://live.douyin.com/"
    with requests.get(url, headers=HEADERS) as resp:
        text = text_within(
            resp.text, 
            '<script class="STREAM_RENDER_DATA" type="application/json">', 
            '</script>', 
        )
        jsdata = loads(unquote(text, encoding='utf-8', errors='replace'))
        return jsdata['value']['data']['data'][0]['room']['id_str']


def get_userid(cookies):
    url = 'https://live.douyin.com/webcast/room/chat/'
    params = {
        'aid': '6383', 
        'room_id': _get_a_room_id(), 
        'content': '?', 
    }
    if isinstance(cookies, str):
        resp = requests.get(url, params=params, headers={"Cookie": cookies})
    else:
        if isinstance(cookies, list):
            cookies = cookie_list_to_cookiejar(cookies)
        resp = requests.get(url, params=params, cookies=cookies)
    jsdata = resp.json()
    if jsdata['status_code'] == 20003:
        return ''
    return str(jsdata['data']['user']['short_id'])


def get_live_info(url):
    with requests.get(url, headers=HEADERS) as resp:
        text = text_within(
            resp.text, 
            '<script id="RENDER_DATA" type="application/json">', 
            '</script>', 
        )
        jsdata = loads(unquote(text, encoding='utf-8', errors='replace'))
        jsdata['ttwid'] = resp.cookies['ttwid']
        return jsdata

