# Graph Report - CRK-Helper-V2  (2026-10-26)

## Corpus Check
- 140 files · ~62,166 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 889 nodes · 2101 edges · 47 communities (38 shown, 9 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 197 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `55b80b7d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- pathlib
- preview-session.test.cjs
- BoundedOCRRuntime
- inspect_preview_identity
- recover_map_aspect
- CRK Helper V2：失敗導向重構設計與分階段驗收
- accept-replay.cjs
- replay-development.cjs
- evidence.test.cjs
- CRK Helper V2 P4-C 正式集合與隨機壓力測試
- ref_node_assert
- ProgressRuntime
- RandomReplayPlanTests
- CRK Helper V2 P0–P3 Implementation Plan
- P4-C 開發進度：尚未正式驗收
- ReferenceLineTests
- PreviewSession
- transaction-map-anchor.test.cjs
- replay-runner.cjs
- higher-floor-replay.test.cjs
- observe-image.cjs
- geometry.test.cjs
- map_aspect.py
- CRK Helper V2：P0–P3核心與審閱修正紀錄
- CorpusFreezerTests
- P4-A 原始影片最小閉環結果
- extract_case
- P4-B 固定縮放閉環結果
- 2026-10-24-crk-helper-v2-p4a-plan.md
- 2026-10-24-crk-helper-v2-p4b-plan.md
- progress.md
- BoundedOCRRuntime
- inspect_map_actions
- ProgressRuntime
- RandomClientTransformTests
- EnglishSceneRuntime
- PrefixFreezerTests
- node-selector.cjs
- preview-session.cjs
- native-preview-sizes.test.cjs
- map-aspect-adapter.test.cjs
- observer-adapter.test.cjs
- PreviewTimerTests
- observer-adapter.cjs
- analyze_cases.py
- ref_node_fs

## God Nodes (most connected - your core abstractions)
1. `BoundedOCRRuntime` - 38 edges
2. `recover_map_aspect()` - 29 edges
3. `P4-C 開發進度：尚未正式驗收` - 28 edges
4. `inspect_preview_identity()` - 26 edges
5. `BoundedOCRRuntime` - 24 edges
6. `adaptPreview()` - 22 edges
7. `MapAspectTests` - 22 edges
8. `G0多來源影格與快取隔離 brief` - 22 edges
9. `adaptMap()` - 21 edges
10. `inspect_map_actions()` - 21 edges

## Surprising Connections (you probably didn't know these)
- `observe()` --calls--> `adaptMap()`  [EXTRACTED]
  tests/map-aspect-adapter.test.cjs → lib/observer-adapter.cjs
- `fixture()` --calls--> `loadReplayFrames()`  [EXTRACTED]
  tests/native-preview-sizes.test.cjs → lib/replay-case.cjs
- `AspectPreviewTests` --uses--> `BoundedOCRRuntime`  [INFERRED]
  tests/test_aspect_preview.py → ml/bounded_ocr.py
- `BoundedOCRRuntime` --uses--> `BoundedOCRRuntime`  [INFERRED]
  tests/test_bounded_ocr.py → ml/bounded_ocr.py
- `BoundedOCRTests` --uses--> `BoundedOCRRuntime`  [INFERRED]
  tests/test_bounded_ocr.py → ml/bounded_ocr.py

## Import Cycles
- None detected.

## Communities (47 total, 9 thin omitted)

### Community 0 - "pathlib"
Cohesion: 0.09
Nodes (5): recover_preview_anchor(), ExactCandidateSearchTests, node_candidates(), FixedScaleTests, scale_png()

### Community 1 - "preview-session.test.cjs"
Cohesion: 0.13
Nodes (20): frame(), intent, map(), preview(), assert, {map,preview,intent}, {runReplay}, {test} (+12 more)

### Community 2 - "BoundedOCRRuntime"
Cohesion: 0.19
Nodes (3): BoundedOCRRuntime, _MeasuredPreprocess, normalize_evidence()

### Community 3 - "inspect_preview_identity"
Cohesion: 0.18
Nodes (4): EnglishPreviewTests, NativePreviewSizeTests, inspect_preview_identity(), PreviewIdentityTests

### Community 4 - "recover_map_aspect"
Cohesion: 0.10
Nodes (6): AspectEndpointProjectionTests, GateSupportedAspectTests, estimate_pixel_aspect(), MapAspectTests, recover_map_aspect(), PreviewPanelScopeTests

### Community 5 - "CRK Helper V2：失敗導向重構設計與分階段驗收"
Cohesion: 0.08
Nodes (25): 10. 本次有條件批准與執行順序, 11. P0–P3 核心實作與審閱修訂（2026-10-24）, 1. 唯一目標與完成邊界, 2.1 已確認的問題, 2.2 尚未證實、需要測試的風險, 2.3 可重用與暫緩處理, 2. 根本原因與證據等級, 3. 方案比較與建議 (+17 more)

### Community 6 - "accept-replay.cjs"
Cohesion: 0.15
Nodes (16): milestoneResult(), evaluateDevelopmentReplay(), evaluateReplay(), gradeReplay(), {adaptMap,adaptPreview}, {captureCodeVersion}, {compareSnapshot}, crypto (+8 more)

### Community 7 - "replay-development.cjs"
Cohesion: 0.15
Nodes (16): writeCaseArtifacts(), buildReplayGate(), invalid(), captureCodeVersion(), walk(), {adaptMap,adaptPreview}, {buildReplayGate,loadReplayFrames}, {captureCodeVersion} (+8 more)

### Community 8 - "evidence.test.cjs"
Cohesion: 0.10
Nodes (21): compareSnapshot(), crypto, digest(), fs, locate(), path, snapshotFiles(), files (+13 more)

### Community 9 - "CRK Helper V2 P4-C 正式集合與隨機壓力測試"
Cohesion: 0.05
Nodes (37): Actual case14 original text and near-native recovery brief, Actual glowing-edge candidate and precision repair brief, Actual native map-title OCR truncation repair brief, Actual second-floor case16 pixel evidence brief, Actual watermarked Chinese title context repair brief, CRK Helper V2 P4-C 正式集合與隨機壓力測試, Current evidence, English source development repair brief (2026-10-25) (+29 more)

### Community 10 - "ref_node_assert"
Cohesion: 0.14
Nodes (11): assert, crypto, fs, path, {spawnSync}, {test}, assert, fs (+3 more)

### Community 11 - "ProgressRuntime"
Cohesion: 0.23
Nodes (4): parse_progress(), ProgressRuntime, EnglishProgressTests, ProgressEvidenceTests

### Community 12 - "RandomReplayPlanTests"
Cohesion: 0.38
Nodes (3): plan_sequences(), RandomReplayPlanTests, render_sequences()

### Community 13 - "CRK Helper V2 P0–P3 Implementation Plan"
Cohesion: 0.15
Nodes (12): CRK Helper V2 P0–P3 Implementation Plan, Global Constraints, Review Focus, T1 / P0：基準凍結與里程碑結果契約, T2 / P1：統一可逆座標, T3 / P2：兩幀地圖到唯一節點證明, T4 / P3：單次交易與獨立預覽確認, T5 / P3：只讀辨識adapter、trace與核心整合 (+4 more)

### Community 14 - "P4-C 開發進度：尚未正式驗收"
Cohesion: 0.07
Nodes (28): 2026-10-25：區域10、人工標註及多來源隔離, 2026-10-25 延續驗證, LX46 英文與浮水印開發驗證（2026-10-25）, P4-C 開發進度：尚未正式驗收, 三種尺寸流程試跑通過, 來源修訂與浮水印場景（最新）, 原生960×720的三段新閉環, 尚待完成 (+20 more)

### Community 17 - "transaction-map-anchor.test.cjs"
Cohesion: 0.18
Nodes (12): {adaptMap,adaptPreview,readDirectMapAnchor}, assert, fixture(), fs, {loadReplayFrames}, observation(), path, replay() (+4 more)

### Community 18 - "replay-runner.cjs"
Cohesion: 0.40
Nodes (3): {performance}, {PreviewSession}, {selectNode}

### Community 19 - "higher-floor-replay.test.cjs"
Cohesion: 0.20
Nodes (9): runReplay(), {adaptMap,adaptPreview}, assert, crypto, fs, path, replay(), {runReplay} (+1 more)

### Community 20 - "observe-image.cjs"
Cohesion: 0.09
Nodes (20): crypto, fs, path, {spawnSync}, crypto, {execFileSync}, fs, path (+12 more)

### Community 21 - "geometry.test.cjs"
Cohesion: 0.29
Nodes (11): analysisToClient(), assertCurrentGeometry(), clientToAnalysis(), clientToScreen(), createGeometry(), finiteArray(), point(), assert (+3 more)

### Community 22 - "map_aspect.py"
Cohesion: 0.06
Nodes (54): completed_geometry(), wrapped(), recover_completed_extents(), completed_node_candidates(), inspect_in_progress(), _groups(), _match_group(), node_candidates() (+46 more)

### Community 23 - "CRK Helper V2：P0–P3核心與審閱修正紀錄"
Cohesion: 0.33
Nodes (5): CRK Helper V2：P0–P3核心與審閱修正紀錄, 尚未驗收與下一個工作, 已交付, 本次實際驗證, 獨立審閱與測試先行修正

### Community 25 - "P4-A 原始影片最小閉環結果"
Cohesion: 0.40
Nodes (4): P4-A 原始影片最小閉環結果, 可重現命令, 真實失敗與修正, 邊界與後續

### Community 27 - "P4-B 固定縮放閉環結果"
Cohesion: 0.50
Nodes (3): P4-B 固定縮放閉環結果, 失敗導向修正, 重現

### Community 30 - "progress.md"
Cohesion: 0.29
Nodes (6): 2026-10-26 continuation: case17 gate proposal and row pitch, Case18 line raster reference repair (current work), Main14 case20 detected-completed extent failure and isolated repair, Main16 case21: transaction-local semantic root after post-click resize, Native completed proposals and independent supplemental gate, SDD ledger — plan: C:/Users/User/Documents/Codex/CRK-Helper-V2/docs/superpowers/plans/2026-10-24-crk-helper-v2-p0-p3-plan.md

### Community 32 - "BoundedOCRRuntime"
Cohesion: 0.16
Nodes (4): AspectPreviewTests, BoundedOCRRuntime, BoundedOCRTests, normalize_evidence()

### Community 33 - "inspect_map_actions"
Cohesion: 0.11
Nodes (8): CompletedNodeCandidateTests, CurrentPositionEvidenceTests, EnglishCurrentTests, inspect_map_actions(), PixelMapActionTests, recover_map_geometry(), SparseMapGeometryTests, WatermarkedCheckTests

### Community 34 - "ProgressRuntime"
Cohesion: 0.19
Nodes (4): EnglishSceneRuntime, MapTitleRereadTests, ProgressRuntime, WatermarkedMapContextTests

### Community 35 - "RandomClientTransformTests"
Cohesion: 0.33
Nodes (3): inverse_point(), RandomClientTransformTests, sample_layout()

### Community 36 - "EnglishSceneRuntime"
Cohesion: 0.23
Nodes (4): EnglishSceneRuntime, semantic_state(), EnglishSceneTests, RemainingTimeLocatorTests

### Community 38 - "node-selector.cjs"
Cohesion: 0.14
Nodes (19): fail(), freeze(), iou(), issued, numbers(), selectNode(), validateFrame(), validateProof() (+11 more)

### Community 39 - "preview-session.cjs"
Cohesion: 0.14
Nodes (13): readDirectMapAnchor(), active, { createGeometry, clientToScreen }, crypto, { readDirectMapAnchor }, { validateProof, validateFrame }, { verifyPreview }, verifyPreview() (+5 more)

### Community 40 - "native-preview-sizes.test.cjs"
Cohesion: 0.25
Nodes (7): {adaptPreview}, assert, {execFileSync}, fixture(), fs, {loadReplayFrames}, {test}

### Community 41 - "map-aspect-adapter.test.cjs"
Cohesion: 0.06
Nodes (33): crypto, fs, loadReplayFrames(), sha(), {adaptMap}, assert, {execFileSync}, fixture() (+25 more)

### Community 42 - "observer-adapter.test.cjs"
Cohesion: 0.20
Nodes (6): {adaptMap,adaptPreview}, assert, crypto, fs, path, {test}

### Community 45 - "observer-adapter.cjs"
Cohesion: 0.15
Nodes (24): boxValid(), adaptMap(), adaptPreview(), aspectGeometry(), bind(), completedGeometry(), crypto, directMapAnchors (+16 more)

### Community 46 - "analyze_cases.py"
Cohesion: 0.07
Nodes (9): case_source_sha(), main(), source_frame_id(), PreviewAnchorTracker, capture_runtime_evidence(), OfflineAnalyzerTests, PreviewAnchorTracker, PreviewRegistrationTests (+1 more)

### Community 52 - "ref_node_fs"
Cohesion: 0.12
Nodes (10): assert, fs, os, path, {test}, {writeCaseArtifacts}, assert, fs (+2 more)

## Knowledge Gaps
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BoundedOCRRuntime` connect `BoundedOCRRuntime` to `pathlib`, `BoundedOCRRuntime`, `inspect_preview_identity`, `EnglishSceneRuntime`, `ProgressRuntime`, `recover_map_aspect`, `ProgressRuntime`, `PreviewTimerTests`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `BoundedOCRRuntime` (e.g. with `.test_actual_anisotropic_preview_recovers_selected_node_using_vertical_spacing()` and `.test_actual_near_native_preview_corrects_pixels_even_with_existing_gate_anchor()`) actually correct?**
  _`BoundedOCRRuntime` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Should `pathlib` be split into smaller, more focused modules?**
  _Cohesion score 0.09473684210526316 - nodes in this community are weakly interconnected._
- **Why does `BoundedOCRRuntime` connect `BoundedOCRRuntime` to `pathlib`, `BoundedOCRRuntime`, `ProgressRuntime`, `inspect_preview_identity`, `EnglishSceneRuntime`, `recover_map_aspect`, `ProgressRuntime`, `PreviewTimerTests`, `analyze_cases.py`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Should `preview-session.test.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.12681159420289856 - nodes in this community are weakly interconnected._
- **Why does `recover_map_aspect()` connect `recover_map_aspect` to `BoundedOCRRuntime`, `inspect_map_actions`, `pathlib`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Should `recover_map_aspect` be split into smaller, more focused modules?**
  _Cohesion score 0.10384615384615385 - nodes in this community are weakly interconnected._