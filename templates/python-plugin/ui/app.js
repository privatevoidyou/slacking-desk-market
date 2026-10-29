const out = document.getElementById("out");

function show(text, isError) {
  out.textContent = text;
  out.className = "sd-card " + (isError ? "error" : "");
}

document.getElementById("greet").onclick = async () => {
  show("等待 Python 回复…");
  try {
    const r = await slacking.backend.call("greet", { name: document.getElementById("name").value });
    show(`${r.text}\n来自 Python ${r.python}（进程 ${r.pid}），这是第 ${r.count} 次问候。`);
  } catch (e) {
    show(`出错了（${e.code}）：${e.message}`, true);
  }
};

document.getElementById("notify").onclick = async () => {
  try {
    await slacking.backend.call("notify_me");
    show("Python 已经请壳发出通知。");
  } catch (e) {
    show(`出错了（${e.code}）：${e.message}`, true);
  }
};
