# Graph Report - CRK-Helper-V2  (2026-10-25)

## Corpus Check
- 111 files · ~47,487 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 702 nodes · 1598 edges · 44 communities (32 shown, 12 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 117 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `195fc3c0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- hashlib
- ref_node_assert
- BoundedOCRRuntime
- inspect_preview_identity
- inspect_map_actions
- CRK Helper V2：失敗導向重構設計與分階段驗收
- accept-replay.cjs
- observer-adapter.cjs
- evidence.test.cjs
- CRK Helper V2 P4-C 正式集合與隨機壓力測試
- replay-development.cjs
- PreviewAnchorTracker
- RandomReplayPlanTests
- CRK Helper V2 P0–P3 Implementation Plan
- P4-C 開發進度：尚未正式驗收
- geometry.test.cjs
- random_replay_plan.py
- observe-image.cjs
- ref_node_fs
- observer-adapter.test.cjs
- review-regressions.test.cjs
- map-aspect-adapter.test.cjs
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
- node-selector.cjs
- ProgressRuntime
- AspectPreviewTests
- EnglishSceneRuntime
- PrefixFreezerTests
- MapTitleRereadTests
- preview-session.cjs
- MapAspectTests
- PreviewSession
- OfflineAnalyzerTests
- replay-runner.cjs

## God Nodes (most connected - your core abstractions)
1. `BoundedOCRRuntime` - 27 edges
2. `main()` - 20 edges
3. `BoundedOCRRuntime` - 20 edges
4. `inspect_preview_identity()` - 19 edges
5. `adaptMap()` - 17 edges
6. `P4-C 開發進度：尚未正式驗收` - 17 edges
7. `adaptPreview()` - 16 edges
8. `selectNode()` - 15 edges
9. `inspect_map_actions()` - 15 edges
10. `ProgressRuntime` - 15 edges

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

## Communities (44 total, 12 thin omitted)

### Community 0 - "hashlib"
Cohesion: 0.05
Nodes (36): case_source_sha(), main(), source_frame_id(), inspect_in_progress(), EnglishSceneRuntime, _groups(), _match_group(), node_candidates() (+28 more)

### Community 1 - "ref_node_assert"
Cohesion: 0.12
Nodes (21): clone(), frame(), intent, map(), preview(), assert, {map,intent,clone}, {selectNode,validateProof} (+13 more)

### Community 2 - "BoundedOCRRuntime"
Cohesion: 0.19
Nodes (3): BoundedOCRRuntime, _MeasuredPreprocess, normalize_evidence()

### Community 3 - "inspect_preview_identity"
Cohesion: 0.23
Nodes (3): EnglishPreviewTests, inspect_preview_identity(), PreviewIdentityTests

### Community 4 - "inspect_map_actions"
Cohesion: 0.13
Nodes (7): CurrentPositionEvidenceTests, EnglishCurrentTests, inspect_map_actions(), PixelMapActionTests, recover_map_geometry(), SparseMapGeometryTests, WatermarkedCheckTests

### Community 5 - "CRK Helper V2：失敗導向重構設計與分階段驗收"
Cohesion: 0.08
Nodes (25): 10. 本次有條件批准與執行順序, 11. P0–P3 核心實作與審閱修訂（2026-10-24）, 1. 唯一目標與完成邊界, 2.1 已確認的問題, 2.2 尚未證實、需要測試的風險, 2.3 可重用與暫緩處理, 2. 根本原因與證據等級, 3. 方案比較與建議 (+17 more)

### Community 6 - "accept-replay.cjs"
Cohesion: 0.14
Nodes (18): writeCaseArtifacts(), evaluateDevelopmentReplay(), evaluateReplay(), gradeReplay(), captureCodeVersion(), walk(), {adaptMap,adaptPreview}, {captureCodeVersion} (+10 more)

### Community 7 - "observer-adapter.cjs"
Cohesion: 0.11
Nodes (27): boxValid(), adaptMap(), adaptPreview(), aspectGeometry(), bind(), crypto, {isDeepStrictEqual}, mapActions() (+19 more)

### Community 8 - "evidence.test.cjs"
Cohesion: 0.10
Nodes (22): compareSnapshot(), crypto, digest(), fs, locate(), milestoneResult(), path, snapshotFiles() (+14 more)

### Community 9 - "CRK Helper V2 P4-C 正式集合與隨機壓力測試"
Cohesion: 0.09
Nodes (21): Actual native map-title OCR truncation repair brief, Actual watermarked Chinese title context repair brief, CRK Helper V2 P4-C 正式集合與隨機壓力測試, Current evidence, English source development repair brief (2026-10-25), G0多來源影格與快取隔離 brief, G0追加實作 brief：實際OCR資產與runtime可追溯, G2評分器校正與開發報告 (+13 more)

### Community 10 - "replay-development.cjs"
Cohesion: 0.13
Nodes (18): buildReplayGate(), crypto, fs, invalid(), loadReplayFrames(), sha(), {adaptMap,adaptPreview}, {buildReplayGate,loadReplayFrames} (+10 more)

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
Cohesion: 0.11
Nodes (17): 2026-10-25：區域10、人工標註及多來源隔離, 2026-10-25 延續驗證, LX46 英文與浮水印開發驗證（2026-10-25）, P4-C 開發進度：尚未正式驗收, 三種尺寸流程試跑通過, 來源修訂與浮水印場景（最新）, 原生960×720的三段新閉環, 尚待完成 (+9 more)

### Community 15 - "geometry.test.cjs"
Cohesion: 0.29
Nodes (11): analysisToClient(), assertCurrentGeometry(), clientToAnalysis(), clientToScreen(), createGeometry(), finiteArray(), point(), assert (+3 more)

### Community 16 - "random_replay_plan.py"
Cohesion: 0.15
Nodes (12): inverse_point(), sample_layout(), transform_box(), transform_png(), _box(), _frame(), plan_sequences(), render_sequences() (+4 more)

### Community 17 - "observe-image.cjs"
Cohesion: 0.09
Nodes (20): crypto, fs, path, {spawnSync}, crypto, {execFileSync}, fs, path (+12 more)

### Community 18 - "ref_node_fs"
Cohesion: 0.08
Nodes (21): assert, fs, os, path, {test}, {writeCaseArtifacts}, assert, fs (+13 more)

### Community 19 - "observer-adapter.test.cjs"
Cohesion: 0.20
Nodes (6): {adaptMap,adaptPreview}, assert, crypto, fs, path, {test}

### Community 20 - "review-regressions.test.cjs"
Cohesion: 0.29
Nodes (6): assert, {map,intent,preview}, {PreviewSession}, {selectNode}, setup(), {test}

### Community 21 - "map-aspect-adapter.test.cjs"
Cohesion: 0.22
Nodes (8): {adaptMap,adaptPreview}, assert, fs, {loadReplayFrames}, observe(), path, {selectNode}, {test}

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
Cohesion: 0.22
Nodes (3): BoundedOCRRuntime, BoundedOCRTests, normalize_evidence()

### Community 33 - "node-selector.cjs"
Cohesion: 0.42
Nodes (8): fail(), freeze(), iou(), issued, numbers(), selectNode(), validateFrame(), validateProof()

### Community 34 - "ProgressRuntime"
Cohesion: 0.31
Nodes (3): EnglishSceneRuntime, ProgressRuntime, WatermarkedMapContextTests

### Community 39 - "preview-session.cjs"
Cohesion: 0.16
Nodes (11): active, { createGeometry, clientToScreen }, crypto, { validateProof, validateFrame }, { verifyPreview }, verifyPreview(), assert, {map,intent,preview} (+3 more)

### Community 40 - "MapAspectTests"
Cohesion: 0.32
Nodes (3): estimate_pixel_aspect(), MapAspectTests, recover_map_aspect()

### Community 44 - "replay-runner.cjs"
Cohesion: 0.20
Nodes (7): {performance}, {PreviewSession}, {selectNode}, assert, {map,preview,intent}, {runReplay}, {test}

## Knowledge Gaps
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BoundedOCRRuntime` connect `BoundedOCRRuntime` to `hashlib`, `BoundedOCRRuntime`, `inspect_preview_identity`, `AspectPreviewTests`, `EnglishSceneRuntime`, `MapTitleRereadTests`, `ProgressRuntime`, `ProgressRuntime`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Should `hashlib` be split into smaller, more focused modules?**
  _Cohesion score 0.05479302832244009 - nodes in this community are weakly interconnected._
- **Why does `BoundedOCRRuntime` connect `BoundedOCRRuntime` to `hashlib`, `BoundedOCRRuntime`, `ProgressRuntime`, `inspect_preview_identity`, `AspectPreviewTests`, `EnglishSceneRuntime`, `MapTitleRereadTests`, `ProgressRuntime`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Should `ref_node_assert` be split into smaller, more focused modules?**
  _Cohesion score 0.12333333333333334 - nodes in this community are weakly interconnected._
- **Why does `OfflineAnalyzerTests` connect `OfflineAnalyzerTests` to `hashlib`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Should `inspect_map_actions` be split into smaller, more focused modules?**
  _Cohesion score 0.12807881773399016 - nodes in this community are weakly interconnected._
- **Should `CRK Helper V2：失敗導向重構設計與分階段驗收` be split into smaller, more focused modules?**
  _Cohesion score 0.07692307692307693 - nodes in this community are weakly interconnected._