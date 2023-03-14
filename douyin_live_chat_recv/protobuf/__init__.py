#!/usr/bin/env python3
# coding: utf-8

__all__ = ["make_parser", "douyin_pb2"]

from os import remove, path
from json import loads
from pathlib import Path
from multiprocessing.connection import Client
from subprocess import Popen
from threading import Lock

from nodejs import node

from . import __init
from . import douyin_pb2


SCRIPT_PATH =  str(Path(__file__).parents[1] / 'js' / 'pb' / 'cli.js')


def make_parser(address='douyin-chat.sock'):
    def gen_client():
        if path.exists(address):
            remove(address)
        p = Popen([node.path, SCRIPT_PATH, address])
        try:
            payload = yield
            with Client(address) as conn:
                while True:
                    conn.send_bytes(payload)
                    payload = yield conn.recv_bytes()
        finally:
            p.kill()
            try:
                remove(address)
            except OSError:
                pass

    def send(payload, lock=Lock()):
        if isinstance(payload, (bytes, bytearray)):
            pass
        elif isinstance(payload, str):
            payload = payload.encode("utf-8")
        else:
            payload = bytes(payload)
        with lock:
            return loads(g.send(payload))

    g = gen_client()
    next(g)

    return send, g.close

