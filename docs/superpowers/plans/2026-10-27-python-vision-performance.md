# Python vision performance and generalization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Steps use checkbox syntax. Execute inline; one independent final branch review.

**Goal:** measured Python optimization without weakening current evidence or safety; reach causal warmed p95<=1500ms or provide measured remaining blockers and stop before40.
**Architecture:** retain existing observer/transaction/proof boundaries. Measure actual work first; share only validated immutable same-frame data or make exact algorithmic changes. No new model or V1 disk edits.
**Tech Stack:** existing Python/Pillow/OpenCV/Node, venv F:/CRK helper/.venv/Scripts/python.exe.
**Spec:** docs/superpowers/specs/2026-10-27-python-vision-performance.md; user's explicit direction supersedes repeated design/implementation approval menus.

## Global Constraints

IoU>=.90 and all source/OCR/geometry thresholds unchanged; no clamp, TTL<=2500ms, deadline15000ms, two independent previews>=200ms, one click. New profiling measurements are not acceptance timing. No native operations/P5, no changed frozen denominators, no future-frame use or cross-source stale cache. Keep old evidence immutable. Work in dedicated existing V2 branch preserving ignored datasets; baseline a7a05a2 has no uncommitted functional files. No merge/push. Old stop39 is superseded only by this user's conditional gate to40–60.

## Review Focus

- Same-frame cache key must include actual source pixels, size, parameters and detector/template identity; mutation must not taint subsequent consumers.
- Failed/UNKNOWN/empty results must not become selection authority; PREVIEW_PENDING remains wait only.
- OpenCV worker calls must be counted, nested inclusive time must not be summed as wall time.
- A source or geometry change invalidates intermediates; restoration on exception must prevent global monkeypatch leaks.
- Known S3 omissions remain visible and regression-tracked even if complete clips pass.

## Task1: reproducible operation-level profiling
Files: new ml/operation_profile.py, scripts/profile-vision.py, tests/test_operation_profile.py; artifacts/performance-20261027.
Interface: process-local diagnostic instrumentation, stage-bound events {function,calls,elapsed,inputShape,frame}; optional cProfile output. No production behavior changes.
- [x] RED: workers counted, stage attribution, exceptions restore originals, return values unchanged; tests/test_operation_profile.py.
- [x] GREEN diagnostic instrumentation and explicit source/output runner with no native imports/actions.
- [x] Freeze representative diagnostic source (including two S3 defects); run no-cache current baseline profile; save cumulative/self and native operation stats and semantic packet comparison.
Acceptance: real call count/time for dominant modules including workers; instrumented vs uninstrumented semantic equality; actual baseline193data/hash retained. Risks: profiler overhead and nested double counting, explicitly separated from performance gate.

## Task2: measured minimum optimization round
Files: only measured V2 hot modules named in spec; focused regression tests and optional small immutable same-frame context.
Interface: existing packet/geometry/proof unchanged; reuse scoped to one current validated frame and exact operation identity; diagnostics for hit/miss costs separate.
- [x] Choose at most two changes from measured call graph, record per-change expected recoverable measured cost and risks before implementing.
- [x] RED->GREEN for exact outputs, mutation/source/parameter isolation, cache hit/miss, negative refusal; preserve original source binding.
- [x] Focus #8/#19/#23/#25/#39 and affected actual frames. Keep only repeatable improvements; revert changes without meaningful measured benefit.
Acceptance: equivalent semantic evidence and no threshold changes; causal/producer improvement measured with full fresh source processing. No optimization justified only by function name. Risks: hidden injected detector dependencies, deep-copy overhead, score ordering/rounding drift.

## Task3: track S3 local coverage defects
Files: source-bound reviewed regression annotations in data/p4c and tests for46047/46057, defect ledger docs/validation.
- [x] Verify source PNG hash and actual missing icon extents; trace candidate extraction vs classification/lattice/NMS loss using profile outputs and intermediate diagnostics.
- [x] Add expected-presence regression at original IoU requirement; if unresolved, explicit expected failures excluded from success count, plus independent unanchored selection refusal tests.
- [x] Do not change detector for one image or mark solved because parent clip closes.
Acceptance: two defects have cause/evidence/current status; safety refusal retained. Risk: relative IDs shift during scroll, match physical boxes, not accidental IDs.

## Task4: correctness + comparable performance and gate
Files: versioned run artifacts, docs/validation/2026-10-27-python-vision-performance.md, progress.md, updated graph.
- [x] Current full Node/Python tests; current39/native20/fixed15/negative30+controls regressions; retain five artifacts/hash/versions.
- [x] Isolated original193frames single worker, warmup10, no-cache, per-module and causal p50/p95, slowest frame/stage and hit/miss costs; save before/after comparable stats.
- [x] Whole-branch independent review; source/asset/hash checks; AST graph update.
- [x] If p95<=1500 and safety/correctness stable, proceed frozen40–60/holdout and retain denominators. Otherwise provide measured next options and stop; no unbounded speculative patches.
Acceptance: explicit unit/offline/CPU/live separation, no G4/P5 promotion without actual gates. P5 remains unauthorized.

Final round result: functional/semantic gates passed; fresh causalCPU p95 3753.4514 -> 2743.6726ms, still FAIL1500. Per Task4 alternative deliver measured remaining bottlenecks and stop before40/holdout/P5. Two known S3 omissions remain expected failures, not passed. See docs/validation/2026-10-27-python-vision-performance.md.
