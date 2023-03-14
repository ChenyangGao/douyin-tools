#!/usr/bin/env python3
# coding: utf-8

from argparse import ArgumentParser

parser = ArgumentParser(description="直播间消息采集器")
parser.add_argument("url", help="直播间链接")
parser.add_argument("-d", "--debug", action="store_true", help="输出debug信息")
args = parser.parse_args()

import sys

sys.path.append(str(__import__("pathlib").Path(__file__).parents[1]))

import logging

from json import dumps

from douyin_live_chat_recv.receiver import DouyinLiveChatReceiver

logging.basicConfig(
    level=logging.DEBUG if args.debug else logging.INFO, 
    format=(
        "[\x1b[1m%(asctime)-15s\x1b[0m] \x1b[36;1m%(name)s\x1b[0m "
        "(\x1b[31;1m%(levelname)s\x1b[0m) \x1b[37;1m%(funcName)s\x1b[0m "
        "➜ %(message)s"
))

def webcast_message(message):
    logging.info(dumps(message, ensure_ascii=False))

DouyinLiveChatReceiver(
    args.url, 
    send = webcast_message, 
    logger = logging, 
).run_forever()

