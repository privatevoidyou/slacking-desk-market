// 插件自己决定界面语言：读 app.info().language
const TEXT = {
  "zh-CN": {
    title: "你好，摸鱼人",
    info: (i) => `壳版本 ${i.shellVersion} · ${i.platform} · ${i.theme === "dark" ? "深色" : "浅色"}主题`,
    countLabel: "你已经摸了这么多次鱼（重启也不会丢）",
    reset: "清零",
    notify: "发一条通知",
    sent: "已发送",
  },
  en: {
    title: "Hello, slacker",
    info: (i) => `Shell ${i.shellVersion} · ${i.platform} · ${i.theme} theme`,
    countLabel: "Times you slacked off (survives restarts)",
    reset: "Reset",
    notify: "Send a notification",
    sent: "Sent",
  },
};

const $ = (id) => document.getElementById(id);
let info;
let T = TEXT["zh-CN"];
let count = 0;

async function init() {
  info = await slacking.app.info();
  T = TEXT[info.language] || TEXT["zh-CN"];
  $("title").textContent = T.title;
  $("info").textContent = T.info(info);
  $("countLabel").textContent = T.countLabel;
  $("reset").textContent = T.reset;
  $("notify").textContent = T.notify;
  // storage：插件自己的小型键值存储，不需要权限
  count = (await slacking.storage.get("count")) || 0;
  $("count").textContent = count;
}

async function setCount(n) {
  count = n;
  $("count").textContent = n;
  await slacking.storage.set("count", n);
}

$("add").onclick = () => setCount(count + 1);
$("reset").onclick = () => setCount(0);

$("notify").onclick = async () => {
  try {
    await slacking.notify.show({ title: T.title, body: `${T.countLabel}: ${count}` });
    $("msg").textContent = T.sent;
    $("msg").className = "sd-muted";
  } catch (e) {
    // 没有 notify 权限时 e.code === "permission_denied"
    $("msg").textContent = `${e.code}: ${e.message}`;
    $("msg").className = "error";
  }
};

// 用户在设置里切换主题时，SDK 会自动更新 data-theme；这里顺便刷新文字
slacking.on("theme.changed", ({ theme }) => {
  if (info) $("info").textContent = T.info({ ...info, theme });
});

init().catch((e) => ($("info").textContent = String(e.message || e)));
