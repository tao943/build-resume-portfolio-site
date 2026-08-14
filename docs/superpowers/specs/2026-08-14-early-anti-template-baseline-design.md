# Early Anti-Template Baseline Design

## Goal

Move anti-template reasoning ahead of the six visual decisions without turning
unapproved recommendations into a final design contract.

## Chosen approach

Use a two-stage contract model:

1. After the database baseline is validated and before the structure question,
   generate a provisional anti-template baseline from approved content,
   reference evidence, and catalog evidence.
2. After all six decisions and final requirements approval, compile the existing
   `creative-direction.json` and `design-contract.json` as the authoritative
   implementation contract.

The provisional artifact constrains discovery but never approves a category,
replaces the user's choice, or authorizes source generation.

## Provisional artifact

Add `reports/design-discovery/anti-template-baseline.json`. It must contain:

- content and catalog evidence IDs;
- the candidate visual protagonist;
- the content-to-form thesis;
- the recommended composition hypothesis;
- one or more candidate signature structural devices;
- a template-independence claim;
- project-specific anti-template rules;
- category obligations describing what each of the six later searches must
  preserve, test, or avoid;
- status showing that the artifact is provisional and unapproved.

Every claim must trace to content, reference, or catalog evidence. Missing
evidence blocks presentation instead of allowing a generic direction.

## Discovery flow

The flow becomes:

`content map -> database baseline -> provisional anti-template baseline -> six
sequential category searches -> final requirements approval -> final creative
direction -> final design contract -> React generation`.

Every category search receives the provisional baseline plus all previously
approved decisions. Its candidates must report whether they strengthen,
preserve, or conflict with the visual protagonist, content-to-form thesis,
signature device, and anti-template rules. Conflicting candidates may be shown
only when clearly labeled as a trade-off; they cannot be recommended silently.

The working decision file accumulates the effect of each approved choice. This
is decision evidence, not a second source of truth. Reversing an earlier core
choice invalidates downstream decisions as it does today.

## Final compilation

Aggregation must consume the validated provisional baseline and six validated
category reports. `creative-direction.json` turns the provisional hypotheses
into approved commitments or records how an approved choice changed them.
`design-contract.json` remains the only authoritative observable contract for
implementation and screenshot audit.

No React source may be edited from the provisional artifact alone.

## Validation and compatibility

- Extend the design-discovery schema and validator with an
  `anti_template_baseline` report type.
- Require every category report to trace its anti-template evaluation to the
  provisional baseline.
- Require aggregation to fail when the baseline is missing, invalid, or not
  represented in the final creative direction.
- Preserve schema-version compatibility for existing work: an in-progress
  discovery created before this change must regenerate discovery from the
  database baseline; confirmed sites and bounded fast changes remain valid.
- Add positive and negative tests for ordering, evidence traceability,
  category inheritance, aggregation, and the prohibition on treating the
  provisional artifact as approval.

## Non-goals

- No image-embedding or external template-library similarity service.
- No blanket ban on cards, gradients, rounded corners, or common layout tools.
- No additional user approval gate before the existing six questions.
- No change to the final screenshot audit and bounded repair loop beyond using
  the stronger final contract it receives.
