# Graph Report - CRK-Helper-V2  (2026-10-25)

## Corpus Check
- 120 files · ~53,430 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 768 nodes · 1793 edges · 45 communities (34 shown, 11 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 171 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1268f82e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- hashlib
- preview-session.test.cjs
- BoundedOCRRuntime
- inspect_preview_identity
- inspect_map_actions
- CRK Helper V2：失敗導向重構設計與分階段驗收
- accept-replay.cjs
- replay-runner.cjs
- evidence.test.cjs
- CRK Helper V2 P4-C 正式集合與隨機壓力測試
- map-aspect-adapter.test.cjs
- PreviewAnchorTracker
- RandomReplayPlanTests
- CRK Helper V2 P0–P3 Implementation Plan
- P4-C 開發進度：尚未正式驗收
- review-regressions.test.cjs
- RandomClientTransformTests
- observe-image.cjs
- ref_node_path
- observer-adapter.cjs
- replay-development.cjs
- ProgressRuntime
- CRK Helper V2：P0–P3核心與審閱修正紀錄
- CorpusFreezerTests
- P4-A 原始影片最小閉環結果
- extract_case
- P4-B 固定縮放閉環結果
- 2026-10-24-crk-helper-v2-p4a-plan.md
- 2026-10-24-crk-helper-v2-p4b-plan.md
- progress.md
- BoundedOCRRuntime
- EnglishPreviewTests
- ProgressRuntime
- OfflineAnalyzerTests
- EnglishSceneRuntime
- PrefixFreezerTests
- MapTitleRereadTests
- preview-session.cjs
- MapAspectTests
- geometry.test.cjs
- node-selector.cjs
- analyze_cases.py
- observer-adapter.test.cjs
- PreviewSession

## God Nodes (most connected - your core abstractions)
1. `BoundedOCRRuntime` - 38 edges
2. `P4-C 開發進度：尚未正式驗收` - 25 edges
3. `BoundedOCRRuntime` - 24 edges
4. `inspect_preview_identity()` - 23 edges
5. `MapAspectTests` - 22 edges
6. `main()` - 20 edges
7. `ProgressRuntime` - 20 edges
8. `recover_map_aspect()` - 18 edges
9. `adaptMap()` - 17 edges
10. `inspect_map_actions()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `observe()` --calls--> `adaptMap()`  [EXTRACTED]
  tests/map-aspect-adapter.test.cjs → lib/observer-adapter.cjs
- `AspectPreviewTests` --uses--> `BoundedOCRRuntime`  [INFERRED]
  tests/test_aspect_preview.py → ml/bounded_ocr.py
- `BoundedOCRRuntime` --uses--> `BoundedOCRRuntime`  [INFERRED]
  tests/test_bounded_ocr.py → ml/bounded_ocr.py
- `BoundedOCRTests` --uses--> `BoundedOCRRuntime`  [INFERRED]
  tests/test_bounded_ocr.py → ml/bounded_ocr.py
- `EnglishPreviewTests` --uses--> `BoundedOCRRuntime`  [INFERRED]
  tests/test_english_preview.py → ml/bounded_ocr.py

## Import Cycles
- None detected.

## Communities (45 total, 11 thin omitted)

### Community 0 - "hashlib"
Cohesion: 0.06
Nodes (24): _box(), freeze_corpus(), main(), validate_corpus(), extract_case(), main(), _decode(), recover_preview_anchor() (+16 more)

### Community 1 - "preview-session.test.cjs"
Cohesion: 0.12
Nodes (21): clone(), frame(), intent, map(), preview(), assert, {map,intent,clone}, {selectNode,validateProof} (+13 more)

### Community 2 - "BoundedOCRRuntime"
Cohesion: 0.19
Nodes (3): BoundedOCRRuntime, _MeasuredPreprocess, normalize_evidence()

### Community 3 - "inspect_preview_identity"
Cohesion: 0.20
Nodes (3): AspectPreviewTests, inspect_preview_identity(), PreviewIdentityTests

### Community 4 - "inspect_map_actions"
Cohesion: 0.13
Nodes (7): CurrentPositionEvidenceTests, EnglishCurrentTests, inspect_map_actions(), PixelMapActionTests, recover_map_geometry(), SparseMapGeometryTests, WatermarkedCheckTests

### Community 5 - "CRK Helper V2：失敗導向重構設計與分階段驗收"
Cohesion: 0.08
Nodes (25): 10. 本次有條件批准與執行順序, 11. P0–P3 核心實作與審閱修訂（2026-10-24）, 1. 唯一目標與完成邊界, 2.1 已確認的問題, 2.2 尚未證實、需要測試的風險, 2.3 可重用與暫緩處理, 2. 根本原因與證據等級, 3. 方案比較與建議 (+17 more)

### Community 6 - "accept-replay.cjs"
Cohesion: 0.14
Nodes (18): writeCaseArtifacts(), evaluateDevelopmentReplay(), evaluateReplay(), gradeReplay(), captureCodeVersion(), walk(), {adaptMap,adaptPreview}, {captureCodeVersion} (+10 more)

### Community 7 - "replay-runner.cjs"
Cohesion: 0.20
Nodes (7): {performance}, {PreviewSession}, {selectNode}, assert, {map,preview,intent}, {runReplay}, {test}

### Community 8 - "evidence.test.cjs"
Cohesion: 0.10
Nodes (22): compareSnapshot(), crypto, digest(), fs, locate(), milestoneResult(), path, snapshotFiles() (+14 more)

### Community 9 - "CRK Helper V2 P4-C 正式集合與隨機壓力測試"
Cohesion: 0.07
Nodes (27): Actual case14 original text and near-native recovery brief, Actual glowing-edge candidate and precision repair brief, Actual native map-title OCR truncation repair brief, Actual second-floor case16 pixel evidence brief, Actual watermarked Chinese title context repair brief, CRK Helper V2 P4-C 正式集合與隨機壓力測試, Current evidence, English source development repair brief (2026-10-25) (+19 more)

### Community 10 - "map-aspect-adapter.test.cjs"
Cohesion: 0.22
Nodes (8): {adaptMap,adaptPreview}, assert, fs, {loadReplayFrames}, observe(), path, {selectNode}, {test}

### Community 11 - "PreviewAnchorTracker"
Cohesion: 0.38
Nodes (3): PreviewAnchorTracker, PreviewRegistrationTests, recover_preview_anchor()

### Community 12 - "RandomReplayPlanTests"
Cohesion: 0.38
Nodes (3): plan_sequences(), RandomReplayPlanTests, render_sequences()

### Community 13 - "CRK Helper V2 P0–P3 Implementation Plan"
Cohesion: 0.15
Nodes (12): CRK Helper V2 P0–P3 Implementation Plan, Global Constraints, Review Focus, T1 / P0：基準凍結與里程碑結果契約, T2 / P1：統一可逆座標, T3 / P2：兩幀地圖到唯一節點證明, T4 / P3：單次交易與獨立預覽確認, T5 / P3：只讀辨識adapter、trace與核心整合 (+4 more)

### Community 14 - "P4-C 開發進度：尚未正式驗收"
Cohesion: 0.08
Nodes (25): 2026-10-25：區域10、人工標註及多來源隔離, 2026-10-25 延續驗證, LX46 英文與浮水印開發驗證（2026-10-25）, P4-C 開發進度：尚未正式驗收, 三種尺寸流程試跑通過, 來源修訂與浮水印場景（最新）, 原生960×720的三段新閉環, 尚待完成 (+17 more)

### Community 15 - "review-regressions.test.cjs"
Cohesion: 0.29
Nodes (6): assert, {map,intent,preview}, {PreviewSession}, {selectNode}, setup(), {test}

### Community 16 - "RandomClientTransformTests"
Cohesion: 0.33
Nodes (3): inverse_point(), RandomClientTransformTests, sample_layout()

### Community 17 - "observe-image.cjs"
Cohesion: 0.09
Nodes (20): crypto, fs, path, {spawnSync}, crypto, {execFileSync}, fs, path (+12 more)

### Community 18 - "ref_node_path"
Cohesion: 0.08
Nodes (21): assert, fs, os, path, {test}, {writeCaseArtifacts}, assert, fs (+13 more)

### Community 19 - "observer-adapter.cjs"
Cohesion: 0.11
Nodes (27): boxValid(), adaptMap(), adaptPreview(), aspectGeometry(), bind(), crypto, {isDeepStrictEqual}, mapActions() (+19 more)

### Community 21 - "replay-development.cjs"
Cohesion: 0.13
Nodes (18): buildReplayGate(), crypto, fs, invalid(), loadReplayFrames(), sha(), {adaptMap,adaptPreview}, {buildReplayGate,loadReplayFrames} (+10 more)

### Community 22 - "ProgressRuntime"
Cohesion: 0.23
Nodes (4): parse_progress(), ProgressRuntime, EnglishProgressTests, ProgressEvidenceTests

### Community 23 - "CRK Helper V2：P0–P3核心與審閱修正紀錄"
Cohesion: 0.33
Nodes (5): CRK Helper V2：P0–P3核心與審閱修正紀錄, 尚未驗收與下一個工作, 已交付, 本次實際驗證, 獨立審閱與測試先行修正

### Community 25 - "P4-A 原始影片最小閉環結果"
Cohesion: 0.40
Nodes (4): P4-A 原始影片最小閉環結果, 可重現命令, 真實失敗與修正, 邊界與後續

### Community 27 - "P4-B 固定縮放閉環結果"
Cohesion: 0.50
Nodes (3): P4-B 固定縮放閉環結果, 失敗導向修正, 重現

### Community 32 - "BoundedOCRRuntime"
Cohesion: 0.18
Nodes (4): BoundedOCRRuntime, BoundedOCRTests, normalize_evidence(), PreviewTimerTests

### Community 34 - "ProgressRuntime"
Cohesion: 0.24
Nodes (4): EnglishSceneRuntime, ProgressRuntime, RemainingTimeLocatorTests, WatermarkedMapContextTests

### Community 36 - "EnglishSceneRuntime"
Cohesion: 0.19
Nodes (5): EnglishSceneRuntime, semantic_state(), EnglishSceneTests, GateSupportedAspectTests, estimate_pixel_aspect()

### Community 39 - "preview-session.cjs"
Cohesion: 0.16
Nodes (11): active, { createGeometry, clientToScreen }, crypto, { validateProof, validateFrame }, { verifyPreview }, verifyPreview(), assert, {map,intent,preview} (+3 more)

### Community 40 - "MapAspectTests"
Cohesion: 0.12
Nodes (9): _cyan_component(), estimate_pixel_aspect(), _gate_pixel_geometry(), _gate_supported_aspect_candidates(), _orange_node_pixel_geometry(), _qualified_aspect_groups(), CompletedNodeCandidateTests, MapAspectTests (+1 more)

### Community 41 - "geometry.test.cjs"
Cohesion: 0.29
Nodes (11): analysisToClient(), assertCurrentGeometry(), clientToAnalysis(), clientToScreen(), createGeometry(), finiteArray(), point(), assert (+3 more)

### Community 42 - "node-selector.cjs"
Cohesion: 0.42
Nodes (8): fail(), freeze(), iou(), issued, numbers(), selectNode(), validateFrame(), validateProof()

### Community 43 - "analyze_cases.py"
Cohesion: 0.09
Nodes (23): case_source_sha(), main(), source_frame_id(), completed_node_candidates(), inspect_in_progress(), _groups(), _match_group(), node_candidates() (+15 more)

### Community 44 - "observer-adapter.test.cjs"
Cohesion: 0.20
Nodes (6): {adaptMap,adaptPreview}, assert, crypto, fs, path, {test}

## Knowledge Gaps
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BoundedOCRRuntime` connect `BoundedOCRRuntime` to `hashlib`, `EnglishPreviewTests`, `BoundedOCRRuntime`, `inspect_preview_identity`, `EnglishSceneRuntime`, `ProgressRuntime`, `MapTitleRereadTests`, `MapAspectTests`, `ProgressRuntime`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `BoundedOCRRuntime` (e.g. with `.test_actual_anisotropic_preview_recovers_selected_node_using_vertical_spacing()` and `.test_actual_near_native_preview_corrects_pixels_even_with_existing_gate_anchor()`) actually correct?**
  _`BoundedOCRRuntime` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Should `hashlib` be split into smaller, more focused modules?**
  _Cohesion score 0.06437346437346438 - nodes in this community are weakly interconnected._
- **Why does `BoundedOCRRuntime` connect `BoundedOCRRuntime` to `hashlib`, `BoundedOCRRuntime`, `EnglishPreviewTests`, `inspect_preview_identity`, `EnglishSceneRuntime`, `ProgressRuntime`, `MapTitleRereadTests`, `MapAspectTests`, `analyze_cases.py`, `ProgressRuntime`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Should `preview-session.test.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.12333333333333334 - nodes in this community are weakly interconnected._
- **Why does `MapAspectTests` connect `MapAspectTests` to `hashlib`, `BoundedOCRRuntime`, `EnglishSceneRuntime`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Should `inspect_map_actions` be split into smaller, more focused modules?**
  _Cohesion score 0.12807881773399016 - nodes in this community are weakly interconnected._