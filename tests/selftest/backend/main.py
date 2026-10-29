import os
import slacking_plugin as sp


@sp.method("echo")
def echo(params):
    # 后端 → 壳的调用：存储可用，未知 API 返回 not_found
    sp.call("storage.set", {"key": "fromBackend", "value": {"pid": os.getpid(), "ctx": sp.context}})
    try:
        sp.call("windows.list")
        denied = "not denied"
    except sp.ShellError as e:
        denied = e.code
    return {"echo": params, "unknownApi": denied}


@sp.method("fail")
def fail(params):
    raise ValueError("故意的错误")


sp.run()
