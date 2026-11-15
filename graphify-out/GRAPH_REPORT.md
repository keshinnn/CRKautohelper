# Graph Report - CRK-Helper-V2  (2026-11-13)

## Corpus Check
- 291 files · ~104,925 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 2, .exe 2, .cfg 1)

## Summary
- 2074 nodes · 4898 edges · 133 communities (85 shown, 48 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 444 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `74ad37d8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- semantic_state
- preview-session.test.cjs
- BoundedOCRRuntime
- inspect_preview_identity
- recover_map_aspect
- CRK Helper V2：失敗導向重構設計與分階段驗收
- fast_map_candidates.py
- validate_groups
- resize_box
- CRK Helper V2 P4-C 正式集合與隨機壓力測試
- evidence.test.cjs
- replay-development.cjs
- RandomReplayPlanTests
- CRK Helper V2 P0–P3 Implementation Plan
- P4-C 開發進度：尚未正式驗收
- ReferenceLineTests
- convergence-regression.py
- inspect_map_actions
- registration_probe.py
- ref_node_fs
- Candidate Shadow PoC Implementation Plan
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
- hashlib
- ProgressRuntime
- re
- Python視覺效能優化與泛化驗證（2026-10-27）
- PrefixFreezerTests
- recover_map_geometry
- map_aspect.py
- train_export.py
- loadReplayFrames
- convergence-negatives.py
- preview-context.cjs
- numpy
- research_pilot.py
- ProgressRuntime
- 74ad37d：功能回歸穩定，效能仍未收斂
- CRK Helper V2 座標與預覽證據收斂 Implementation Plan
- candidate_poc/progress.md
- FrameIntermediatesTests
- OfflineAnalyzerTests
- ContextLineRemeasurementTests
- ConvergenceRunnerTests
- negative-selection-check.cjs
- episode-replay.cjs
- M1有限實作與離線驗證計畫
- Python vision performance and generalization Implementation Plan
- V2 座標／預覽收斂驗證紀錄
- GateSupportedAspectTests
- S3ScrollCoverageDefects
- 集中功能修復 Implementation Plan
- math
- PhaseMapPipelineTests
- preflight.py
- audit_full_frame
- .observe
- Coverage 當版回歸：第31組幾何退步
- prepare_qa.py
- analyze_cases.py
- node_candidates
- CacheBackendIdentityTests
- LegacyCurrentPhaseTests
- node_candidates
- specs/2026-10-27-python-vision-performance.md
- 2026-10-26-convergence-execution-ledger.md
- 2026-11-02-phase-observation-status.md
- SmallAspectSparseTests
- 幾何模板比對：等價提前淘汰與效能驗證
- audit_duplicates
- PhaseObserverCliTests
- verify_research.cjs
- M1有限實作與驗證：第41組通過，第42組停在範圍邊界
- rift-completion.cjs
- 353b2c9：正確性回歸通過，因嚴重效能退步停止
- PhaseRouteParityTests
- OfflineAnalyzerTests
- 2026-10-27-development-40-60.md
- 2026-10-27-case40-high-handoff.md
- 2026-10-27-development40-60-execution-ledger.md
- 2026-10-27-python-vision-execution-ledger.md
- StageTiming
- preflight.py
- Bounded Coverage Implementation Plan
- CompletedIntegerGridTests
- result-evidence.cjs
- CRK Helper V2：60組離線閉環測試報告
- BoundedCoverageTests
- choose_indices
- CompletedNodeCandidateTests
- pathlib
- 2026-10-28-bounded-coverage-design.md
- rift-context.cjs
- Phase observation implementation plan
- 原生候選稽核：閉環通過但局部候選退步
- EnglishSceneRuntime
- IconRankingTests
- NominalQuantizationTests
- proof_compatibility.cjs
- 幾何效能修正：等價的必要條件提前拒絕
- 2026-11-02-offline-exploration-43-60.md
- manifest.json
- map-aspect-adapter.test.cjs
- rift-proof.cjs
- CRK Helper V2：集中功能修復與完整回歸
- transaction-map-anchor.test.cjs
- pil
- adaptMap
- audit_full_frame
- CRK Helper V2 — 2026-11-12 訓練啟動準備與實際准入結果
- convergence-regression.py
- profile-vision.py
- result-evidence.test.cjs
- GateReferenceFamilyTests
- reference_line_geometry.py
- observer-adapter.cjs
- s3-scroll-refusal.test.cjs
- PreviewLineEvidenceTests
- NativeEllipsePreviewTests
- EnglishCurrentTests
- V2 座標與點後等待契約 v1

## God Nodes (most connected - your core abstractions)
1. `BoundedOCRRuntime` - 60 edges
2. `adaptMap()` - 48 edges
3. `loadReplayFrames()` - 39 edges
4. `BoundedOCRRuntime` - 37 edges
5. `adaptPreview()` - 36 edges
6. `recover_map_aspect()` - 36 edges
7. `ProgressRuntime` - 31 edges
8. `FrameIntermediates` - 29 edges
9. `inspect_preview_identity()` - 29 edges
10. `inspect_preview_context()` - 28 edges

## Surprising Connections (you probably didn't know these)
- `2. 74ad37d：單次完成節點搜尋內的精確分類重用` --references--> `completed_node_candidates()`  [INFERRED]
  docs/validation/2026-11-02-performance-optimization-stop.md → ml/completed_node_candidates.py
- `2. 已保留的最小優化` --references--> `FrameIntermediates`  [INFERRED]
  docs/validation/2026-10-27-python-vision-performance.md → ml/frame_intermediates.py
- `C2 現有入口模板家族` --references--> `_gate_pixel_geometry()`  [INFERRED]
  docs/validation/2026-11-03-concentrated-repair-analysis.md → ml/map_aspect.py
- `已定位的資料流` --references--> `_supplement_orange_candidates()`  [INFERRED]
  docs/validation/2026-10-27-case41-high-handoff.md → ml/map_aspect.py
- `2.1 已確認的問題` --references--> `inspect_map()`  [INFERRED]
  docs/superpowers/specs/2026-10-24-crk-helper-v2-design.md → ml/map_observer.py

## Import Cycles
- None detected.

## Communities (133 total, 48 thin omitted)

### Community 0 - "semantic_state"
Cohesion: 0.24
Nodes (4): semantic_state(), EnglishContextEvidenceTests, reread_english_context(), EnglishSceneTests

### Community 1 - "preview-session.test.cjs"
Cohesion: 0.08
Nodes (33): evaluateDevelopmentReplay(), evaluateReplay(), gradeReplay(), clone(), frame(), intent, map(), preview() (+25 more)

### Community 2 - "BoundedOCRRuntime"
Cohesion: 0.15
Nodes (7): BoundedOCRRuntime, _context_claim_agrees(), _context_reading_key(), _MeasuredPreprocess, normalize_evidence(), _remaining_timer_locators(), PreviewTimerConflictTests

### Community 3 - "inspect_preview_identity"
Cohesion: 0.12
Nodes (6): AspectPreviewTests, EnglishPreviewTests, NativePreviewSizeTests, OrdinaryWhitespaceTests, inspect_preview_identity(), PreviewIdentityTests

### Community 4 - "recover_map_aspect"
Cohesion: 0.15
Nodes (3): MapAspectTests, recover_map_aspect(), PreviewPanelScopeTests

### Community 5 - "CRK Helper V2：失敗導向重構設計與分階段驗收"
Cohesion: 0.08
Nodes (25): 10. 本次有條件批准與執行順序, 11. P0–P3 核心實作與審閱修訂（2026-10-24）, 1. 唯一目標與完成邊界, 2.1 已確認的問題, 2.2 尚未證實、需要測試的風險, 2.3 可重用與暫緩處理, 2. 根本原因與證據等級, 3. 方案比較與建議 (+17 more)

### Community 7 - "validate_groups"
Cohesion: 0.22
Nodes (5): readiness(), _sha(), validate_groups(), DataAdmissionTests, record()

### Community 8 - "resize_box"
Cohesion: 0.17
Nodes (11): 座標, recover_completed_extents(), node_geometry(), analysis_raster(), geometry_certificate(), resize_box(), resize_point(), _size() (+3 more)

### Community 9 - "CRK Helper V2 P4-C 正式集合與隨機壓力測試"
Cohesion: 0.05
Nodes (42): Actual case14 original text and near-native recovery brief, Actual glowing-edge candidate and precision repair brief, Actual native map-title OCR truncation repair brief, Actual second-floor case16 pixel evidence brief, Actual watermarked Chinese title context repair brief, CRK Helper V2 P4-C 正式集合與隨機壓力測試, Current evidence, English source development repair brief (2026-10-25) (+34 more)

### Community 10 - "evidence.test.cjs"
Cohesion: 0.07
Nodes (33): compareSnapshot(), crypto, digest(), fs, locate(), milestoneResult(), path, snapshotFiles() (+25 more)

### Community 11 - "replay-development.cjs"
Cohesion: 0.05
Nodes (38): crypto, fs, path, {spawnSync}, crypto, {execFileSync}, fs, path (+30 more)

### Community 12 - "RandomReplayPlanTests"
Cohesion: 0.38
Nodes (3): plan_sequences(), RandomReplayPlanTests, render_sequences()

### Community 13 - "CRK Helper V2 P0–P3 Implementation Plan"
Cohesion: 0.15
Nodes (12): CRK Helper V2 P0–P3 Implementation Plan, Global Constraints, Review Focus, T1 / P0：基準凍結與里程碑結果契約, T2 / P1：統一可逆座標, T3 / P2：兩幀地圖到唯一節點證明, T4 / P3：單次交易與獨立預覽確認, T5 / P3：只讀辨識adapter、trace與核心整合 (+4 more)

### Community 14 - "P4-C 開發進度：尚未正式驗收"
Cohesion: 0.07
Nodes (28): 2026-10-25：區域10、人工標註及多來源隔離, 2026-10-25 延續驗證, LX46 英文與浮水印開發驗證（2026-10-25）, P4-C 開發進度：尚未正式驗收, 三種尺寸流程試跑通過, 來源修訂與浮水印場景（最新）, 原生960×720的三段新閉環, 尚待完成 (+20 more)

### Community 17 - "convergence-regression.py"
Cohesion: 0.14
Nodes (3): OperationProfile, measured(), OperationProfileTests

### Community 18 - "inspect_map_actions"
Cohesion: 0.20
Nodes (4): CurrentPositionEvidenceTests, inspect_map_actions(), PixelMapActionTests, ReferenceCurrentRingTests

### Community 19 - "registration_probe.py"
Cohesion: 0.11
Nodes (11): box_error(), main(), non_authority_result(), pair_blockers(), pixel_probe(), read(), save(), sha() (+3 more)

### Community 20 - "ref_node_fs"
Cohesion: 0.04
Nodes (39): assert, fs, os, path, {test}, {writeCaseArtifacts}, {adaptMap}, assert (+31 more)

### Community 21 - "Candidate Shadow PoC Implementation Plan"
Cohesion: 0.18
Nodes (10): Candidate Shadow PoC Implementation Plan, Global Constraints, Review Focus, Task 1：鎖定基準、資料隔離與外緣標註規則, Task 2：只產生提案的座標與來源契約, Task 3：單次訓練與鎖定候選評估, Task 4：有界同幀證據橋接與安全RED, Task 5：隔離成本、版本綁定與最終決策 (+2 more)

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
Cohesion: 0.15
Nodes (12): 2026-10-26 continuation: case17 gate proposal and row pitch, Case18 line raster reference repair (current work), Latest 2026-11-02 — performance guard STOP, no43+, Latest strategy — frozen independent offline exploration43..60, Main14 case20 detected-completed extent failure and isolated repair, Main16 case21: transaction-local semantic root after post-click resize, Native completed proposals and independent supplemental gate, SDD ledger — plan: C:/Users/User/Documents/Codex/CRK-Helper-V2/docs/superpowers/plans/2026-10-24-crk-helper-v2-p0-p3-plan.md (+4 more)

### Community 32 - "BoundedOCRRuntime"
Cohesion: 0.13
Nodes (5): BoundedOCRRuntime, BoundedOCRTests, normalize_evidence(), PreviewContextAspectTests, PreviewTimerTests

### Community 33 - "hashlib"
Cohesion: 0.11
Nodes (13): signature(), _box(), freeze_corpus(), main(), validate_corpus(), freeze_prefixes(), _sha(), extract_case() (+5 more)

### Community 34 - "ProgressRuntime"
Cohesion: 0.17
Nodes (5): EnglishSceneRuntime, ProgressRuntime, RemainingTimeLocatorTests, SplitRemainingClockTests, WatermarkedMapContextTests

### Community 35 - "re"
Cohesion: 0.29
Nodes (9): _box(), _english_ordinary_crop(), _enter_original_crop(), inspect_preview_context(), _ordinary_crop_scale(), _timer_line_original_crop(), _timer_original_crop(), actual_frame() (+1 more)

### Community 36 - "Python視覺效能優化與泛化驗證（2026-10-27）"
Cohesion: 0.18
Nodes (10): 1. 操作層量測，而非依名稱判斷, 2. 已保留的最小優化, 3. 有量測但未採用的方案, 4. S3缺陷仍OPEN, 5. 獨立審查與當版回歸, 6. 完整成對效能測量, 7. 未達標原因與下一輪有限方案, 8. 執行取捨、審查界限與未完成事項 (+2 more)

### Community 38 - "recover_map_geometry"
Cohesion: 0.36
Nodes (3): recover_map_geometry(), SparseMapGeometryTests, WatermarkedCheckTests

### Community 39 - "map_aspect.py"
Cohesion: 0.22
Nodes (15): completed_geometry(), wrapped(), raster_round(), _cyan_component(), estimate_pixel_aspect(), _gate_pixel_geometry(), _gate_supported_aspect_candidates(), _orange_node_pixel_geometry() (+7 more)

### Community 40 - "train_export.py"
Cohesion: 0.10
Nodes (22): prepare_dataset(), ProjectTrainingBudgetTests, TrainingEntryTests, TrainingLaunchReviewTests, bound_json(), claim_attempt(), claim_training_attempt(), claim_worker() (+14 more)

### Community 41 - "loadReplayFrames"
Cohesion: 0.04
Nodes (60): crypto, fs, invalid(), loadReplayFrames(), sha(), {adaptMap}, assert, {execFileSync} (+52 more)

### Community 42 - "convergence-negatives.py"
Cohesion: 0.19
Nodes (7): capture_runtime_evidence(), control_case(), control_request(), main(), check(), unchanged(), require_phase_backend()

### Community 43 - "preview-context.cjs"
Cohesion: 0.09
Nodes (31): analysisRaster(), {isDeepStrictEqual:eq}, nativeGeometryEvidence(), resizeBox(), resizePoint(), size(), validateGeometryCertificate(), adaptPreviewContext() (+23 more)

### Community 44 - "numpy"
Cohesion: 0.14
Nodes (14): completed_node_candidates(), inspect_in_progress(), _reference_ring(), _bounds(), _key(), reread_english_context(), heal_node_candidates(), rank_required_icon() (+6 more)

### Community 45 - "research_pilot.py"
Cohesion: 0.22
Nodes (10): fit(), main(), predict_images(), require_supervisor(), supervise(), main(), main(), validate_loaded_model() (+2 more)

### Community 46 - "ProgressRuntime"
Cohesion: 0.17
Nodes (5): parse_progress(), ProgressRuntime, EnglishProgressTests, MapTitleRereadTests, ProgressEvidenceTests

### Community 47 - "74ad37d：功能回歸穩定，效能仍未收斂"
Cohesion: 0.20
Nodes (10): 1. c235f6a：必要家族先算、必定失敗時提前結束, 2. 74ad37d：單次完成節點搜尋內的精確分類重用, 74ad37d：功能回歸穩定，效能仍未收斂, 下一步最小方案（尚未執行）, 保存與不可挪用事項, 同193張隔離CPU比較, 實作內容與經證明的收益, 新的尾延遲證據 (+2 more)

### Community 48 - "CRK Helper V2 座標與預覽證據收斂 Implementation Plan"
Cohesion: 0.20
Nodes (9): CRK Helper V2 座標與預覽證據收斂 Implementation Plan, Global Constraints, Review Focus, Task 1：根因重現、契約與聚焦測試, Task 2：最小幾何契約, Task 3：預覽控制／身份與等待能力分離, Task 4：同版本回歸、稽核與停止交付, 執行紀錄 (+1 more)

### Community 54 - "negative-selection-check.cjs"
Cohesion: 0.11
Nodes (16): {adaptMap,adaptPreview}, analyzed, assert, {captureCodeVersion}, crypto, frames, fs, [input,out] (+8 more)

### Community 55 - "episode-replay.cjs"
Cohesion: 0.15
Nodes (18): {adaptMap,adaptPreview}, crypto, {decodeRgbPng}, fileHash(), fs, {loadReplayFrames,buildReplayGate}, main(), path (+10 more)

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

### Community 61 - "集中功能修復 Implementation Plan"
Cohesion: 0.25
Nodes (7): Global Constraints, Review Focus, Task A: English complete semantic rereading, Task B: Preview chain, Task C: Map candidate and geometry, Task D: Unified verification and report, 集中功能修復 Implementation Plan

### Community 62 - "math"
Cohesion: 0.16
Nodes (11): inverse_point(), sample_layout(), transform_box(), transform_png(), _box(), _frame(), plan_sequences(), _sha() (+3 more)

### Community 64 - "preflight.py"
Cohesion: 0.06
Nodes (30): 1. 新來源與split預留, 2. 20張QA材料如何產生, 3. 兩份判讀與一次有界規則澄清, 4. 工程驗證、成本與版本, 5. 目前Go／No-Go, CRK Helper V2：新來源取得與20張邊界QA結果, 1. 實際完成與版本邊界, 2.1 實際來源盤點 (+22 more)

### Community 65 - "audit_full_frame"
Cohesion: 0.22
Nodes (3): audit_full_frame(), augment(), AnnotationAuditTests

### Community 67 - "Coverage 當版回歸：第31組幾何退步"
Cohesion: 0.20
Nodes (8): Coverage 當版回歸：第31組幾何退步, 使用者後續批准及更窄可行方案, 可重現的根因, 已執行與分母, 最小下一步設計（尚未實作）, 證據索引, 驗收與風險, Bounded coverage：第42修復，但第31回歸退步

### Community 68 - "prepare_qa.py"
Cohesion: 0.24
Nodes (5): extract_frame(), file_hash(), main(), validate_reservations(), SourcePreparationTests

### Community 69 - "analyze_cases.py"
Cohesion: 0.16
Nodes (9): case_source_sha(), effective_observation_state(), main(), source_frame_id(), coverage_node_candidates(), node_candidates(), observe_geometry(), inspect_preview_identity() (+1 more)

### Community 70 - "node_candidates"
Cohesion: 0.35
Nodes (5): _CandidateScan, _coverage_groups(), _groups(), _nominal_groups(), _supplement_groups()

### Community 73 - "node_candidates"
Cohesion: 0.43
Nodes (3): ExactCandidateSearchTests, node_candidates(), SparsePeerBootstrapTests

### Community 76 - "2026-11-02-phase-observation-status.md"
Cohesion: 0.14
Nodes (13): 353b2c9 前42組當版全面回歸通過, 353b2c9 聚焦閉環已完整通過, 已依使用者指示恢復, 已依使用者要求暫停, 已批准的觀察階段分離：當版驗證進行中, 最新74ad37d：功能回歸通過，效能閘門停止, 最新：60組凍結離線探索已完成（2026-11-03）, 最新：候選稽核抓到46045退步，已做最小修正、等待當版重新驗證 (+5 more)

### Community 79 - "幾何模板比對：等價提前淘汰與效能驗證"
Cohesion: 0.20
Nodes (8): 原193張隔離CPU基準, 實際驗證, 已實作範圍, 幾何模板比對：等價提前淘汰與效能驗證, 待完成與狀態, 最新結果：74ad37d效能停止，功能回歸通過, 第二項局部修正：74ad37d, 補充比對工具的錯誤紀錄

### Community 82 - "verify_research.cjs"
Cohesion: 0.23
Nodes (11): capabilities(), crc32(), crypto, decodeRgbPng(), deny(), fs, {performance}, sha() (+3 more)

### Community 84 - "rift-completion.cjs"
Cohesion: 0.17
Nodes (12): {adaptMap}, compact(), completeRift(), sources(), {convertedBattle}, fs, {identity,pending,verifyPair,trustedResultFrame,validatePhaseFrames}, loading() (+4 more)

### Community 85 - "353b2c9：正確性回歸通過，因嚴重效能退步停止"
Cohesion: 0.22
Nodes (8): 353b2c9：正確性回歸通過，因嚴重效能退步停止, 下一步建議與需批准的範圍, 同次配對matcher測量, 已完成正確性與證據驗證, 結論與停止範圍, 耗時來源與目前能確認的根因, 證據位置, 隔離基準的可比數據

### Community 87 - "OfflineAnalyzerTests"
Cohesion: 0.24
Nodes (4): PreviewAnchorTracker, PreviewAnchorTracker, PreviewRegistrationTests, recover_preview_anchor()

### Community 93 - "preflight.py"
Cohesion: 0.25
Nodes (8): digest(), lock_baseline(), main(), negative_cases(), negative_suite(), write_json(), BaselineLockTests, outline_size_hypotheses()

### Community 94 - "Bounded Coverage Implementation Plan"
Cohesion: 0.25
Nodes (7): Bounded Coverage Implementation Plan, Global Constraints, One review fix pass, Review Focus, Task1: RED/GREEN bounded coverage, Task2: current fresh qualification, Task3: finish remaining frozen offline corpus

### Community 96 - "result-evidence.cjs"
Cohesion: 0.24
Nodes (11): compact(), crypto, {decodeRgbPng}, fs, identity(), path, pending(), sha() (+3 more)

### Community 97 - "CRK Helper V2：60組離線閉環測試報告"
Cohesion: 0.20
Nodes (8): 2aeae97 當版完整結果, 第40組修復進行狀態（接續High評估）, High接續時的界線, 停止狀態, 已完成的當版驗證, 已定位的資料流, 第41組：候選恢復阻塞與High接續資料, 第41組完整失敗證據

### Community 101 - "pathlib"
Cohesion: 0.11
Nodes (4): OneUseWorkerTests, render_sequences(), _save_manifest(), SameFramePipelineTests

### Community 103 - "rift-context.cjs"
Cohesion: 0.24
Nodes (8): crypto, {decodeRgbPng}, fs, norm(), path, sha(), {spawnSync}, verifyContextPixels()

### Community 104 - "Phase observation implementation plan"
Cohesion: 0.29
Nodes (6): 2026-11-02 補充：幾何路由接受邊界仍須隔離, Phase observation implementation plan, Stop boundaries, Task1: RED -> GREEN scoped backend and incremental raw scan, Task2: RED -> GREEN source routing integration, Task3: current-version qualification

### Community 105 - "原生候選稽核：閉環通過但局部候選退步"
Cohesion: 0.29
Nodes (6): 46045 根因, 原生候選稽核：閉環通過但局部候選退步, 實際完成結果, 待驗證與風險, 本輪最小修正, 證據

### Community 109 - "proof_compatibility.cjs"
Cohesion: 0.18
Nodes (9): {adaptMap,adaptPreview}, crypto, fs, {loadReplayFrames}, path, {performance}, root, run() (+1 more)

### Community 110 - "幾何效能修正：等價的必要條件提前拒絕"
Cohesion: 0.33
Nodes (5): c235f6a實測後的第二項局部修正, 實作順序與驗收, 幾何效能修正：等價的必要條件提前拒絕, 量測依據與範圍, 風險與控制

### Community 112 - "manifest.json"
Cohesion: 0.40
Nodes (4): cases, purpose, rows, sourceCommit

### Community 113 - "map-aspect-adapter.test.cjs"
Cohesion: 0.20
Nodes (9): {adaptMap,adaptPreview}, assert, fixture(), fs, {loadReplayFrames}, observe(), path, {selectNode} (+1 more)

### Community 114 - "rift-proof.cjs"
Cohesion: 0.08
Nodes (49): convertedBattle(), {createGeometry,clientToScreen}, crypto, {decodeRgbPng}, dispatchOnce(), facts(), fail(), freeze() (+41 more)

### Community 115 - "CRK Helper V2：集中功能修復與完整回歸"
Cohesion: 0.20
Nodes (9): A 英文完整語義, B 預覽context與身份鏈, C1 完成勾號：同一半徑內補齊格點，隔離幾何路由, C2 現有入口模板家族, C 初始診斷（下列C1／C2補證之前）, 最終回歸進行中：子階段不可當閉環, 獨立審查修正, 集中修復：共因、最小修改與驗收 (+1 more)

### Community 116 - "transaction-map-anchor.test.cjs"
Cohesion: 0.05
Nodes (56): fail(), freeze(), iou(), issued, numbers(), selectNode(), validateFrame(), validateProof() (+48 more)

### Community 118 - "adaptMap"
Cohesion: 0.06
Nodes (56): {adaptMap,adaptPreview}, {plan}, {runReplay}, runSecond(), same(), {adaptMap,adaptPreview}, crypto, fs (+48 more)

### Community 119 - "audit_full_frame"
Cohesion: 0.12
Nodes (11): box_iou(), aggregate(), benchmark(), main(), overlay(), check_split(), score(), augment() (+3 more)

### Community 120 - "CRK Helper V2 — 2026-11-12 訓練啟動準備與實際准入結果"
Cohesion: 0.25
Nodes (7): CRK Helper V2 — 2026-11-12 訓練啟動準備與實際准入結果, 實際產出, 未完成的具體缺口與下一步, 本輪標註證據與失敗處理, 版本與依據, 結論, 訓練入口與本輪修正

### Community 121 - "convergence-regression.py"
Cohesion: 0.35
Nodes (7): check_snapshot(), code_snapshot(), dependency_snapshot(), main(), merge_cases(), replay_command(), sha()

### Community 123 - "result-evidence.test.cjs"
Cohesion: 0.29
Nodes (7): assert, {identity,validatePair,trustedResultFrame,validatePhaseFrames}, row(), {test}, valid(), trustedResultFrame(), validatePhaseFrames()

### Community 125 - "reference_line_geometry.py"
Cohesion: 0.38
Nodes (4): reference_geometry(), wrapped(), measure(), reference_line()

### Community 126 - "observer-adapter.cjs"
Cohesion: 0.22
Nodes (18): boxValid(), aspectGeometry(), completedCheckValid(), completedGeometry(), crypto, directMapAnchors, healGeometry(), {isDeepStrictEqual} (+10 more)

### Community 127 - "s3-scroll-refusal.test.cjs"
Cohesion: 0.29
Nodes (6): {adaptMap}, assert, fs, {loadReplayFrames}, {selectNode}, {test}

### Community 132 - "V2 座標與點後等待契約 v1"
Cohesion: 0.50
Nodes (3): V2 座標與點後等待契約 v1, 回歸版本, 預覽控制、身份與操作權限

## Knowledge Gaps
- **48 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `readiness()` connect `validate_groups` to `preflight.py`, `train_export.py`, `preflight.py`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Should `preview-session.test.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.07948717948717948 - nodes in this community are weakly interconnected._
- **Why does `A0–A2 isolated candidate research` connect `preflight.py` to `validate_groups`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Should `BoundedOCRRuntime` be split into smaller, more focused modules?**
  _Cohesion score 0.1471861471861472 - nodes in this community are weakly interconnected._
- **Why does `BoundedOCRRuntime` connect `BoundedOCRRuntime` to `semantic_state`, `NativeEllipsePreviewTests`, `BoundedOCRRuntime`, `inspect_preview_identity`, `ProgressRuntime`, `recover_map_aspect`, `re`, `PreviewLineEvidenceTests`, `EnglishSceneRuntime`, `ProgressRuntime`, `bounded_ocr.py`, `ContextLineRemeasurementTests`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Should `inspect_preview_identity` be split into smaller, more focused modules?**
  _Cohesion score 0.12315270935960591 - nodes in this community are weakly interconnected._
- **Should `recover_map_aspect` be split into smaller, more focused modules?**
  _Cohesion score 0.1477832512315271 - nodes in this community are weakly interconnected._