#!/usr/bin/env python3
# coding: utf-8

__all__ = ["LiveRecvException", "InvalidLive", "NotOnLive", "WebcastParseError"]


class LiveRecvException(RuntimeError):
    pass


class InvalidLive(LiveRecvException):
    pass


class NotOnLive(LiveRecvException):
    pass


class WebcastParseError(LiveRecvException):
    pass

