"""Python 示例插件的后端。界面通过 slacking.backend.call("greet", ...) 调用这里的方法。"""

import os
import platform
from pathlib import Path

import slacking_plugin as sp


@sp.method("greet")
def greet(params):
    name = (params.get("name") or "").strip() or "摸鱼人"
    # dataDir 是插件自己的数据目录，升级插件也不会丢
    counter = Path(sp.context["dataDir"]) / "greet-count.txt"
    count = int(counter.read_text() or 0) + 1 if counter.exists() else 1
    counter.write_text(str(count))
    print("greet 被调用了", count, "次")  # print 会写进插件日志
    return {
        "text": "你好，%s！" % name,
        "python": platform.python_version(),
        "pid": os.getpid(),
        "count": count,
    }


@sp.method("notify_me")
def notify_me(params):
    # 后端也可以调用壳的 API，权限和界面共用（这里需要 notify 权限）
    sp.notify("来自 Python 的问候", "Python %s 正在为你摸鱼" % platform.python_version())
    return True


sp.run()
