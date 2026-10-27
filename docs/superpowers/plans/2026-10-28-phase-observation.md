# Phase observation implementation plan

Approved by the user in this thread after case31 routing report. Goal: retain M1 as same-frame routing evidence while enabling bounded coverage explicitly, without changing estimator/raster/thresholds/proof or native operations.

Spec: docs/validation/2026-10-28-coverage-regression-case31.md. Execute inline with Superpowers executing-plans, TDD and one fresh final review of this implementation; no per-task agent loop. Preserve baseline5e2 failures and frozen60/30 corpus.

Pre-flight: matcher Scan -> FrameIntermediates consumes immutable result and shares only exact source/model/asset/backend-bound raw work; context -> map pipeline temporarily selects coverage and restores M1; pipeline -> analyzer retains existing v2OriginalMapReview provenance for baseline raw map; runners -> analyzer must explicitly opt in coverage. Shared keys must distinguish backend modes but share the same scan implementation only when input and processing identity match.

Ruling: a same-image feasibility probe shows existing map_aspect already honors v2OriginalMapReview as raw routing evidence. Retaining fresh M1 prior recovers case31 IoU .9388056/.9358738 without editing map_aspect at all. Prefer this narrower integration over changing estimator or branching rules. Risk: phase identity and intermediate caching must be explicit, and complete downstream regression must confirm no changed provenance semantics.

## Task1: RED -> GREEN scoped backend and incremental raw scan
- Add new tests before source changes: temporary backend scope restores on success/error, distinct backend result cache, disabled-cache control, no cross-frame/image/config reuse; real M1->coverage->M1 has exact outputs, one Canny and original kernel multiplicities only once across phases.
- Extract existing matcher preprocessing/base-NMS/M1/coverage stages into one raw CandidateScan with lazy results. Preserve _groups/_match_group, .48/NMS and default function/API/output. Retain independent copies for consumers.
- FrameIntermediates explicit backend context method, actual backend identity on result keys, exact scan identity for sharing lazy raw work across its two known fast backends; scope must restore in finally. Disabled control does not share work. No authority cache.
- Focused context + existing nine context, five M1, four coverage, original fast equivalence.

## Task2: RED -> GREEN source routing integration
- New real-source unit tests case31 two frames: with M1 baseline and explicit coverage, retain raw prior, proper unanchored recovery, GT IoU>=.90; same fresh source hash, no intent supplied to observer. Case42 two frames retain added target and original M1 prefix. Enabled/disabled same-frame reuse must yield identical semantic packet.
- New ml/map_pipeline.py contains existing sparse/aspect sequence and explicit augmentation phase. Copy same-frame M1 map as v2OriginalMapReview, inspect coverage source map in scoped backend, reuse original header, then run unchanged sparse/aspect recovery while prior remains baseline. Same already existing provenance field, no future/old-frame input. Return existing packet with no fabricated authority.
- Analyzer installs M1 default under --fast-map; new explicit --map-coverage requires --fast-map. Coverage adds new backend mode identity; existing fast-map legacy behavior stays intact. No map_aspect, calibrator, raster, Selector, Transaction or Preview edits.
- Convergence and benchmark runners explicitly enable coverage. S3 focused defect tests target explicit coverage; existing old M1/frame-context semantic assertions remain unchanged. Cache CLI tests cover coverage/M1/original transitions and matching-mode reuse.
- Full CLI source tests and source/bundle binding review. Graph AST update, freeze source commit; one fresh whole-change review, one RED/GREEN important fix pass if needed.

## Task3: current-version qualification
- Fresh full case31(29), case41(266), case42(265), including causal transaction and independent geometry/identity grade. Do not substitute component success for closure.
- Full prefix42/current native20/fixed15/negative30+controls/full Node/Python/native1551+seven+new candidate pixel review/rounding pressure/paired matcher+same193 isolated producer baseline. Save all failures, source/runner/code/model/runtime hashes and actual fresh/cache stats. No old passes as current.
- G4 remains OPEN unless all original criteria including p95<=1500 and real age/deadline evidence are met; no P5.
- After stable necessary regression, ordered43..60 then frozen native held10 and transformed held30 with unchanged evaluator disclosed, no holdout tuning/replacement. Final actual60 report, first-trace history, regressions, remaining defects.

## Stop boundaries
No threshold relaxation, frame-ID hacks, unknown skipping, corpus changes, estimator/raster/model rewrite or native operations. New integration defects: diagnose source and repair only within this approved scope. Broader redesign requires user approval. Do not promote partial batch/suffix diagnostics into a passing full regression.
