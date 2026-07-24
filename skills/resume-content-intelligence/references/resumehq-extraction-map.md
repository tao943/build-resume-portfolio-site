# ResumeHQ Extraction Map

This map records what the new Codex skill learns from the checked-out ResumeHQ repository without importing its provider-specific runtime.

| ResumeHQ source | Capability | Decision | New-skill treatment |
|---|---|---|---|
| `commands/writing-coach.md`, `resume_builder.py` | Rewrite bullets around outcomes, actions, scope, and evidence | adopt | Convert the writing rules into provider-neutral prompt guidance. |
| `text_extractor.py` | Extract text from local resume files | adapt | Implement deterministic local PDF/DOCX/MD/TXT extraction with explicit warnings. |
| `evidence_audit.py` | Detect unsupported claims and preserve evidence | adopt | Use evidence IDs and confirmation status for every generated claim. |
| `mcp_scorer.py` | Expose resume tools to an agent | adapt | Expose the workflow as a Codex skill, without requiring ResumeHQ MCP or Anthropic. |
| `resume_builder.py` | Structured resume and application content | adapt | Define a smaller content package for the portfolio-site handoff. |
| `job_discovery.py`, `jd_fetcher.py` | Job discovery and search live jobs | exclude | Outside the personal-site content scope. |
| `ats_scorer.py`, `hr_scorer.py`, `scorer_server.py` | ATS/HR scoring services | exclude | Defer until a separate JD/ATS plan exists; no cloud dependency in v1. |
| `docx_generator.py`, `tracker_utils.py` | Application DOCX and tracker output | exclude | Not needed to generate a personal website. |
| `.codex.mcp.json`, cloud setup, API configuration | MCP server, cloud scoring, provider credentials | exclude | The new skill uses the active Codex model and local scripts. |

## Reuse boundary

Use the repository as a reference for workflow ideas and MIT-licensed source patterns. Do not copy Anthropic SDK calls, cloud scoring endpoints, job-board integrations, or application-tracker behavior into the skill.
