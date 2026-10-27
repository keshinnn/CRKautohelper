# Bounded Coverage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement task-by-task. Keep one final fresh review for the source repair.

**Goal:** repair case42 local candidate omissions and finish frozen remaining offline cases without weakening safety.
**Architecture:** backward-compatible M1 default plus explicit bounded coverage backend; incremental banks, shared Canny, preserved base candidates.
**Tech Stack:** Python/OpenCV/Pillow, unchanged Node causal replay.
**Spec:** docs/superpowers/specs/2026-10-28-bounded-coverage-design.md

## Global Constraints
.48 score, original NMS, IoU, threepeer, source/geometry/identity proof, two independent previews, singleclick,15s deadline,2500ms age unchanged. Original corpus60/held30 unchanged. No P5/model/raster/calibrator/Selector/Transaction/Preview edits. Keep original M1 tests/API; new mode has explicit separate tests.

## Review Focus
- Already >=4 candidates but requested node missing: true source restores with no runtime GT hint.
- New score higher near base: never replace original base box/order.
- Source width/height rounding and template metadata: use same nominal factor, symmetric onepixel bound only.
- Same-frame reuse asset identity: no authority cache or cross-source result reuse.
- Additional UI/partial candidates: actual changed-pixel audit and existing negatives must reject unsupported operations.

## Task1: RED/GREEN bounded coverage
Files: ml/fast_map_candidates.py (new bank/helper flag/wrapper), ml/analyze_cases.py:41 (install new wrapper); new tests/test_bounded_coverage.py. Existing tests untouched.
- [ ] RED tests on two frozen case42 sources/hash/model, base11 preservation, target score/IoU/class; Canny once and unique bounded scans; blank negative.
- [ ] Minimal bank helper, keyword coverage defaultFalse, wrapper, hook. No dependency installs or unrelated refactor.
- [ ] GREEN focused + old M1+fast equivalence. Graph AST update and source review; commit source/version.

## Task2: current fresh qualification
- [ ] New case42 run full265 fresh/no cache. Preserve old failed run.
- [ ] Current prefix41 full1849/native20 full1551/fixed15 full381, negatives30+grader controls, full Node/Python.
- [ ] Source/hash/bundle audit, native1551+seven+all changed candidate pixel review, boundary stress, isolated same193 performance and paired matcher baseline; separate fresh/reuse timing.
- [ ] Stop at any new wrong candidate or severe regression; no frame hacks/future evidence/UNKNOWN skipping.

## Task3: finish remaining frozen offline corpus
- [ ] 43..60 sequential, fullfresh, save each firstfailure/trace. Necessary small repairs only with TDD/regression.
- [ ] All60 must pass before frozen held30; use proper formal gate, do not label development grader as formal G4.
- [ ] Final60 table/first trace history/current regression/source hashes/OPEN defects and unmet G4; no native.

## One review fix pass
- [x] RealCLI RED3tests/5failures for stale/missing backend cache identity, then backend admission+sharedmetadata identity fix. Both directions and valid same-mode cache reuse covered.
- [x] Additional prefix RED on oldM1lowcount output; preserve full M1 prefix by ordered stages and omit already-scanned nominal kernels fromcoverage.
- [x] Strengthen unique-kernel test for both712(highcount) and721(lowcount); retain original204 multiplicities, no extra duplicates. Initial global-uniqueness assumption corrected to preserve17 original duplicate size pairs at721.
- [x] S3 fresh independent physical labels now pass(.951/.931IoU); remove2expectedFailure decorators only, assertions unchanged.
- [ ] Finalsourcecommit, newfullcase42fresh02, complete all current regressions; preliminary3562case42pass is prior evidence only, never substituted as final-version pass.
