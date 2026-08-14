# Design Contract

## Purpose

`reports/design-contract.json` compiles approved identity and creative intent
into observable implementation commitments. Content establishes identity fit;
it does not prove aesthetic quality. This report is internal build input, not a
new user choice, approval gate, template, component tree, or source payload.

## Transaction

Use this exact order after requirements, TODO-plan, and execution-strategy
approval:

```text
site-design-spec.json + design-intelligence.json + creative-direction.json
-> write a temporary design-contract.json sibling
-> validate_design_contract.py
-> atomically replace reports/design-contract.json
-> first React source edit
```

Run:

```powershell
python "$SKILL_ROOT\scripts\validate_design_contract.py" `
  ".resume-site-work\reports\design-contract.json"
```

Continue only on exit `0`. An invalid contract freezes React edits and preserves
the last valid preview and snapshot.

## Required sections

- `identity_strategy` defines audience, narrative priority, density, and
  content-to-form relationships from approved facts.
- `signature` commits to one visual protagonist, composition, recognizable
  structural device, and template-independence claim.
- `layout`, `typography`, `color`, and `surface` translate approved decisions
  into relationships, ranges, responsive transformations, fallbacks, and
  explicit prohibited arrangements.
- `motion` defines exactly one primary system plus compatible secondary effects,
  purpose, controller ownership, reduced motion, coarse pointer, and fallbacks.
- `anti_template_rules` contains contextual, observable failure detectors.
  Compile them from `creative-direction.anti_template_resolutions`; every
  provisional rule must be adopted, refined, or explicitly rejected by an
  approved choice before contract validation.
- `acceptance_checks` keeps identity fit and aesthetic quality separate and also
  covers accessibility, responsive integrity, and runtime safety.
- `traceability` links every design section to approved decision IDs and
  creative-direction paths, including the evidence for each anti-template
  resolution.

Every rule has a stable `rule_id`, criterion, required evidence IDs, and
severity. Use exact tokens when they implement an approved or accessibility
requirement; otherwise prefer observable relationships and ranges over arbitrary
pixel prescriptions.

## Boundaries

The contract may refine an approved choice but cannot contradict or reopen it.
A strong identity-fit result cannot compensate for failed aesthetic quality,
and decorative polish cannot compensate for generic or inaccurate identity fit.
Do not include JSX, HTML, component trees, source code, personal secrets, or
unapproved factual claims.
