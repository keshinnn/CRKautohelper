# Graph Report - CRK-Helper-V2  (2026-10-26)

## Corpus Check
- 120 files · ~53,955 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 772 nodes · 1800 edges · 40 communities (31 shown, 9 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 173 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3e986b9d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- hashlib
- preview-session.cjs
- BoundedOCRRuntime
- inspect_preview_identity
- inspect_map_actions
- CRK Helper V2：失敗導向重構設計與分階段驗收
- accept-replay.cjs
- higher-floor-replay.test.cjs
- evidence.test.cjs
- CRK Helper V2 P4-C 正式集合與隨機壓力測試
- map-aspect-adapter.test.cjs
- PreviewAnchorTracker
- RandomReplayPlanTests
- CRK Helper V2 P0–P3 Implementation Plan
- P4-C 開發進度：尚未正式驗收
- replay-saved.cjs
- RandomClientTransformTests
- observe-image.cjs
- ref_node_path
- observer-adapter.cjs
- replay-development-cli.test.cjs
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
- EnglishSceneRuntime
- PrefixFreezerTests
- MapTitleRereadTests
- MapAspectTests
- analyze_cases.py

## God Nodes (most connected - your core abstractions)
1. `BoundedOCRRuntime` - 38 edges
2. `P4-C 開發進度：尚未正式驗收` - 26 edges
3. `BoundedOCRRuntime` - 24 edges
4. `inspect_preview_identity()` - 23 edges
5. `MapAspectTests` - 22 edges
6. `main()` - 20 edges
7. `ProgressRuntime` - 20 edges
8. `recover_map_aspect()` - 19 edges
9. `inspect_map_actions()` - 18 edges
10. `adaptMap()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `AspectPreviewTests` --uses--> `BoundedOCRRuntime`  [INFERRED]
  tests/test_aspect_preview.py → ml/bounded_ocr.py
- `BoundedOCRRuntime` --uses--> `BoundedOCRRuntime`  [INFERRED]
  tests/test_bounded_ocr.py → ml/bounded_ocr.py
- `BoundedOCRTests` --uses--> `BoundedOCRRuntime`  [INFERRED]
  tests/test_bounded_ocr.py → ml/bounded_ocr.py
- `EnglishPreviewTests` --uses--> `BoundedOCRRuntime`  [INFERRED]
  tests/test_english_preview.py → ml/bounded_ocr.py
- `EnglishProgressTests` --uses--> `BoundedOCRRuntime`  [INFERRED]
  tests/test_english_progress.py → ml/bounded_ocr.py

## Import Cycles
- None detected.

## Communities (40 total, 9 thin omitted)

### Community 0 - "hashlib"
Cohesion: 0.06
Nodes (39): completed_node_candidates(), inspect_in_progress(), _groups(), _match_group(), node_candidates(), _box(), freeze_corpus(), main() (+31 more)

### Community 1 - "preview-session.cjs"
Cohesion: 0.05
Nodes (59): analysisToClient(), assertCurrentGeometry(), clientToAnalysis(), clientToScreen(), createGeometry(), finiteArray(), point(), boxValid() (+51 more)

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
Cohesion: 0.15
Nodes (15): milestoneResult(), captureCodeVersion(), walk(), {adaptMap,adaptPreview}, {captureCodeVersion}, {compareSnapshot}, crypto, {evaluateReplay} (+7 more)

### Community 7 - "higher-floor-replay.test.cjs"
Cohesion: 0.14
Nodes (12): {performance}, {PreviewSession}, runReplay(), {selectNode}, {adaptMap,adaptPreview}, assert, crypto, fs (+4 more)

### Community 8 - "evidence.test.cjs"
Cohesion: 0.10
Nodes (21): compareSnapshot(), crypto, digest(), fs, locate(), path, snapshotFiles(), files (+13 more)

### Community 9 - "CRK Helper V2 P4-C 正式集合與隨機壓力測試"
Cohesion: 0.07
Nodes (27): Actual case14 original text and near-native recovery brief, Actual glowing-edge candidate and precision repair brief, Actual native map-title OCR truncation repair brief, Actual second-floor case16 pixel evidence brief, Actual watermarked Chinese title context repair brief, CRK Helper V2 P4-C 正式集合與隨機壓力測試, Current evidence, English source development repair brief (2026-10-25) (+19 more)

### Community 10 - "map-aspect-adapter.test.cjs"
Cohesion: 0.14
Nodes (14): buildReplayGate(), crypto, fs, invalid(), loadReplayFrames(), sha(), {adaptMap,adaptPreview}, assert (+6 more)

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
Cohesion: 0.07
Nodes (26): 2026-10-25：區域10、人工標註及多來源隔離, 2026-10-25 延續驗證, LX46 英文與浮水印開發驗證（2026-10-25）, P4-C 開發進度：尚未正式驗收, 三種尺寸流程試跑通過, 來源修訂與浮水印場景（最新）, 原生960×720的三段新閉環, 尚待完成 (+18 more)

### Community 15 - "replay-saved.cjs"
Cohesion: 0.16
Nodes (12): crypto, fs, path, {spawnSync}, writeCaseArtifacts(), {adaptMap,adaptPreview}, crypto, fs (+4 more)

### Community 16 - "RandomClientTransformTests"
Cohesion: 0.31
Nodes (4): inverse_point(), transform_png(), RandomClientTransformTests, sample_layout()

### Community 17 - "observe-image.cjs"
Cohesion: 0.15
Nodes (12): {adaptMap,adaptPreview}, bundle, crypto, frame, fs, id, packet, path (+4 more)

### Community 18 - "ref_node_path"
Cohesion: 0.08
Nodes (19): assert, fs, os, path, {test}, {writeCaseArtifacts}, assert, fs (+11 more)

### Community 19 - "observer-adapter.cjs"
Cohesion: 0.12
Nodes (17): adaptMap(), adaptPreview(), aspectGeometry(), bind(), crypto, {isDeepStrictEqual}, mapActions(), markerCurrent() (+9 more)

### Community 20 - "replay-development-cli.test.cjs"
Cohesion: 0.15
Nodes (10): crypto, {execFileSync}, fs, path, assert, crypto, fs, path (+2 more)

### Community 21 - "replay-development.cjs"
Cohesion: 0.17
Nodes (14): evaluateDevelopmentReplay(), evaluateReplay(), gradeReplay(), {adaptMap,adaptPreview}, {buildReplayGate,loadReplayFrames}, {captureCodeVersion}, crypto, {evaluateDevelopmentReplay} (+6 more)

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

### Community 40 - "MapAspectTests"
Cohesion: 0.18
Nodes (3): CompletedNodeCandidateTests, MapAspectTests, recover_map_aspect()

### Community 43 - "analyze_cases.py"
Cohesion: 0.06
Nodes (15): case_source_sha(), main(), source_frame_id(), _cyan_component(), estimate_pixel_aspect(), _gate_pixel_geometry(), _gate_supported_aspect_candidates(), _orange_node_pixel_geometry() (+7 more)

## Knowledge Gaps
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BoundedOCRRuntime` connect `BoundedOCRRuntime` to `hashlib`, `EnglishPreviewTests`, `BoundedOCRRuntime`, `inspect_preview_identity`, `EnglishSceneRuntime`, `ProgressRuntime`, `MapTitleRereadTests`, `MapAspectTests`, `ProgressRuntime`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `BoundedOCRRuntime` (e.g. with `.test_actual_anisotropic_preview_recovers_selected_node_using_vertical_spacing()` and `.test_actual_near_native_preview_corrects_pixels_even_with_existing_gate_anchor()`) actually correct?**
  _`BoundedOCRRuntime` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Should `hashlib` be split into smaller, more focused modules?**
  _Cohesion score 0.055538907202077714 - nodes in this community are weakly interconnected._
- **Why does `BoundedOCRRuntime` connect `BoundedOCRRuntime` to `hashlib`, `BoundedOCRRuntime`, `EnglishPreviewTests`, `inspect_preview_identity`, `EnglishSceneRuntime`, `ProgressRuntime`, `MapTitleRereadTests`, `MapAspectTests`, `analyze_cases.py`, `ProgressRuntime`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Should `preview-session.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.05263157894736842 - nodes in this community are weakly interconnected._
- **Why does `MapAspectTests` connect `MapAspectTests` to `hashlib`, `BoundedOCRRuntime`, `analyze_cases.py`, `EnglishSceneRuntime`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Should `inspect_map_actions` be split into smaller, more focused modules?**
  _Cohesion score 0.12807881773399016 - nodes in this community are weakly interconnected._