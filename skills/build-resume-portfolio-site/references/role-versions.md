# General and role-specific versions

Use when the user supplies a JD, asks to compare tailored wording, or switches
applications. Keep one factual master. A new employer is not permission to add
credentials, outcomes or tools. Follow `jd-customization-rules.md` for matching.

## Save an approved baseline

After `CONTENT_READY`, save the general version once:

```sh
"$PYTHON" "$SKILL_ROOT/scripts/manage_resume_versions.py" --workspace-root "$WORKSPACE" save general --label "通用版"
```

For a new role, prepare its copy and quality/JD reports in a separate workspace.
Copy the factual master unchanged, draft only supported changes, show the exact
wording and evidence, obtain copy approval, and validate that workspace. Then:

```sh
"$PYTHON" "$SKILL_ROOT/scripts/manage_resume_versions.py" --workspace-root "$WORKSPACE" save frontend --source-workspace "$ROLE_WORKSPACE" --label "前端岗位版"
"$PYTHON" "$SKILL_ROOT/scripts/manage_resume_versions.py" --workspace-root "$WORKSPACE" compare general frontend --output "$WORKSPACE/role-comparison.md"
```

The local comparison includes old/new text, factual sources, evidence excerpts,
ordering changes, partial/transferable/unmatched requirements and questions.
Do not publish it or put it in the site's `public` directory. Explain that a gap
means evidence is absent or incomplete, not that the person lacks the ability.
No numerical hiring probability is produced.

## Select and continue

```sh
"$PYTHON" "$SKILL_ROOT/scripts/manage_resume_versions.py" --workspace-root "$WORKSPACE" list
"$PYTHON" "$SKILL_ROOT/scripts/manage_resume_versions.py" --workspace-root "$WORKSPACE" select frontend
```

`select` returns the version's standalone workspace and records it in
`.resume-site-work/content-versions/active-version.json`. Use that returned path
for PDF export and subsequent site work. The general workspace and other sites
remain intact. On resume, inspect the active marker when present; do not silently
operate on a different version. Each version can have its own site and build state.

Saved handoff files are immutable and checked by hashes. Save changed, newly
approved wording as `frontend-v2`; do not edit the snapshot's input/review files.
If factual evidence changes, prepare and approve a new general master in a new
workspace before creating its role variants. Review any existing site copy and
PDF export plan against that new master before reusing them.

Versioning checks approval status and evidence links, not the truth of arbitrary
claims. The Agent still performs the fact review and records actual user approval.
