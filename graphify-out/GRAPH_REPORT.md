# Graph Report - CRK-Helper-V2  (2026-11-02)

## Corpus Check
- 225 files · ~86,614 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 2)

## Summary
- 1541 nodes · 3551 edges · 104 communities (63 shown, 41 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 376 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `24bfb2a5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- preview-session.test.cjs
- BoundedOCRRuntime
- inspect_preview_identity
- recover_map_aspect
- CRK Helper V2：失敗導向重構設計與分階段驗收
- pathlib
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
- ref_node_fs
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
- math
- M1有限實作與離線驗證計畫
- Python vision performance and generalization Implementation Plan
- V2 座標／預覽收斂驗證紀錄
- GateSupportedAspectTests
- S3ScrollCoverageDefects
- json
- node-selector.cjs
- numpy
- PhaseMapPipelineTests
- resize_box
- CRK Helper V2：60組開發測試階段報告（coverage當版回歸未通過）
- PreviewPanelScopeTests
- StageTiming
- _supplement_groups
- CacheBackendIdentityTests
- LegacyCurrentPhaseTests
- node_candidates
- specs/2026-10-27-python-vision-performance.md
- 2026-10-26-convergence-execution-ledger.md
- NativeEllipsePreviewTests
- re
- SmallAspectSparseTests
- reference_line_geometry.py
- EnglishCurrentTests
- PhaseObserverCliTests
- OfflineAnalyzerTests
- aspect-endpoints.test.cjs
- native-ellipse-preview.test.cjs
- small-aspect-sparse.test.cjs
- PhaseRouteParityTests
- V2 座標與點後等待契約 v1
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
- MapTitleRereadTests
- CompletedNodeCandidateTests
- test_fixed_scale.py
- 2026-10-28-bounded-coverage-design.md
- ReferenceCurrentRingTests

## God Nodes (most connected - your core abstractions)
1. `BoundedOCRRuntime` - 57 edges
2. `adaptMap()` - 35 edges
3. `recover_map_aspect()` - 35 edges
4. `loadReplayFrames()` - 34 edges
5. `BoundedOCRRuntime` - 34 edges
6. `adaptPreview()` - 30 edges
7. `ProgressRuntime` - 30 edges
8. `FrameIntermediates` - 29 edges
9. `inspect_preview_identity()` - 29 edges
10. `P4-C 開發進度：尚未正式驗收` - 28 edges

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

## Communities (104 total, 41 thin omitted)

### Community 1 - "preview-session.test.cjs"
Cohesion: 0.10
Nodes (25): clone(), frame(), intent, map(), preview(), assert, {map,intent,clone}, {selectNode,validateProof} (+17 more)

### Community 2 - "BoundedOCRRuntime"
Cohesion: 0.15
Nodes (7): BoundedOCRRuntime, _context_claim_agrees(), _context_reading_key(), _MeasuredPreprocess, normalize_evidence(), _remaining_timer_locators(), OrdinaryWhitespaceTests

### Community 3 - "inspect_preview_identity"
Cohesion: 0.14
Nodes (5): AspectPreviewTests, EnglishPreviewTests, NativePreviewSizeTests, inspect_preview_identity(), PreviewIdentityTests

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
Cohesion: 0.13
Nodes (17): coverage_node_candidates(), node_candidates(), raster_round(), _cyan_component(), estimate_pixel_aspect(), _gate_pixel_geometry(), _gate_supported_aspect_candidates(), _qualified_aspect_groups() (+9 more)

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
Nodes (43): crypto, fs, path, {spawnSync}, writeCaseArtifacts(), evaluateDevelopmentReplay(), evaluateReplay(), gradeReplay() (+35 more)

### Community 17 - "convergence-regression.py"
Cohesion: 0.14
Nodes (3): OperationProfile, measured(), OperationProfileTests

### Community 18 - "inspect_map_actions"
Cohesion: 0.26
Nodes (3): CurrentPositionEvidenceTests, inspect_map_actions(), PixelMapActionTests

### Community 19 - "第41組候選生成與重採樣穩定性分析"
Cohesion: 0.07
Nodes (26): 3.1 像素內容並未讓下方節點消失, 3.2 比例量測成功，但有數值偏差；座標投影契約沒有算錯, 3.3 模板尺寸取整是可直接重現的斷點, 3.4 影像與模板集合的交叉實驗, 3.5 Canny不是把整張圖的邊緣都弄丟；NMS也不是主要肇因, 3.6 恢復篩選與安全拒絕是後果, 一、結論與建議, 七、推薦M1的最小修改設計（未批准、未實作） (+18 more)

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

### Community 35 - "ref_node_fs"
Cohesion: 0.08
Nodes (22): crypto, {execFileSync}, fs, path, assert, fs, path, {spawnSync} (+14 more)

### Community 36 - "Python視覺效能優化與泛化驗證（2026-10-27）"
Cohesion: 0.18
Nodes (10): 1. 操作層量測，而非依名稱判斷, 2. 已保留的最小優化, 3. 有量測但未採用的方案, 4. S3缺陷仍OPEN, 5. 獨立審查與當版回歸, 6. 完整成對效能測量, 7. 未達標原因與下一輪有限方案, 8. 執行取捨、審查界限與未完成事項 (+2 more)

### Community 38 - "recover_map_geometry"
Cohesion: 0.36
Nodes (3): recover_map_geometry(), SparseMapGeometryTests, WatermarkedCheckTests

### Community 39 - "ref_node_fs"
Cohesion: 0.06
Nodes (27): assert, fs, os, path, {test}, {writeCaseArtifacts}, {adaptMap,adaptPreview}, assert (+19 more)

### Community 40 - "transaction-map-anchor.test.cjs"
Cohesion: 0.18
Nodes (12): {adaptMap,adaptPreview,readDirectMapAnchor}, assert, fixture(), fs, {loadReplayFrames}, observation(), path, replay() (+4 more)

### Community 41 - "loadReplayFrames"
Cohesion: 0.06
Nodes (35): buildReplayGate(), crypto, fs, invalid(), loadReplayFrames(), sha(), {adaptPreview}, assert (+27 more)

### Community 42 - "hashlib"
Cohesion: 0.11
Nodes (14): extract_case(), main(), main(), scale_png(), main(), percentiles(), check_snapshot(), code_snapshot() (+6 more)

### Community 43 - "CRK Helper V2 P4-C 正式集合與隨機壓力測試"
Cohesion: 0.13
Nodes (15): Actual case14 original text and near-native recovery brief, Actual glowing-edge candidate and precision repair brief, Actual second-floor case16 pixel evidence brief, CRK Helper V2 P4-C 正式集合與隨機壓力測試, Current evidence, G0追加實作 brief：實際OCR資產與runtime可追溯, G2評分器校正與開發報告, P3回放分支補強：沒有有效點擊不得讀取人工後續 (+7 more)

### Community 44 - "observe-image.cjs"
Cohesion: 0.10
Nodes (18): {adaptMap,adaptPreview}, bundle, crypto, frame, fs, id, packet, path (+10 more)

### Community 45 - "observer-adapter.cjs"
Cohesion: 0.25
Nodes (16): boxValid(), aspectGeometry(), completedGeometry(), crypto, directMapAnchors, healGeometry(), {isDeepStrictEqual}, mapActions() (+8 more)

### Community 46 - "ProgressRuntime"
Cohesion: 0.23
Nodes (4): parse_progress(), ProgressRuntime, EnglishProgressTests, ProgressEvidenceTests

### Community 48 - "CRK Helper V2 座標與預覽證據收斂 Implementation Plan"
Cohesion: 0.20
Nodes (9): CRK Helper V2 座標與預覽證據收斂 Implementation Plan, Global Constraints, Review Focus, Task 1：根因重現、契約與聚焦測試, Task 2：最小幾何契約, Task 3：預覽控制／身份與等待能力分離, Task 4：同版本回歸、稽核與停止交付, 執行紀錄 (+1 more)

### Community 49 - "analyze_cases.py"
Cohesion: 0.20
Nodes (8): case_source_sha(), effective_observation_state(), main(), source_frame_id(), _orange_node_pixel_geometry(), inspect_preview_identity(), outline_size_hypotheses(), capture_runtime_evidence()

### Community 51 - "preview-panel-scope.test.cjs"
Cohesion: 0.22
Nodes (7): {adaptPreview}, assert, currentPackets, fixture(), fs, {loadReplayFrames}, {test}

### Community 54 - "preview-session.cjs"
Cohesion: 0.25
Nodes (7): readDirectMapAnchor(), active, { createGeometry, clientToScreen }, crypto, { readDirectMapAnchor }, { validateProof, validateFrame }, { verifyPreview }

### Community 55 - "math"
Cohesion: 0.12
Nodes (16): _box(), freeze_corpus(), main(), validate_corpus(), inverse_point(), sample_layout(), transform_box(), transform_png() (+8 more)

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
Cohesion: 0.18
Nodes (3): AspectEndpointProjectionTests, GateSupportedAspectTests, estimate_pixel_aspect()

### Community 60 - "S3ScrollCoverageDefects"
Cohesion: 0.20
Nodes (4): checked_coverage(), GroundTruthFixtureContractTests, iou(), S3ScrollCoverageDefects

### Community 61 - "json"
Cohesion: 0.21
Nodes (6): control_case(), control_request(), main(), check(), unchanged(), require_phase_backend()

### Community 62 - "node-selector.cjs"
Cohesion: 0.20
Nodes (14): fail(), freeze(), iou(), issued, numbers(), selectNode(), validateFrame(), validateProof() (+6 more)

### Community 63 - "numpy"
Cohesion: 0.23
Nodes (11): completed_node_candidates(), inspect_in_progress(), _reference_ring(), heal_node_candidates(), _check_masks(), _green(), inspect_map_actions(), _neutral_overlay_check() (+3 more)

### Community 66 - "resize_box"
Cohesion: 0.20
Nodes (9): recover_completed_extents(), node_geometry(), analysis_raster(), geometry_certificate(), resize_box(), resize_point(), _size(), _ordinary_crop_scale() (+1 more)

### Community 67 - "CRK Helper V2：60組開發測試階段報告（coverage當版回歸未通過）"
Cohesion: 0.07
Nodes (24): 60 組明細, CRK Helper V2：60 組開發閉環測試進度, 未完成與已知限制, 當版證據與歷史區分, 2026-11-02 補充：幾何路由接受邊界仍須隔離, Phase observation implementation plan, Stop boundaries, Task1: RED -> GREEN scoped backend and incremental raw scan (+16 more)

### Community 70 - "_supplement_groups"
Cohesion: 0.32
Nodes (6): _CandidateScan, _coverage_groups(), _groups(), _match_group(), _nominal_groups(), _supplement_groups()

### Community 73 - "node_candidates"
Cohesion: 0.43
Nodes (3): ExactCandidateSearchTests, node_candidates(), SparsePeerBootstrapTests

### Community 77 - "re"
Cohesion: 0.24
Nodes (8): freeze_prefixes(), _sha(), _box(), _english_ordinary_crop(), inspect_preview_context(), _timer_original_crop(), actual_frame(), PreviewContextTests

### Community 79 - "reference_line_geometry.py"
Cohesion: 0.28
Nodes (6): completed_geometry(), wrapped(), reference_geometry(), wrapped(), measure(), reference_line()

### Community 83 - "aspect-endpoints.test.cjs"
Cohesion: 0.25
Nodes (7): {adaptMap}, assert, {execFileSync}, fixture(), fs, {loadReplayFrames}, {test}

### Community 84 - "native-ellipse-preview.test.cjs"
Cohesion: 0.25
Nodes (7): {adaptPreview}, assert, {execFileSync}, fixture(), fs, {loadReplayFrames}, {test}

### Community 85 - "small-aspect-sparse.test.cjs"
Cohesion: 0.25
Nodes (7): {adaptMap}, assert, {execFileSync}, fixture(), fs, {loadReplayFrames}, {test}

### Community 87 - "V2 座標與點後等待契約 v1"
Cohesion: 0.40
Nodes (4): V2 座標與點後等待契約 v1, 回歸版本, 座標, 預覽控制、身份與操作權限

### Community 92 - "higher-floor-replay.test.cjs"
Cohesion: 0.08
Nodes (31): adaptMap(), adaptPreview(), bind(), markDirectMapAnchor(), previewAnchor(), {performance}, {PreviewSession}, runReplay() (+23 more)

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
- **41 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `aspectGeometry()` connect `observer-adapter.cjs` to `第41組候選生成與重採樣穩定性分析`, `higher-floor-replay.test.cjs`, `geometry-contract.test.cjs`?**
  _High betweenness centrality (0.363) - this node is a cross-community bridge._
- **Should `preview-session.test.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.10344827586206896 - nodes in this community are weakly interconnected._
- **Should `BoundedOCRRuntime` be split into smaller, more focused modules?**
  _Cohesion score 0.1471861471861472 - nodes in this community are weakly interconnected._
- **Should `inspect_preview_identity` be split into smaller, more focused modules?**
  _Cohesion score 0.13675213675213677 - nodes in this community are weakly interconnected._
- **Should `CRK Helper V2：失敗導向重構設計與分階段驗收` be split into smaller, more focused modules?**
  _Cohesion score 0.08 - nodes in this community are weakly interconnected._
- **Should `pathlib` be split into smaller, more focused modules?**
  _Cohesion score 0.13734658094681473 - nodes in this community are weakly interconnected._
- **Should `CRK Helper V2 — 閉環測試階段性技術審查報告` be split into smaller, more focused modules?**
  _Cohesion score 0.05128205128205128 - nodes in this community are weakly interconnected._