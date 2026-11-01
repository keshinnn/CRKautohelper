# Phase observation implementation plan

Approved by the user in this thread after case31 routing report. Goal: retain M1 as same-frame routing evidence while enabling bounded coverage explicitly, without changing estimator/raster/thresholds/proof or native operations.

Spec: docs/validation/2026-10-28-coverage-regression-case31.md. Execute inline with Superpowers executing-plans, TDD and one fresh final review of this implementation; no per-task agent loop. Preserve baseline5e2 failures and frozen60/30 corpus.

Pre-flight: matcher Scan -> FrameIntermediates consumes immutable result and shares only exact source/model/asset/backend-bound raw work; context -> map pipeline temporarily selects coverage and restores M1; pipeline -> analyzer retains existing v2OriginalMapReview provenance for baseline raw map; runners -> analyzer must explicitly opt in coverage. Shared keys must distinguish backend modes but share the same scan implementation only when input and processing identity match.

Ruling: a same-image feasibility probe shows existing map_aspect already honors v2OriginalMapReview as raw routing evidence. Retaining fresh M1 prior recovers case31 IoU .9388056/.9358738 without editing map_aspect at all. Prefer this narrower integration over changing estimator or branching rules. Risk: phase identity and intermediate caching must be explicit, and complete downstream regression must confirm no changed provenance semantics.

## Task1: RED -> GREEN scoped backend and incremental raw scan
- Add new tests before source changes: temporary backend scope restores on success/error, distinct backend result cache, disabled-cache control, no cross-frame/image/config reuse; real M1->coverage->M1 has exact outputs, one Canny and original kernel multiplicities only once across phases.
- Extract existing matcher preprocessing/base-NMS/M1/coverage stages into one raw CandidateScan with lazy results. Preserve _groups/_match_group, .48/NMS and default function/API/output. Retain independent copies for consumers.
- FrameIntermediates explicit backend context method, actual backend identity on result keys, exact scan identity for sharing lazy raw work across its two known fast backends; scope must restore in finally. Disabled control does not share work. No authority cache.
- Focused context + existing nine context, five M1, four coverage, original fast equivalence.

## Task2: RED -> GREEN source routing integration
- New real-source unit tests case31 two frames: with M1 baseline and explicit coverage, retain raw prior, proper unanchored recovery, GT IoU>=.90; same fresh source hash, no intent supplied to observer. Case42 two frames retain added target and original M1 prefix. Enabled/disabled same-frame reuse must yield identical semantic packet.
- New ml/map_pipeline.py contains existing sparse/aspect sequence and explicit augmentation phase. Copy same-frame M1 map as v2OriginalMapReview, inspect coverage source map in scoped backend, reuse original header, then run unchanged sparse/aspect recovery while prior remains baseline. Same already existing provenance field, no future/old-frame input. Return existing packet with no fabricated authority.
- Analyzer installs M1 default under --fast-map; new explicit --map-coverage requires --fast-map. Coverage adds new backend mode identity; existing fast-map legacy behavior stays intact. No map_aspect, calibrator, raster, Selector, Transaction or Preview edits.
- Convergence and benchmark runners explicitly enable coverage. S3 focused defect tests target explicit coverage; existing old M1/frame-context semantic assertions remain unchanged. Cache CLI tests cover coverage/M1/original transitions and matching-mode reuse.
- Full CLI source tests and source/bundle binding review. Graph AST update, freeze source commit; one fresh whole-change review, one RED/GREEN important fix pass if needed.

## Task3: current-version qualification
- Fresh full case31(29), case41(266), case42(265), including causal transaction and independent geometry/identity grade. Do not substitute component success for closure.
- Full prefix42/current native20/fixed15/negative30+controls/full Node/Python/native1551+seven+new candidate pixel review/rounding pressure/paired matcher+same193 isolated producer baseline. Save all failures, source/runner/code/model/runtime hashes and actual fresh/cache stats. No old passes as current.
- G4 remains OPEN unless all original criteria including p95<=1500 and real age/deadline evidence are met; no P5.
- After stable necessary regression, ordered43..60 then frozen native held10 and transformed held30 with unchanged evaluator disclosed, no holdout tuning/replacement. Final actual60 report, first-trace history, regressions, remaining defects.

## Stop boundaries
No threshold relaxation, frame-ID hacks, unknown skipping, corpus changes, estimator/raster/model rewrite or native operations. New integration defects: diagnose source and repair only within this approved scope. Broader redesign requires user approval. Do not promote partial batch/suffix diagnostics into a passing full regression.
# 2026-11-02 補充：幾何路由接受邊界仍須隔離

當版24bfb2a的42組／native20／fixed15閉環與負例30皆通過，但1551張稽核的31張候選變動中，S3 46045一個原本合法的戰鬥節點消失。原圖SHA `2cbdc12a5820b74618251719d9bd683bd08480fa0afd5cea9482b893eca40886`。原生4個候選補強後仍4個；比例恢復在M1模式沒有接受校正圖，而coverage模式接受1231×720→960×561校正圖的7個候選並替換原圖，丟掉原圖右下候選。不是快取、OCR、點擊或預覽身份失敗。完整兩模式邊界重現：`artifacts/phase-routing-20261028-01/native46045-loss-01/boundary-trace.json`。

這仍是已批准的Observer／比例恢復呼叫邊界隔離範圍，不修改估計器、raster、模板銀行、JS權威或驗收閾值。原始M1地圖欄位只保留資料，尚不足以保存整個既有幾何接受路徑。

最小修正與驗收：

1. 先新增真實46045的RED回歸：同幀M1未接受校正時，補強不得憑增加候選另選校正raster而丟掉原本候選；共用與停用模式結果必須一致。保持所有既有測試斷言。
2. 在`map_pipeline.py`先以原M1 backend完整執行既有幾何路徑，保存當幀基準結果；這不是上一張影格或舊快取。
3. 補強後的幾何結果僅在是否校正、source／rectified／analysis尺寸及正反矩陣完全符合當幀基準時接受。M1未接受校正而coverage新接受時，保留補強後的source工作觀察；M1已接受但coverage結果不同時，保留同幀已驗證的M1結果。保留拒絕結果與原因供稽核，不將其作為操作權限。不以新IoU容差、clamp或舊節點座標補洞。
4. 最終同幀currentPosition照既有方法重新測量，來源綁定、proof／JS獨立驗證及交易保持不變。
5. 先聚焦46045、31／41／42及S3兩張，再完整單元與當版全套必要回歸。修改後必須使用新版本／新證據目錄，不把24bfb2a通過紀錄算入新版。
6. 原生1551／七張及所有候選變動像素稽核必須沒有新增錯誤或原有合法候選消失。完整回歸、壓力與效能穩定後才43～60；不啟動保留集或P5。

只讀反事實試驗`route-parity-study-02/report.json`在9張聚焦影格中恢復46045原4個候選，同時保持31／41／42目標IoU≥.90與S3兩個獨立GT通過；不是生產修正、閉環或效能驗收。第一版試驗將41組轉換前35928與轉換後GT混比造成斷言失敗，原始腳本／日誌保留；第二版採該組凍結的preFrames35929、35935，沒有改動凍結資料或正式測試。

主要風險是多跑同幀M1幾何增加CPU耗時，與拒絕新校正路徑可能降低補強收益。原圖與校正圖的raw匹配仍共用同幀中間結果；須以原193張隔離基準實測，不宣稱已改善效能。若仍需新候選融合演算法、估計器／raster修改或放寬安全條件，停止並回報。

---

