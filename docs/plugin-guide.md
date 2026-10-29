# 摸鱼工作台插件开发指南

> 适用于 Slacking Desk 0.1.x（manifestVersion 1）。这是 M1 阶段的初稿，API 会随着用到它们的插件逐步加入。

## 1. 五分钟上手

1. 复制 `templates/js-plugin`（纯网页）或 `templates/python-plugin`（网页界面 + Python 后端）到任意位置。
2. 修改 `plugin.json` 里的 `id`、`name` 等字段。
3. 打开摸鱼工作台 →「插件」→「加载本地文件夹」，选中你的插件文件夹，在确认框里点「同意并加载」。
4. 有 `ui` 的插件安装后会自动出现在首页，点击即可打开（用户可以从首页移除，不影响插件本身）。
5. 修改文件后，在插件页点「重新加载」。界面窗口开着的话会自动重新打开。

调试：

- 插件详情里的「开发者工具」可以打开插件窗口的 DevTools（窗口打开时才有）。
- 「查看日志」打开 `logs/plugins/<id>.log`，后端的 stderr 和 `print()` 都在这里。

开发者模式直接使用你的文件夹，不会复制文件。插件市场（M3）上线后，普通用户从市场或 zip 安装。

## 2. 目录结构

```
my-plugin/
  plugin.json        必需：插件清单
  icon.svg           可选：图标（PNG 或 SVG，建议 256×256）
  ui/index.html      可选：界面
  background.html    可选：后台页
  backend/main.py    可选：本地程序
```

插件能读到的只有自己目录里的文件。插件的数据保存在壳的数据目录 `plugin-data/<id>/`，和插件文件分开，升级插件不会丢数据。

## 3. plugin.json

```json
{
  "manifestVersion": 1,
  "id": "yourname.hello",
  "name": "你好",
  "version": "0.1.0",
  "author": "你的名字",
  "description": "一句话介绍",
  "icon": "icon.svg",
  "minShellVersion": "0.1.0",
  "ui": { "page": "ui/index.html", "width": 480, "height": 360 },
  "background": "background.html",
  "backend": { "runtime": "python", "entry": "backend/main.py" },
  "permissions": ["notify"],
  "i18n": { "en": { "name": "Hello", "description": "One-line intro" } }
}
```

| 字段 | 必填 | 说明 |
|---|---|---|
| manifestVersion | 是 | 固定为 1。更高的版本会被拒绝，并提示升级壳 |
| id | 是 | 小写字母、数字、`.`、`-`，长度 3–64，首尾必须是字母或数字。建议 `作者.插件名` |
| name | 是 | 显示名称 |
| version | 是 | `x.y.z` |
| author / description | 否 | 纯文本 |
| icon | 否 | 插件目录内的 PNG 或 SVG |
| minShellVersion | 是 | 需要的最低壳版本，`x.y.z` |
| ui | 否 | 点击首页图标时打开的页面。`width`、`height` 取 200–4000，默认 480×360 |
| background | 否 | 常驻的隐藏页面，壳启动时自动运行，见第 6 节 |
| backend | 否 | 本地程序，见第 7 节 |
| permissions | 否 | 见第 5 节 |
| i18n | 否 | 其他语言的 `name` 和 `description`，目前只用 `en` |

规则：

- `ui` 和 `background` 至少要有一个。
- 所有路径都是插件目录内的相对路径。不能用 `..`，也不能用指向目录外的符号链接。
- 不认识的字段会被忽略，加载时会显示提示。

## 4. 网页插件

插件页面运行在一个**沙箱 iframe** 里（没有 `allow-same-origin`），所以：

- 拿不到壳和其他插件的任何东西，只能通过 SDK 调用壳的 API。
- `localStorage`、`IndexedDB`、cookie 都不能用。小数据用 `slacking.storage`。
- 没有 `network` 权限时，不能访问任何外部地址（fetch、图片、字体、跳转都会被拦住），只能加载自己目录里的文件。
- 可以用 `alert` / `confirm`，不能弹新窗口。
- 壳会在插件页面里自动加一段小脚本：去掉网页默认的右键菜单（输入框里仍可复制粘贴）、禁止拖动图片；正式版还会屏蔽 F5、Ctrl+R、Ctrl+P、Ctrl+F、F12 等浏览器快捷键。插件可以自己处理 `contextmenu` 事件做自定义菜单。
- 支持 `<script type="module">`，可以用 Vite 等工具打包后放进插件目录。

引入 SDK（地址固定，由壳提供）：

```html
<link rel="stylesheet" href="/__sdk__/slacking.css" />
<script src="/__sdk__/slacking.js"></script>
```

`slacking.css` 提供和壳一致的颜色变量（`--sd-text`、`--sd-bg`、`--sd-accent` 等）和基础控件样式，并自动跟随浅色 / 深色主题（`<html data-theme="dark">`）。可以不用。

插件自己的文件用相对路径引用，例如 `<script src="app.js">`。

### JS API

所有方法都返回 Promise。失败时 reject 一个 `Error`，带 `code` 字段。

| 方法 | 权限 | 说明 |
|---|---|---|
| `slacking.app.info()` | 无 | `{ shellVersion, platform, language, theme, pluginId }`。platform 是 `windows` / `macos` / `linux`，language 是 `zh-CN` / `en`，theme 是 `light` / `dark` |
| `slacking.on(name, fn)` | 无 | 监听事件，返回取消函数。目前只有 `theme.changed`（参数 `{ theme }`） |
| `slacking.storage.get(key)` | 无 | 读取，不存在时返回 `null` |
| `slacking.storage.set(key, value)` | 无 | value 可以是任何 JSON。总大小上限 1MB |
| `slacking.storage.remove(key)` | 无 | 删除 |
| `slacking.notify.show({ title, body })` | notify | 系统通知 |
| `slacking.backend.call(method, params)` | 无 | 调用插件自己的本地程序，见第 7 节 |
| `slacking.call(method, params)` | — | 底层调用，一般不用 |

错误码只有 6 个：

| code | 含义 |
|---|---|
| `permission_denied` | 没有申请对应权限 |
| `unsupported_platform` | 当前系统不支持这个功能 |
| `invalid_params` | 参数不对 |
| `not_found` | 没有这个 API 或方法 |
| `timeout` | 超时（后端调用 30 秒） |
| `internal` | 其他错误，`message` 里有说明 |

快捷键、窗口操作、联网请求等 API 会在用到它们的插件开发时加入（M4 起）。

## 5. 权限

安装时，用户会看到插件申请的全部权限，整体同意后才能使用。v1 不能单独撤销某项权限，想收回就禁用插件。

| 权限 | 风险 | 用户看到的说明 |
|---|---|---|
| notify | 低 | 发送系统通知 |
| hotkey | 低 | 注册全局快捷键 |
| windows.read | 中 | 读取所有窗口的标题和程序名 |
| windows.control | 中 | 隐藏、显示、置顶、最大化其他程序的窗口 |
| wallpaper | 中 | 把其他程序的窗口嵌入桌面，或修改它的边框 |
| network | 中 | 访问互联网 |
| llm | 中 | 使用用户配置的 AI 接口 |
| files | 中 | 读写用户在对话框里选择的文件 |
| input | 高 | 记录和模拟键盘鼠标操作 |

读写自己的数据、打开自己的窗口不需要权限。

另外，确认框还会显示：

- 有 `background` 时显示「常驻后台运行」。
- 有 `backend` 时醒目警告「包含本地程序」：本地程序以用户身份运行，**权限管不住它**，可以直接读写文件、联网。

插件升级后申请了新权限，壳会停用插件，等用户在「重新加载」时再次确认。

## 6. 后台页

需要在界面关闭后继续工作的插件（闹钟、老板键等）可以声明 `background`。壳启动时会为它打开一个看不见的窗口。

- **后台页必须引入 `slacking.js`。** 壳每 5 秒发一次心跳，SDK 自动回应。超过 10 秒没有回应，壳会停掉后台页，并提示「无响应」。用户在插件页点「重启」后才会再次运行。
- 每个后台页会多占几十 MB 内存，只在真正需要时使用。
- 后台页和界面是两个独立的页面，不共享变量。需要共享的数据存在 `storage` 里。

## 7. 本地程序（backend）

```json
"backend": { "runtime": "python", "entry": "backend/main.py" }
```

| runtime | 说明 |
|---|---|
| python | M1 使用电脑上已安装的 Python 3.10 以上版本。之后会改为由壳自动下载运行环境，每个插件一个独立环境 |
| node | 使用电脑上已安装的 Node.js |
| binary | 插件自带的可执行文件。`entry` 可以按平台写：`{"windows-x64": "bin/app.exe", "macos-arm64": "bin/app", "macos-x64": "bin/app-x64", "linux-x64": "bin/app"}` |

### 生命周期

- 第一次调用 `slacking.backend.call` 时启动。
- 插件的所有窗口（界面和后台页）都关闭后，壳会结束它。
- 结束流程：发送 `shutdown` → 关闭 stdin → 等 3 秒 → 强制结束。**它启动的子进程也会一起被结束**（Windows 用 Job Object，macOS / Linux 用进程组）。
- 意外退出时，插件显示「已崩溃」和最后 20 行日志，不会自动重启。用户点「重启」后，下次调用时重新启动。

### 协议

stdin / stdout 上的 JSON-RPC 2.0，**一行一条 JSON**，UTF-8。

- **stdout 只能写协议消息。** 日志写 stderr，壳会保存到 `logs/plugins/<id>.log`（超过 1MB 轮换）。stdout 里的非 JSON 内容会被忽略并记进日志。
- 壳启动进程时设置了 `PYTHONUTF8=1`、`PYTHONUNBUFFERED=1`、`PYTHONIOENCODING=utf-8`，工作目录是插件目录。

壳发给插件：

| 消息 | 说明 |
|---|---|
| `initialize`（请求，id 为 0） | 参数 `{ shellVersion, pluginId, dataDir, language, platform }`。`dataDir` 是插件自己的数据目录。回复任意结果即可 |
| `shutdown`（通知） | 准备退出，3 秒后强制结束 |
| 其他方法（请求） | 界面调用 `slacking.backend.call(method, params)` 时转发过来，30 秒内必须回复 |

插件发给壳：调用和网页插件同名的 API，例如：

```json
{"jsonrpc":"2.0","id":1,"method":"notify.show","params":{"title":"到点了"}}
```

后端和界面共用同一组权限。`backend.call` 只能由界面调用。

错误格式：

```json
{"jsonrpc":"2.0","id":1,"error":{"code":-32000,"message":"给人看的说明","data":{"code":"permission_denied"}}}
```

`data.code` 是第 4 节的 6 个错误码之一。

### Python SDK

`templates/python-plugin/backend/slacking_plugin.py`，零依赖，复制到插件里使用：

```python
import slacking_plugin as sp

@sp.method("greet")
def greet(params):
    sp.notify("有人打招呼", params.get("name", ""))   # 调用壳的 API
    return {"text": "你好"}

sp.run()   # 放在最后
```

- `sp.context`：`initialize` 传来的信息，例如 `sp.context["dataDir"]`。
- `sp.call(method, params)`：调用壳的 API，失败时抛 `sp.ShellError`（有 `code` 和 `message`）。
- 每个请求在单独的线程里处理，处理函数里可以放心调用 `sp.call`。
- 导入 SDK 后，`print()` 会写到 stderr（日志），不会破坏协议。

## 8. 测试用的坏插件

`tests/` 里有几个故意写坏的插件，用来确认壳不会被插件拖垮：

| 文件夹 | 测试内容 |
|---|---|
| `tests/bad-web` | 沙箱越权检查（拿 Tauri 接口、读宿主页面、联网、读其他插件文件、无权限发通知等），以及让自己的窗口死循环 |
| `tests/bad-background` | 后台页 15 秒后死循环，壳应在约 10 秒后停掉它并通知 |
| `tests/bad-python` | Python 后端崩溃、卡住超时、刷屏输出、留下子进程 |
| `tests/selftest` | 无界面自检：后台页把 API、沙箱、CSP、后端调用的结果写进自己的 storage，供自动化测试读取 |

## 9. 平台差异

壳在不同系统上的差异集中记录在壳仓库的 [docs/platform.md](https://github.com/privatevoidyou/slacking-desk/blob/main/docs/platform.md)。插件可以用 `slacking.app.info().platform` 判断当前系统。
