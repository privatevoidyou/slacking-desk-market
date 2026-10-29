# 给接手的 AI / 开发者

项目总说明、协作规则、路线图都在壳仓库的 [AGENTS.md](https://github.com/privatevoidyou/slacking-desk/blob/main/AGENTS.md)，先读那份。

本仓库只放插件相关的东西：

- `docs/plugin-guide.md`：插件开发指南，要写得能直接喂给 AI 照着生成插件。壳的 API 有变化时同步更新。
- `templates/`：JS、Python 两个模板，同时也是示例插件。
- `tests/`：坏插件和自检插件，每个里程碑验收都要用。
- 以后：`index.json`（市场索引，M3，带 ed25519 签名）和所有内置插件（每个插件一个文件夹）。

规则：

- 所有插件都放这里，**不要内嵌进壳**（只有设置类功能属于壳）。
- `templates/python-plugin/backend/slacking_plugin.py` 是 Python SDK 的正本，`tests/` 里的副本要跟它保持一致。
- 推送同样走每个里程碑一个分支 + PR。
