const EXPECT = {
  ping: "返回 Python 进程号。",
  crash: "这里报错；插件页显示「已崩溃」和最后几行日志，并弹出通知。点「重启」后才能再次使用。",
  hang: "约 30 秒后这里显示 timeout 错误。",
  spam: "立即返回。几秒内日志文件会轮换（超过 1MB 改名为 .log.1），壳不卡。",
  spawn_child: "返回子进程号。然后关闭这个窗口（或禁用插件），再打开它点「检查上次的子进程」。",
  check_child: "子进程应该已经结束（alive 为 false）。",
};
const out = document.getElementById("out");

document.querySelectorAll("button[data-m]").forEach((b) => {
  b.onclick = async () => {
    const m = b.dataset.m;
    out.textContent = `调用 ${m}…\n预期：${EXPECT[m]}`;
    const t0 = Date.now();
    try {
      const r = await slacking.backend.call(m);
      out.textContent += `\n\n结果（${((Date.now() - t0) / 1000).toFixed(1)} 秒）：${JSON.stringify(r)}`;
    } catch (e) {
      out.textContent += `\n\n错误（${((Date.now() - t0) / 1000).toFixed(1)} 秒）：${e.code}：${e.message}`;
    }
  };
});
