# Xinghuo Cup Qualifier MVP Design

## Goal

Migrate the resume portfolio Skill into a publishable iFLYTEK Astron Agent
qualifier MVP. The Agent verifies resume facts, tailors approved copy to a
target role, plans an evidence-led portfolio, and returns one shareable online
HTML preview. Full React + Vite project delivery remains a post-qualifier
extension.

## Competition constraints

- Astron Agent is the public entry point and primary orchestration runtime.
- The entry must be published to the Astron Agent marketplace before the
  qualifier deadline.
- The MVP targets university students seeking internships or graduate roles.
- Spark model nodes perform factual extraction, JD matching, writing, creative
  direction, and final HTML generation.
- An external service may validate and host the preview, but it must not call a
  competing model or replace the Agent's decision flow.
- Demo resumes, logs, screenshots, and public previews must be anonymized.

## Scope

### Included

- PDF or pasted-text resume intake with a pasted-text fallback.
- Optional target-role or JD input.
- Evidence-linked fact extraction and one-question-at-a-time clarification.
- JD decomposition, supported matching, and visible unmatched requirements.
- Two or three content strategies, explicit strategy selection, tailored copy,
  and separate final-copy approval.
- An approved content map and two or three content-derived creative directions.
- Explicit creative-direction approval.
- Spark-generated self-contained HTML/CSS.
- Deterministic security, content-fidelity, responsive, and
  template-independence validation.
- Immutable public preview artifact and one focused revision cycle.

### Excluded

- A complete React + Vite source project.
- Six independent visual-choice rounds.
- Multi-agent execution.
- Automatic custom-domain deployment.
- Advanced media generation.
- Site snapshot rollback and multi-version editing.

The excluded capabilities remain compatible future extensions; the MVP does
not fake or partially expose them.

## Reuse assessment

The current Skill repository is the behavioral source of truth. Reuse the
fact/evidence rules, JD matching contract, content approval separation,
creative-direction contract, and template-independence test.

The older ResumeSite application may be wrapped only for PDF extraction,
Pydantic validation patterns, HTML security checks, artifact storage, and
public artifact delivery. Do not reuse its fixed HTML templates, style catalog,
block renderers, or template compiler.

Use Astron-native start, model, decision, question-and-answer, variable, code,
and tool nodes directly. Use the Apache-2.0 `iflytek/astron-agent` repository as
reference material only; do not add it as a runtime dependency. SkillHub is not
part of the competition runtime. No new third-party dependency is required for
the MVP.

## Architecture

```text
Student
  -> Astron Agent workflow
       -> resume intake and factual inventory
       -> clarification loop
       -> JD match and content strategy
       -> approved tailored copy
       -> content map and creative directions
       -> approved creative direction
       -> Spark-generated HTML/CSS
       -> preview validation and hosting tool
  <- public preview URL and focused revision choice
```

Astron owns cognition, decisions, questions, and generation. The preview
service is a deterministic execution boundary: it accepts approved inputs and
generated HTML, rejects unsafe or unfaithful output, stores a versioned
artifact, and returns a URL.

## Workflow nodes

1. **Start** accepts `resume_file`, `resume_text`, `target_role`, `jd_text`,
   `public_name`, and contact-visibility preferences. At least one resume input
   is required.
2. **Extract facts** emits stable `FACT-*` and `EVID-*` identifiers and marks
   confidence and contradiction state.
3. **Validate facts** rejects prompt injection and identifies unsupported
   dates, titles, metrics, technologies, or ownership claims.
4. **Clarification decision** routes critical uncertainty to the clarification
   loop and otherwise advances.
5. **Clarification question** asks exactly one highest-impact question per
   turn. A qualitative rewrite or omission is valid when a metric cannot be
   verified.
6. **JD match** classifies hard requirements, core capabilities, and bonus
   signals, then records strong, partial, transferable, or unmatched status.
7. **Content strategies** presents two or three materially different narrative
   approaches with one recommendation and explicit trade-offs.
8. **Copy approval** generates role-tailored copy only after strategy choice
   and requires a separate explicit approval of the final wording.
9. **Content map** orders the hero proposition, evidence, skills, projects,
   experience, and authorized public contact details.
10. **Creative directions** presents two or three content-derived directions,
    each with a visual protagonist, composition commitment, type/color
    character, representative interaction, avoid rules, and responsive
    fallback.
11. **Direction approval** freezes the creative floor without converting it
    into a fixed component tree.
12. **Preview delivery** asks Spark to generate self-contained HTML/CSS, calls
    the preview service, returns the public URL, and offers acceptance or one
    focused revision.

Strategy approval never implies copy approval. Copy approval never implies
creative-direction approval. Silence, page access, or a browser click never
counts as approval.

## State contracts

The workflow stores these separate values:

- `source_facts`: extracted claims with evidence and confidence.
- `confirmed_facts`: facts explicitly confirmed or unambiguously supported.
- `clarification_queue`: unresolved critical facts in priority order.
- `jd_match_matrix`: JD phrases, priority, fact/evidence links, and status.
- `approved_copy`: only user-approved visible wording.
- `content_map`: approved-copy placement and attention priority.
- `creative_direction`: fixed, open, and avoided design choices.
- `preview_artifact`: identifier, URL, input revisions, checks, and status.

Generated wording cannot overwrite `source_facts`. Every visible claim must
reference evidence or explicit user confirmation. A revision increments the
content or direction revision rather than mutating an approved record in place.

## Preview service

The MVP exposes:

```http
POST /api/v1/competition/previews
GET  /api/v1/competition/previews/{preview_id}
GET  /p/{public_token}
```

The create operation consumes `approved_copy`, `content_map`,
`creative_direction`, and `generated_html`. It returns a `preview_id`, public
URL, status, and named validation results.

The service performs no generative inference. It:

- rejects scripts, forms, frames, external trackers, unapproved assets, and
  unsafe URLs;
- applies a restrictive content security policy;
- checks visible text against approved copy and fixed labels;
- checks that private contact fields are absent unless explicitly authorized;
- checks basic desktop/mobile readability and overflow rules;
- checks the creative protagonist and composition commitment are observable;
- stores the accepted HTML and validation report as an immutable artifact.

## Template-independence requirements

- The page must still express the candidate's profession and evidence after
  the name is removed.
- Projects must not collapse into identical repeated cards.
- The default gradient-hero, three-skill-card, timeline, and contact-CTA stack
  is prohibited.
- Hierarchy must use composition, rhythm, or contrast in addition to font size.
- The approved visual protagonist must appear in the first or core region.
- At least one project must receive evidence-specific treatment.
- The composition must remain recognizable without final imagery or complex
  motion.

These checks protect a creative floor without introducing a finite template
catalog. Layout and surface treatment remain open within the approved
direction.

## Failure handling

- If document extraction fails, retain the session and request pasted text.
- If critical facts conflict, block tailored copy until the user resolves or
  removes the claim.
- If a JD requirement lacks evidence, expose it as unmatched; never invent it.
- If model output is malformed, retry the failed generation once with the
  validation errors.
- If preview validation fails twice, retain the approved content and direction,
  report the failed checks, and do not publish the artifact.
- If the public artifact cannot be stored, return no fabricated URL and keep
  the workflow resumable.

## Verification

Contract tests cover:

- evidence IDs and fact/copy separation;
- one-question clarification ordering;
- JD unmatched requirements and prohibited keyword invention;
- independent strategy, copy, and creative-direction approvals;
- preview payload validation and immutable artifact metadata;
- prompt injection and malicious HTML rejection;
- contact-detail authorization;
- mobile overflow and readable layout constraints;
- template-independence failure examples;
- one-retry behavior with no false success.

End-to-end fixtures cover an anonymized student resume without metrics, a
technical resume with a JD, conflicting dates, and a resume containing hostile
instructions. The release checklist also includes a manual Astron workflow
debug run, marketplace publication, public-link access, and a fully anonymized
demonstration.

## Delivery boundary

The repository deliverable contains the platform build guide, node prompts,
JSON contracts, preview-service endpoints, validation tests, deployment notes,
and competition demo fixture. Publishing the final Agent in the user's Astron
account remains an authenticated console action; completion requires verifying
the published marketplace link.
