# Site Planning Contract

Create `.resume-site-work/reports/site-implementation-plan.json` only after the
site design specification is explicitly approved.

Each task records:

- stable task ID and dependencies;
- exact writable files;
- inputs consumed and interfaces produced;
- acceptance criteria;
- exact verification commands;
- rollback and snapshot boundaries.

Select `single-agent`, `fresh-agent-sequential`, or `parallel-wave`.
Multi-agent strategies require explicit user authorization and a separately
validated `multi-agent-implementation.json`. Validate the site plan before any
React source edit.
