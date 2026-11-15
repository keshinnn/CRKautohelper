# Candidate Shadow PoC Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 以一次有界離線實驗評估新候選生成器，能否改善52／53、55～57、58／59並保持既有安全證據鏈。

**Architecture:** 新模型只在隔離PoC產生不可信候選；既有正式模板路徑與Node權威不變。先評估資料及候選，再檢查同幀證據橋接；橋接不相容即停止，不擴寫正式Verifier。

**Tech Stack:** 建議YOLO26n、640輸入、FP32 ONNX、ONNX Runtime CPU、Python隔離環境、現有Node離線交易驗證。實際版本在環境預檢後鎖定，未完成預檢不得訓練。

**Spec:** [人工MVP與候選架構設計](../../reports/crk-helper-v2-assisted-mvp-and-candidate-options.md)。此計畫只涵蓋候選PoC，人工MVP為獨立交付，不在此混做。

**Status:** 2026-11-05，待使用者批准；以下步驟全部未執行。這不是已授權的模型替換或正式開發排程。

> 2026-11-08修訂：產品目標改為全自主冥界；人工MVP暫停。依[修訂自主架構](../../reports/crk-helper-v2-autonomous-direction-2026-11-08.md)，Task4若遇模板proof不相容，停止原proof橋接，但可另提出版本化、原圖獨立驗證的新證據契約；不把相容舊模板當架構必要條件。新契約仍僅設計／離線研究，正式Verifier修改與P5均須另批。舊資料／單次訓練預算及安全限制保留，未開始執行。

## Global Constraints

- 正式程式、凍結輸入／真值、原Node安全模組均不得修改；只新增`experiments/candidate_poc/`及新的實驗工件。
- G4整體暖機p95≤1500ms，送出畫面年齡≤2500ms，15秒內明確結果；原IoU及身份要求不變。
- 保留三peer、至少5配準對跨2行、兩張獨立一致預覽至少間隔200ms、單次點擊、UNKNOWN拒絕與來源綁定。
- 不以frameId／案例ID、真值、intent、舊座標或未來影格生成候選；不以模型信心填寫模板分數／proof。
- 新資料上限400張；單一模型／輸入尺寸／seed；單次訓練最多50 epochs或4 GPU小時，先到即止。
- 只做離線分析與虛擬點擊，0原生操作。不得安裝或更動V1／正式Python環境套件。
- 任一階段不滿足前置條件即保存證據與結論；不自動擴張模型、門檻或演算法。

## Review Focus

1. 同一地圖在影片不同時間重現，必須被視為同組，不能跨訓練與測試洩漏（Task1）。
2. 寬窄截圖及letterbox padding下仍須精確反投影；非法框拒絕而非clamp（Task2）。
3. 隱藏節點／UI圖示／浮水印不能變成可配準或可點擊證據（Task3、4）。
4. 新候選較準但原橢圓精修又覆蓋框時，不能只報模型框IoU（Task4、5）。
5. 同畫面重送、來源替換或幾何版本變動，不得透過新模型取得舊證據權限（Task4）。

## 檔案與介面邊界（皆為擬新增）

|檔案|責任|
|---|---|
|`experiments/candidate_poc/freeze_inputs.py`|新訓練資料分組、凍結評估清單、洩漏／雜湊檢查|
|`experiments/candidate_poc/proposals.py`|RGB→tensor、模型推論、source浮點框與來源封裝|
|`experiments/candidate_poc/train_export.py`|單一有界訓練、匯出、模型版本與驗證集操作點鎖定|
|`experiments/candidate_poc/evaluate.py`|候選輸出後獨立載入真值評分；不供模型使用|
|`experiments/candidate_poc/proof_bridge.py`|只用同幀原圖及既有建構器嘗試建立合法證據|
|`experiments/candidate_poc/replay.cjs`|實驗專用離線入口，沿用原Node模組，無原生輸入|
|`experiments/candidate_poc/benchmark.py`|隔離成本量測與可比條件檢查|
|`experiments/candidate_poc/test_contracts.py`、`test_data.py`、`test_metrics.py`|下列RED／GREEN契約測試|
|`artifacts/candidate-poc-<run-id>/`|新增資料索引、版本、逐幀輸出、疊圖、日誌、失敗與摘要|

不修改`ml/map_aspect.py`、`ml/preview_identity.py`、`ml/preview_registration.py`、`lib/observer-adapter.cjs`、Node Selector、Click Transaction或Preview Verifier。若隔離入口無法合法重用這些模組，停止並提出另案。

所有JSON中的`Proposal`欄位：`schemaVersion, sourcePngSha256, sourceRgbSha256, sourceSize, frameToken, modelSha256, preprocessSha256, sourceToTensor, tensorToSource, className, confidence, sourceBox`。`sourceBox`為float64 `[x,y,w,h]`；不含`verified`／權限／絕對樓層。模型session只接收tensor；`frameToken`僅由外層關聯結果。

## Task 1：鎖定基準、資料隔離與外緣標註規則

**Interfaces:** `freeze_inputs(config: dict) -> dict`，產生來源／分組／split／SHA及評估影格清單；`validate_groups(manifest: dict) -> list[str]`回傳違規，不自動搬移測試影格。

- [ ] 建立`test_data.py` RED：同一run／layout近重複跨split、凍結互動進訓練、原檔SHA改變、新來源測試無獨立來源，均回傳違規並拒絕freeze。
- [ ] 用新隔離環境執行`python -m unittest discover -s experiments/candidate_poc -p test_data.py -v`，保存RED；只因缺介面失敗不能代替資料洩漏案例。
- [ ] 實作分組及來源雜湊核對；保留既有223檔、依賴及凍結manifest的基準副本索引。
- [ ] 先核對素材能否提供240／80／80張獨立分組新資料；不得把已曝光凍結資料拿來補數。
- [ ] 對20張新資料做兩次獨立外緣標註；記錄分歧、可見／部分遮擋與光暈準則。分歧未能用可觀察邊界解決即停止外框PoC，不反推正式GT。
- [ ] 凍結7焦點1035張、12控制1573張、30負例及2評分器對照；先登記64張篩選清單，預登記後不得換容易影格。
- [ ] 重跑上述測試，保存GREEN及資料就緒／阻塞報告。未就緒則止於此，不訓練。

## Task 2：只產生提案的座標與來源契約

**Interfaces:** `propose(rgb: ndarray, session: object, config: dict) -> list[dict]`只讀像素／模型設定；`bind_proposals(proposals: list[dict], source: dict) -> list[dict]`附加來源，不能新增權限。

- [ ] 在`test_contracts.py`先建立RED：寬／窄圖letterbox往返殘差≤1e-9；超界／NaN框拒絕；同像素改frameToken推論框不變；同token換像素不能重用結果；無`verified`欄位。
- [ ] 執行`python -m unittest discover -s experiments/candidate_poc -p test_contracts.py -v`並保留RED日誌。
- [ ] 實作source→640 letterbox→float端點反投影，不clamp、不混入analysis／rectified座標；記錄實際padding／矩陣。
- [ ] 固定batch1、FP32、CPU provider與明確執行緒；環境預檢確認模型可匯出／載入並記錄所有版本。依賴不相容即報告，不改正式環境。
- [ ] 重跑契約測試至GREEN，檢查輸出程序不讀取GT、intent或其他影格；模型提案仍不授權任何交易。

## Task 3：單次訓練與鎖定候選評估

**Interfaces:** `train_export(manifest: dict, config: dict) -> dict`輸出模型與完整訓練記錄；`score_proposals(proposals_path: str, truth_manifest_path: str) -> dict`只在生成完畢後評分。

- [ ] `test_metrics.py`先建立RED：已知框的IoU正確；隱藏／部分可見與完整可見分母分開；重複預測只匹配一次；模型可讀輸入不含真值；官方mAP不能代替正式框IoU。
- [ ] 執行`python -m unittest discover -s experiments/candidate_poc -p test_metrics.py -v`保存RED；再實作最小評分與有界train/export入口，跑至GREEN。
- [ ] 以單一seed訓練一次，最多50 epochs／4 GPU小時。只在新val挑操作點、提前停止；固定後再讀鎖定測試。記錄confidence操作點，該值不改原安全閘門。
- [ ] 先跑64張篩選：沒有候選改善或明顯UI誤檢即停，報告原始數據。不得據此回頭調測試集參數。
- [ ] 有改善才跑完整2608張正例、30負例及新來源80張；逐來源／尺寸／遮擋報TP、FP、FN與框IoU，另報55～57目標框。
- [ ] D1：完整可見precision與recall @IoU.5各≥95%；55～57目標框各≥.90。失敗保存，不自動第二次訓練；D1通過亦不得寫成PREVIEW_CONFIRMED。

## Task 4：有界同幀證據橋接與安全RED

**Interfaces:** `build_evidence(rgb: ndarray, proposals: list[dict], source: dict) -> dict`只回傳既有建構器的合法輸出，或`PROOF_COMPATIBILITY_BLOCKED`與拒絕原因。`replay.cjs`只消費既有Node可獨立驗證格式；不從序列化JSON偽造私有authority。

- [ ] 先建立RED：錯來源SHA、過期、新幾何、重複影格、少於3peer、少於5對／2行及遮擋虛構對應點均拒絕；模型信心再高亦無效。
- [ ] 核對現有proof建構可用性：是否必須改舊模板專用proof或原Node規則才能接新框？若是，直接產生阻塞結論，Task4不繼續。
- [ ] 可重用時才實作隔離橋接，記錄原提案、原圖測量、最後權威框及各拒絕階段。舊外推器改框時，不得只以新提案框計分。
- [ ] 執行Python契約測試及實驗Node安全測試；確認無原生dispatch、舊證據不被新提案重新授權。
- [ ] D2通過後，以同一凍結實驗版本獨立執行7焦點及12控制完整回放，負例30及對照2一併驗證。每例失敗停止該交易，保留證據；不在批次中改演算法。
- [ ] D3以完整原評分判定，焦點7／7、控制12／12且負例無錯誤授權才可稱完整PoC閉環通過；其餘標PARTIAL或BLOCKED。保留所有未通過及來源不足的結果。

## Task 5：隔離成本、版本綁定與最終決策

**Interfaces:** `benchmark(config: dict) -> dict`核對原基準manifest／硬體／worker／warmup設定後輸出分段及端到端原始時序。不同條件時回報`NOT_COMPARABLE`，不計改善百分比。

- [ ] 先建立RED：快取命中不可列fresh、官方均值不可列本機p95、不可比較環境不得輸出改善率、晚到影格不得延長TTL／deadline。
- [ ] 建立最小計時與可比條件檢查，聚焦測試GREEN後才量測；不得同時訓練／跑其他回歸污染CPU。
- [ ] 使用同基準影格／暖機規則，分別量模型新鮮推論、證據重用、producer及完整Node因果路徑p50／p95／最慢階段。保留逐張原始時間。
- [ ] 候選p95>350ms停止擴大整合；整體p95>1500ms保留G4 FAIL，不延長期限、不進量化／多模型效能探索。
- [ ] 整理版本manifest：基準223檔hash、PoC新增檔hash、runner、環境依賴、模型、資料、標註、split、配置及所有測試結果；未執行項目明示。
- [ ] 核對正式223檔／凍結資料／舊證據未變，產生`docs/reports/crk-helper-v2-candidate-poc-results.md`及工件索引。分開呈現D1、D2、D3、G4與P5；沒有完整新60回歸就不宣稱60組結果改善。

## 決策出口與預估成本

資料／外緣不成立：停止訓練，交資料缺口與標註分歧。候選無改善：停止模型試驗，交逐來源失敗分布。候選改善但proof不相容：保留研究結果，另提證據層設計，未批准前不擴寫。完整離線成功但效能不足：標示功能有潛力、G4仍FAIL。任一錯誤授權：立即停止交易實驗並封存。

規劃量級約5～8人日，主要變數是新資料隔離、人工標註與proof相容性；不包含等待新素材或另案架構調整。不是已支出工時。每個Task到停止點即交付，不以湊滿預算延長實驗。

本計畫完成前也不推進正式模型替換、全60矩陣／正式保留集驗收或P5。批准設計只授權上述有限PoC，不推定包含後續部署。
