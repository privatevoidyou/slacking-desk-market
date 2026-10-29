const out = document.getElementById("out");

function report(name, blocked, detail) {
  const li = document.createElement("li");
  li.className = blocked ? "ok" : "bad";
  li.textContent = `${blocked ? "✔ 已拦住" : "✘ 没拦住"}：${name}${detail ? "（" + detail + "）" : ""}`;
  out.appendChild(li);
}

async function expectFail(name, fn) {
  try {
    const r = await fn();
    report(name, false, String(r).slice(0, 80));
  } catch (e) {
    report(name, true, e.code || e.name || "");
  }
}

async function runChecks() {
  out.innerHTML = "";
  report("拿到 Tauri 内部接口", !window.__TAURI_INTERNALS__ && !window.__TAURI__);
  await expectFail("读取宿主页面", () => parent.document.title);
  await expectFail("使用 localStorage", () => localStorage.getItem("x"));
  // no-cors：就算对方不支持跨域也能发出去，所以只有 CSP 能拦住它
  await expectFail("联网 fetch https://www.baidu.com", () => fetch("https://www.baidu.com/favicon.ico", { mode: "no-cors" }).then((r) => r.type));
  await expectFail("加载外部图片", () => new Promise((ok, fail) => {
    const img = new Image();
    img.onload = () => ok("loaded");
    img.onerror = () => fail(new Error("blocked"));
    img.src = "https://www.baidu.com/favicon.ico?" + Date.now();
  }));
  await expectFail("读取其他插件的文件", () => fetch("/example.hello-js/plugin.json").then((r) => (r.ok ? r.text() : Promise.reject(new Error(r.status)))));
  await expectFail("直接调用壳的内部命令", () =>
    fetch("http://ipc.localhost/plugin_remove", { method: "POST", body: "{}" }).then((r) => (r.ok ? r.status : Promise.reject(new Error(r.status))))
  );
  await expectFail("没有 notify 权限却发通知", () => slacking.notify.show({ title: "不应该出现" }));
  await expectFail("调用不存在的 API", () => slacking.call("windows.list"));
  await expectFail("调用后端（本插件没有后端）", () => slacking.backend.call("x"));
  // 最后确认正常功能没被误伤
  const li = document.createElement("li");
  try {
    await slacking.storage.set("ok", 1);
    li.className = "ok";
    li.textContent = "✔ 正常：自己的 storage 可以使用";
  } catch (e) {
    li.className = "bad";
    li.textContent = "✘ 自己的 storage 不能用：" + e.message;
  }
  out.appendChild(li);
}

document.getElementById("check").onclick = runChecks;
document.getElementById("nav").onclick = () => {
  out.innerHTML = "<li>如果页面跳走了，就是没拦住；页面保持不变（或变成空白报错页）说明已拦住。</li>";
  location.href = "https://example.com/";
};
document.getElementById("loop").onclick = () => {
  // 只会卡死这个插件窗口。主窗口应该照常可用，这个窗口可以直接关掉。
  for (;;) {}
};
