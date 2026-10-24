# Graph Report - CRK-Helper-V2  (2026-10-25)

## Corpus Check
- 91 files · ~32,958 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 578 nodes · 1230 edges · 37 communities (29 shown, 8 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 88 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `08f2b67b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- hashlib
- preview-session.test.cjs
- BoundedOCRRuntime
- replay-saved.cjs
- inspect_map_actions
- CRK Helper V2：失敗導向重構設計與分階段驗收
- accept-replay.cjs
- observer-adapter.cjs
- evidence.test.cjs
- CRK Helper V2 P4-C 正式集合與隨機壓力測試
- analyze_cases.py
- PreviewAnchorTracker
- CRK Helper V2 P0–P3 Implementation Plan
- P4-C 開發進度：尚未正式驗收
- geometry.test.cjs
- random_client_transform.py
- observe-image.cjs
- artifact-writer.cjs
- observer-adapter.test.cjs
- higher-floor-replay.test.cjs
- OfflineAnalyzerTests
- freeze-baseline.cjs
- CRK Helper V2：P0–P3核心與審閱修正紀錄
- CorpusFreezerTests
- P4-A 原始影片最小閉環結果
- extract_case
- P4-B 固定縮放閉環結果
- 2026-10-24-crk-helper-v2-p4a-plan.md
- 2026-10-24-crk-helper-v2-p4b-plan.md
- progress.md
- node-selector.cjs
- preview-session.cjs
- PreviewSession
- replay-evaluator.test.cjs
- node-selector.test.cjs
- review-regressions.test.cjs

## God Nodes (most connected - your core abstractions)
1. `main()` - 19 edges
2. `BoundedOCRRuntime` - 19 edges
3. `BoundedOCRRuntime` - 17 edges
4. `inspect_preview_identity()` - 16 edges
5. `inspect_map_actions()` - 15 edges
6. `selectNode()` - 14 edges
7. `PreviewSession` - 14 edges
8. `ProgressRuntime` - 13 edges
9. `CRK Helper V2 P4-C 正式集合與隨機壓力測試` - 13 edges
10. `adaptMap()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `EnglishProgressTests` --uses--> `BoundedOCRRuntime`  [INFERRED]
  tests/test_english_progress.py → ml/bounded_ocr.py
- `EnglishSceneTests` --uses--> `ProgressRuntime`  [INFERRED]
  tests/test_english_scene.py → ml/progress_evidence.py
- `MapTitleRereadTests` --uses--> `ProgressRuntime`  [INFERRED]
  tests/test_map_title_reread.py → ml/progress_evidence.py
- `ProgressRuntime` --uses--> `ProgressRuntime`  [INFERRED]
  tests/test_progress_evidence.py → ml/progress_evidence.py
- `main()` --calls--> `compareSnapshot()`  [EXTRACTED]
  scripts/accept-replay.cjs → lib/evidence.cjs

## Import Cycles
- None detected.

## Communities (37 total, 8 thin omitted)

### Community 0 - "hashlib"
Cohesion: 0.08
Nodes (15): _box(), freeze_corpus(), main(), validate_corpus(), extract_case(), main(), _decode(), recover_preview_anchor() (+7 more)

### Community 1 - "preview-session.test.cjs"
Cohesion: 0.15
Nodes (16): clone(), frame(), map(), preview(), assert, {map,intent,preview,clone}, {PreviewSession}, {selectNode} (+8 more)

### Community 2 - "BoundedOCRRuntime"
Cohesion: 0.05
Nodes (15): BoundedOCRRuntime, _MeasuredPreprocess, normalize_evidence(), EnglishSceneRuntime, semantic_state(), BoundedOCRRuntime, BoundedOCRTests, normalize_evidence() (+7 more)

### Community 3 - "replay-saved.cjs"
Cohesion: 0.29
Nodes (6): {adaptMap,adaptPreview}, crypto, fs, path, {runReplay}, {writeCaseArtifacts}

### Community 4 - "inspect_map_actions"
Cohesion: 0.13
Nodes (7): CurrentPositionEvidenceTests, EnglishCurrentTests, inspect_map_actions(), PixelMapActionTests, recover_map_geometry(), SparseMapGeometryTests, WatermarkedCheckTests

### Community 5 - "CRK Helper V2：失敗導向重構設計與分階段驗收"
Cohesion: 0.08
Nodes (25): 10. 本次有條件批准與執行順序, 11. P0–P3 核心實作與審閱修訂（2026-10-24）, 1. 唯一目標與完成邊界, 2.1 已確認的問題, 2.2 尚未證實、需要測試的風險, 2.3 可重用與暫緩處理, 2. 根本原因與證據等級, 3. 方案比較與建議 (+17 more)

### Community 6 - "accept-replay.cjs"
Cohesion: 0.14
Nodes (21): writeCaseArtifacts(), adaptMap(), adaptPreview(), bind(), runReplay(), captureCodeVersion(), walk(), {adaptMap,adaptPreview} (+13 more)

### Community 7 - "observer-adapter.cjs"
Cohesion: 0.29
Nodes (6): crypto, {isDeepStrictEqual}, mapActions(), markerCurrent(), previewAnchor(), {validateFrame,boxValid}

### Community 8 - "evidence.test.cjs"
Cohesion: 0.15
Nodes (15): compareSnapshot(), crypto, digest(), fs, locate(), milestoneResult(), path, snapshotFiles() (+7 more)

### Community 9 - "CRK Helper V2 P4-C 正式集合與隨機壓力測試"
Cohesion: 0.11
Nodes (17): Actual native map-title OCR truncation repair brief, CRK Helper V2 P4-C 正式集合與隨機壓力測試, Current evidence, English source development repair brief (2026-10-25), G0多來源影格與快取隔離 brief, G0追加實作 brief：實際OCR資產與runtime可追溯, G2評分器校正與開發報告, P3回放分支補強：沒有有效點擊不得讀取人工後續 (+9 more)

### Community 10 - "analyze_cases.py"
Cohesion: 0.09
Nodes (19): case_source_sha(), main(), source_frame_id(), inspect_in_progress(), _groups(), _match_group(), node_candidates(), _check_masks() (+11 more)

### Community 12 - "PreviewAnchorTracker"
Cohesion: 0.24
Nodes (4): PreviewAnchorTracker, PreviewAnchorTracker, PreviewRegistrationTests, recover_preview_anchor()

### Community 13 - "CRK Helper V2 P0–P3 Implementation Plan"
Cohesion: 0.15
Nodes (12): CRK Helper V2 P0–P3 Implementation Plan, Global Constraints, Review Focus, T1 / P0：基準凍結與里程碑結果契約, T2 / P1：統一可逆座標, T3 / P2：兩幀地圖到唯一節點證明, T4 / P3：單次交易與獨立預覽確認, T5 / P3：只讀辨識adapter、trace與核心整合 (+4 more)

### Community 14 - "P4-C 開發進度：尚未正式驗收"
Cohesion: 0.15
Nodes (12): 2026-10-25：區域10、人工標註及多來源隔離, LX46 英文與浮水印開發驗證（2026-10-25）, P4-C 開發進度：尚未正式驗收, 原生960×720的三段新閉環, 尚待完成, 新增使用者提供的含浮水印影片, 新鮮辨識量測與資料追溯, 最新原生來源凍結與開發檢查（2026-10-25） (+4 more)

### Community 15 - "geometry.test.cjs"
Cohesion: 0.29
Nodes (11): analysisToClient(), assertCurrentGeometry(), clientToAnalysis(), clientToScreen(), createGeometry(), finiteArray(), point(), assert (+3 more)

### Community 16 - "random_client_transform.py"
Cohesion: 0.23
Nodes (6): inverse_point(), sample_layout(), transform_box(), transform_png(), RandomClientTransformTests, sample_layout()

### Community 17 - "observe-image.cjs"
Cohesion: 0.15
Nodes (12): {adaptMap,adaptPreview}, bundle, crypto, frame, fs, id, packet, path (+4 more)

### Community 18 - "artifact-writer.cjs"
Cohesion: 0.12
Nodes (14): crypto, fs, path, {spawnSync}, crypto, {execFileSync}, fs, path (+6 more)

### Community 19 - "observer-adapter.test.cjs"
Cohesion: 0.20
Nodes (6): {adaptMap,adaptPreview}, assert, crypto, fs, path, {test}

### Community 20 - "higher-floor-replay.test.cjs"
Cohesion: 0.22
Nodes (7): {adaptMap,adaptPreview}, assert, crypto, fs, path, {runReplay}, {test}

### Community 22 - "freeze-baseline.cjs"
Cohesion: 0.25
Nodes (7): files, fs, out, path, ranges, {snapshotFiles}, walk()

### Community 23 - "CRK Helper V2：P0–P3核心與審閱修正紀錄"
Cohesion: 0.33
Nodes (5): CRK Helper V2：P0–P3核心與審閱修正紀錄, 尚未驗收與下一個工作, 已交付, 本次實際驗證, 獨立審閱與測試先行修正

### Community 25 - "P4-A 原始影片最小閉環結果"
Cohesion: 0.40
Nodes (4): P4-A 原始影片最小閉環結果, 可重現命令, 真實失敗與修正, 邊界與後續

### Community 27 - "P4-B 固定縮放閉環結果"
Cohesion: 0.50
Nodes (3): P4-B 固定縮放閉環結果, 失敗導向修正, 重現

### Community 32 - "node-selector.cjs"
Cohesion: 0.23
Nodes (12): boxValid(), fail(), freeze(), iou(), issued, numbers(), selectNode(), validateFrame() (+4 more)

### Community 33 - "preview-session.cjs"
Cohesion: 0.16
Nodes (11): active, { createGeometry, clientToScreen }, crypto, { validateProof, validateFrame }, { verifyPreview }, verifyPreview(), assert, {map,intent,preview} (+3 more)

### Community 35 - "replay-evaluator.test.cjs"
Cohesion: 0.29
Nodes (8): evaluateDevelopmentReplay(), evaluateReplay(), gradeReplay(), intent, assert, {map,preview,intent}, {runReplay}, {test}

### Community 36 - "node-selector.test.cjs"
Cohesion: 0.17
Nodes (9): assert, {map,intent,clone}, {selectNode,validateProof}, {test}, assert, fs, os, path (+1 more)

### Community 37 - "review-regressions.test.cjs"
Cohesion: 0.29
Nodes (6): assert, {map,intent,preview}, {PreviewSession}, {selectNode}, setup(), {test}

## Knowledge Gaps
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BoundedOCRRuntime` connect `BoundedOCRRuntime` to `hashlib`, `analyze_cases.py`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Should `hashlib` be split into smaller, more focused modules?**
  _Cohesion score 0.08081791626095423 - nodes in this community are weakly interconnected._
- **Why does `BoundedOCRRuntime` connect `BoundedOCRRuntime` to `hashlib`, `analyze_cases.py`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Should `BoundedOCRRuntime` be split into smaller, more focused modules?**
  _Cohesion score 0.05427547363031234 - nodes in this community are weakly interconnected._
- **Why does `OfflineAnalyzerTests` connect `OfflineAnalyzerTests` to `hashlib`, `analyze_cases.py`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Should `inspect_map_actions` be split into smaller, more focused modules?**
  _Cohesion score 0.12807881773399016 - nodes in this community are weakly interconnected._
- **Should `CRK Helper V2：失敗導向重構設計與分階段驗收` be split into smaller, more focused modules?**
  _Cohesion score 0.07692307692307693 - nodes in this community are weakly interconnected._