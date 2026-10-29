import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import slacking_plugin as sp


def pid_file():
    return Path(sp.context["dataDir"]) / "child.pid"


@sp.method("ping")
def ping(params):
    return {"pid": os.getpid()}


@sp.method("crash")
def crash(params):
    print("即将崩溃：这几行应该出现在插件页的崩溃详情里")
    print("Traceback (most recent call last): 模拟的错误")
    sys.stderr.flush()
    os._exit(3)


@sp.method("hang")
def hang(params):
    time.sleep(60)
    return "不应该等到这里"


@sp.method("spam")
def spam(params):
    def flood():
        for i in range(200000):
            sys.stderr.write("刷屏日志 %d %s\n" % (i, "x" * 80))
            if i % 1000 == 0:
                sp._proto_out.write("这不是 JSON，壳应该忽略并记进日志\n")
                sp._proto_out.flush()
    threading.Thread(target=flood, daemon=True).start()
    return "已开始刷屏，大约持续几秒"


@sp.method("spawn_child")
def spawn_child(params):
    # 子进程什么也不做，只是一直活着。关闭插件窗口或禁用插件后，它应该被壳一起结束。
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(3600)"])
    pid_file().write_text(str(child.pid))
    return {"pid": child.pid}


@sp.method("check_child")
def check_child(params):
    f = pid_file()
    if not f.exists():
        return {"pid": None, "alive": False}
    pid = int(f.read_text())
    return {"pid": pid, "alive": alive(pid), "me": os.getpid()}


def alive(pid):
    if os.name == "nt":
        import ctypes

        k = ctypes.windll.kernel32
        h = k.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return False
        code = ctypes.c_ulong()
        k.GetExitCodeProcess(h, ctypes.byref(code))
        k.CloseHandle(h)
        return code.value == 259  # STILL_ACTIVE
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    # 僵尸进程也算已结束
    try:
        with open("/proc/%d/stat" % pid) as s:
            return s.read().split()[2] != "Z"
    except OSError:
        return True


sp.run()
