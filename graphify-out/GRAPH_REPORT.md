# Graph Report - CRK-Helper-V2  (2026-10-26)

## Corpus Check
- 148 files · ~64,114 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 933 nodes · 2223 edges · 56 communities (40 shown, 16 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 219 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5ab25956`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- hashlib
- preview-session.test.cjs
- BoundedOCRRuntime
- inspect_preview_identity
- MapAspectTests
- CRK Helper V2：失敗導向重構設計與分階段驗收
- accept-replay.cjs
- semantic_state
- evidence.test.cjs
- CRK Helper V2 P4-C 正式集合與隨機壓力測試
- ref_node_assert
- inspect_map_actions
- RandomReplayPlanTests
- CRK Helper V2 P0–P3 Implementation Plan
- P4-C 開發進度：尚未正式驗收
- ReferenceLineTests
- PreviewSession
- transaction-map-anchor.test.cjs
- recover_map_aspect
- higher-floor-replay.test.cjs
- recover_map_geometry
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
- preview-registration.test.cjs
- ProgressRuntime
- random_replay_plan.py
- PreviewAnchorTracker
- PrefixFreezerTests
- node-selector.cjs
- preview-session.cjs
- aspect-endpoints.test.cjs
- ref_node_fs
- native-ellipse-preview.test.cjs
- PreviewTimerTests
- OfflineAnalyzerTests
- observer-adapter.cjs
- ProgressRuntime
- PreviewPanelScopeTests
- preview-panel-scope.test.cjs
- preview-session.test.cjs
- SmallAspectSparseTests
- replay-runner.cjs
- ref_node_path
- NativeEllipsePreviewTests
- CompletedNodeCandidateTests
- EnglishCurrentTests

## God Nodes (most connected - your core abstractions)
1. `BoundedOCRRuntime` - 42 edges
2. `recover_map_aspect()` - 32 edges
3. `inspect_preview_identity()` - 28 edges
4. `P4-C 開發進度：尚未正式驗收` - 28 edges
5. `BoundedOCRRuntime` - 26 edges
6. `G0多來源影格與快取隔離 brief` - 25 edges
7. `adaptPreview()` - 24 edges
8. `ProgressRuntime` - 23 edges
9. `adaptMap()` - 22 edges
10. `MapAspectTests` - 22 edges

## Surprising Connections (you probably didn't know these)
- `observe()` --calls--> `adaptMap()`  [EXTRACTED]
  tests/map-aspect-adapter.test.cjs → lib/observer-adapter.cjs
- `fixture()` --calls--> `loadReplayFrames()`  [EXTRACTED]
  tests/aspect-endpoints.test.cjs → lib/replay-case.cjs
- `fixture()` --calls--> `loadReplayFrames()`  [EXTRACTED]
  tests/native-ellipse-preview.test.cjs → lib/replay-case.cjs
- `AspectPreviewTests` --uses--> `BoundedOCRRuntime`  [INFERRED]
  tests/test_aspect_preview.py → ml/bounded_ocr.py
- `BoundedOCRRuntime` --uses--> `BoundedOCRRuntime`  [INFERRED]
  tests/test_bounded_ocr.py → ml/bounded_ocr.py

## Import Cycles
- None detected.

## Communities (56 total, 16 thin omitted)

### Community 0 - "hashlib"
Cohesion: 0.07
Nodes (18): _box(), freeze_corpus(), main(), validate_corpus(), extract_case(), main(), _orange_reference_extent(), _decode() (+10 more)

### Community 1 - "preview-session.test.cjs"
Cohesion: 0.13
Nodes (19): frame(), intent, map(), preview(), assert, {map,preview,intent}, {runReplay}, {test} (+11 more)

### Community 2 - "BoundedOCRRuntime"
Cohesion: 0.17
Nodes (4): BoundedOCRRuntime, _MeasuredPreprocess, normalize_evidence(), _remaining_timer_locators()

### Community 3 - "inspect_preview_identity"
Cohesion: 0.16
Nodes (4): AspectPreviewTests, NativePreviewSizeTests, inspect_preview_identity(), PreviewIdentityTests

### Community 4 - "MapAspectTests"
Cohesion: 0.13
Nodes (3): AspectEndpointProjectionTests, estimate_pixel_aspect(), MapAspectTests

### Community 5 - "CRK Helper V2：失敗導向重構設計與分階段驗收"
Cohesion: 0.08
Nodes (25): 10. 本次有條件批准與執行順序, 11. P0–P3 核心實作與審閱修訂（2026-10-24）, 1. 唯一目標與完成邊界, 2.1 已確認的問題, 2.2 尚未證實、需要測試的風險, 2.3 可重用與暫緩處理, 2. 根本原因與證據等級, 3. 方案比較與建議 (+17 more)

### Community 6 - "accept-replay.cjs"
Cohesion: 0.09
Nodes (33): writeCaseArtifacts(), milestoneResult(), buildReplayGate(), invalid(), evaluateDevelopmentReplay(), evaluateReplay(), gradeReplay(), runReplay() (+25 more)

### Community 7 - "semantic_state"
Cohesion: 0.24
Nodes (4): EnglishSceneRuntime, semantic_state(), EnglishSceneTests, SplitRemainingClockTests

### Community 8 - "evidence.test.cjs"
Cohesion: 0.10
Nodes (21): compareSnapshot(), crypto, digest(), fs, locate(), path, snapshotFiles(), files (+13 more)

### Community 9 - "CRK Helper V2 P4-C 正式集合與隨機壓力測試"
Cohesion: 0.05
Nodes (40): Actual case14 original text and near-native recovery brief, Actual glowing-edge candidate and precision repair brief, Actual native map-title OCR truncation repair brief, Actual second-floor case16 pixel evidence brief, Actual watermarked Chinese title context repair brief, CRK Helper V2 P4-C 正式集合與隨機壓力測試, Current evidence, English source development repair brief (2026-10-25) (+32 more)

### Community 10 - "ref_node_assert"
Cohesion: 0.06
Nodes (27): assert, fs, os, path, {test}, {writeCaseArtifacts}, {adaptMap,adaptPreview}, assert (+19 more)

### Community 11 - "inspect_map_actions"
Cohesion: 0.26
Nodes (3): CurrentPositionEvidenceTests, inspect_map_actions(), PixelMapActionTests

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

### Community 19 - "higher-floor-replay.test.cjs"
Cohesion: 0.22
Nodes (7): {adaptMap,adaptPreview}, assert, crypto, fs, path, {runReplay}, {test}

### Community 20 - "recover_map_geometry"
Cohesion: 0.36
Nodes (3): recover_map_geometry(), SparseMapGeometryTests, WatermarkedCheckTests

### Community 21 - "geometry.test.cjs"
Cohesion: 0.29
Nodes (11): analysisToClient(), assertCurrentGeometry(), clientToAnalysis(), clientToScreen(), createGeometry(), finiteArray(), point(), assert (+3 more)

### Community 22 - "numpy"
Cohesion: 0.07
Nodes (39): case_source_sha(), main(), source_frame_id(), completed_geometry(), wrapped(), recover_completed_extents(), completed_node_candidates(), inspect_in_progress() (+31 more)

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
Nodes (4): BoundedOCRRuntime, BoundedOCRTests, normalize_evidence(), EnglishPreviewTests

### Community 33 - "preview-registration.test.cjs"
Cohesion: 0.29
Nodes (6): verifyPreview(), assert, {map,intent,preview}, {selectNode}, {test}, {verifyPreview}

### Community 34 - "ProgressRuntime"
Cohesion: 0.24
Nodes (4): EnglishSceneRuntime, ProgressRuntime, RemainingTimeLocatorTests, WatermarkedMapContextTests

### Community 35 - "random_replay_plan.py"
Cohesion: 0.17
Nodes (10): inverse_point(), sample_layout(), transform_box(), transform_png(), _box(), _frame(), plan_sequences(), _sha() (+2 more)

### Community 36 - "PreviewAnchorTracker"
Cohesion: 0.24
Nodes (4): PreviewAnchorTracker, PreviewAnchorTracker, PreviewRegistrationTests, recover_preview_anchor()

### Community 38 - "node-selector.cjs"
Cohesion: 0.20
Nodes (14): fail(), freeze(), iou(), issued, numbers(), selectNode(), validateFrame(), validateProof() (+6 more)

### Community 39 - "preview-session.cjs"
Cohesion: 0.25
Nodes (7): readDirectMapAnchor(), active, { createGeometry, clientToScreen }, crypto, { readDirectMapAnchor }, { validateProof, validateFrame }, { verifyPreview }

### Community 40 - "aspect-endpoints.test.cjs"
Cohesion: 0.25
Nodes (7): {adaptMap}, assert, {execFileSync}, fixture(), fs, {loadReplayFrames}, {test}

### Community 41 - "ref_node_fs"
Cohesion: 0.06
Nodes (34): crypto, fs, loadReplayFrames(), sha(), {adaptPreview}, assert, fixture(), fs (+26 more)

### Community 42 - "native-ellipse-preview.test.cjs"
Cohesion: 0.25
Nodes (7): {adaptPreview}, assert, {execFileSync}, fixture(), fs, {loadReplayFrames}, {test}

### Community 45 - "observer-adapter.cjs"
Cohesion: 0.14
Nodes (27): boxValid(), adaptMap(), adaptPreview(), aspectGeometry(), bind(), completedGeometry(), crypto, directMapAnchors (+19 more)

### Community 46 - "ProgressRuntime"
Cohesion: 0.17
Nodes (5): parse_progress(), ProgressRuntime, EnglishProgressTests, MapTitleRereadTests, ProgressEvidenceTests

### Community 48 - "preview-panel-scope.test.cjs"
Cohesion: 0.25
Nodes (6): {adaptPreview}, assert, currentPackets, fs, {loadReplayFrames}, {test}

### Community 49 - "preview-session.test.cjs"
Cohesion: 0.29
Nodes (6): assert, {map,intent,preview,clone}, {PreviewSession}, {selectNode}, setup(), {test}

### Community 51 - "replay-runner.cjs"
Cohesion: 0.40
Nodes (3): {performance}, {PreviewSession}, {selectNode}

### Community 52 - "ref_node_path"
Cohesion: 0.09
Nodes (20): crypto, fs, path, {spawnSync}, crypto, {execFileSync}, fs, path (+12 more)

## Knowledge Gaps
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BoundedOCRRuntime` connect `BoundedOCRRuntime` to `hashlib`, `BoundedOCRRuntime`, `inspect_preview_identity`, `MapAspectTests`, `ProgressRuntime`, `semantic_state`, `PreviewTimerTests`, `ProgressRuntime`, `recover_map_aspect`, `NativeEllipsePreviewTests`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `BoundedOCRRuntime` (e.g. with `.test_actual_anisotropic_preview_recovers_selected_node_using_vertical_spacing()` and `.test_actual_near_native_preview_corrects_pixels_even_with_existing_gate_anchor()`) actually correct?**
  _`BoundedOCRRuntime` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Should `hashlib` be split into smaller, more focused modules?**
  _Cohesion score 0.06846755011892626 - nodes in this community are weakly interconnected._
- **Why does `BoundedOCRRuntime` connect `BoundedOCRRuntime` to `hashlib`, `BoundedOCRRuntime`, `ProgressRuntime`, `inspect_preview_identity`, `MapAspectTests`, `semantic_state`, `PreviewTimerTests`, `ProgressRuntime`, `recover_map_aspect`, `NativeEllipsePreviewTests`, `numpy`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Should `preview-session.test.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.13438735177865613 - nodes in this community are weakly interconnected._
- **Why does `recover_map_aspect()` connect `recover_map_aspect` to `hashlib`, `inspect_preview_identity`, `MapAspectTests`, `PreviewPanelScopeTests`, `SmallAspectSparseTests`, `CompletedNodeCandidateTests`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Should `MapAspectTests` be split into smaller, more focused modules?**
  _Cohesion score 0.13405797101449277 - nodes in this community are weakly interconnected._