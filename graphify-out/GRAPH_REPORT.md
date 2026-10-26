# Graph Report - CRK-Helper-V2  (2026-10-27)

## Corpus Check
- 182 files · ~71,107 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 2)

## Summary
- 1198 nodes · 2868 edges · 60 communities (46 shown, 14 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 277 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f88cb93c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- json
- ref_node_assert
- BoundedOCRRuntime
- inspect_preview_identity
- recover_map_aspect
- CRK Helper V2：失敗導向重構設計與分階段驗收
- convergence-regression.py
- CRK Helper V2 — 閉環測試階段性技術審查報告
- evidence.test.cjs
- CRK Helper V2 P4-C 正式集合與隨機壓力測試
- observe-image.cjs
- negative-selection-check.cjs
- RandomReplayPlanTests
- CRK Helper V2 P0–P3 Implementation Plan
- P4-C 開發進度：尚未正式驗收
- ReferenceLineTests
- adaptMap
- accept-replay.cjs
- inspect_map_actions
- higher-floor-replay.test.cjs
- preview-context.cjs
- geometry.test.cjs
- hashlib
- CRK Helper V2：P0–P3核心與審閱修正紀錄
- CorpusFreezerTests
- P4-A 原始影片最小閉環結果
- extract_case
- P4-B 固定縮放閉環結果
- 2026-10-24-crk-helper-v2-p4a-plan.md
- 2026-10-24-crk-helper-v2-p4b-plan.md
- progress.md
- BoundedOCRRuntime
- pending-preview.test.cjs
- ProgressRuntime
- CRK Helper V2 P4-C 正式集合與隨機壓力測試
- ref_node_fs
- PrefixFreezerTests
- map-aspect-adapter.test.cjs
- preview-panel-scope.test.cjs
- transaction-map-anchor.test.cjs
- loadReplayFrames
- OfflineAnalyzerTests
- PreviewRegistrationTests
- preview-session.cjs
- observer-adapter.cjs
- ProgressRuntime
- PreviewSession
- CRK Helper V2 座標與預覽證據收斂 Implementation Plan
- small-aspect-sparse.test.cjs
- EnglishPreviewTests
- native-preview-sizes.test.cjs
- ConvergenceRunnerTests
- random_replay_plan.py
- V2 座標／預覽收斂驗證紀錄
- reference-current-ring.test.cjs
- node-selector.cjs
- NativeEllipsePreviewTests
- MapTitleRereadTests
- actual_frame

## God Nodes (most connected - your core abstractions)
1. `BoundedOCRRuntime` - 47 edges
2. `recover_map_aspect()` - 35 edges
3. `adaptMap()` - 33 edges
4. `loadReplayFrames()` - 33 edges
5. `adaptPreview()` - 30 edges
6. `BoundedOCRRuntime` - 29 edges
7. `inspect_preview_identity()` - 29 edges
8. `P4-C 開發進度：尚未正式驗收` - 28 edges
9. `G0多來源影格與快取隔離 brief` - 27 edges
10. `ProgressRuntime` - 25 edges

## Surprising Connections (you probably didn't know these)
- `2.1 已確認的問題` --references--> `inspect_map()`  [INFERRED]
  docs/superpowers/specs/2026-10-24-crk-helper-v2-design.md → ml/map_observer.py
- `預覽控制、身份與操作權限` --references--> `effective_observation_state()`  [INFERRED]
  docs/superpowers/specs/2026-10-26-geometry-preview-contract.md → ml/analyze_cases.py
- `座標` --references--> `analysis_raster()`  [INFERRED]
  docs/superpowers/specs/2026-10-26-geometry-preview-contract.md → ml/geometry_contract.py
- `座標` --references--> `inspect_map()`  [INFERRED]
  docs/superpowers/specs/2026-10-26-geometry-preview-contract.md → ml/map_observer.py
- `observe()` --calls--> `adaptMap()`  [EXTRACTED]
  tests/map-aspect-adapter.test.cjs → lib/observer-adapter.cjs

## Import Cycles
- None detected.

## Communities (60 total, 14 thin omitted)

### Community 0 - "json"
Cohesion: 0.07
Nodes (14): _decode(), recover_preview_anchor(), main(), scale_png(), main(), percentiles(), control_case(), control_request() (+6 more)

### Community 1 - "ref_node_assert"
Cohesion: 0.10
Nodes (25): clone(), frame(), intent, map(), preview(), assert, {map,intent,clone}, {selectNode,validateProof} (+17 more)

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

### Community 6 - "convergence-regression.py"
Cohesion: 0.17
Nodes (13): _box(), freeze_corpus(), main(), validate_corpus(), extract_case(), main(), check_snapshot(), code_snapshot() (+5 more)

### Community 7 - "CRK Helper V2 — 閉環測試階段性技術審查報告"
Cohesion: 0.05
Nodes (39): 0. 審查方法與證據解讀, 1.1 目前完成與未完成, 1.2 「60組」的正確分母, 1.3 P0～P5狀態, 1.4 G0～G5狀態：維持原標準, 2.1 表格讀法與逐組證據, 2.2 失敗原因與已記錄修正, 2.3 首次結果、修正負擔與回歸趨勢 (+31 more)

### Community 8 - "evidence.test.cjs"
Cohesion: 0.10
Nodes (22): compareSnapshot(), crypto, digest(), fs, locate(), milestoneResult(), path, snapshotFiles() (+14 more)

### Community 9 - "CRK Helper V2 P4-C 正式集合與隨機壓力測試"
Cohesion: 0.07
Nodes (27): Actual native map-title OCR truncation repair brief, Actual watermarked Chinese title context repair brief, English source development repair brief (2026-10-25), G0多來源影格與快取隔離 brief, Native coordinate convention regression, Sparse native map geometry failure brief, Task2/3 next isolated defect: offscreen-gate ordinary preview scope, Task2/4 actual anisotropic zero-candidate failure brief (+19 more)

### Community 10 - "observe-image.cjs"
Cohesion: 0.06
Nodes (30): crypto, fs, path, {spawnSync}, crypto, {execFileSync}, fs, path (+22 more)

### Community 11 - "negative-selection-check.cjs"
Cohesion: 0.10
Nodes (16): {adaptMap,adaptPreview}, analyzed, assert, {captureCodeVersion}, crypto, frames, fs, [input,out] (+8 more)

### Community 12 - "RandomReplayPlanTests"
Cohesion: 0.38
Nodes (3): plan_sequences(), RandomReplayPlanTests, render_sequences()

### Community 13 - "CRK Helper V2 P0–P3 Implementation Plan"
Cohesion: 0.17
Nodes (12): CRK Helper V2 P0–P3 Implementation Plan, Global Constraints, Review Focus, T1 / P0：基準凍結與里程碑結果契約, T2 / P1：統一可逆座標, T3 / P2：兩幀地圖到唯一節點證明, T4 / P3：單次交易與獨立預覽確認, T5 / P3：只讀辨識adapter、trace與核心整合 (+4 more)

### Community 14 - "P4-C 開發進度：尚未正式驗收"
Cohesion: 0.07
Nodes (28): 2026-10-25：區域10、人工標註及多來源隔離, 2026-10-25 延續驗證, LX46 英文與浮水印開發驗證（2026-10-25）, P4-C 開發進度：尚未正式驗收, 三種尺寸流程試跑通過, 來源修訂與浮水印場景（最新）, 原生960×720的三段新閉環, 尚待完成 (+20 more)

### Community 16 - "adaptMap"
Cohesion: 0.11
Nodes (31): writeCaseArtifacts(), adaptMap(), adaptPreview(), bind(), markDirectMapAnchor(), previewAnchor(), runReplay(), captureCodeVersion() (+23 more)

### Community 17 - "accept-replay.cjs"
Cohesion: 0.15
Nodes (14): evaluateDevelopmentReplay(), evaluateReplay(), gradeReplay(), {adaptMap,adaptPreview}, {captureCodeVersion}, {compareSnapshot}, crypto, {evaluateReplay} (+6 more)

### Community 18 - "inspect_map_actions"
Cohesion: 0.10
Nodes (9): CompletedNodeCandidateTests, CurrentPositionEvidenceTests, EnglishCurrentTests, inspect_map_actions(), PixelMapActionTests, ReferenceCurrentRingTests, recover_map_geometry(), SparseMapGeometryTests (+1 more)

### Community 19 - "higher-floor-replay.test.cjs"
Cohesion: 0.11
Nodes (15): {performance}, {PreviewSession}, {selectNode}, {adaptMap,adaptPreview}, fs, {loadReplayFrames,buildReplayGate}, {performance}, {runReplay} (+7 more)

### Community 20 - "preview-context.cjs"
Cohesion: 0.38
Nodes (8): adaptPreviewContext(), authority, box(), englishProvenance(), {isDeepStrictEqual:eq}, originalRow(), textBox(), timerProvenance()

### Community 21 - "geometry.test.cjs"
Cohesion: 0.29
Nodes (11): analysisToClient(), assertCurrentGeometry(), clientToAnalysis(), clientToScreen(), createGeometry(), finiteArray(), point(), assert (+3 more)

### Community 22 - "hashlib"
Cohesion: 0.05
Nodes (60): V2 座標與點後等待契約 v1, 回歸版本, 座標, 預覽控制、身份與操作權限, case_source_sha(), effective_observation_state(), main(), source_frame_id() (+52 more)

### Community 23 - "CRK Helper V2：P0–P3核心與審閱修正紀錄"
Cohesion: 0.18
Nodes (5): CRK Helper V2：P0–P3核心與審閱修正紀錄, 尚未驗收與下一個工作, 已交付, 本次實際驗證, 獨立審閱與測試先行修正

### Community 25 - "P4-A 原始影片最小閉環結果"
Cohesion: 0.40
Nodes (4): P4-A 原始影片最小閉環結果, 可重現命令, 真實失敗與修正, 邊界與後續

### Community 27 - "P4-B 固定縮放閉環結果"
Cohesion: 0.50
Nodes (3): P4-B 固定縮放閉環結果, 失敗導向修正, 重現

### Community 30 - "progress.md"
Cohesion: 0.33
Nodes (6): 2026-10-26 continuation: case17 gate proposal and row pitch, Case18 line raster reference repair (current work), Main14 case20 detected-completed extent failure and isolated repair, Main16 case21: transaction-local semantic root after post-click resize, Native completed proposals and independent supplemental gate, SDD ledger — plan: C:/Users/User/Documents/Codex/CRK-Helper-V2/docs/superpowers/plans/2026-10-24-crk-helper-v2-p0-p3-plan.md

### Community 32 - "BoundedOCRRuntime"
Cohesion: 0.18
Nodes (4): BoundedOCRRuntime, BoundedOCRTests, normalize_evidence(), PreviewTimerTests

### Community 33 - "pending-preview.test.cjs"
Cohesion: 0.12
Nodes (16): verifyPreview(), {adaptMap,readDirectMapAnchor}, assert, {execFileSync}, fixture(), fs, {loadReplayFrames}, {PreviewSession} (+8 more)

### Community 34 - "ProgressRuntime"
Cohesion: 0.13
Nodes (9): EnglishSceneRuntime, semantic_state(), EnglishSceneRuntime, EnglishSceneTests, ProgressRuntime, RemainingTimeLocatorTests, SplitDayClockTests, SplitRemainingClockTests (+1 more)

### Community 35 - "CRK Helper V2 P4-C 正式集合與隨機壓力測試"
Cohesion: 0.13
Nodes (15): Actual case14 original text and near-native recovery brief, Actual glowing-edge candidate and precision repair brief, Actual second-floor case16 pixel evidence brief, CRK Helper V2 P4-C 正式集合與隨機壓力測試, Current evidence, G0追加實作 brief：實際OCR資產與runtime可追溯, G2評分器校正與開發報告, P3回放分支補強：沒有有效點擊不得讀取人工後續 (+7 more)

### Community 36 - "ref_node_fs"
Cohesion: 0.05
Nodes (38): assert, fs, os, path, {test}, {writeCaseArtifacts}, assert, fs (+30 more)

### Community 38 - "map-aspect-adapter.test.cjs"
Cohesion: 0.20
Nodes (9): {adaptMap,adaptPreview}, assert, fixture(), fs, {loadReplayFrames}, observe(), path, {selectNode} (+1 more)

### Community 39 - "preview-panel-scope.test.cjs"
Cohesion: 0.22
Nodes (7): {adaptPreview}, assert, currentPackets, fixture(), fs, {loadReplayFrames}, {test}

### Community 40 - "transaction-map-anchor.test.cjs"
Cohesion: 0.18
Nodes (12): {adaptMap,adaptPreview,readDirectMapAnchor}, assert, fixture(), fs, {loadReplayFrames}, observation(), path, replay() (+4 more)

### Community 41 - "loadReplayFrames"
Cohesion: 0.06
Nodes (33): buildReplayGate(), crypto, fs, invalid(), loadReplayFrames(), sha(), {adaptMap}, assert (+25 more)

### Community 43 - "PreviewRegistrationTests"
Cohesion: 0.24
Nodes (4): PreviewAnchorTracker, PreviewAnchorTracker, PreviewRegistrationTests, recover_preview_anchor()

### Community 44 - "preview-session.cjs"
Cohesion: 0.25
Nodes (7): readDirectMapAnchor(), active, { createGeometry, clientToScreen }, crypto, { readDirectMapAnchor }, { validateProof, validateFrame }, { verifyPreview }

### Community 45 - "observer-adapter.cjs"
Cohesion: 0.15
Nodes (26): analysisRaster(), {isDeepStrictEqual:eq}, nativeGeometryEvidence(), resizeBox(), resizePoint(), size(), validateGeometryCertificate(), boxValid() (+18 more)

### Community 46 - "ProgressRuntime"
Cohesion: 0.23
Nodes (4): parse_progress(), ProgressRuntime, EnglishProgressTests, ProgressEvidenceTests

### Community 48 - "CRK Helper V2 座標與預覽證據收斂 Implementation Plan"
Cohesion: 0.20
Nodes (9): CRK Helper V2 座標與預覽證據收斂 Implementation Plan, Global Constraints, Review Focus, Task 1：根因重現、契約與聚焦測試, Task 2：最小幾何契約, Task 3：預覽控制／身份與等待能力分離, Task 4：同版本回歸、稽核與停止交付, 執行紀錄 (+1 more)

### Community 49 - "small-aspect-sparse.test.cjs"
Cohesion: 0.25
Nodes (7): {adaptMap}, assert, {execFileSync}, fixture(), fs, {loadReplayFrames}, {test}

### Community 51 - "native-preview-sizes.test.cjs"
Cohesion: 0.25
Nodes (7): {adaptPreview}, assert, {execFileSync}, fixture(), fs, {loadReplayFrames}, {test}

### Community 55 - "random_replay_plan.py"
Cohesion: 0.14
Nodes (12): inverse_point(), sample_layout(), transform_box(), transform_png(), _box(), _frame(), plan_sequences(), render_sequences() (+4 more)

### Community 58 - "V2 座標／預覽收斂驗證紀錄"
Cohesion: 0.18
Nodes (10): V2 座標／預覽收斂驗證紀錄, 原始1551影格與七張歷史變動的當版核對, 固定倍率工具相容性修正, 基準與範圍, 已發現並處理的迴歸, 最新階段結果（後續驗證仍進行中）, 最終工具版本與驗收邊界, 本輪明確取捨與剩餘限制 (+2 more)

### Community 59 - "reference-current-ring.test.cjs"
Cohesion: 0.25
Nodes (7): {adaptMap}, assert, {execFileSync}, fixture(), fs, {loadReplayFrames}, {test}

### Community 62 - "node-selector.cjs"
Cohesion: 0.20
Nodes (14): fail(), freeze(), iou(), issued, numbers(), selectNode(), validateFrame(), validateProof() (+6 more)

## Knowledge Gaps
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `inspect_map()` connect `hashlib` to `json`, `CRK Helper V2：失敗導向重構設計與分階段驗收`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Should `json` be split into smaller, more focused modules?**
  _Cohesion score 0.07119741100323625 - nodes in this community are weakly interconnected._
- **Why does `2.1 已確認的問題` connect `CRK Helper V2：失敗導向重構設計與分階段驗收` to `hashlib`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._
- **Should `ref_node_assert` be split into smaller, more focused modules?**
  _Cohesion score 0.10344827586206896 - nodes in this community are weakly interconnected._
- **Should `recover_map_aspect` be split into smaller, more focused modules?**
  _Cohesion score 0.0677555958862674 - nodes in this community are weakly interconnected._
- **Should `CRK Helper V2：失敗導向重構設計與分階段驗收` be split into smaller, more focused modules?**
  _Cohesion score 0.08 - nodes in this community are weakly interconnected._
- **Should `CRK Helper V2 — 閉環測試階段性技術審查報告` be split into smaller, more focused modules?**
  _Cohesion score 0.05128205128205128 - nodes in this community are weakly interconnected._