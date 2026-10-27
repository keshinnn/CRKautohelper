# Graph Report - CRK-Helper-V2  (2026-10-27)

## Corpus Check
- 206 files · ~81,291 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 2)

## Summary
- 1369 nodes · 3225 edges · 98 communities (65 shown, 33 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 333 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fb204757`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- preview-registration.test.cjs
- BoundedOCRRuntime
- inspect_preview_identity
- MapAspectTests
- CRK Helper V2：失敗導向重構設計與分階段驗收
- hashlib
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
- convergence-regression.py
- inspect_map_actions
- replay-runner.cjs
- geometry-contract.test.cjs
- geometry.test.cjs
- resize_box
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
- audit-native-convergence.cjs
- ref_node_assert
- PrefixFreezerTests
- map-aspect-adapter.test.cjs
- numpy
- transaction-map-anchor.test.cjs
- loadReplayFrames
- OfflineAnalyzerTests
- PreviewRegistrationTests
- observer-adapter.cjs
- ProgressRuntime
- PreviewSession
- CRK Helper V2 座標與預覽證據收斂 Implementation Plan
- re
- FrameIntermediatesTests
- analyze_cases.py
- ContextLineRemeasurementTests
- ConvergenceRunnerTests
- higher-floor-replay.test.cjs
- random_replay_plan.py
- convergence-regression.py
- Python vision performance and generalization Implementation Plan
- V2 座標／預覽收斂驗證紀錄
- GateSupportedAspectTests
- S3ScrollCoverageDefects
- Python視覺效能優化與泛化驗證（2026-10-27）
- node-selector.cjs
- MapTitleRereadTests
- observer-adapter.test.cjs
- PreviewPanelScopeTests
- actual_frame
- FrameIntermediates
- RandomClientTransformTests
- recover_map_geometry
- preview-session.test.cjs
- preview-panel-scope.test.cjs
- CRK Helper V2：60組離線閉環階段報告（第40組停止，待High評估）
- ordinary-aspect-context.test.cjs
- specs/2026-10-27-python-vision-performance.md
- 2026-10-26-convergence-execution-ledger.md
- NativeEllipsePreviewTests
- StageTiming
- aspect-endpoints.test.cjs
- s3-scroll-refusal.test.cjs
- node_candidates
- SmallAspectSparseTests
- review-regressions.test.cjs
- 四、回歸測試與安全性
- CompletedNodeCandidateTests
- EnglishCurrentTests
- ReferenceCurrentRingTests
- 七、最終結論與下一階段建議
- 2026-10-27-development-40-60.md
- 2026-10-27-case40-high-handoff.md
- 2026-10-27-development40-60-execution-ledger.md
- 2026-10-27-python-vision-execution-ledger.md
- 一、開發進度總覽
- 三、視覺辨識與跨尺寸穩定性
- 二、60組測試詳細分析
- 六、最近約兩天的開發效率
- SameFramePipelineTests
- 2026-10-27-case40-resume-status.md

## God Nodes (most connected - your core abstractions)
1. `BoundedOCRRuntime` - 57 edges
2. `adaptMap()` - 36 edges
3. `recover_map_aspect()` - 35 edges
4. `loadReplayFrames()` - 34 edges
5. `BoundedOCRRuntime` - 34 edges
6. `adaptPreview()` - 30 edges
7. `ProgressRuntime` - 30 edges
8. `inspect_preview_identity()` - 29 edges
9. `P4-C 開發進度：尚未正式驗收` - 28 edges
10. `G0多來源影格與快取隔離 brief` - 27 edges

## Surprising Connections (you probably didn't know these)
- `第40組：實際失敗與根因` --references--> `adaptMap()`  [INFERRED]
  docs/reports/crk-helper-v2-development-60-report.md → lib/observer-adapter.cjs
- `2.1 已確認的問題` --references--> `inspect_map()`  [INFERRED]
  docs/superpowers/specs/2026-10-24-crk-helper-v2-design.md → ml/map_observer.py
- `預覽控制、身份與操作權限` --references--> `effective_observation_state()`  [INFERRED]
  docs/superpowers/specs/2026-10-26-geometry-preview-contract.md → ml/analyze_cases.py
- `2. 已保留的最小優化` --references--> `FrameIntermediates`  [INFERRED]
  docs/validation/2026-10-27-python-vision-performance.md → ml/frame_intermediates.py
- `座標` --references--> `analysis_raster()`  [INFERRED]
  docs/superpowers/specs/2026-10-26-geometry-preview-contract.md → ml/geometry_contract.py

## Import Cycles
- None detected.

## Communities (98 total, 33 thin omitted)

### Community 1 - "preview-registration.test.cjs"
Cohesion: 0.13
Nodes (19): frame(), intent, map(), preview(), assert, {map,intent,preview}, {selectNode}, {test} (+11 more)

### Community 2 - "BoundedOCRRuntime"
Cohesion: 0.15
Nodes (7): BoundedOCRRuntime, _context_claim_agrees(), _context_reading_key(), _MeasuredPreprocess, normalize_evidence(), _remaining_timer_locators(), OrdinaryWhitespaceTests

### Community 3 - "inspect_preview_identity"
Cohesion: 0.14
Nodes (5): AspectPreviewTests, EnglishPreviewTests, NativePreviewSizeTests, inspect_preview_identity(), PreviewIdentityTests

### Community 5 - "CRK Helper V2：失敗導向重構設計與分階段驗收"
Cohesion: 0.08
Nodes (25): 10. 本次有條件批准與執行順序, 11. P0–P3 核心實作與審閱修訂（2026-10-24）, 1. 唯一目標與完成邊界, 2.1 已確認的問題, 2.2 尚未證實、需要測試的風險, 2.3 可重用與暫緩處理, 2. 根本原因與證據等級, 3. 方案比較與建議 (+17 more)

### Community 6 - "hashlib"
Cohesion: 0.08
Nodes (18): _box(), freeze_corpus(), main(), validate_corpus(), extract_case(), main(), main(), scale_png() (+10 more)

### Community 7 - "CRK Helper V2 — 閉環測試階段性技術審查報告"
Cohesion: 0.22
Nodes (9): 0. 審查方法與證據解讀, 5.1 五個核心責任, 5.2 隱藏耦合、狀態與重複實作, A.1 四部來源影片, A.2 指紋登錄, A.3 尚不能確認的事項, CRK Helper V2 — 閉環測試階段性技術審查報告, 五、程式架構與技術債 (+1 more)

### Community 8 - "evidence.test.cjs"
Cohesion: 0.10
Nodes (22): compareSnapshot(), crypto, digest(), fs, locate(), milestoneResult(), path, snapshotFiles() (+14 more)

### Community 9 - "CRK Helper V2 P4-C 正式集合與隨機壓力測試"
Cohesion: 0.05
Nodes (42): Actual case14 original text and near-native recovery brief, Actual glowing-edge candidate and precision repair brief, Actual native map-title OCR truncation repair brief, Actual second-floor case16 pixel evidence brief, Actual watermarked Chinese title context repair brief, CRK Helper V2 P4-C 正式集合與隨機壓力測試, Current evidence, English source development repair brief (2026-10-25) (+34 more)

### Community 10 - "observe-image.cjs"
Cohesion: 0.15
Nodes (12): {adaptMap,adaptPreview}, bundle, crypto, frame, fs, id, packet, path (+4 more)

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
Cohesion: 0.07
Nodes (45): writeCaseArtifacts(), adaptMap(), adaptPreview(), bind(), markDirectMapAnchor(), evaluateDevelopmentReplay(), evaluateReplay(), gradeReplay() (+37 more)

### Community 17 - "convergence-regression.py"
Cohesion: 0.14
Nodes (3): OperationProfile, measured(), OperationProfileTests

### Community 18 - "inspect_map_actions"
Cohesion: 0.20
Nodes (3): CurrentPositionEvidenceTests, inspect_map_actions(), PixelMapActionTests

### Community 19 - "replay-runner.cjs"
Cohesion: 0.40
Nodes (3): {performance}, {PreviewSession}, {selectNode}

### Community 20 - "geometry-contract.test.cjs"
Cohesion: 0.17
Nodes (21): analysisRaster(), {isDeepStrictEqual:eq}, nativeGeometryEvidence(), resizeBox(), resizePoint(), size(), validateGeometryCertificate(), adaptPreviewContext() (+13 more)

### Community 21 - "geometry.test.cjs"
Cohesion: 0.29
Nodes (11): analysisToClient(), assertCurrentGeometry(), clientToAnalysis(), clientToScreen(), createGeometry(), finiteArray(), point(), assert (+3 more)

### Community 22 - "resize_box"
Cohesion: 0.09
Nodes (29): V2 座標與點後等待契約 v1, 回歸版本, 座標, 預覽控制、身份與操作權限, wrapped(), recover_completed_extents(), node_geometry(), analysis_raster() (+21 more)

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
Cohesion: 0.11
Nodes (18): readDirectMapAnchor(), active, { createGeometry, clientToScreen }, crypto, { readDirectMapAnchor }, { validateProof, validateFrame }, { verifyPreview }, verifyPreview() (+10 more)

### Community 34 - "ProgressRuntime"
Cohesion: 0.13
Nodes (9): EnglishSceneRuntime, semantic_state(), EnglishSceneRuntime, EnglishSceneTests, ProgressRuntime, RemainingTimeLocatorTests, SplitDayClockTests, SplitRemainingClockTests (+1 more)

### Community 35 - "audit-native-convergence.cjs"
Cohesion: 0.07
Nodes (28): crypto, fs, path, {spawnSync}, crypto, {execFileSync}, fs, path (+20 more)

### Community 36 - "ref_node_assert"
Cohesion: 0.05
Nodes (35): assert, fs, path, {spawnSync}, {test}, {adaptMap}, assert, {execFileSync} (+27 more)

### Community 38 - "map-aspect-adapter.test.cjs"
Cohesion: 0.20
Nodes (9): {adaptMap,adaptPreview}, assert, fixture(), fs, {loadReplayFrames}, observe(), path, {selectNode} (+1 more)

### Community 39 - "numpy"
Cohesion: 0.13
Nodes (17): completed_geometry(), completed_node_candidates(), inspect_in_progress(), _reference_ring(), _groups(), _match_group(), node_candidates(), heal_node_candidates() (+9 more)

### Community 40 - "transaction-map-anchor.test.cjs"
Cohesion: 0.18
Nodes (12): {adaptMap,adaptPreview,readDirectMapAnchor}, assert, fixture(), fs, {loadReplayFrames}, observation(), path, replay() (+4 more)

### Community 41 - "loadReplayFrames"
Cohesion: 0.06
Nodes (38): buildReplayGate(), crypto, fs, invalid(), loadReplayFrames(), sha(), {adaptMap,adaptPreview}, fs (+30 more)

### Community 43 - "PreviewRegistrationTests"
Cohesion: 0.38
Nodes (3): PreviewAnchorTracker, PreviewRegistrationTests, recover_preview_anchor()

### Community 45 - "observer-adapter.cjs"
Cohesion: 0.23
Nodes (17): boxValid(), aspectGeometry(), completedGeometry(), crypto, directMapAnchors, healGeometry(), {isDeepStrictEqual}, mapActions() (+9 more)

### Community 46 - "ProgressRuntime"
Cohesion: 0.23
Nodes (4): parse_progress(), ProgressRuntime, EnglishProgressTests, ProgressEvidenceTests

### Community 48 - "CRK Helper V2 座標與預覽證據收斂 Implementation Plan"
Cohesion: 0.20
Nodes (9): CRK Helper V2 座標與預覽證據收斂 Implementation Plan, Global Constraints, Review Focus, Task 1：根因重現、契約與聚焦測試, Task 2：最小幾何契約, Task 3：預覽控制／身份與等待能力分離, Task 4：同版本回歸、稽核與停止交付, 執行紀錄 (+1 more)

### Community 49 - "re"
Cohesion: 0.20
Nodes (7): freeze_prefixes(), _sha(), _box(), _english_ordinary_crop(), inspect_preview_context(), _ordinary_crop_scale(), _timer_original_crop()

### Community 51 - "analyze_cases.py"
Cohesion: 0.20
Nodes (6): case_source_sha(), effective_observation_state(), main(), source_frame_id(), PreviewAnchorTracker, capture_runtime_evidence()

### Community 54 - "higher-floor-replay.test.cjs"
Cohesion: 0.22
Nodes (7): {adaptMap,adaptPreview}, assert, crypto, fs, path, {runReplay}, {test}

### Community 55 - "random_replay_plan.py"
Cohesion: 0.16
Nodes (13): _box(), ordinary_preview_panel_scope(), _decode(), recover_preview_anchor(), sample_layout(), transform_box(), transform_png(), _box() (+5 more)

### Community 56 - "convergence-regression.py"
Cohesion: 0.24
Nodes (7): check_snapshot(), code_snapshot(), dependency_snapshot(), main(), merge_cases(), replay_command(), sha()

### Community 57 - "Python vision performance and generalization Implementation Plan"
Cohesion: 0.25
Nodes (7): Global Constraints, Python vision performance and generalization Implementation Plan, Review Focus, Task1: reproducible operation-level profiling, Task2: measured minimum optimization round, Task3: track S3 local coverage defects, Task4: correctness + comparable performance and gate

### Community 58 - "V2 座標／預覽收斂驗證紀錄"
Cohesion: 0.17
Nodes (11): V2 座標／預覽收斂驗證紀錄, 原始1551影格與七張歷史變動的當版核對, 固定倍率工具相容性修正, 基準與範圍, 已發現並處理的迴歸, 最終工具版本與驗收邊界, 最終階段結果, 本輪明確取捨與剩餘限制 (+3 more)

### Community 59 - "GateSupportedAspectTests"
Cohesion: 0.24
Nodes (3): AspectEndpointProjectionTests, GateSupportedAspectTests, estimate_pixel_aspect()

### Community 60 - "S3ScrollCoverageDefects"
Cohesion: 0.19
Nodes (4): checked_coverage(), GroundTruthFixtureContractTests, iou(), S3ScrollCoverageDefects

### Community 61 - "Python視覺效能優化與泛化驗證（2026-10-27）"
Cohesion: 0.20
Nodes (9): 1. 操作層量測，而非依名稱判斷, 3. 有量測但未採用的方案, 4. S3缺陷仍OPEN, 5. 獨立審查與當版回歸, 6. 完整成對效能測量, 7. 未達標原因與下一輪有限方案, 8. 執行取捨、審查界限與未完成事項, Python視覺效能優化與泛化驗證（2026-10-27） (+1 more)

### Community 62 - "node-selector.cjs"
Cohesion: 0.22
Nodes (13): fail(), freeze(), iou(), issued, numbers(), selectNode(), validateFrame(), validateProof() (+5 more)

### Community 64 - "observer-adapter.test.cjs"
Cohesion: 0.20
Nodes (6): {adaptMap,adaptPreview}, assert, crypto, fs, path, {test}

### Community 68 - "RandomClientTransformTests"
Cohesion: 0.33
Nodes (3): inverse_point(), RandomClientTransformTests, sample_layout()

### Community 69 - "recover_map_geometry"
Cohesion: 0.36
Nodes (3): recover_map_geometry(), SparseMapGeometryTests, WatermarkedCheckTests

### Community 70 - "preview-session.test.cjs"
Cohesion: 0.29
Nodes (6): assert, {map,intent,preview,clone}, {PreviewSession}, {selectNode}, setup(), {test}

### Community 71 - "preview-panel-scope.test.cjs"
Cohesion: 0.22
Nodes (7): {adaptPreview}, assert, currentPackets, fixture(), fs, {loadReplayFrames}, {test}

### Community 72 - "CRK Helper V2：60組離線閉環階段報告（第40組停止，待High評估）"
Cohesion: 0.25
Nodes (7): 60組逐項狀態, CRK Helper V2：60組離線閉環階段報告（第40組停止，待High評估）, 回歸、剩餘缺陷與證據, 數量、通過率與首次成功率, 未採用修補與停止界線, 版本與測試口徑, 第40組：實際失敗與根因

### Community 73 - "ordinary-aspect-context.test.cjs"
Cohesion: 0.22
Nodes (7): {adaptMap}, assert, fs, path, {readPreviewWaitAuthority}, {test}, {verifyPreview}

### Community 78 - "aspect-endpoints.test.cjs"
Cohesion: 0.25
Nodes (7): {adaptMap}, assert, {execFileSync}, fixture(), fs, {loadReplayFrames}, {test}

### Community 79 - "s3-scroll-refusal.test.cjs"
Cohesion: 0.29
Nodes (6): {adaptMap}, assert, fs, {loadReplayFrames}, {selectNode}, {test}

### Community 80 - "node_candidates"
Cohesion: 0.43
Nodes (3): ExactCandidateSearchTests, node_candidates(), SparsePeerBootstrapTests

### Community 82 - "review-regressions.test.cjs"
Cohesion: 0.29
Nodes (6): assert, {map,intent,preview}, {PreviewSession}, {selectNode}, setup(), {test}

### Community 83 - "四、回歸測試與安全性"
Cohesion: 0.33
Nodes (6): 4.1 最新可核對測試結果, 4.2 錯點、重點與錯誤預覽, 4.3 第39組：安全停下，但可用性仍未達標, 4.4 證據不足與負例是否真的執行, 4.5 1551張原生影格與「六張過渡候選變動」, 四、回歸測試與安全性

### Community 87 - "七、最終結論與下一階段建議"
Cohesion: 0.33
Nodes (6): 7.1 技術成熟度, 7.2 明確選項：C．需要局部架構調整, 7.3 最值得優先解決的三個問題, 7.4 是否需要提高Codex推理強度, 7.5 何時才適合真實遊戲驗收, 七、最終結論與下一階段建議

### Community 92 - "一、開發進度總覽"
Cohesion: 0.40
Nodes (5): 1.1 目前完成與未完成, 1.2 「60組」的正確分母, 1.3 P0～P5狀態, 1.4 G0～G5狀態：維持原標準, 一、開發進度總覽

### Community 93 - "三、視覺辨識與跨尺寸穩定性"
Cohesion: 0.40
Nodes (5): 3.1 八個關鍵環節, 3.2 哪些修正有泛化能力，哪些仍偏局部, 3.3 75%、100%、125%目前能說什麼, 3.4 是否需要YOLO或其他模型, 三、視覺辨識與跨尺寸穩定性

### Community 94 - "二、60組測試詳細分析"
Cohesion: 0.50
Nodes (4): 2.1 表格讀法與逐組證據, 2.2 失敗原因與已記錄修正, 2.3 首次結果、修正負擔與回歸趨勢, 二、60組測試詳細分析

### Community 95 - "六、最近約兩天的開發效率"
Cohesion: 0.50
Nodes (4): 6.1 可量化工作分布, 6.2 耗時與效能證據, 6.3 逐組方式是否有效率, 六、最近約兩天的開發效率

## Knowledge Gaps
- **33 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CRK Helper V2：失敗導向重構設計與分階段驗收` connect `CRK Helper V2：失敗導向重構設計與分階段驗收` to `CRK Helper V2：P0–P3核心與審閱修正紀錄`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Are the 47 inferred relationships involving `BoundedOCRRuntime` (e.g. with `.test_actual_anisotropic_preview_recovers_selected_node_using_vertical_spacing()` and `.test_actual_near_native_preview_corrects_pixels_even_with_existing_gate_anchor()`) actually correct?**
  _`BoundedOCRRuntime` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Should `json` be split into smaller, more focused modules?**
  _Cohesion score 0.14216575922565033 - nodes in this community are weakly interconnected._
- **Why does `inspect_map()` connect `resize_box` to `re`, `CRK Helper V2：失敗導向重構設計與分階段驗收`, `hashlib`, `numpy`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Should `preview-registration.test.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.13438735177865613 - nodes in this community are weakly interconnected._
- **Why does `2.1 已確認的問題` connect `CRK Helper V2：失敗導向重構設計與分階段驗收` to `resize_box`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **Should `BoundedOCRRuntime` be split into smaller, more focused modules?**
  _Cohesion score 0.1471861471861472 - nodes in this community are weakly interconnected._