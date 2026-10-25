# Graph Report - CRK-Helper-V2  (2026-10-26)

## Corpus Check
- 125 files · ~57,975 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 806 nodes · 1890 edges · 46 communities (34 shown, 12 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 185 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8e6a0579`
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
- higher-floor-replay.test.cjs
- evidence.test.cjs
- CRK Helper V2 P4-C 正式集合與隨機壓力測試
- map-aspect-adapter.test.cjs
- PreviewAnchorTracker
- RandomReplayPlanTests
- CRK Helper V2 P0–P3 Implementation Plan
- P4-C 開發進度：尚未正式驗收
- ReferenceLineTests
- RandomClientTransformTests
- preview-session.cjs
- ref_node_path
- observer-adapter.cjs
- replay-development-cli.test.cjs
- geometry.test.cjs
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
- replay-runner.cjs
- EnglishSceneRuntime
- PrefixFreezerTests
- node-selector.cjs
- PreviewSession
- freeze-baseline.cjs
- review-regressions.test.cjs
- observer-adapter.test.cjs
- analyze_cases.py
- OfflineAnalyzerTests
- MapTitleRereadTests

## God Nodes (most connected - your core abstractions)
1. `BoundedOCRRuntime` - 38 edges
2. `P4-C 開發進度：尚未正式驗收` - 28 edges
3. `BoundedOCRRuntime` - 24 edges
4. `recover_map_aspect()` - 24 edges
5. `inspect_preview_identity()` - 23 edges
6. `MapAspectTests` - 22 edges
7. `inspect_map_actions()` - 21 edges
8. `main()` - 20 edges
9. `ProgressRuntime` - 20 edges
10. `adaptMap()` - 17 edges

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

## Communities (46 total, 12 thin omitted)

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
Cohesion: 0.06
Nodes (12): CompletedNodeCandidateTests, CurrentPositionEvidenceTests, EnglishCurrentTests, GateSupportedAspectTests, inspect_map_actions(), PixelMapActionTests, estimate_pixel_aspect(), MapAspectTests (+4 more)

### Community 5 - "CRK Helper V2：失敗導向重構設計與分階段驗收"
Cohesion: 0.08
Nodes (25): 10. 本次有條件批准與執行順序, 11. P0–P3 核心實作與審閱修訂（2026-10-24）, 1. 唯一目標與完成邊界, 2.1 已確認的問題, 2.2 尚未證實、需要測試的風險, 2.3 可重用與暫緩處理, 2. 根本原因與證據等級, 3. 方案比較與建議 (+17 more)

### Community 6 - "accept-replay.cjs"
Cohesion: 0.09
Nodes (30): writeCaseArtifacts(), evaluateDevelopmentReplay(), evaluateReplay(), gradeReplay(), runReplay(), captureCodeVersion(), walk(), {adaptMap,adaptPreview} (+22 more)

### Community 7 - "higher-floor-replay.test.cjs"
Cohesion: 0.22
Nodes (7): {adaptMap,adaptPreview}, assert, crypto, fs, path, {runReplay}, {test}

### Community 8 - "evidence.test.cjs"
Cohesion: 0.16
Nodes (15): compareSnapshot(), crypto, digest(), fs, locate(), milestoneResult(), path, snapshotFiles() (+7 more)

### Community 9 - "CRK Helper V2 P4-C 正式集合與隨機壓力測試"
Cohesion: 0.06
Nodes (31): Actual case14 original text and near-native recovery brief, Actual glowing-edge candidate and precision repair brief, Actual native map-title OCR truncation repair brief, Actual second-floor case16 pixel evidence brief, Actual watermarked Chinese title context repair brief, CRK Helper V2 P4-C 正式集合與隨機壓力測試, Current evidence, English source development repair brief (2026-10-25) (+23 more)

### Community 10 - "map-aspect-adapter.test.cjs"
Cohesion: 0.13
Nodes (15): buildReplayGate(), crypto, fs, invalid(), loadReplayFrames(), sha(), {adaptMap,adaptPreview}, assert (+7 more)

### Community 11 - "PreviewAnchorTracker"
Cohesion: 0.24
Nodes (4): PreviewAnchorTracker, PreviewAnchorTracker, PreviewRegistrationTests, recover_preview_anchor()

### Community 12 - "RandomReplayPlanTests"
Cohesion: 0.38
Nodes (3): plan_sequences(), RandomReplayPlanTests, render_sequences()

### Community 13 - "CRK Helper V2 P0–P3 Implementation Plan"
Cohesion: 0.15
Nodes (12): CRK Helper V2 P0–P3 Implementation Plan, Global Constraints, Review Focus, T1 / P0：基準凍結與里程碑結果契約, T2 / P1：統一可逆座標, T3 / P2：兩幀地圖到唯一節點證明, T4 / P3：單次交易與獨立預覽確認, T5 / P3：只讀辨識adapter、trace與核心整合 (+4 more)

### Community 14 - "P4-C 開發進度：尚未正式驗收"
Cohesion: 0.07
Nodes (28): 2026-10-25：區域10、人工標註及多來源隔離, 2026-10-25 延續驗證, LX46 英文與浮水印開發驗證（2026-10-25）, P4-C 開發進度：尚未正式驗收, 三種尺寸流程試跑通過, 來源修訂與浮水印場景（最新）, 原生960×720的三段新閉環, 尚待完成 (+20 more)

### Community 16 - "RandomClientTransformTests"
Cohesion: 0.33
Nodes (3): inverse_point(), RandomClientTransformTests, sample_layout()

### Community 17 - "preview-session.cjs"
Cohesion: 0.16
Nodes (11): active, { createGeometry, clientToScreen }, crypto, { validateProof, validateFrame }, { verifyPreview }, verifyPreview(), assert, {map,intent,preview} (+3 more)

### Community 18 - "ref_node_path"
Cohesion: 0.10
Nodes (15): assert, fs, os, path, {test}, {writeCaseArtifacts}, assert, fs (+7 more)

### Community 19 - "observer-adapter.cjs"
Cohesion: 0.16
Nodes (21): boxValid(), adaptMap(), adaptPreview(), aspectGeometry(), bind(), completedGeometry(), crypto, {isDeepStrictEqual} (+13 more)

### Community 20 - "replay-development-cli.test.cjs"
Cohesion: 0.07
Nodes (26): crypto, fs, path, {spawnSync}, crypto, {execFileSync}, fs, path (+18 more)

### Community 21 - "geometry.test.cjs"
Cohesion: 0.29
Nodes (11): analysisToClient(), assertCurrentGeometry(), clientToAnalysis(), clientToScreen(), createGeometry(), finiteArray(), point(), assert (+3 more)

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

### Community 30 - "progress.md"
Cohesion: 0.33
Nodes (5): 2026-10-26 continuation: case17 gate proposal and row pitch, Case18 line raster reference repair (current work), Main14 case20 detected-completed extent failure and isolated repair, Native completed proposals and independent supplemental gate, SDD ledger — plan: C:/Users/User/Documents/Codex/CRK-Helper-V2/docs/superpowers/plans/2026-10-24-crk-helper-v2-p0-p3-plan.md

### Community 32 - "BoundedOCRRuntime"
Cohesion: 0.18
Nodes (4): BoundedOCRRuntime, BoundedOCRTests, normalize_evidence(), PreviewTimerTests

### Community 34 - "ProgressRuntime"
Cohesion: 0.19
Nodes (6): semantic_state(), EnglishSceneRuntime, EnglishSceneTests, ProgressRuntime, RemainingTimeLocatorTests, WatermarkedMapContextTests

### Community 35 - "replay-runner.cjs"
Cohesion: 0.20
Nodes (7): {performance}, {PreviewSession}, {selectNode}, assert, {map,preview,intent}, {runReplay}, {test}

### Community 38 - "node-selector.cjs"
Cohesion: 0.42
Nodes (8): fail(), freeze(), iou(), issued, numbers(), selectNode(), validateFrame(), validateProof()

### Community 40 - "freeze-baseline.cjs"
Cohesion: 0.25
Nodes (7): files, fs, out, path, ranges, {snapshotFiles}, walk()

### Community 41 - "review-regressions.test.cjs"
Cohesion: 0.29
Nodes (6): assert, {map,intent,preview}, {PreviewSession}, {selectNode}, setup(), {test}

### Community 42 - "observer-adapter.test.cjs"
Cohesion: 0.20
Nodes (6): {adaptMap,adaptPreview}, assert, crypto, fs, path, {test}

### Community 43 - "analyze_cases.py"
Cohesion: 0.07
Nodes (36): case_source_sha(), main(), source_frame_id(), completed_geometry(), wrapped(), recover_completed_extents(), completed_node_candidates(), inspect_in_progress() (+28 more)

## Knowledge Gaps
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BoundedOCRRuntime` connect `BoundedOCRRuntime` to `hashlib`, `EnglishPreviewTests`, `BoundedOCRRuntime`, `inspect_preview_identity`, `ProgressRuntime`, `inspect_map_actions`, `MapTitleRereadTests`, `ProgressRuntime`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `BoundedOCRRuntime` (e.g. with `.test_actual_anisotropic_preview_recovers_selected_node_using_vertical_spacing()` and `.test_actual_near_native_preview_corrects_pixels_even_with_existing_gate_anchor()`) actually correct?**
  _`BoundedOCRRuntime` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Should `hashlib` be split into smaller, more focused modules?**
  _Cohesion score 0.06224256292906179 - nodes in this community are weakly interconnected._
- **Why does `BoundedOCRRuntime` connect `BoundedOCRRuntime` to `hashlib`, `BoundedOCRRuntime`, `EnglishPreviewTests`, `inspect_preview_identity`, `ProgressRuntime`, `inspect_map_actions`, `analyze_cases.py`, `MapTitleRereadTests`, `ProgressRuntime`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Should `preview-session.test.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.12333333333333334 - nodes in this community are weakly interconnected._
- **Why does `MapAspectTests` connect `inspect_map_actions` to `hashlib`, `BoundedOCRRuntime`, `analyze_cases.py`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Should `inspect_map_actions` be split into smaller, more focused modules?**
  _Cohesion score 0.06448412698412699 - nodes in this community are weakly interconnected._