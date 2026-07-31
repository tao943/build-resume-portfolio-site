# Resume Portfolio Workflow

一个将简历材料转化为已核验内容与 React + Vite 个人作品集网站的 Codex
Skill 组合。

## Skills

- `resume-portfolio-workflow`：在内容工作、完整建站和已有网站局部修改之间路由。
- `resume-content-intelligence`：提取、核验并优化简历事实与文案。
- `build-resume-portfolio-site`：确认完整设计需求和 TODO Plan 后，一次生成完整网站。

## 完整建站流程

```text
内容核验
→ 整体结构
→ 字体排版
→ 配色系统
→ 条件性媒体处理
→ 主动效
→ 可多选的兼容副动效
→ 完整需求确认
→ 可读 TODO Plan 展示与批准
→ 可验证实施计划
→ 一次生成完整 React + Vite 网站
→ 自动构建、截图审查与有限修复
→ 接受 / 加强动效 / 提出修改
```

每个启用的设计类别都会先在对话中给出候选与建议。用户初选后，Skill
会单独询问是否打开浏览器预览。因此最多可以分别打开六次浏览器；每次
预览相互独立，不累计，也不会拼接成最终网站。

## Visual Companion

内置 Visual Companion 只依赖 Node.js 内置模块，不要求安装 Browser 插件
或 npm 包。它在 `127.0.0.1` 启动带随机会话密钥的只读服务，同时保留静态
`gallery.html` 作为回退。

浏览器只负责视觉展示：没有选择按钮、审批控件、表单、分析或事件收集。
用户必须返回 conversation 明确确认。打开、刷新或截图都不算批准。

这种方式可以被具备 Node.js、Shell、文件系统和浏览器访问能力的本地 coding
agent 使用，包括 Codex、Claude Code、Cursor 和 Copilot CLI。宿主无法保持
本地服务时，可以直接展示静态 HTML；远程环境只使用用户已经授权的端口转发。

## 计划门禁

完整需求确认后，Skill 先生成
`.resume-site-work/reports/site-todo-plan.md`，展示文件范围、任务、验证和
交付物，并等待用户明确批准。随后生成机器可验证的
`site-implementation-plan.json`。两个计划门禁完成前不得编辑 React 源码。

## 最终验收

完整网站展示后提供三个选择：

- `当前效果满意，完成`
- `加强动效`
- `提出修改`

加强动效只修改动效层；局部反馈直接修复。推翻结构、排版、配色等核心决定时，
只返回受影响的选择阶段，并重新确认需求和 TODO Plan。

## 使用

通常调用总控 Skill：

```text
$resume-portfolio-workflow
```

边界明确时也可以直接调用：

```text
$build-resume-portfolio-site
```

插件清单位于 `.codex-plugin/plugin.json`。用户简历、媒体、构建结果、缓存和
`.resume-site-work/` 不属于插件发布内容；凭据只能由运行环境变量提供。
