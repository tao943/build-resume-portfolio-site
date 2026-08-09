# Portfolio Aesthetic Quality Loop Design

## Goal

Improve the visual quality and distinctiveness of generated portfolio sites
without adding another user decision stage, generating multiple full sites, or
assuming that content fit implies aesthetic quality. Keep the existing six
design decisions, independent browser previews, one integrated React + Vite
generation, and two-round repair limit.

The new internal flow is:

```text
approved content and design choices
-> creative direction
-> executable design contract
-> integrated site
-> responsive and interaction capture
-> deterministic audit plus visual-quality review
-> evidence-linked local repair
```

## Reuse assessment

The implementation adds no runtime dependency or external service.

- **Impeccable — wrapped-method adoption:** reuse its separation between product
  context, design context, deterministic detectors, critique, and focused polish.
  The Skill owns its smaller portfolio-specific rule set and does not invoke an
  external Skill at runtime.
- **Taste Skill — wrapped-method adoption:** reuse its anti-template preflight
  concepts for hierarchy, typography, composition, spacing, motion, and visual
  specificity. Do not copy a generic style preset into generated sites.
- **ArtifactsBench — reference only:** reuse the method of rendered evidence,
  task-specific checklists, and visual judging. Do not vendor its benchmark,
  dataset, model integration, or evaluation infrastructure.
- **json-render and A2UI — architecture reference only:** reuse the separation
  between a constrained semantic specification and its renderer. Do not replace
  the existing direct React + Vite generation with a component-catalog runtime.
- **DesignBench — workflow reference only:** retain generation, inspection,
  repair, and compile verification as distinct stages. Do not add its datasets,
  browsers, API keys, or model dependencies.

Impeccable and json-render/A2UI use Apache-2.0 licenses; Taste Skill uses MIT.
Reference-only projects contribute method, not copied source. Preserve upstream
attribution if any future change copies protected text or code.

## Scope

### In scope

- compile approved creative intent into an executable design contract;
- distinguish identity fit from aesthetic quality;
- add deterministic anti-template and production-quality checks;
- make browser captures formal inputs to aesthetic review;
- link every repair to evidence, a contract rule, and a bounded source region;
- activate the existing local-repair prompt;
- validate all new report shapes and required Skill resources;
- synchronize the verified source Skill to the installed global Skill.

### Out of scope

- a local or remote image/reference library;
- multiple complete website candidates;
- a new browser approval mechanism;
- automatic selection or approval from browser activity;
- a hard aesthetic guarantee or universal aesthetic score;
- a hosted evaluator, paid model API, or new package dependency;
- changing the six user-facing discovery categories or their order.

## Content and aesthetic responsibility

Content determines identity, narrative priority, density, proof, and domain
specificity. It may propose design hypotheses, but it cannot by itself approve a
style or prove that the output is attractive.

Evaluate two independent dimensions:

1. **Identity fit:** personal specificity, narrative priority, role relevance,
   content-to-form relationship, and avoidance of unrelated metaphors.
2. **Aesthetic quality:** visual hierarchy, typography, color relationships,
   spatial rhythm, composition, distinctiveness, purposeful motion, responsive
   integrity, and production polish.

A site must pass both dimensions. A strong identity-fit result cannot compensate
for weak visual quality, and decorative polish cannot compensate for a generic
or inaccurate personal narrative.

## Executable design contract

Add schema-version-1 `reports/design-contract.json`. Generate it after the
approved `site-design-spec.json`, `design-intelligence.json`, and
`creative-direction.json`, and before the first React edit. This is an internal
compiled artifact, not another confirmation gate.

Required sections:

- `identity_strategy`: audience, narrative priority, density, and content-form
  relationships derived from approved facts;
- `signature`: visual protagonist, composition commitment, one recognizable
  structural device, and a template-independence claim;
- `layout`: hierarchy, section rhythm, alignment logic, density ranges,
  responsive transformations, and prohibited generic arrangements;
- `typography`: roles, scale relationships, measure, rhythm, contrast, and
  fallback behavior;
- `color`: semantic roles, proportion guidance, contrast targets, surface
  relationships, and prohibited effects;
- `surface`: container, border, radius, shadow, texture, and repetition rules;
- `motion`: exactly one primary system, compatible secondary effects, purpose,
  controller ownership, reduced-motion, coarse-pointer, and fallback behavior;
- `anti_template_rules`: observable portfolio-specific slop detectors;
- `acceptance_checks`: observable checks mapped to identity fit, aesthetic
  quality, accessibility, responsive behavior, and runtime safety;
- `traceability`: source decision IDs and creative-direction fields used to
  compile each commitment.

Use ranges, proportions, relationships, and observable commitments where exact
values would overfit. Allow exact tokens when they implement an approved color,
type, breakpoint, or accessibility requirement. The contract may refine an
approved choice but cannot reopen or contradict it.

Validate the report atomically with a dedicated schema and validator. Missing
signature, anti-template, responsive, reduced-motion, or traceability data is a
blocking validation failure.

## Deterministic audit

Extend screenshot review with deterministic findings that can be established
from source, computed layout, capture metadata, or repeatable visual inspection.
At minimum check:

- horizontal overflow, clipping, overlap, console errors, and broken navigation;
- contrast, readable type sizes, line measure, heading hierarchy, and focus;
- spacing rhythm, unintended alignment drift, and excessive density;
- repeated uniform-card treatment across unrelated content;
- generic centered hero plus symmetric feature-grid composition when prohibited;
- indiscriminate glass, glow, gradient, pill, radius, and shadow repetition;
- missing visual protagonist or missing signature structural device;
- motion without an identified content or navigation purpose;
- responsive collapse that destroys the approved hierarchy;
- missing coarse-pointer, reduced-motion, loading, error, or Poster fallback.

Each finding records `rule_id`, viewport/state, selector or region, evidence,
severity, affected contract path, and permitted repair scope. Avoid universal
style prohibitions: a detector only fails when it contradicts the approved
contract, appears as indiscriminate repetition, or causes an observable quality
or usability defect.

## Visual-quality review

Upgrade `reports/visual-audit.json` so browser screenshots and interaction-state
captures are required evidence for a checklist-guided review. Record separate
dimension results for identity fit and aesthetic quality. Each dimension has:

- a concise verdict;
- supporting screenshot or capture evidence;
- observable strengths and findings;
- contract paths used as criteria; and
- `pass`, `repairable`, or `blocking` status.

The aesthetic checklist covers hierarchy, typography, color coherence, spatial
rhythm, composition distinctiveness, surface restraint, purposeful motion,
responsive integrity, and production polish. The identity checklist covers
personal specificity, narrative accuracy, priority, domain relevance, and
content-form fit.

Do not use a single opaque beauty score as the gate. Scores may be included as
diagnostic values only when their rubric and evidence are present. Status and
observable findings control repair.

## Evidence-linked repair

Replace the unavailable repair prompt with a production-ready local repair
contract. A repair item must contain:

- finding and severity;
- screenshot/capture evidence;
- violated `rule_id` and design-contract path;
- affected React/CSS region and permitted files;
- preserved user decisions and invariants;
- intended observable result; and
- verification captures to repeat.

Modify only the smallest region capable of resolving the finding. Never use the
repair loop to choose a new style, change approved content, replace the primary
motion system, or rewrite the complete page. Rebuild and recapture desktop,
tablet, mobile, and affected interaction/fallback states after each completed
round. Keep the existing limit of two completed rounds and preserve the last
valid preview on any failure.

If blocking findings remain after round two, set `visual_blocked` and report the
evidence. If only advisory findings remain, present them with the integrated site
instead of silently extending the loop.

## Files and interfaces

Expected source changes are limited to the canonical Skill package:

- `SKILL.md` — insert the design-contract and dual-audit stages;
- `references/design-contract.md` and schema — define the compiled artifact;
- `scripts/validate_design_contract.py` and tests — deterministic validation;
- `references/screenshot-review-rules.md` — add anti-template and dual-dimension
  review requirements;
- `prompts/01-generate-integrated-site.md` — require and obey the contract;
- `prompts/04-audit-screenshot.md` — produce evidence-linked dual review;
- `prompts/05-repair-local-issues.md` — activate bounded repair;
- `scripts/validate_skill_resources.py` and behavior tests — require the new
  resources and enforce ordering;
- installed global Skill — receive a file-for-file sync only after verification.

Do not modify Xinghuo competition or Worker service files for this feature.

## Error handling and compatibility

- Older workspaces without a design contract return to the pre-generation
  compilation step; do not fabricate approval evidence.
- A contract validation failure freezes React edits and keeps the last valid
  preview and snapshot.
- A capture or audit infrastructure failure does not consume a repair round.
- A visual-review failure preserves successful build evidence but cannot promote
  the candidate as confirmed.
- Existing schema-version-4 state remains valid because the current
  `visual_repair_round` and stage model already represent bounded repair.
- Existing user approvals remain valid when the contract only compiles them. A
  contradiction requires returning to the affected discovery decision.

## Testing

Follow RED-GREEN-REFACTOR without spawning agents because the user selected
current-session single-Agent execution.

1. Add behavior tests that fail against the current Skill because the design
   contract, dual audit, anti-template rules, and usable repair prompt are absent.
2. Add validator tests for valid input, missing signature, contradictory trace,
   missing responsive/motion fallback, invalid finding paths, and atomic failure.
3. Implement the smallest contracts and validator that pass the focused tests.
4. Run all Skill script tests and repository behavior tests.
5. Run resource validation and the official Skill quick validator.
6. Compare canonical and installed file sets and hashes after synchronization.

Acceptance requires proof that the Skill:

- never treats content fit as aesthetic approval;
- compiles approved decisions before React source generation;
- blocks generation on an invalid contract;
- reviews identity fit and aesthetic quality separately;
- records screenshot-backed, contract-linked findings;
- detects template-like repetition without banning approved intentional styles;
- performs only bounded local repair for at most two completed rounds;
- preserves browser consent and conversational approval semantics; and
- adds no new dependency or external runtime requirement.
