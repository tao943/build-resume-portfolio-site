# build-resume-portfolio-site

把简历和可选岗位 JD 转化为有事实依据的内容，生成可运行的 React + Vite 作品集网站，以及同一份内容的投递用 PDF。

适合已经使用编程 Agent、希望获得可自行维护的网站源码的求职者。支持中文和英文简历；不虚构经历、职责、指标或岗位要求。

## 从这里开始

1. 将仓库中的 `skills/build-resume-portfolio-site/` 安装到所用 Agent 的技能目录；ZIP 用户解压后使用同名目录。
2. 在对话里输入下方示例，并附简历。首次运行会检查环境，说明哪些能力可用。
3. 确认简历事实和最终文案，选择推荐的快速模式或深度定制，查看成品并提出修改。

```text
$build-resume-portfolio-site
请根据这份简历制作作品集，使用快速模式；同时生成一份投递用 PDF。
```

不想先使用个人信息时，可用 [有经验者示例](skills/build-resume-portfolio-site/assets/examples/experienced.txt)、[应届生示例](skills/build-resume-portfolio-site/assets/examples/graduate.txt) 和 [岗位 JD 示例](skills/build-resume-portfolio-site/assets/examples/frontend-jd.txt)。这些人物、经历与岗位均为虚构演示材料。

## 两种使用模式

| 模式 | 适合场景 | 操作方式 |
| --- | --- | --- |
| 快速生成 | 希望尽快获得完整成品 | Agent 推荐兼容的字体、配色、媒体和动效；在一个预览中查看，一次确认设计与执行计划 |
| 深度定制 | 有明确视觉偏好 | 逐项比较设计选择，保留细节控制；复用同一个预览会话 |

两种模式都会核对事实、确认具体文案和公开字段。已经明确的偏好与授权会被复用；内容改变时只重新确认受影响部分。旧工作区保留原有确认状态。

## 内容与岗位版本

- 从材料提取事实和证据，标记矛盾、缺失与待确认内容。
- 按岗位区分硬性要求、核心能力和加分项，显示充分匹配、部分匹配、可迁移能力或缺少证据。
- 审查职责归属、STAR 叙述、文字可读性和真实关键词；没有证据时保留定性描述。
- 保存通用版和多个岗位版，展示文案前后对照、事实出处、证据及待补充条件。
- 版本共用事实母版，分别保留网站和 PDF。旧版不会被岗位改写覆盖。

可以直接说：“保存这份通用版，再针对这个 JD 制作岗位版，并告诉我具体改了什么。”

## 文件导入与环境

运行需要能读取文件和执行本地命令的 Agent、Python 3.10+、Node.js 22.12+ 与 npm。无需全局安装 npm 包。

```sh
python3 skills/build-resume-portfolio-site/scripts/check_environment.py
```

- DOCX 正文、表格、超链接文字及 UTF-8 文本：Python 标准库即可读取。
- PDF：使用可选 `pdfplumber`；空页、疑似乱码和多栏顺序风险会生成带页码的核对报告。
- 图片／扫描件：可使用宿主图像阅读，或用户选择的本地 Tesseract OCR。识别结果仍需核对，不自动上传到第三方服务。
- PDF 导出：需要 `reportlab`、`pypdf`；中文需要覆盖相应字符的本地 TrueType 字体。字体会嵌入 PDF，缺字时明确报错。

缺少工具时会给出具体补充方式。详见 [导入与环境指南](skills/build-resume-portfolio-site/references/import-guide.md)。模型额度、域名与托管服务由使用者自行准备。

## 交付内容

- React + Vite 网站源码、生产构建与本地运行说明。
- 同一份已确认文案生成的 PDF 和打印 HTML；检查文字提取顺序、分页与显示效果。
- 经过公开字段确认后，网站可包含该公开版 PDF 的下载入口。
- 实际完成的构建、响应式、键盘访问、减少动态效果及视觉检查结果。
- 后续局部修改、岗位版本切换与失败恢复方式。

私有投递 PDF、原始简历、证据和对照报告不会作为网站公开文件。发布网站仍由使用者另行指定和授权，本次版本没有新增部署流程。不承诺求职结果或通用 ATS 通过率。

## 验证与开发

```sh
python3 -m unittest discover -s skills/build-resume-portfolio-site/scripts -p 'test_*.py'
python3 -m unittest discover -s tools -p 'test_*.py'
python3 tools/package_skill.py skills/build-resume-portfolio-site /absolute/output/build-resume-portfolio-site.zip
```

PDF 实测需要上述可选库；浏览器会话测试需要 Node 和允许本地回环服务的环境。测试报告会明确跳过的项目。Windows 使用实际安装的 Python 3 命令替换 `python3`。

`tools/create_demo_workspace.py` 可以创建两种虚构资料的内容测试工作区。里面的审批记录明确标为模拟测试，不能复制到真实用户流程。完整网站和 PDF 的实际验证情况见 [验证记录](docs/validation-v1.4.md)。

发布包只收录运行资源，排除测试、缓存、工作区和环境密钥文件，保留第三方许可；拒绝覆盖旧包并输出 SHA-256。主入口按阶段加载指南，无需额外子 Skill。
