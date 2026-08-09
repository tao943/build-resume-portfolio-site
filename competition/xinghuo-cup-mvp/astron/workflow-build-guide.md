# 星辰 Agent 初赛工作流搭建指南

本指南把 `workflow-spec.json` 映射为星辰 Workflow 控制台节点。先完成比赛
报名，再在星辰 Agent 创建“工作流 Agent”。所有批准必须来自问答节点的会话
回复；浏览器打开、预览访问和沉默都不是批准。

## 开始参数

创建 `resume_file`、`resume_text`、`target_role`、`jd_text`、`public_name`、
`contact_visibility` 六个输入。`resume_file` 与 `resume_text` 至少提供一个；文件
解析失败时由消息节点要求用户粘贴文本，不丢弃当前会话变量。

## 节点映射

| ID | 星辰节点 | 输入 | 输出 | 超时/重试 | 下一条边 |
|---|---|---|---|---|---|
| `start` | 开始 | 六个开始参数 | 原始输入变量 | 平台默认 | `extract_facts` |
| `extract_facts` | 大模型 | 简历文本、既有确认 | `source_facts`、`confirmed_facts`、`clarification_queue` | 60 秒，格式错误重试 1 次 | `validate_facts` |
| `validate_facts` | Python 代码 | 事实 JSON | `facts_valid`、`critical_question` | 10 秒，不重试 | `clarification_decision` |
| `clarification_decision` | 判断 | `critical_question` | 路由 | 无 | 有问题到 `clarification_question`，否则到 `jd_match` |
| `clarification_question` | 问答 | 单个关键问题 | `user_confirmed` 回答 | 必填，最多 1 个问题/轮 | 回到 `extract_facts`，再经 `clarification_decision` |
| `jd_match` | 大模型 | JD、确认事实、证据 | `jd_match_matrix` | 60 秒，格式错误重试 1 次 | `content_strategies` |
| `content_strategies` | 大模型 | 事实与匹配矩阵 | 两到三个策略及推荐 | 60 秒，重试 1 次 | `strategy_approval` |
| `strategy_approval` | 问答选项 | 策略 ID、利弊、推荐 | 明确选择的策略 ID | 必选，不从推荐自动推断 | `tailored_copy` |
| `tailored_copy` | 大模型 | 选中策略、事实、JD 矩阵 | 待批准文案 | 60 秒，格式错误重试 1 次 | `copy_approval` |
| `copy_approval` | 问答 | 完整文案与修改选项 | 批准或聚焦反馈 | 必选；策略批准不能代替 | 批准到 `content_map`，修改回 `tailored_copy` |
| `content_map` | 大模型 | `approved_copy`、公开授权 | `content_map` | 45 秒，重试 1 次 | `creative_directions` |
| `creative_directions` | 大模型 | 内容地图、岗位 | 两到三个创意方向 | 60 秒，重试 1 次 | `direction_approval` |
| `direction_approval` | 问答选项 | 创意方向及推荐 | 选中 `creative_direction` | 必选，不能由浏览器活动推断 | `generate_preview_html` |
| `generate_preview_html` | 大模型 | 批准文案、地图、方向 | 完整 HTML | 90 秒，格式错误重试 1 次 | `preview_delivery` |
| `preview_delivery` | 自定义工具 | 批准数据与 HTML | `preview_artifact`、在线 URL、检查结果 | 30 秒，工具失败重试 1 次 | 成功到 `preview_review`；失败显示检查项 |
| `preview_review` | 问答选项 | 在线 URL、检查结果 | 接受或一次聚焦修改 | 必选 | 接受结束；首次修改回 `generate_preview_html`；第二次失败结束并保留内容包 |

## Python 事实校验节点

`validate_facts` 检查 JSON 可解析、事实 ID/证据 ID 唯一、每条可见事实有证据或
`user_confirmed` 状态，并从 `clarification_queue` 只取第一条阻断问题。代码节点
不得改写事实或文案。

## 变量保存

用会话变量保存 `source_facts`、`confirmed_facts`、`clarification_queue`、
`jd_match_matrix`、`approved_copy`、`content_map`、`creative_direction` 和
`preview_artifact`。每次批准后保存新 revision，不覆盖已经批准的旧值。

## 自定义工具

Task 5 的 OpenAPI 文件发布为自定义 HTTP 工具。鉴权使用平台 Service/Header
配置 Bearer Token；Token 不进入 Prompt、工作流变量、导出文件或截图。

## 调试与导出

逐节点调试后执行一次完整匿名演示，确认三次批准都发生中断与恢复、工具返回
真实在线地址、失败时没有虚假成功。只有成功调试并发布工具后，才发布 Agent。
平台导出的 YML 只在成功调试后保存到发布材料，因为 YML 导入格式与资源绑定由
当前星辰平台版本负责；本仓库不伪造“可导入”YML。
