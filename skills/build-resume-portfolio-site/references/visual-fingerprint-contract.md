# Visual fingerprint contract

Store accepted-generation history at
`.resume-site-work/history/visual-fingerprints.json`. History is workspace-local,
contains at most 20 entries, and is used to discourage recent structural and
visual repetition. Topology and protagonist fields carry more novelty weight
than palette so recoloring is not treated as a new direction.

Write only after the final visual audit passes. Writes are atomic and idempotent
by `generation_id`. Missing history is empty history. A malformed file is moved
aside with a `.corrupt-<uuid>` suffix and reported; it is never silently erased.
