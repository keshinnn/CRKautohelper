# Graph Report - CRK-Helper-V2  (2026-10-25)

## Corpus Check
- 97 files · ~40,444 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 590 nodes · 1275 edges · 32 communities (25 shown, 7 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 105 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `16608469`
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
- observer-adapter.cjs
- evidence.test.cjs
- CRK Helper V2 P4-C 正式集合與隨機壓力測試
- replay-saved.cjs
- BoundedOCRRuntime
- PreviewAnchorTracker
- CRK Helper V2 P0–P3 Implementation Plan
- P4-C 開發進度：尚未正式驗收
- preview-session.cjs
- random_client_transform.py
- observe-image.cjs
- artifact-writer.cjs
- observer-adapter.test.cjs
- higher-floor-replay.test.cjs
- OfflineAnalyzerTests
- CRK Helper V2：P0–P3核心與審閱修正紀錄
- CorpusFreezerTests
- P4-A 原始影片最小閉環結果
- extract_case
- P4-B 固定縮放閉環結果
- 2026-10-24-crk-helper-v2-p4a-plan.md
- 2026-10-24-crk-helper-v2-p4b-plan.md
- progress.md
- node-selector.cjs

## God Nodes (most connected - your core abstractions)
1. `BoundedOCRRuntime` - 24 edges
2. `main()` - 19 edges
3. `BoundedOCRRuntime` - 19 edges
4. `inspect_preview_identity()` - 16 edges
5. `inspect_map_actions()` - 15 edges
6. `ProgressRuntime` - 15 edges
7. `selectNode()` - 14 edges
8. `PreviewSession` - 14 edges
9. `ProgressRuntime` - 14 edges
10. `P4-C 開發進度：尚未正式驗收` - 14 edges

## Surprising Connections (you probably didn't know these)
- `BoundedOCRRuntime` --uses--> `BoundedOCRRuntime`  [INFERRED]
  tests/test_bounded_ocr.py → ml/bounded_ocr.py
- `BoundedOCRTests` --uses--> `BoundedOCRRuntime`  [INFERRED]
  tests/test_bounded_ocr.py → ml/bounded_ocr.py
- `EnglishPreviewTests` --uses--> `BoundedOCRRuntime`  [INFERRED]
  tests/test_english_preview.py → ml/bounded_ocr.py
- `EnglishProgressTests` --uses--> `BoundedOCRRuntime`  [INFERRED]
  tests/test_english_progress.py → ml/bounded_ocr.py
- `EnglishSceneTests` --uses--> `BoundedOCRRuntime`  [INFERRED]
  tests/test_english_scene.py → ml/bounded_ocr.py

## Import Cycles
- None detected.

## Communities (32 total, 7 thin omitted)

### Community 0 - "hashlib"
Cohesion: 0.06
Nodes (30): case_source_sha(), main(), source_frame_id(), inspect_in_progress(), _groups(), _match_group(), node_candidates(), _box() (+22 more)

### Community 1 - "preview-session.test.cjs"
Cohesion: 0.06
Nodes (45): evaluateDevelopmentReplay(), evaluateReplay(), gradeReplay(), assert, fs, os, path, {test} (+37 more)

### Community 2 - "BoundedOCRRuntime"
Cohesion: 0.07
Nodes (14): EnglishSceneRuntime, semantic_state(), parse_progress(), ProgressRuntime, BoundedOCRRuntime, BoundedOCRTests, normalize_evidence(), EnglishProgressTests (+6 more)

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
Nodes (17): writeCaseArtifacts(), runReplay(), captureCodeVersion(), walk(), {adaptMap,adaptPreview}, {captureCodeVersion}, {compareSnapshot}, crypto (+9 more)

### Community 7 - "observer-adapter.cjs"
Cohesion: 0.27
Nodes (11): boxValid(), adaptMap(), adaptPreview(), bind(), crypto, {isDeepStrictEqual}, mapActions(), markerCurrent() (+3 more)

### Community 8 - "evidence.test.cjs"
Cohesion: 0.10
Nodes (22): compareSnapshot(), crypto, digest(), fs, locate(), milestoneResult(), path, snapshotFiles() (+14 more)

### Community 9 - "CRK Helper V2 P4-C 正式集合與隨機壓力測試"
Cohesion: 0.11
Nodes (18): Actual native map-title OCR truncation repair brief, Actual watermarked Chinese title context repair brief, CRK Helper V2 P4-C 正式集合與隨機壓力測試, Current evidence, English source development repair brief (2026-10-25), G0多來源影格與快取隔離 brief, G0追加實作 brief：實際OCR資產與runtime可追溯, G2評分器校正與開發報告 (+10 more)

### Community 10 - "replay-saved.cjs"
Cohesion: 0.29
Nodes (6): {adaptMap,adaptPreview}, crypto, fs, path, {runReplay}, {writeCaseArtifacts}

### Community 11 - "BoundedOCRRuntime"
Cohesion: 0.19
Nodes (3): BoundedOCRRuntime, _MeasuredPreprocess, normalize_evidence()

### Community 12 - "PreviewAnchorTracker"
Cohesion: 0.24
Nodes (4): PreviewAnchorTracker, PreviewAnchorTracker, PreviewRegistrationTests, recover_preview_anchor()

### Community 13 - "CRK Helper V2 P0–P3 Implementation Plan"
Cohesion: 0.15
Nodes (12): CRK Helper V2 P0–P3 Implementation Plan, Global Constraints, Review Focus, T1 / P0：基準凍結與里程碑結果契約, T2 / P1：統一可逆座標, T3 / P2：兩幀地圖到唯一節點證明, T4 / P3：單次交易與獨立預覽確認, T5 / P3：只讀辨識adapter、trace與核心整合 (+4 more)

### Community 14 - "P4-C 開發進度：尚未正式驗收"
Cohesion: 0.13
Nodes (14): 2026-10-25：區域10、人工標註及多來源隔離, LX46 英文與浮水印開發驗證（2026-10-25）, P4-C 開發進度：尚未正式驗收, 來源修訂與浮水印場景（最新）, 原生960×720的三段新閉環, 尚待完成, 後續實際失敗與修正, 新增使用者提供的含浮水印影片 (+6 more)

### Community 15 - "preview-session.cjs"
Cohesion: 0.14
Nodes (18): analysisToClient(), assertCurrentGeometry(), clientToAnalysis(), clientToScreen(), createGeometry(), finiteArray(), point(), active (+10 more)

### Community 16 - "random_client_transform.py"
Cohesion: 0.23
Nodes (6): inverse_point(), sample_layout(), transform_box(), transform_png(), RandomClientTransformTests, sample_layout()

### Community 17 - "observe-image.cjs"
Cohesion: 0.15
Nodes (12): {adaptMap,adaptPreview}, bundle, crypto, frame, fs, id, packet, path (+4 more)

### Community 18 - "artifact-writer.cjs"
Cohesion: 0.12
Nodes (13): crypto, fs, path, {spawnSync}, crypto, {execFileSync}, fs, path (+5 more)

### Community 19 - "observer-adapter.test.cjs"
Cohesion: 0.20
Nodes (6): {adaptMap,adaptPreview}, assert, crypto, fs, path, {test}

### Community 20 - "higher-floor-replay.test.cjs"
Cohesion: 0.22
Nodes (7): {adaptMap,adaptPreview}, assert, crypto, fs, path, {runReplay}, {test}

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
Nodes (11): fail(), freeze(), iou(), issued, numbers(), selectNode(), validateFrame(), validateProof() (+3 more)

## Knowledge Gaps
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BoundedOCRRuntime` connect `BoundedOCRRuntime` to `hashlib`, `BoundedOCRRuntime`, `inspect_preview_identity`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Should `hashlib` be split into smaller, more focused modules?**
  _Cohesion score 0.05896595926506196 - nodes in this community are weakly interconnected._
- **Why does `BoundedOCRRuntime` connect `BoundedOCRRuntime` to `hashlib`, `inspect_preview_identity`, `BoundedOCRRuntime`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Should `preview-session.test.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.05974025974025974 - nodes in this community are weakly interconnected._
- **Why does `OfflineAnalyzerTests` connect `OfflineAnalyzerTests` to `hashlib`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Should `BoundedOCRRuntime` be split into smaller, more focused modules?**
  _Cohesion score 0.07474600870827286 - nodes in this community are weakly interconnected._
- **Should `inspect_map_actions` be split into smaller, more focused modules?**
  _Cohesion score 0.12807881773399016 - nodes in this community are weakly interconnected._