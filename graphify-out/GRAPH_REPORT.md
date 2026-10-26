# Graph Report - CRK-Helper-V2  (2026-10-26)

## Corpus Check
- 156 files · ~65,374 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 972 nodes · 2348 edges · 55 communities (40 shown, 15 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 239 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `37cfaadd`
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
- EnglishSceneRuntime
- evidence.test.cjs
- CRK Helper V2 P4-C 正式集合與隨機壓力測試
- ref_node_assert
- hashlib
- RandomReplayPlanTests
- CRK Helper V2 P0–P3 Implementation Plan
- P4-C 開發進度：尚未正式驗收
- ReferenceLineTests
- PreviewSession
- transaction-map-anchor.test.cjs
- inspect_map_actions
- higher-floor-replay.test.cjs
- observer-adapter.test.cjs
- geometry.test.cjs
- numpy
- CRK Helper V2：P0–P3核心與審閱修正紀錄
- CorpusFreezerTests
- P4-A 原始影片最小閉環結果
- extract_case
- P4-B 固定縮放閉環結果
- 2026-10-24-crk-helper-v2-p4a-plan.md
- 2026-10-24-crk-helper-v2-p4b-plan.md
- progress.md
- BoundedOCRRuntime
- preview-session.cjs
- ProgressRuntime
- random_replay_plan.py
- PreviewAnchorTracker
- PrefixFreezerTests
- node-selector.cjs
- sparse-peer-bootstrap.test.cjs
- aspect-endpoints.test.cjs
- ref_node_fs
- MapTitleRereadTests
- ordinary_preview_panel_scope
- OfflineAnalyzerTests
- observer-adapter.cjs
- ProgressRuntime
- recover_map_aspect
- analyze_cases.py
- ref_node_fs
- NativeEllipsePreviewTests
- re
- RandomClientTransformTests
- small-aspect-sparse.test.cjs
- EnglishPreviewTests

## God Nodes (most connected - your core abstractions)
1. `BoundedOCRRuntime` - 45 edges
2. `recover_map_aspect()` - 34 edges
3. `inspect_preview_identity()` - 29 edges
4. `BoundedOCRRuntime` - 28 edges
5. `P4-C 開發進度：尚未正式驗收` - 28 edges
6. `G0多來源影格與快取隔離 brief` - 27 edges
7. `ProgressRuntime` - 25 edges
8. `adaptMap()` - 24 edges
9. `adaptPreview()` - 24 edges
10. `loadReplayFrames()` - 24 edges

## Surprising Connections (you probably didn't know these)
- `fixture()` --calls--> `loadReplayFrames()`  [EXTRACTED]
  tests/aspect-endpoints.test.cjs → lib/replay-case.cjs
- `fixture()` --calls--> `loadReplayFrames()`  [EXTRACTED]
  tests/small-aspect-sparse.test.cjs → lib/replay-case.cjs
- `fixture()` --calls--> `loadReplayFrames()`  [EXTRACTED]
  tests/sparse-peer-bootstrap.test.cjs → lib/replay-case.cjs
- `AspectPreviewTests` --uses--> `BoundedOCRRuntime`  [INFERRED]
  tests/test_aspect_preview.py → ml/bounded_ocr.py
- `BoundedOCRRuntime` --uses--> `BoundedOCRRuntime`  [INFERRED]
  tests/test_bounded_ocr.py → ml/bounded_ocr.py

## Import Cycles
- None detected.

## Communities (55 total, 15 thin omitted)

### Community 1 - "preview-session.test.cjs"
Cohesion: 0.11
Nodes (24): clone(), frame(), intent, map(), preview(), assert, {map,intent,clone}, {selectNode,validateProof} (+16 more)

### Community 2 - "BoundedOCRRuntime"
Cohesion: 0.15
Nodes (5): BoundedOCRRuntime, _MeasuredPreprocess, normalize_evidence(), _remaining_timer_locators(), OrdinaryWhitespaceTests

### Community 3 - "inspect_preview_identity"
Cohesion: 0.16
Nodes (4): AspectPreviewTests, NativePreviewSizeTests, inspect_preview_identity(), PreviewIdentityTests

### Community 4 - "recover_map_aspect"
Cohesion: 0.07
Nodes (10): AspectEndpointProjectionTests, ExactCandidateSearchTests, node_candidates(), GateSupportedAspectTests, estimate_pixel_aspect(), MapAspectTests, recover_map_aspect(), PreviewPanelScopeTests (+2 more)

### Community 5 - "CRK Helper V2：失敗導向重構設計與分階段驗收"
Cohesion: 0.08
Nodes (25): 10. 本次有條件批准與執行順序, 11. P0–P3 核心實作與審閱修訂（2026-10-24）, 1. 唯一目標與完成邊界, 2.1 已確認的問題, 2.2 尚未證實、需要測試的風險, 2.3 可重用與暫緩處理, 2. 根本原因與證據等級, 3. 方案比較與建議 (+17 more)

### Community 6 - "accept-replay.cjs"
Cohesion: 0.08
Nodes (30): buildReplayGate(), invalid(), evaluateDevelopmentReplay(), evaluateReplay(), gradeReplay(), captureCodeVersion(), walk(), {adaptMap,adaptPreview} (+22 more)

### Community 8 - "evidence.test.cjs"
Cohesion: 0.10
Nodes (22): compareSnapshot(), crypto, digest(), fs, locate(), milestoneResult(), path, snapshotFiles() (+14 more)

### Community 9 - "CRK Helper V2 P4-C 正式集合與隨機壓力測試"
Cohesion: 0.05
Nodes (42): Actual case14 original text and near-native recovery brief, Actual glowing-edge candidate and precision repair brief, Actual native map-title OCR truncation repair brief, Actual second-floor case16 pixel evidence brief, Actual watermarked Chinese title context repair brief, CRK Helper V2 P4-C 正式集合與隨機壓力測試, Current evidence, English source development repair brief (2026-10-25) (+34 more)

### Community 10 - "ref_node_assert"
Cohesion: 0.14
Nodes (11): assert, fs, os, path, {test}, {writeCaseArtifacts}, assert, fs (+3 more)

### Community 11 - "hashlib"
Cohesion: 0.28
Nodes (8): _box(), freeze_corpus(), main(), validate_corpus(), extract_case(), main(), main(), scale_png()

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

### Community 18 - "inspect_map_actions"
Cohesion: 0.10
Nodes (9): CompletedNodeCandidateTests, CurrentPositionEvidenceTests, EnglishCurrentTests, inspect_map_actions(), PixelMapActionTests, ReferenceCurrentRingTests, recover_map_geometry(), SparseMapGeometryTests (+1 more)

### Community 19 - "higher-floor-replay.test.cjs"
Cohesion: 0.10
Nodes (20): writeCaseArtifacts(), {performance}, {PreviewSession}, runReplay(), {selectNode}, {adaptMap,adaptPreview}, crypto, fs (+12 more)

### Community 20 - "observer-adapter.test.cjs"
Cohesion: 0.20
Nodes (6): {adaptMap,adaptPreview}, assert, crypto, fs, path, {test}

### Community 21 - "geometry.test.cjs"
Cohesion: 0.29
Nodes (11): analysisToClient(), assertCurrentGeometry(), clientToAnalysis(), clientToScreen(), createGeometry(), finiteArray(), point(), assert (+3 more)

### Community 22 - "numpy"
Cohesion: 0.19
Nodes (13): wrapped(), recover_completed_extents(), completed_node_candidates(), inspect_in_progress(), _reference_ring(), _groups(), _match_group(), node_candidates() (+5 more)

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
Cohesion: 0.18
Nodes (4): BoundedOCRRuntime, BoundedOCRTests, normalize_evidence(), PreviewTimerTests

### Community 33 - "preview-session.cjs"
Cohesion: 0.14
Nodes (13): readDirectMapAnchor(), active, { createGeometry, clientToScreen }, crypto, { readDirectMapAnchor }, { validateProof, validateFrame }, { verifyPreview }, verifyPreview() (+5 more)

### Community 34 - "ProgressRuntime"
Cohesion: 0.17
Nodes (7): semantic_state(), EnglishSceneRuntime, EnglishSceneTests, ProgressRuntime, RemainingTimeLocatorTests, SplitRemainingClockTests, WatermarkedMapContextTests

### Community 35 - "random_replay_plan.py"
Cohesion: 0.21
Nodes (11): _decode(), recover_preview_anchor(), sample_layout(), transform_box(), transform_png(), _box(), _frame(), plan_sequences() (+3 more)

### Community 36 - "PreviewAnchorTracker"
Cohesion: 0.24
Nodes (4): PreviewAnchorTracker, PreviewAnchorTracker, PreviewRegistrationTests, recover_preview_anchor()

### Community 38 - "node-selector.cjs"
Cohesion: 0.18
Nodes (15): fail(), freeze(), iou(), issued, numbers(), selectNode(), validateFrame(), validateProof() (+7 more)

### Community 39 - "sparse-peer-bootstrap.test.cjs"
Cohesion: 0.25
Nodes (7): {adaptMap}, assert, {execFileSync}, fixture(), fs, {loadReplayFrames}, {test}

### Community 40 - "aspect-endpoints.test.cjs"
Cohesion: 0.25
Nodes (7): {adaptMap}, assert, {execFileSync}, fixture(), fs, {loadReplayFrames}, {test}

### Community 41 - "ref_node_fs"
Cohesion: 0.05
Nodes (39): crypto, fs, loadReplayFrames(), sha(), {adaptPreview}, assert, fixture(), fs (+31 more)

### Community 45 - "observer-adapter.cjs"
Cohesion: 0.13
Nodes (29): boxValid(), adaptMap(), adaptPreview(), aspectGeometry(), bind(), completedGeometry(), crypto, directMapAnchors (+21 more)

### Community 46 - "ProgressRuntime"
Cohesion: 0.23
Nodes (4): parse_progress(), ProgressRuntime, EnglishProgressTests, ProgressEvidenceTests

### Community 47 - "recover_map_aspect"
Cohesion: 0.16
Nodes (16): completed_geometry(), _cyan_component(), estimate_pixel_aspect(), _gate_pixel_geometry(), _gate_supported_aspect_candidates(), _orange_node_pixel_geometry(), _qualified_aspect_groups(), recover_map_aspect() (+8 more)

### Community 50 - "analyze_cases.py"
Cohesion: 0.19
Nodes (4): case_source_sha(), main(), source_frame_id(), capture_runtime_evidence()

### Community 52 - "ref_node_fs"
Cohesion: 0.06
Nodes (30): crypto, fs, path, {spawnSync}, crypto, {execFileSync}, fs, path (+22 more)

### Community 54 - "re"
Cohesion: 0.25
Nodes (8): freeze_prefixes(), _sha(), _box(), _english_ordinary_crop(), inspect_preview_identity(), outline_size_hypotheses(), _orange_reference_extent(), _timer_original_crop()

### Community 55 - "RandomClientTransformTests"
Cohesion: 0.33
Nodes (3): inverse_point(), RandomClientTransformTests, sample_layout()

### Community 57 - "small-aspect-sparse.test.cjs"
Cohesion: 0.25
Nodes (7): {adaptMap}, assert, {execFileSync}, fixture(), fs, {loadReplayFrames}, {test}

## Knowledge Gaps
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BoundedOCRRuntime` connect `BoundedOCRRuntime` to `pathlib`, `BoundedOCRRuntime`, `inspect_preview_identity`, `ProgressRuntime`, `recover_map_aspect`, `EnglishSceneRuntime`, `MapTitleRereadTests`, `ProgressRuntime`, `NativeEllipsePreviewTests`, `EnglishPreviewTests`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Are the 35 inferred relationships involving `BoundedOCRRuntime` (e.g. with `.test_actual_anisotropic_preview_recovers_selected_node_using_vertical_spacing()` and `.test_actual_near_native_preview_corrects_pixels_even_with_existing_gate_anchor()`) actually correct?**
  _`BoundedOCRRuntime` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Should `pathlib` be split into smaller, more focused modules?**
  _Cohesion score 0.10126582278481013 - nodes in this community are weakly interconnected._
- **Why does `recover_map_aspect()` connect `recover_map_aspect` to `pathlib`, `inspect_map_actions`, `inspect_preview_identity`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Should `preview-session.test.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.10837438423645321 - nodes in this community are weakly interconnected._
- **Why does `BoundedOCRRuntime` connect `BoundedOCRRuntime` to `pathlib`, `BoundedOCRRuntime`, `ProgressRuntime`, `inspect_preview_identity`, `recover_map_aspect`, `EnglishSceneRuntime`, `MapTitleRereadTests`, `ProgressRuntime`, `analyze_cases.py`, `NativeEllipsePreviewTests`, `EnglishPreviewTests`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Should `recover_map_aspect` be split into smaller, more focused modules?**
  _Cohesion score 0.07012987012987013 - nodes in this community are weakly interconnected._