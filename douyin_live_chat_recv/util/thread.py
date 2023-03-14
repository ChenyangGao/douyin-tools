#!/usr/bin/env python3
# coding: utf-8

__all__ = ["as_thread", "as_future", "run_timeout", "run_interval0", "run_interval"]

from concurrent.futures import Future
from functools import partial
from threading import Thread, Timer


def as_thread(function, /, *args, **kwds):
    t = Thread(target=function, args=args, kwargs=kwds, daemon=True)
    t.start()
    return t


def as_future(function, /, *args, **kwds):
    fu = Future()
    def wrapper():
        try:
            fu.set_result(function(*args, **kwds))
        except BaseException as exc:
            fu.set_exception(exc)
    Thread(target=wrapper, daemon=True).start()
    return fu


def run_timeout(timeout, function, /, *args, **kwds):
    t = Timer(timeout, function, args, kwds)
    t.start()
    return t.cancel


def run_interval0(timeout, function, /, *args, **kwds):
    def wrapper():
        nonlocal timer
        timer = Timer(timeout, wrapper)
        timer.start()
        function(*args, **kwds)
    timer = Timer(0, wrapper)
    timer.start()
    return lambda: timer.cancel()


def run_interval(timeout, function, /, *args, **kwds):
    def wrapper():
        nonlocal timer
        timer = Timer(timeout, wrapper)
        timer.start()
        function(*args, **kwds)
    timer = Timer(timeout, wrapper)
    timer.start()
    return lambda: timer.cancel()

