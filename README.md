# build-resume-portfolio-site

一个自包含的简历作品集网站 Skill：将简历材料和可选岗位 JD 转化为经过事实核验、用户批准的内容，并生成可运行的 React + Vite 个人作品集网站。

## 能力

- 提取简历事实与证据，区分事实、推断、待确认内容和最终文案。
- 通过对话逐项澄清日期、职责、项目范围、成果、指标和公开信息。
- 对岗位 JD 进行匹配分析，保留硬性要求、核心能力和加分项，并标记匹配、部分匹配、可迁移能力或未匹配。
- 对每段经历和项目文案执行写作、STAR、ATS、事实证据与 JD 相关性质量门；只有证据充分时才提供加强版本。
- 在生成网站前分别确认整体结构、字体排版、配色、媒体处理、主动效和副动效。
- 每个启用的设计类别都可在用户明确同意后打开独立的浏览器视觉预览；预览只用于展示，不代替对话批准。
- 在明确需求后生成 TODO 计划，等待批准，再生成并验证完整网站。
- 自动执行 React + Vite 构建、响应式检查、视觉审计和有限范围修复。
- 网站完成后支持“满意完成”“加强动效”或“提出修改”三种验收路径。
- 按当前阶段加载内容、设计、实施或验收指南，避免启动时读取所有流程细节。
- 不依赖额外 Word 库即可读取 DOCX 正文、表格和超链接文字；支持带 BOM 的 UTF-8 简历文本。

## 工作流程

```text
简历/JD 内容准备
→ 事实与证据核验
→ JD 匹配（可选）
→ 内容策略与文案批准
→ 内容质量报告验证
→ 整体结构
→ 字体排版
→ 配色系统
→ 媒体处理
→ 主动效
→ 副动效
→ 完整需求确认
→ TODO 计划展示与批准
→ 实施计划验证
→ 一次生成完整 React + Vite 网站
→ 构建、截图审查与有限修复
→ 最终验收
```

Skill 会保留事实与证据边界：未匹配的 JD 要求不会被自动写入简历或网站，缺少证据的指标、职责、日期和技术不会被虚构。

## 使用

将 `skills/build-resume-portfolio-site/` 安装为本地 Skill 后，在对话中调用：

```text
$build-resume-portfolio-site
```

然后提供简历文件、文本材料、岗位 JD、作品集素材或已有网站信息。Skill 会在内容未就绪时先完成内容准备，在设计选择前询问是否需要浏览器视觉展示，并在最终生成前等待明确的计划批准。

## 浏览器视觉预览

内置 Visual Companion 使用 Node.js 内置模块启动本地只读展示页，不依赖浏览器插件或 npm 包。浏览器只负责呈现候选风格；选择、批准和流程推进始终以对话中的明确回复为准。

如果宿主无法启动本地服务，Skill 会提供静态 HTML 回退。用户也可以拒绝某一类别的浏览器预览，继续使用文本方式完成选择。

## 目录

```text
README.md
skills/build-resume-portfolio-site/
├── SKILL.md              # 主流程与状态门禁
├── prompts/              # 内容、设计、生成和审查提示
├── references/           # 内容、JD、设计、动效和输出契约
├── scripts/              # 本地校验、预览和构建辅助脚本
├── assets/               # Visual Companion 和参考资源
└── vendor/ui-ux-pro-max/ # 本地 UI/UX 设计数据库
```

本 Skill 不要求其他内容 Skill、远程组件注册表或专用云端模型服务。需要能读取文件、运行命令的编程 Agent，以及 Python 3 和 Node.js/npm。生成 React + Vite 项目时需要安装项目依赖，使用的模型额度、域名和部署服务由使用者自行准备。

DOCX 和 UTF-8 文本提取使用 Python 标准库；PDF 提取仅在环境已有对应库时作为可选辅助。扫描件、页眉页脚、批注和嵌入图片中的文字应通过原生读取或用户确认补充，不以提取结果代替事实核验。

## 交付范围

Skill 包含工作流、校验工具、设计资料和本地视觉预览工具。运行后交付网站源码、构建产物、本地运行方式和实际完成的验证结果；网站发布需要使用者指定部署目标并授权。简历公开字段以使用者确认内容为准，不虚构经历、指标或 JD 要求，不承诺求职结果。

## 验证与打包

```sh
python3 -m unittest discover -s skills/build-resume-portfolio-site/scripts -p 'test_*.py'
python3 -m unittest discover -s tools -p 'test_*.py'
python3 tools/package_skill.py skills/build-resume-portfolio-site /absolute/output/build-resume-portfolio-site.zip
```

Windows 可使用已安装的 Python 3 命令替换 `python3`。发布包只收录 Skill 运行资料，保留第三方许可；不包含测试、缓存、工作目录或环境密钥文件。打包命令拒绝覆盖已有发布包，并输出 SHA-256 供核验。
