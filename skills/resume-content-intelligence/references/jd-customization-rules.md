# JD Customization Rules

Use this reference only when the user supplies a job description or asks for a role-specific version.

## JD decomposition

Classify each JD statement as:

- `hard_requirement`: degree, location, work authorization, required years, or explicitly required technology;
- `core_capability`: recurring responsibility, technical skill, or behavior the role will evaluate;
- `bonus_signal`: preferred domain, tool, or context.

Record the exact JD phrase, a normalized concept, and its priority. Do not claim that a keyword is important solely because of a general ATS statistic.

## Matching matrix

For every high-priority JD item, create:

```text
JD phrase | priority | supported fact IDs | evidence IDs | match status | resume location
```

Use `strong_match`, `partial_match`, `transferable`, or `unmatched`. `unmatched` means omit it or ask whether the user has unlisted evidence; it never means add the skill.

## Versioning strategy

- Keep one factual master content package.
- Produce a role-specific approved copy layer for each JD.
- Reorder projects and bullets by supported relevance.
- Use the JD's exact term only when it accurately describes an existing fact; include a common abbreviation when useful.
- Preserve the factual master package unchanged when creating a tailored version.

## Output

Return a compact match summary, the proposed changes, unmatched requirements, and the revised copy. Require user approval before writing a role-specific approved package.
