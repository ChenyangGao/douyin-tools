#!/usr/bin/env python3
# coding: utf-8

__all__ = ["DouyinLiveChatReceiver"]

from gzip import decompress
from http.cookiejar import CookieJar
from io import IOBase
from json import loads
from os import PathLike
from threading import Thread
from time import sleep
from traceback import format_exc
from typing import Any, Callable, Optional, Union
from urllib.parse import urlencode

import websocket
from websocket import WebSocketApp

from .protobuf import douyin_pb2, make_parser
from .exception import InvalidLive, NotOnLive
from .util.calc_sig import calc_sig
from .util.text import text_within
from .util.thread import run_interval
from .util.cookies import cookie_list_to_cookiejar
from .util.douyin_utils import get_live_info


class DouyinLiveChatReceiver:
    """创建一个抖音弹幕采集器。
        请调用 start 方法运行，close 方法结束；
        或者 调用 run_forever 方法运行，quit_forever 方法结束。

    :param url: 直播间链接
    :param send: 请提供一个可调用对象，用于接收弹幕消息（更准确地说，弹幕事件），这些消息
        都是具有复杂嵌套结构的字典。如果接收到的消息中 "error" 为 True，说明发生了异常，
        形如
            {
                "error": True, 
                "method": message.method, # 消息类型
                "payload_hex": message.payload.hex(), # 消息的荷载数据（16进制）
                "exception": "...", # 错误信息
                "traceback": "...", # python 调用栈信息，如果发生 Python 异常
                "stack": "...",     # nodejs 调用栈信息，如果发生 nodejs 错误
            }
    :param cookies: 传入一段 cookies 数据，用于确认用户身份。通常，如果这是你自己的直播
        间，而且你设置了用户名隐藏（会把用户名中的大部分字符替换成若干*），那么只有你自己的
        登录 cookies 才能让你看到弹幕中用户的完整名称。
            None: 不提供（默认）
            bytes | str: 会当作 JSON 数据解析
            PathLike: 路径，会被读取
            IOBase: 类文件对象，会被读取
            list[dict] ｜ CookieJar: 每个元素都是一个 cookie
            dict: 每个键值对，就是一个 cookie
    :param logger: 请提供一个日志输出类的实例，具有 debug, info, error 等方法，通常你
        可以直接传入 logging 模块，或者 logging.getLogger 获取到的实例。
        如果传入 None (默认)，则不进行日志输出，这个参数也会被绑定为实例属性。
    """
    def __init__(
        self, 
        url: str, 
        send: Optional[Callable] = None, 
        cookies: Union[None, bytes, str, PathLike, IOBase, list[dict], dict, CookieJar] = None, 
        logger: Any = None, 
    ):
        self.url = url
        self.send = send
        self.cookies: Union[None, str, dict, CookieJar]
        if cookies is None or isinstance(cookies, (str, dict, CookieJar)):
            self.cookies = cookies
        else:
            if isinstance(cookies, PathLike):
                cookies = open(cookies, encoding="utf-8")
            if isinstance(cookies, IOBase):
                cookies = cookies.read()
            if isinstance(cookies, (bytes, str)):
                cookies = loads(cookies)
            if isinstance(cookies, list):
                cookies = self.cookies = cookie_list_to_cookiejar(cookies)
            else:
                self.cookies = cookies # type: ignore
        self.cookie: Optional[str] = None
        if cookies is None or isinstance(cookies, str):
            self.cookie = cookies
        elif isinstance(cookies, dict):
            self.cookie = "; ".join(f"{k}={v}" for k, v in cookies.items())
        elif isinstance(cookies, CookieJar):
            self.cookie = "; ".join(f"{c.name}={c.value}" for c in cookies)
        self.logger = logger
        self._running: bool = False

    @property
    def running(self) -> bool:
        "是否运行中，同一个实例只能同时运行一个收集器。"
        return self._running

    #def __enter__
    #def __exit__

    def refresh(self):
        "更新直播间信息，即 liveinfo 实例属性。"
        liveinfo = self.liveinfo = get_live_info(self.url)
        self.ttwid = liveinfo['ttwid']
        self.user_unique_id = liveinfo['app']['odin']['user_unique_id']
        roominfo = self.roominfo = liveinfo['app']['initialState']['roomStore']['roomInfo']
        roomid = self.roomid = roominfo['roomId']
        roomtitle = self.roomtitle = roominfo['room']['title']
        status = self.status = roominfo['room']['status']

        if self.logger:
            self.logger.debug(f'🔔Live status: {status}')
        if status != 2:
            self.close()
            raise NotOnLive("Off live")

    def ping(self, ws: WebSocketApp):
        "【自动调用】发送心跳 ping"
        obj = douyin_pb2.PushFrame()
        obj.payloadType = 'hb'
        data = obj.SerializeToString()
        ws.send(data, websocket.ABNF.OPCODE_BINARY)
        if self.logger: 
            self.logger.debug(f"💗PING :: Heartbeat")

    def pong(
        self, 
        ws: WebSocketApp, 
        logid: Union[int, str], 
        internalExt: str, 
    ):
        "【自动调用】发送回应 ack"
        obj = douyin_pb2.PushFrame()
        obj.payloadType = 'ack'
        obj.logid = logid
        obj.payloadType = internalExt
        data = obj.SerializeToString()
        ws.send(data, websocket.ABNF.OPCODE_BINARY)
        if self.logger: 
            self.logger.debug(f"🌟PONG :: Ack")

    def on_open(self, ws: WebSocketApp):
        "【自动调用】websocket open事件"
        self._cancel_ping = run_interval(10, self.ping, ws)
        self._cancel_refresh = run_interval(10, self.refresh)
        if self.logger:
            self.logger.info(f"📖 [room_id: {self.roomid}] [title: {self.roomtitle!r}]")

    def on_message(
        self, 
        ws: WebSocketApp, 
        message: bytes, 
    ):
        "【自动调用】websocket message事件"
        logger = self.logger
        if logger:
            logger.debug(f"📨 Received {len(message)} bytes")
        pushframe = douyin_pb2.PushFrame()
        pushframe.ParseFromString(message)
        response = douyin_pb2.Response()
        response.ParseFromString(decompress(pushframe.payload))
        if response.needAck:
            self.pong(ws, pushframe.logid, response.internalExt)
        send = self.send
        if send:
            for msg in response.messagesList:
                try:
                    json_msg = self.parse_message(msg.method.encode() + b"|" + msg.payload)
                    if json_msg.get("error"):
                        send({
                            **json_msg, 
                            "method": msg.method, 
                            "payload_hex": msg.payload.hex(), 
                        })
                    else:
                        send(json_msg)
                except Exception as e:
                    if logger:
                        logger.error(e)
                    send({
                        "error": True, 
                        "method": msg.method, 
                        "payload_hex": msg.payload.hex(), 
                        "exception": repr(e), 
                        "traceback": format_exc(), 
                    })

    def on_error(
        self, 
        ws: WebSocketApp, 
        error: BaseException, 
    ):
        "【自动调用】websocket error事件"
        logger = self.logger
        if logger: logger.error(f'🔥ERROR {error!r}')
        if isinstance(error, KeyboardInterrupt):
            self.close()
            raise error

    def on_close(self, ws):
        "【自动调用】websocket close事件"
        logger = self.logger
        if logger: logger.info(f'🔒CLOSE [room_id: {self.roomid}]')

    def __del__(self):
        try:
            self._cancel_ping()
        except:
            pass
        try:
            self._cancel_refresh()
        except:
            pass

    def run(self):
        "启动（同时最多运行一个）"
        try:
            self.refresh()
        except KeyError:
            raise InvalidLive("Invalid live")
        self.logger.info(f"🎆live data: {self.liveinfo}")

        if self._running:
            raise RuntimeError("Already running!")
        self._running = True
        try:
            self.parse_message, close_parser = make_parser()
            sleep(0.1)
            websocket.enableTrace(False)
            WebSocketUrl = 'wss://webcast3-ws-web-lq.douyin.com/webcast/im/push/v2/'
            params = {
                'live_id': "1", 
                'aid': "6383", 
                'version_code': "180800", 
                'webcast_sdk_version': '1.3.0',
                'room_id': self.roomid, 
                'sub_room_id': "", 
                'sub_channel_id': "", 
                'did_rule': "3",
                'user_unique_id': self.user_unique_id, 
                'device_platform': "web", 
                'device_type': "", 
                'ac': "", 
                'identity': "audience", 
            }
            params.update(
                signature=calc_sig(params), 
                compress="gzip", 
            )
            headers = {
                'cookie': "ttwid=" + self.ttwid,
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit'
                              '/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            }
            ws = self.ws = WebSocketApp(
                WebSocketUrl + "?" + urlencode(params), 
                cookie=self.cookie, 
                on_open=self.on_open, 
                on_message=self.on_message, 
                on_error=self.on_error, 
                on_close=self.on_close,
                on_ping=getattr(self, 'on_ping', None), 
                on_pong=getattr(self, 'on_pong', None), 
                on_cont_message=getattr(self, 'on_cont_message', None), 
                on_data=getattr(self, 'on_data', None), 
                header=headers, 
            )
            self.logger.info("🎆Websocket client started, press <CTRL>+<C> "
                             "or call .stop() method to stop")
            ws.run_forever()
        finally:
            close_parser()
            self._running = False

    def start(self, run_in_thread=False):
        "启动，run_in_thread 为 True 时在子线程运行"
        if run_in_thread:
            Thread(self.run).start()
        else:
            self.run()

    def close(self):
        "停止"
        try:
            self._cancel_ping()
            self._cancel_refresh()
            self.ws.close()
        except (AttributeError, websocket.WebSocketConnectionClosedException):
            pass

    def run_forever(self):
        "启动，失败会重启"
        self._quit = False
        logger = self.logger
        while not self._quit:
            try:
                self.run()
            except websocket.WebSocketException as e:
                msg = f"🚔 websocket.WebSocketException occured, retrying: {e!r}"
                if logger:
                    logger.error(msg)
                else:
                    print(msg)
            except NotOnLive:
                if logger:
                    logger.warn(f"📢Off live, try after 1 second ~")
                sleep(1)
            except KeyboardInterrupt:
                msg = "⚠️ Terminated, bye bye ~"
                if logger:
                    logger.warn(msg)
                else:
                    print(msg)
                break
            finally:
                self.close()

    def quit_forever(self):
        "停用，失败会重启"
        self._quit = True
        self.close()

