#!/usr/bin/env python3
# coding: utf-8

__all__ = ["ctx_browser"]

import platform

# TODO: 自动搜寻最新版
if platform.system() == "Windows":
    RECOMMENDED_CHROMIUM_REVISION = "1000204"
else:
    RECOMMENDED_CHROMIUM_REVISION = '1109567'

def _init():
    import os

    os.environ['PYPPETEER_CHROMIUM_REVISION'] = RECOMMENDED_CHROMIUM_REVISION
    # https://npm.taobao.org/mirrors/chromium-browser-snapshots/
    os.environ['PYPPETEER_DOWNLOAD_HOST'] = "https://registry.npmmirror.com/-/binary"

    import pyppeteer

    pyppeteer.__chromium_revision__ = RECOMMENDED_CHROMIUM_REVISION

    if platform.system() == 'Darwin' \
        and platform.processor() == "arm" \
        and int(pyppeteer.chromium_downloader.REVISION) >= 938248 \
    :
        downloadURLs = pyppeteer.chromium_downloader.downloadURLs
        downloadURLs["mac"] = downloadURLs["mac"].replace("/Mac/", "/Mac_Arm/")

    from pyppeteer import launcher

    launcher.DEFAULT_ARGS.remove("--enable-automation")

_init()

from contextlib import asynccontextmanager

from pyppeteer import launch


DEFAULT_LAUNCH_CONFIG = {
    "headless": False, 
    "dumpio": True, 
    "defaultViewport": None, 
    'handleSIGINT':False, 
    'handleSIGTERM': False, 
    'handleSIGHUP': False, 
    #"executablePath": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "args": [
        # See: https://peter.sh/experiments/chromium-command-line-switches/
        "--no-default-browser-check", 
        #"--no-sandbox", 
        #"--disable-setuid-sandbox", 
        #"--disable-gpu", 
        "--disable-infobars", 
        "--log-level=INFO", 
        "--window-size=1280,720", 
        #"--start-maximized", 
        #"--proxy-server=http://127.0.0.1:80", 
    ], 
    "userDataDir": "", 
}


async def _prevent_check(page):
    await page.evaluate("() => { Object.defineProperties( navigator, { webdriver: { get: () => undefined } } ) }")
    await page.evaluate("() => { window.navigator.chrome = { runtime: {} } }")
    await page.evaluate("() => { Object.defineProperty( navigator, 'languages', { get: () => ['en-US', 'en'] }) }")
    await page.evaluate("() => { Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5, 6] } ) }")


def _wapper_newPage(browser):
    m = browser.newPage
    async def newPage(*args, **kwds):
        page = await m(*args, **kwds)
        await _prevent_check(page)
        return page
    browser.newPage = newPage


@asynccontextmanager
async def ctx_browser(launch_config=None, /, **launch_kwds):
    config = dict(DEFAULT_LAUNCH_CONFIG)
    if launch_config:
        config.update(launch_config)
    if launch_kwds:
        config.update(launch_kwds)
    browser = await launch(config)
    try:
        _wapper_newPage(browser)
        pages = await browser.pages()
        await _prevent_check(pages[0])
        yield browser
    finally:
        await browser.close()

