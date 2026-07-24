# build-resume-portfolio-site

一个包含两个协作 skill 的 Codex plugin：先验证简历内容，再生成分阶段的 React + Vite 个人简历与作品集网站。

## 能力

- 内容预检与事实边界
- 视觉概念原型与创意方向
- 媒体艺术指导与参考图库
- 截图审计、响应式修复与可访问性检查
- 安全动效、视频 Poster 与本地视频升级
- 可选的 APIHz 媒体搜索与导入流程

## 包含的 skills

- `resume-content-intelligence`：提取事实、核验经历、优化文案并生成已确认内容包
- `build-resume-portfolio-site`：根据已确认内容生成、审计和增强 React + Vite 网站

Plugin manifest：`.codex-plugin/plugin.json`

## 使用

在 Codex 中安装此 plugin 后，可以分别调用两个 skill；也可以直接描述目标。网站 skill 在发现内容包缺失时，会要求先走内容核验流程。

## 敏感信息

API 凭据必须通过运行环境变量提供，不要写入仓库。用户素材、构建产物、缓存和 `.resume-site-work/` 状态目录不属于本 skill 发布内容。
