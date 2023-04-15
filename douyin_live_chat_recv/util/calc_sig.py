#!/usr/bin/env python3
# coding: utf-8

__all__ = ["calc_sig"]

import asyncio

from json import dumps, loads
from pathlib import Path
from subprocess import PIPE
from urllib.parse import quote

from nodejs import node

from .browser import ctx_browser


JSDIR = str(Path(__file__).parent.with_name("js"))


def inverse_endian(i, length=None):
    if length is None:
        l, r = divmod(i.bit_length(), 8)
        l += (r > 0)
    else:
        l = length
    return int.from_bytes(i.to_bytes(l, 'big'), 'little')


def bytes_to_words(b, endian='big'):
    start = 0
    ls = []
    for stop in range(4, len(b), 4):
        ls.append(int.from_bytes(b[start:stop], endian))
        start = stop
    remain = b[start:]
    if len(remain) < 4:
        if endian == 'big':
            remain += b'\x00'*(4-len(remain))
        else:
            remain = b'\x00'*(4-len(remain)) + remain
    ls.append(int.from_bytes(remain, endian))
    return ls


def words_to_bytes(ws, endian='big'):
    return b''.join(int.to_bytes(w, 4, endian) for w in ws)


def calc_ms_stub(b):
    ws = bytes_to_words(b)
    cmd = f'''\
_mod = require("./o.js");
console.log(JSON.stringify(_mod.o(%(jsdata)s, %(len)d)))''' % dict(jsdata=dumps(ws), len=len(b))
    r = node.run(["--no-warnings", "-e", cmd], stdout=PIPE, check=True, cwd=JSDIR)
    ws = loads(r.stdout)
    return {"X-MS-STUB": words_to_bytes(ws, 'little').hex()}


def calc_sign(payload={}):
    async def intercept(request):
        if request.resourceType in ("image", "media", "eventsource", "websocket", "stylesheet", "font"):
            await request.abort()
        else:
            await request.continue_()
    async def calc():
        async with ctx_browser({"headless": True}) as browser:
            pages = await browser.pages()
            page = pages[0]
            await page.setRequestInterception(True)
            page.on('request', lambda req: asyncio.ensure_future(intercept(req)))
            await page.goto('https://live.douyin.com')
            return (await page.evaluate(f'window.byted_acrawler.frontierSign({dumps(payload)})'))
    return asyncio.new_event_loop().run_until_complete(calc())


def calc_sig(s):
    if isinstance(s, str):
        b = s.encode("utf-8")
    elif isinstance(s, dict):
        b = b",".join(
            f"{quote(str(k))}={quote(str(v))}".encode("ascii") 
            for k, v in s.items())
    else:
        b = bytes(s)
    
    ms_stub = calc_ms_stub(b)
    sign = calc_sign(ms_stub)
    return sign['X-Bogus']


if __name__ == "__main__":
    b = b'live_id=1,aid=6383,version_code=180800,webcast_sdk_version=1.3.0,room_id=7208887202750057216,sub_room_id=,sub_channel_id=,did_rule=3,user_unique_id=7203268407125394977,device_platform=web,device_type=,ac=,identity=audience'
    print("Source:", b)
    print("X-MS-STUB:", calc_ms_stub(b))
    print("X-Bogus:", calc_sig(b))

