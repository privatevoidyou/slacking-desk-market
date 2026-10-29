# Slacking Desk Market / 摸鱼工作台插件市场

[摸鱼工作台](https://github.com/privatevoidyou/slacking-desk)的插件、插件模板和开发文档。壳本身不带任何插件，所有功能都从这里安装。

> 当前处于 M1 阶段：市场索引（`index.json`）和一键安装在 M3 加入。现在可以用壳的「加载本地文件夹」试用下面的插件。

## 目录

| 路径 | 内容 |
|---|---|
| `templates/js-plugin` | 纯网页插件模板（也是 JS 示例插件） |
| `templates/python-plugin` | 网页界面 + Python 后端模板（也是 Python 示例插件），含零依赖的 `slacking_plugin.py` |
| `tests/` | 故意写坏的插件，用来测试壳的隔离和容错 |
| `docs/plugin-guide.md` | 插件开发指南 |

## 试用示例插件

1. 点本页右上角 **Code → Download ZIP**，解压。
2. 打开摸鱼工作台 →「插件」→「加载本地文件夹」，选择解压后的 `templates/js-plugin`。
3. 在确认框里点「同意并加载」，首页就会出现「JS 示例」。

Python 示例需要电脑上已安装 Python 3.10 或更高版本（安装时勾选「Add python.exe to PATH」）。

## 许可

MIT
