# Graph Report - CRK-Helper-V2  (2026-11-02)

## Corpus Check
- 224 files · ~86,075 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 2)

## Summary
- 1531 nodes · 3524 edges · 97 communities (61 shown, 36 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 373 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `99f5121e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- preview-session.test.cjs
- BoundedOCRRuntime
- inspect_preview_identity
- recover_map_aspect
- CRK Helper V2：失敗導向重構設計與分階段驗收
- CRK Helper V2 — 閉環測試階段性技術審查報告
- evidence.test.cjs
- CRK Helper V2 P4-C 正式集合與隨機壓力測試
- map_aspect.py
- negative-selection-check.cjs
- RandomReplayPlanTests
- CRK Helper V2 P0–P3 Implementation Plan
- P4-C 開發進度：尚未正式驗收
- ReferenceLineTests
- accept-replay.cjs
- convergence-regression.py
- inspect_map_actions
- 第41組候選生成與重採樣穩定性分析
- geometry-contract.test.cjs
- geometry.test.cjs
- FrameIntermediates
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
- ref_node_assert
- Python視覺效能優化與泛化驗證（2026-10-27）
- PrefixFreezerTests
- recover_map_geometry
- ref_node_fs
- transaction-map-anchor.test.cjs
- loadReplayFrames
- hashlib
- CRK Helper V2 P4-C 正式集合與隨機壓力測試
- observe-image.cjs
- observer-adapter.cjs
- ProgressRuntime
- PreviewSession
- CRK Helper V2 座標與預覽證據收斂 Implementation Plan
- analyze_cases.py
- FrameIntermediatesTests
- preview-panel-scope.test.cjs
- ContextLineRemeasurementTests
- ConvergenceRunnerTests
- preview-session.cjs
- random_replay_plan.py
- M1有限實作與離線驗證計畫
- Python vision performance and generalization Implementation Plan
- V2 座標／預覽收斂驗證紀錄
- GateSupportedAspectTests
- S3ScrollCoverageDefects
- json
- node-selector.cjs
- replay-evaluator.test.cjs
- PhaseMapPipelineTests
- RandomClientTransformTests
- CRK Helper V2：60組開發測試階段報告（coverage當版回歸未通過）
- PreviewPanelScopeTests
- StageTiming
- review-regressions.test.cjs
- CacheBackendIdentityTests
- LegacyCurrentPhaseTests
- node_candidates
- specs/2026-10-27-python-vision-performance.md
- 2026-10-26-convergence-execution-ledger.md
- NativeEllipsePreviewTests
- actual_frame
- SmallAspectSparseTests
- EnglishCurrentTests
- PhaseObserverCliTests
- OfflineAnalyzerTests
- convergence-regression.py
- map-aspect-adapter.test.cjs
- observer-adapter.test.cjs
- 2026-10-27-development-40-60.md
- 2026-10-27-case40-high-handoff.md
- 2026-10-27-development40-60-execution-ledger.md
- 2026-10-27-python-vision-execution-ledger.md
- higher-floor-replay.test.cjs
- PreviewRegistrationTests
- Bounded Coverage Implementation Plan
- NominalQuantizationTests
- SameFramePipelineTests
- CRK Helper V2：60組離線閉環測試報告
- BoundedCoverageTests
- 2026-10-28-bounded-coverage-design.md

## God Nodes (most connected - your core abstractions)
1. `BoundedOCRRuntime` - 57 edges
2. `adaptMap()` - 35 edges
3. `recover_map_aspect()` - 35 edges
4. `loadReplayFrames()` - 34 edges
5. `BoundedOCRRuntime` - 34 edges
6. `adaptPreview()` - 30 edges
7. `ProgressRuntime` - 30 edges
8. `inspect_preview_identity()` - 29 edges
9. `P4-C 開發進度：尚未正式驗收` - 28 edges
10. `FrameIntermediates` - 27 edges

## Surprising Connections (you probably didn't know these)
- `為什麼不直接改用參考內框校準` --references--> `aspectGeometry()`  [INFERRED]
  docs/reports/2026-10-27-case41-candidate-resampling-analysis.md → lib/observer-adapter.cjs
- `2. 已保留的最小優化` --references--> `FrameIntermediates`  [INFERRED]
  docs/validation/2026-10-27-python-vision-performance.md → ml/frame_intermediates.py
- `不同部分` --references--> `heal_node_candidates()`  [INFERRED]
  docs/reports/2026-10-27-case41-candidate-resampling-analysis.md → ml/heal_node_candidates.py
- `3.6 恢復篩選與安全拒絕是後果` --references--> `_supplement_orange_candidates()`  [INFERRED]
  docs/reports/2026-10-27-case41-candidate-resampling-analysis.md → ml/map_aspect.py
- `已定位的資料流` --references--> `_supplement_orange_candidates()`  [INFERRED]
  docs/validation/2026-10-27-case41-high-handoff.md → ml/map_aspect.py

## Import Cycles
- None detected.

## Communities (97 total, 36 thin omitted)

### Community 1 - "preview-session.test.cjs"
Cohesion: 0.13
Nodes (19): clone(), frame(), map(), preview(), assert, {map,intent,clone}, {selectNode,validateProof}, {test} (+11 more)

### Community 2 - "BoundedOCRRuntime"
Cohesion: 0.15
Nodes (7): BoundedOCRRuntime, _context_claim_agrees(), _context_reading_key(), _MeasuredPreprocess, normalize_evidence(), _remaining_timer_locators(), OrdinaryWhitespaceTests

### Community 3 - "inspect_preview_identity"
Cohesion: 0.14
Nodes (5): AspectPreviewTests, EnglishPreviewTests, NativePreviewSizeTests, inspect_preview_identity(), PreviewIdentityTests

### Community 4 - "recover_map_aspect"
Cohesion: 0.13
Nodes (3): AspectEndpointProjectionTests, estimate_pixel_aspect(), MapAspectTests

### Community 5 - "CRK Helper V2：失敗導向重構設計與分階段驗收"
Cohesion: 0.08
Nodes (25): 10. 本次有條件批准與執行順序, 11. P0–P3 核心實作與審閱修訂（2026-10-24）, 1. 唯一目標與完成邊界, 2.1 已確認的問題, 2.2 尚未證實、需要測試的風險, 2.3 可重用與暫緩處理, 2. 根本原因與證據等級, 3. 方案比較與建議 (+17 more)

### Community 7 - "CRK Helper V2 — 閉環測試階段性技術審查報告"
Cohesion: 0.05
Nodes (39): 0. 審查方法與證據解讀, 1.1 目前完成與未完成, 1.2 「60組」的正確分母, 1.3 P0～P5狀態, 1.4 G0～G5狀態：維持原標準, 2.1 表格讀法與逐組證據, 2.2 失敗原因與已記錄修正, 2.3 首次結果、修正負擔與回歸趨勢 (+31 more)

### Community 8 - "evidence.test.cjs"
Cohesion: 0.10
Nodes (22): compareSnapshot(), crypto, digest(), fs, locate(), milestoneResult(), path, snapshotFiles() (+14 more)

### Community 9 - "CRK Helper V2 P4-C 正式集合與隨機壓力測試"
Cohesion: 0.07
Nodes (27): Actual native map-title OCR truncation repair brief, Actual watermarked Chinese title context repair brief, English source development repair brief (2026-10-25), G0多來源影格與快取隔離 brief, Native coordinate convention regression, Sparse native map geometry failure brief, Task2/3 next isolated defect: offscreen-gate ordinary preview scope, Task2/4 actual anisotropic zero-candidate failure brief (+19 more)

### Community 10 - "map_aspect.py"
Cohesion: 0.05
Nodes (60): 3.2 比例量測成功，但有數值偏差；座標投影契約沒有算錯, 座標, completed_geometry(), wrapped(), recover_completed_extents(), node_geometry(), completed_node_candidates(), inspect_in_progress() (+52 more)

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

### Community 16 - "accept-replay.cjs"
Cohesion: 0.06
Nodes (41): writeCaseArtifacts(), runReplay(), captureCodeVersion(), walk(), crypto, {execFileSync}, fs, path (+33 more)

### Community 17 - "convergence-regression.py"
Cohesion: 0.14
Nodes (3): OperationProfile, measured(), OperationProfileTests

### Community 18 - "inspect_map_actions"
Cohesion: 0.20
Nodes (4): CurrentPositionEvidenceTests, inspect_map_actions(), PixelMapActionTests, ReferenceCurrentRingTests

### Community 19 - "第41組候選生成與重採樣穩定性分析"
Cohesion: 0.08
Nodes (25): 3.1 像素內容並未讓下方節點消失, 3.3 模板尺寸取整是可直接重現的斷點, 3.4 影像與模板集合的交叉實驗, 3.5 Canny不是把整張圖的邊緣都弄丟；NMS也不是主要肇因, 3.6 恢復篩選與安全拒絕是後果, 一、結論與建議, 七、推薦M1的最小修改設計（未批准、未實作）, 三、第41組的具體原因 (+17 more)

### Community 20 - "geometry-contract.test.cjs"
Cohesion: 0.11
Nodes (28): analysisRaster(), {isDeepStrictEqual:eq}, nativeGeometryEvidence(), resizeBox(), resizePoint(), size(), validateGeometryCertificate(), adaptPreviewContext() (+20 more)

### Community 21 - "geometry.test.cjs"
Cohesion: 0.29
Nodes (11): analysisToClient(), assertCurrentGeometry(), clientToAnalysis(), clientToScreen(), createGeometry(), finiteArray(), point(), assert (+3 more)

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
Cohesion: 0.13
Nodes (5): BoundedOCRRuntime, BoundedOCRTests, normalize_evidence(), PreviewContextAspectTests, PreviewTimerTests

### Community 33 - "pending-preview.test.cjs"
Cohesion: 0.12
Nodes (16): verifyPreview(), {adaptMap,readDirectMapAnchor}, assert, {execFileSync}, fixture(), fs, {loadReplayFrames}, {PreviewSession} (+8 more)

### Community 34 - "ProgressRuntime"
Cohesion: 0.13
Nodes (9): EnglishSceneRuntime, semantic_state(), EnglishSceneRuntime, EnglishSceneTests, ProgressRuntime, RemainingTimeLocatorTests, SplitDayClockTests, SplitRemainingClockTests (+1 more)

### Community 35 - "ref_node_assert"
Cohesion: 0.05
Nodes (37): {adaptMap}, assert, {execFileSync}, fixture(), fs, {loadReplayFrames}, {test}, assert (+29 more)

### Community 36 - "Python視覺效能優化與泛化驗證（2026-10-27）"
Cohesion: 0.18
Nodes (10): 1. 操作層量測，而非依名稱判斷, 2. 已保留的最小優化, 3. 有量測但未採用的方案, 4. S3缺陷仍OPEN, 5. 獨立審查與當版回歸, 6. 完整成對效能測量, 7. 未達標原因與下一輪有限方案, 8. 執行取捨、審查界限與未完成事項 (+2 more)

### Community 38 - "recover_map_geometry"
Cohesion: 0.36
Nodes (3): recover_map_geometry(), SparseMapGeometryTests, WatermarkedCheckTests

### Community 39 - "ref_node_fs"
Cohesion: 0.07
Nodes (25): crypto, fs, path, {spawnSync}, {adaptMap,adaptPreview}, crypto, fs, path (+17 more)

### Community 40 - "transaction-map-anchor.test.cjs"
Cohesion: 0.18
Nodes (11): {adaptMap,adaptPreview,readDirectMapAnchor}, assert, fixture(), fs, {loadReplayFrames}, path, replay(), {runReplay} (+3 more)

### Community 41 - "loadReplayFrames"
Cohesion: 0.05
Nodes (40): buildReplayGate(), crypto, fs, invalid(), loadReplayFrames(), sha(), {adaptPreview}, assert (+32 more)

### Community 42 - "hashlib"
Cohesion: 0.14
Nodes (11): _box(), freeze_corpus(), main(), validate_corpus(), extract_case(), main(), main(), scale_png() (+3 more)

### Community 43 - "CRK Helper V2 P4-C 正式集合與隨機壓力測試"
Cohesion: 0.13
Nodes (15): Actual case14 original text and near-native recovery brief, Actual glowing-edge candidate and precision repair brief, Actual second-floor case16 pixel evidence brief, CRK Helper V2 P4-C 正式集合與隨機壓力測試, Current evidence, G0追加實作 brief：實際OCR資產與runtime可追溯, G2評分器校正與開發報告, P3回放分支補強：沒有有效點擊不得讀取人工後續 (+7 more)

### Community 44 - "observe-image.cjs"
Cohesion: 0.15
Nodes (12): {adaptMap,adaptPreview}, bundle, crypto, frame, fs, id, packet, path (+4 more)

### Community 45 - "observer-adapter.cjs"
Cohesion: 0.17
Nodes (26): boxValid(), adaptMap(), adaptPreview(), aspectGeometry(), bind(), completedGeometry(), crypto, directMapAnchors (+18 more)

### Community 46 - "ProgressRuntime"
Cohesion: 0.17
Nodes (5): parse_progress(), ProgressRuntime, EnglishProgressTests, MapTitleRereadTests, ProgressEvidenceTests

### Community 48 - "CRK Helper V2 座標與預覽證據收斂 Implementation Plan"
Cohesion: 0.20
Nodes (9): CRK Helper V2 座標與預覽證據收斂 Implementation Plan, Global Constraints, Review Focus, Task 1：根因重現、契約與聚焦測試, Task 2：最小幾何契約, Task 3：預覽控制／身份與等待能力分離, Task 4：同版本回歸、稽核與停止交付, 執行紀錄 (+1 more)

### Community 49 - "analyze_cases.py"
Cohesion: 0.16
Nodes (7): V2 座標與點後等待契約 v1, 回歸版本, 預覽控制、身份與操作權限, case_source_sha(), effective_observation_state(), main(), source_frame_id()

### Community 51 - "preview-panel-scope.test.cjs"
Cohesion: 0.22
Nodes (7): {adaptPreview}, assert, currentPackets, fixture(), fs, {loadReplayFrames}, {test}

### Community 54 - "preview-session.cjs"
Cohesion: 0.25
Nodes (7): readDirectMapAnchor(), active, { createGeometry, clientToScreen }, crypto, { readDirectMapAnchor }, { validateProof, validateFrame }, { verifyPreview }

### Community 55 - "random_replay_plan.py"
Cohesion: 0.15
Nodes (11): _decode(), recover_preview_anchor(), sample_layout(), transform_box(), transform_png(), _box(), _frame(), plan_sequences() (+3 more)

### Community 56 - "M1有限實作與離線驗證計畫"
Cohesion: 0.25
Nodes (7): Interfaces / review focus, M1有限實作與離線驗證計畫, Task 1：RED、增量補強、聚焦GREEN, Task 2：凍結候選版本，第41完整新鮮, Task 3：依序當版回歸, Task 4：效能與證據, Task 5：42～60與報告

### Community 57 - "Python vision performance and generalization Implementation Plan"
Cohesion: 0.25
Nodes (7): Global Constraints, Python vision performance and generalization Implementation Plan, Review Focus, Task1: reproducible operation-level profiling, Task2: measured minimum optimization round, Task3: track S3 local coverage defects, Task4: correctness + comparable performance and gate

### Community 58 - "V2 座標／預覽收斂驗證紀錄"
Cohesion: 0.17
Nodes (11): V2 座標／預覽收斂驗證紀錄, 原始1551影格與七張歷史變動的當版核對, 固定倍率工具相容性修正, 基準與範圍, 已發現並處理的迴歸, 最終工具版本與驗收邊界, 最終階段結果, 本輪明確取捨與剩餘限制 (+3 more)

### Community 59 - "GateSupportedAspectTests"
Cohesion: 0.21
Nodes (3): CompletedNodeCandidateTests, GateSupportedAspectTests, recover_map_aspect()

### Community 60 - "S3ScrollCoverageDefects"
Cohesion: 0.20
Nodes (4): checked_coverage(), GroundTruthFixtureContractTests, iou(), S3ScrollCoverageDefects

### Community 61 - "json"
Cohesion: 0.18
Nodes (9): capture_runtime_evidence(), main(), percentiles(), control_case(), control_request(), main(), check(), unchanged() (+1 more)

### Community 62 - "node-selector.cjs"
Cohesion: 0.36
Nodes (9): fail(), freeze(), iou(), issued, numbers(), selectNode(), validateFrame(), validateProof() (+1 more)

### Community 63 - "replay-evaluator.test.cjs"
Cohesion: 0.29
Nodes (8): evaluateDevelopmentReplay(), evaluateReplay(), gradeReplay(), intent, assert, {map,preview,intent}, {runReplay}, {test}

### Community 66 - "RandomClientTransformTests"
Cohesion: 0.33
Nodes (3): inverse_point(), RandomClientTransformTests, sample_layout()

### Community 67 - "CRK Helper V2：60組開發測試階段報告（coverage當版回歸未通過）"
Cohesion: 0.08
Nodes (22): 60組當版狀態, CRK Helper V2：60組開發測試階段報告（coverage當版回歸未通過）, 剩餘缺陷與未完成事項, 回歸、稽核與效能, 已執行結果與首筆紀錄, 本輪修改及新增風險, Phase observation implementation plan, Stop boundaries (+14 more)

### Community 70 - "review-regressions.test.cjs"
Cohesion: 0.29
Nodes (6): assert, {map,intent,preview}, {PreviewSession}, {selectNode}, setup(), {test}

### Community 73 - "node_candidates"
Cohesion: 0.43
Nodes (3): ExactCandidateSearchTests, node_candidates(), SparsePeerBootstrapTests

### Community 84 - "convergence-regression.py"
Cohesion: 0.24
Nodes (7): check_snapshot(), code_snapshot(), dependency_snapshot(), main(), merge_cases(), replay_command(), sha()

### Community 85 - "map-aspect-adapter.test.cjs"
Cohesion: 0.20
Nodes (9): {adaptMap,adaptPreview}, assert, fixture(), fs, {loadReplayFrames}, observe(), path, {selectNode} (+1 more)

### Community 86 - "observer-adapter.test.cjs"
Cohesion: 0.20
Nodes (6): {adaptMap,adaptPreview}, assert, crypto, fs, path, {test}

### Community 92 - "higher-floor-replay.test.cjs"
Cohesion: 0.11
Nodes (15): {performance}, {PreviewSession}, {selectNode}, {adaptMap,adaptPreview}, fs, {loadReplayFrames,buildReplayGate}, {performance}, {runReplay} (+7 more)

### Community 93 - "PreviewRegistrationTests"
Cohesion: 0.24
Nodes (4): PreviewAnchorTracker, PreviewAnchorTracker, PreviewRegistrationTests, recover_preview_anchor()

### Community 94 - "Bounded Coverage Implementation Plan"
Cohesion: 0.25
Nodes (7): Bounded Coverage Implementation Plan, Global Constraints, One review fix pass, Review Focus, Task1: RED/GREEN bounded coverage, Task2: current fresh qualification, Task3: finish remaining frozen offline corpus

### Community 97 - "CRK Helper V2：60組離線閉環測試報告"
Cohesion: 0.20
Nodes (8): 2aeae97 當版完整結果, 第40組修復進行狀態（接續High評估）, High接續時的界線, 停止狀態, 已完成的當版驗證, 已定位的資料流, 第41組：候選恢復阻塞與High接續資料, 第41組完整失敗證據

## Knowledge Gaps
- **36 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `aspectGeometry()` connect `observer-adapter.cjs` to `第41組候選生成與重採樣穩定性分析`, `geometry-contract.test.cjs`?**
  _High betweenness centrality (0.372) - this node is a cross-community bridge._
- **Should `preview-session.test.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.12648221343873517 - nodes in this community are weakly interconnected._
- **Should `BoundedOCRRuntime` be split into smaller, more focused modules?**
  _Cohesion score 0.1471861471861472 - nodes in this community are weakly interconnected._
- **Should `inspect_preview_identity` be split into smaller, more focused modules?**
  _Cohesion score 0.13675213675213677 - nodes in this community are weakly interconnected._
- **Should `recover_map_aspect` be split into smaller, more focused modules?**
  _Cohesion score 0.13405797101449277 - nodes in this community are weakly interconnected._
- **Should `CRK Helper V2：失敗導向重構設計與分階段驗收` be split into smaller, more focused modules?**
  _Cohesion score 0.08 - nodes in this community are weakly interconnected._
- **Should `pathlib` be split into smaller, more focused modules?**
  _Cohesion score 0.12462189957652753 - nodes in this community are weakly interconnected._