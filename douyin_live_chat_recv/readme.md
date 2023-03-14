# 抖音弹幕采集器

欢迎使用抖音字幕采集器，这是一个完全免费开源项目。

## 使用说明

> 请使用 Python 3.9 或更高版本。

### 帮助信息

```sh
$ python douyin_live_chat_recv -h

usage: douyin_live_chat_recv [-h] [-d] url

直播间消息采集器

positional arguments:
  url          直播间链接

optional arguments:
  -h, --help   show this help message and exit
  -d, --debug  输出debug信息
```

### 具体使用

启动监听某个直播间（需要传入直播链接），按 <keyboard>CTRL</keyboard> + <keyboard>C</keyboard> 以关闭程序。

```
$ python douyin_live_chat_recv https://live.douyin.com/834102083442
[2023-03-14 13:03:11,005] root (INFO) run ➜ 🎆live data: {'_location': '/834102083442', ...}
[2023-03-14 13:03:11,220] root (INFO) run ➜ 🎆Websocket client started, press <CTRL>+<C> or call .stop() method to stop
[2023-03-14 13:03:12,139] root (INFO) on_open ➜ 📖 [room_id: 7210246874790382396] [title: 'Sky李晓峰我来了~']
[2023-03-14 13:03:12,452] root (INFO) webcast_message ➜ {"common": {"method": "WebcastRoomMessage", ...}
[2023-03-14 13:03:12,459] root (INFO) webcast_message ➜ {"common": {"method": "WebcastRoomIntroMessage", ...}
[2023-03-14 13:03:12,461] root (INFO) webcast_message ➜ {"common": {"method": "WebcastRoomStatsMessage", ...}
[2023-03-14 13:03:12,465] root (INFO) webcast_message ➜ {"common": {"method": "WebcastRoomRankMessage", ...}
[2023-03-14 13:03:12,471] root (INFO) webcast_message ➜ {"common": {"method": "WebcastMemberMessage", ...}
[2023-03-14 13:03:12,477] root (INFO) webcast_message ➜ {"common": {"method": "WebcastGiftMessage", ...}
...
[2023-03-14 13:20:26,131] root (ERROR) on_error ➜ 🔥ERROR KeyboardInterrupt()
[2023-03-14 13:20:26,311] root (WARNING) run_forever ➜ ⚠️ Terminated, bye bye ~
```

如果直播间已关闭，会每分钟重试一次，按 <keyboard>CTRL</keyboard> + <keyboard>C</keyboard> 以关闭程序。

```sh
$ python douyin_live_chat_recv https://live.douyin.com/401818337019
[2023-03-14 12:59:07,600] root (WARNING) run_forever ➜ 📢Off live, try after 1 second ~
[2023-03-14 12:59:09,091] root (WARNING) run_forever ➜ 📢Off live, try after 1 second ~
...
[2023-03-14 13:01:11,236] root (WARNING) run_forever ➜ ⚠️ Terminated, bye bye ~
```

## 接口说明

主要提供了一个 `DouyinLiveChatReceiver` 类

```python
from douyin_live_chat_recv import DouyinLiveChatReceiver
```

帮助说明如下：

```
Help on class DouyinLiveChatReceiver in module douyin_live_chat_recv.receiver:

class DouyinLiveChatReceiver(builtins.object)
 |  DouyinLiveChatReceiver(url: str, send: Optional[Callable] = None, cookies: Union[NoneType, bytes, str, os.PathLike, io.IOBase, list[dict], dict
, http.cookiejar.CookieJar] = None, logger: Any = None)
 |  
 |  创建一个抖音弹幕采集器。
 |      请调用 start 方法运行，close 方法结束；
 |      或者 调用 run_forever 方法运行，quit_forever 方法结束。
 |  
 |  :param url: 直播间链接
 |  :param send: 请提供一个可调用对象，用于接收弹幕消息（更准确地说，弹幕事件），这些消息
 |      都是具有复杂嵌套结构的字典。如果接收到的消息中 "error" 为 True，说明发生了异常，
 |      形如
 |          {
 |              "error": True, 
 |              "method": message.method, # 消息类型
 |              "payload_hex": message.payload.hex(), # 消息的荷载数据（16进制）
 |              "exception": "...", # 错误信息
 |              "traceback": "...", # python 调用栈信息，如果发生 Python 异常
 |              "stack": "...",     # nodejs 调用栈信息，如果发生 nodejs 错误
 |          }
 |  :param cookies: 传入一段 cookies 数据，用于确认用户身份。通常，如果这是你自己的直播
 |      间，而且你设置了用户名隐藏（会把用户名中的大部分字符替换成若干*），那么只有你自己的
 |      登录 cookies 才能让你看到弹幕中用户的完整名称。
 |          None: 不提供（默认）
 |          bytes | str: 会当作 JSON 数据解析
 |          PathLike: 路径，会被读取
 |          IOBase: 类文件对象，会被读取
 |          list[dict] ｜ CookieJar: 每个元素都是一个 cookie
 |          dict: 每个键值对，就是一个 cookie
 |  :param logger: 请提供一个日志输出类的实例，具有 debug, info, error 等方法，通常你
 |      可以直接传入 logging 模块，或者 logging.getLogger 获取到的实例。
 |      如果传入 None (默认)，则不进行日志输出，这个参数也会被绑定为实例属性。
 |  
 |  Methods defined here:
 |  
 |  __del__(self)
 |  
 |  __init__(self, url: str, send: Optional[Callable] = None, cookies: Union[NoneType, bytes, str, os.PathLike, io.IOBase, list[dict], dict, http.c
ookiejar.CookieJar] = None, logger: Any = None)
 |      Initialize self.  See help(type(self)) for accurate signature.
 |  
 |  close(self)
 |      停止
 |  
 |  on_close(self, ws)
 |      【自动调用】websocket close事件
 |  
 |  on_error(self, ws: websocket._app.WebSocketApp, error: BaseException)
 |      【自动调用】websocket error事件
 |  
 |  on_message(self, ws: websocket._app.WebSocketApp, message: bytes)
 |      【自动调用】websocket message事件
 |  
 |  on_open(self, ws: websocket._app.WebSocketApp)
 |      【自动调用】websocket open事件
 |  
 |  ping(self, ws: websocket._app.WebSocketApp)
 |      【自动调用】发送心跳 ping
 |  
 |  pong(self, ws: websocket._app.WebSocketApp, logid: Union[int, str], internalExt: str)
 |      【自动调用】发送回应 ack
 |  
 |  quit_forever(self)
 |      停用，失败会重启
 |  
 |  refresh(self)
 |      更新直播间信息，即 liveinfo 实例属性。
 |  
 |  run(self)
 |      启动（同时最多运行一个）
 |  
 |  run_forever(self)
 |      启动，失败会重启
 |  
 |  start(self, run_in_thread=False)
 |      启动，run_in_thread 为 True 时在子线程运行
 |  
 |  ----------------------------------------------------------------------
 |  Readonly properties defined here:
 |  
 |  running
 |      是否运行中，同一个实例只能同时运行一个收集器。
 |  
```
