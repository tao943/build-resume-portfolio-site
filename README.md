# Resume Portfolio Workflow

一个包含三个协作 Skill 的 Codex 插件：先识别任务路径，再验证简历内容，最后生成具有明确视觉方向的 React + Vite 个人网站。

## 包含的 Skills

- `resume-portfolio-workflow`：在内容全流程、网站全流程和已有网站快速修改之间进行路由。
- `resume-content-intelligence`：提取与核验事实，比较内容策略，生成实施计划，并输出用户批准的内容包。
- `build-resume-portfolio-site`：比较创意版式方向，在用户批准后生成实施计划，再构建、审查和增强 React + Vite 网站。

## 核心链路

```text
任务路由
→ 内容盘点与逐问澄清
→ 2–3 种内容策略
→ 内容策略批准与实施计划
→ 最终文案批准
→ 2–3 种网站视觉方向
→ 网站设计批准与实施计划
→ 单 Agent 或经授权的多 Agent 实现
→ 构建、截图审查、动效与媒体增强
→ 最终验证和交付
```

新网站、内容变化和结构/视觉方向变化必须经过完整探索与计划流程。只有已有确认版本上的局部修改，且不改变事实、定位、结构、视觉命题或交互架构时，才能进入快速修改路径。

## 内置能力

- Superpowers 式逐步头脑风暴、方案比较、显式批准和可执行计划。
- 基于证据的简历内容核验，禁止虚构指标、经历和技能。
- Taste 风格的创意版式词汇与开放视觉探索。
- 离线 UI/UX 设计目录、媒体艺术指导和参考图工作流。
- 内置 Visual Companion：无需 Codex Browser 插件或 npm 安装，在系统浏览器中并排展示 2–3 个视觉方向，最终选择与批准只在 conversation 中完成。
- 经用户明确授权后使用多 Agent，并通过文件所有权避免并行冲突。
- 截图审查、响应式修复、可访问性检查和安全动效。
- 可选 APIHz 媒体搜索、本地 Poster 和视频升级。
- `build-state.json` schema v4，以及安全的 v3→v4 原子迁移工具。

## 使用

安装插件后，通常直接调用总控 Skill：

```text
$resume-portfolio-workflow
```

也可以在边界明确时单独调用内容或网站 Skill。网站 Skill 检测到内容包缺失或需要事实修改时，会要求先执行内容核验流程。

插件清单位于 `.codex-plugin/plugin.json`。

## 跨 Agent 视觉预览

网站 Skill 自带纯 Node.js Visual Companion，只使用 Node 内置模块。它生成
display-only 本地画廊，默认监听 `127.0.0.1`，并返回带随机会话密钥的完整
URL。浏览器不会提交选择；用户必须回到 conversation 明确批准。

支持具备 Node.js、Shell、文件系统和浏览器访问路径的本地 coding agent：

- Codex：使用可持续运行或异步终端命令；
- Claude Code：使用后台 Shell 任务；
- Cursor：使用其终端后台任务；
- Copilot CLI：使用异步 Shell；
- 其他本地 Agent：保持前台服务器进程，或直接展示静态 HTML。

自动打开浏览器失败时继续提供 URL；服务器不能存活或远程 loopback
不可访问时，保留并展示静态 `gallery.html`。远程场景只使用用户已授权的
端口转发，不上传简历或视觉稿。

## 安全边界

API 凭据只能通过运行环境变量提供，不应写入仓库。用户简历、个人素材、构建产物、缓存和 `.resume-site-work/` 状态目录均不属于插件发布内容。
