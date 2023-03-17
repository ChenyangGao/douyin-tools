#!/usr/bin/env python3
# coding: utf-8

__all__ = ["make_parser", "douyin_pb2"]

from json import loads
from os import close, read, write, remove, path
from pathlib import Path
from platform import system
from multiprocessing.connection import Client, Connection
from subprocess import Popen
from tempfile import gettempdir
from threading import Lock
from time import sleep
from uuid import uuid4

from nodejs import node

from . import __init
from . import douyin_pb2


SCRIPT_PATH = str(Path(__file__).parents[1] / 'js' / 'pb' / 'cli.js')
IS_WINDOWS = system() == "Windows"


class _FileConnection(Connection):

    def _close(self, _close=close):
        _close(self._handle)
    _write = write
    _read = read

    def _send(self, buf, write=_write):
        return super()._send(buf, write)

    def _recv(self, size, read=_read):
        return super()._recv(size, read)


def make_parser(address=None):
    if address is None:
        if IS_WINDOWS:
            address = fr'\\.\pipe\{uuid4()}'
        else:
            address = path.join(gettempdir(), f"{uuid4()}.sock")

    def gen_client():
        if not IS_WINDOWS and path.exists(address):
            remove(address)

        p = Popen([node.path, SCRIPT_PATH, address])

        for _ in range(10):
            try:
                if IS_WINDOWS:
                    f = open(address, "rb+", buffering=0)
                    conn = _FileConnection(f.fileno())
                else:
                    conn = Client(address)
                break
            except FileNotFoundError as e:
                sleep(1)
                ex = e
        else:
            raise ex

        try:
            with conn:
                payload = yield
                while True:
                    conn.send_bytes(payload)
                    payload = yield conn.recv_bytes()
        finally:
            p.kill()
            try:
                if IS_WINDOWS:
                    f.close()
                else:
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

