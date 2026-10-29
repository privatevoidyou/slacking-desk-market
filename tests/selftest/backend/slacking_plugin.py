"""Slacking Desk Python 插件 SDK（零依赖，只用标准库）。把这个文件复制到你的插件里使用。

协议：壳通过 stdin/stdout 和插件交换 JSON-RPC 2.0 消息，一行一条 JSON。
stdout 只能用来传协议消息，所以本模块在导入时把 print() 重定向到 stderr（壳会写进插件日志）。

用法：
    import slacking_plugin as sp

    @sp.method("greet")
    def greet(params):
        return {"text": "你好，" + params.get("name", "")}

    sp.run()
"""

import itertools
import json
import os
import sys
import threading
import traceback

_proto_out = sys.stdout
sys.stdout = sys.stderr  # print() 进日志，不会破坏协议

_handlers = {}
_pending = {}
_lock = threading.Lock()
_write_lock = threading.Lock()
_ids = itertools.count(1)
_on_shutdown = []

#: 壳在启动时传来的信息：shellVersion、pluginId、dataDir（插件自己的数据目录）、language、platform
context = {}


class ShellError(Exception):
    """调用壳的 API 失败。code 是 permission_denied、invalid_params、not_found、timeout、internal 等。"""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


def method(name):
    """注册一个方法，插件界面通过 slacking.backend.call(name, params) 调用它。返回值必须能转成 JSON。"""

    def deco(fn):
        _handlers[name] = fn
        return fn

    return deco


def on_shutdown(fn):
    """壳关闭插件前调用（最多等 3 秒）。"""
    _on_shutdown.append(fn)
    return fn


def call(method, params=None, timeout=30):
    """调用壳的 API，例如 call("notify.show", {"title": "到点了"})。失败时抛 ShellError。"""
    rid = next(_ids)
    done = threading.Event()
    slot = {}
    with _lock:
        _pending[rid] = (done, slot)
    _send({"jsonrpc": "2.0", "id": rid, "method": method, "params": params if params is not None else {}})
    if not done.wait(timeout):
        with _lock:
            _pending.pop(rid, None)
        raise ShellError("timeout", method + " 超时")
    if "error" in slot:
        err = slot["error"] or {}
        raise ShellError((err.get("data") or {}).get("code", "internal"), err.get("message", ""))
    return slot.get("result")


def notify(title, body=""):
    """发送系统通知（需要 notify 权限）。"""
    return call("notify.show", {"title": title, "body": body})


def run():
    """处理壳发来的消息，直到壳关闭管道。放在脚本最后调用。"""
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            print("收到无法解析的消息：", line[:200])
            continue
        name = msg.get("method")
        if name == "initialize":
            context.update(msg.get("params") or {})
            _reply(msg.get("id"), {})
        elif name == "shutdown":
            break
        elif name is not None:
            # 每个请求一个线程：处理函数里可以再调用 call()，不会卡住读消息
            threading.Thread(target=_handle_request, args=(msg,), daemon=True).start()
        else:
            with _lock:
                entry = _pending.pop(msg.get("id"), None)
            if entry:
                done, slot = entry
                slot.update(msg)
                done.set()
    for fn in _on_shutdown:
        try:
            fn()
        except Exception:
            traceback.print_exc()
    sys.stderr.flush()
    os._exit(0)  # 不等还在运行的处理线程


def _send(msg):
    line = json.dumps(msg, ensure_ascii=False)
    with _write_lock:
        _proto_out.write(line + "\n")
        _proto_out.flush()


def _reply(rid, result=None, error=None):
    if rid is None:
        return
    msg = {"jsonrpc": "2.0", "id": rid}
    if error is None:
        msg["result"] = result
    else:
        msg["error"] = error
    _send(msg)


def _handle_request(msg):
    rid, name = msg.get("id"), msg.get("method")
    fn = _handlers.get(name)
    if fn is None:
        _reply(rid, error={"code": -32601, "message": "没有这个方法：" + str(name), "data": {"code": "not_found"}})
        return
    try:
        _reply(rid, fn(msg.get("params") or {}))
    except ShellError as e:
        _reply(rid, error={"code": -32000, "message": e.message, "data": {"code": e.code}})
    except Exception as e:
        traceback.print_exc()
        _reply(rid, error={"code": -32000, "message": "%s: %s" % (type(e).__name__, e), "data": {"code": "internal"}})
