# 星火杯初赛 MVP

该目录把 Resume Portfolio Skill 迁移为可发布的讯飞星辰工作流 Agent。初赛
闭环为：简历事实核验、JD 定制、作品集规划、非模板化单页 HTML 生成、在线
预览验证与托管。

星辰负责认知、决策、审批和 HTML 生成；Cloudflare Worker 只执行确定性的安全
验证和托管，不调用任何模型。

## 目录

- `astron/workflow-spec.json`：机器可验证的节点顺序与状态契约。
- `astron/workflow-build-guide.md`：星辰控制台搭建与变量连线。
- `astron/prompts/`：七个 Spark 大模型节点 Prompt。
- `contracts/preview-request.example.json`：预览工具合法请求示例。
- `openapi/preview-plugin.openapi.yaml`：星辰自定义 HTTP 工具接口契约。
- `demo/`：完全匿名的简历、JD 和三分钟演示脚本。
- `scripts/`：工作流与发布包验证器。
- `../../services/xinghuo-preview-worker/`：无第三方运行依赖的在线预览服务。

## 本地验证

从仓库根目录执行：

```powershell
python competition/xinghuo-cup-mvp/scripts/validate_workflow_spec.py competition/xinghuo-cup-mvp/astron/workflow-spec.json
python competition/xinghuo-cup-mvp/scripts/validate_release.py competition/xinghuo-cup-mvp
Push-Location services/xinghuo-preview-worker
npm test
npm run check
Pop-Location
python -m unittest tests.test_xinghuo_mvp_contract -v
python -m unittest discover -s tests -v
```

全部命令退出码必须为 0。发布验证器会检查七个 Prompt、工作流节点、Worker
源文件、演示材料和常见密钥误提交。

## 部署预览 Worker

部署会创建 Cloudflare KV、Secret 和 Worker，属于外部状态变更，应在操作者明确
批准后进行。

1. 复制配置模板：

```powershell
Copy-Item services/xinghuo-preview-worker/wrangler.toml.example services/xinghuo-preview-worker/wrangler.toml
```

2. 使用已登录的 Wrangler 创建生产和预览 KV，将返回的 ID 写入本地
   `wrangler.toml`。不要提交该文件。
3. 生成至少 32 字节随机值，通过 `wrangler secret put PREVIEW_WRITE_TOKEN`
   保存；不要把值写入命令历史、Prompt、截图或仓库。
4. 在 `services/xinghuo-preview-worker` 执行 `wrangler deploy`。
5. 用匿名示例请求验证：无 Bearer 返回 401，合法请求返回 201，公开 URL 返回
   HTML 且包含 `default-src 'none'` CSP。

## 配置星辰自定义工具

1. 将 `preview-plugin.openapi.yaml` 的 `servers[0].url` 替换为真实 Worker URL。
2. 在星辰工具开发中新建自定义 HTTP 工具。若当前控制台支持 OpenAPI 导入，
   导入该文件；否则按文件中的字段和响应 Schema 手动创建。
3. 鉴权选择 Service/Header Bearer 配置，Secret 使用与 Worker 相同的值，但不
   暴露给模型 Prompt 或普通工作流变量。
4. 调试合法请求，确认 `preview_id`、`preview_url`、`status` 和四项 `checks`。
5. 发布工具，只有已发布工具才能绑定到正式工作流。

## 搭建并发布星辰 Agent

1. 按 `astron/workflow-build-guide.md` 创建 16 个节点并连线。
2. 将七个 Prompt 分别粘贴到对应 Spark 大模型节点，保持 JSON 输出约束。
3. 创建八个会话变量，三次批准分别使用独立问答节点。
4. 将已发布的预览工具绑定到 `preview_delivery`。
5. 用 `demo/` 材料完整调试，验证事实澄清循环、`unmatched`、三次批准、一次
   聚焦修改上限和真实预览 URL。
6. 发布 Agent，确认它能在智能体广场检索，并使用评审视角账号完成一次体验。
7. 从平台导出成功运行后的 YML，作为复现材料；不要用仓库中的
   `workflow-spec.json` 冒充平台 YML。

## 初赛提交检查

- 已在赛事官网报名并完成团队实名认证。
- Agent 已发布并可在智能体广场检索。
- 初赛作品信息文档已填写并在截止前提交。
- 演示视频只使用匿名材料。
- Worker 和 Agent 公共链接可从评审网络访问。
- 星辰 Agent 是入口与核心运行载体，预览服务没有模型推理。
- 项目名称与主要功能在赛程中保持一致。
- 发布后将真实 Agent URL 记录在团队内部提交清单，不写入含密钥的配置文件。

## 失败边界

平台账号登录、KV 创建、Secret 写入、Worker 部署、星辰控制台编辑和广场发布都
是认证后的外部操作。本地代码通过不等于比赛发布完成；只有真实 Agent URL、
公开预览和广场可检索性都验证成功，才能标记初赛 MVP 发布完成。
