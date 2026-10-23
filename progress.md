# SDD ledger — plan: C:/Users/User/Documents/Codex/CRK-Helper-V2/docs/superpowers/plans/2026-10-24-crk-helper-v2-p0-p3-plan.md

Scope: user conditionally approved P0–P3; P4 phased A/B/C; P5 not approved.
Pre-flight: T1 produces evidence and baseline used by T5; T2 produces client geometry consumed by T3/T4; T3 produces branded immutable proof used by T4; T4 consumes independent preview evidence from T5. Shared signatures checked against plan.
Ruling: V1 git work-tree operations fail with permissions; V2 lives in a new isolated repository on codex/v2-minimal-loop under writable workspace. V1 remains read-only. Cost: later integration is separate and not claimed done.
Ruling: Source candidate ranges are unreviewed and cannot count toward five original-resolution closures. Cost: P4-A needs manual verification before execution.
T1 RED: node --test tests/evidence.test.cjs failed because lib/evidence.cjs did not exist; captured artifacts/T1-red.log.
Task 1: complete — evidence tests RED→GREEN, suite 3/3; baseline and five unreviewed candidates frozen. G4 not run.
Task 2: complete — geometry RED→GREEN, whole suite 6/6. Added assertCurrentGeometry for explicit stale-frame rejection; no DPI multiplication. Local commits attributed to Codex, no user git identity changed.
