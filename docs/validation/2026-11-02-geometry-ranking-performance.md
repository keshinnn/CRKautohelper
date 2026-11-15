# 最新結果：74ad37d效能停止，功能回歸通過

本文件保留各階段過程記錄。最終當版193張整體因果CPU p95=4033.06ms，仍超出3561.14ms退步保護線及正式1500ms；第43～60及保留集未開始。完整當版回歸、失敗分析與後續方案見[最終階段報告](2026-11-02-performance-optimization-stop.md)。c235f6a3519ms是中間版，不是74ad37d結果。以下「待完成／正在執行」僅記錄當時狀態。

---

# 幾何模板比對：等價提前淘汰與效能驗證

本輪接續使用者「請繼續修正」的指示。程式版本 `c235f6a864d08797671d7840c0fcbc5f660c5cda`；213 個程式／資料檔案的 SHA 與原 runtime、141 個外部依賴綁定於 `artifacts/geometry-perf-20261102-01/source-freeze.json`。不進行實機操作。

## 已實作範圍

新增 `ml/icon_ranking.py`，僅替換 `completed_node_candidates.py` 與 `map_aspect.py` 的圖示分類內圈。原作法對每個 bounded-alignment 切片先比對全部 17 個模板，再檢查必要家族分數、差距與 incumbent。新作法先比對必要家族；若原 `.9` 分數門檻、原 incumbent 條件或原 `.08` 家族差距已必定失敗，便停止剩餘比較。接受的候選仍比較全部模板，winner／runner-up tuple 及數值完全沿用原計算。

未修改校準演算法、raster、幾何路由、候選門檻、IoU、三 peer、身份與來源驗證、交易狀態、TTL 或期限。沒有新增跨影格快取，沒有省略第二輪幾何處理。

## 實際驗證

- 舊版 353b2c9 實際執行捕捉 21 張 34×34 RGB 切片：完成圖示 12 張、orange 核心 9 張，保存來源 PNG／函式 SHA、原 winner／other／incumbent 及拒絕原因。不是變更凍結測試資料。
- `ranking-red.log`：4 個測試方法、40 個 subtest assertion 失敗，原因為必要分類模組尚未實作。`ranking-green.log`：4/4 通過；接受分數使用精確相等，沒有新增浮點容差。
- 完成節點聚焦 2/2，原幾何路由與關閉共用控制 3/3 通過，日誌 `completed-focused.log`、`parity-focused.log`。
- Python 全套 **243/243**（381.910 秒），Node 全套 **127/127**（84.973 秒）。`unit-validation.json` 記錄實際日誌 SHA；測試於提交前相同 working bytes 執行，提交後核對 213 檔 SHA 一致。這不是當版完整閉環回歸。
- 最慢既有影格所屬完整 45 張片段，全部重新推論，逐欄比較舊版未插樁的原 193 張基準中相同來源影格：**45/45 語義一致**。只排除 `analysisTiming`、`frameIntermediates`、程式 SHA 及 OCR recognition crop 的 `elapsedMs`，候選、分數、座標、來源、狀態與 proof 不排除。證據 `fresh45-comparison.json`、`fresh45-after/manifest.json`。
- 45 張局部比較：舊 p50/p95 4573.29/6050.49 ms，新 3485.37/3718.13 ms。此比較暖機及樣本位置不同，**只屬診斷，不能充作正式193張或G4效能**。
- 21 張圖示交錯 100 組 old/new、預熱10組、計時與呼叫次數分開測量：模板比對總次數 357→138；各切片 p50 的中位數 0.3835→0.0454 ms。接受結果仍全17模板。證據 `ranking-benchmark.json`，僅分類內圈，不是整體加速比例。

## 原193張隔離CPU基準

193/193新鮮分析、0 raw cache、5/5離線閉環、5虛擬點擊／0實機操作。使用原資料SHA `cd118ade5bb862a2e11225a483d4f95dfadbfe086196e8f87a0fe3eb0e269073`，與353b2c9相同執行器、runtime、141外部依賴、平台、單worker及暖機10張。沒有其他專案測試／推論並行。

|指標|353b2c9 p50／p95 ms|c235f6a p50／p95 ms|樣本|
|---|---:|---:|---:|
|Producer|3801.97／5015.00|2797.87／3569.71|183|
|Node因果路徑|2.82／5.03|2.53／4.35|124|
|Producer＋Node因果CPU|3699.63／5842.53|2780.82／3519.40|124|

整體CPU p95改善39.76%，低於既有M1×1.5的嚴重退步診斷保護線3561.14ms，但仍高於正式1500ms。不是實機延遲，未包含capture／IPC／報告I/O；CPU頻率／溫度未記錄，不能將所有差異完全歸因程式。證據 `producer-isolated-01/performance.json`、`performance-comparison.json`（比較器核對可比條件與全部213檔SHA）。

## 待完成與狀態

當版前42組、原生20組、固定15組、正式負例與1551／七張候選稽核仍須在新版本重跑，舊353b2c9結果不能代替。5/5基準閉環也不能代替42組全回歸。下一步針對同45張進行操作級剖析，核對剩餘成本及完全相同的純像素計算是否重複；僅觀察，尚未增加快取或跳過任何處理。

歷史開發分母仍42通過／18未測；不得將本輪45張或分類切片計為新開發組別通過。43～60及保留集尚未啟動。G4維持OPEN，正式整體暖機p95≤1500ms；P5未授權。

## 第二項局部修正：74ad37d

45張操作剖析的NCC呼叫1026297→207907；完成候選搜尋inclusive34.86→11.87秒、orange15.28→6.64秒（插樁總時間非可加牆鐘／G4）。在原最慢57943另量測各次搜尋內重複輸入：整張影格4086→1772次分類；其中四次completed搜尋3988→1674，兩次orange核心98次不重用。不同輸入按各次呼叫的RGB、gray、模板、incumbent分開計算。只在同一次completed_node_candidates呼叫建立最多1024筆local dictionary，key含RGB bytes、shape、dtype、incumbent；模板／必要家族在該呼叫內固定。滿後繼續計算，每次呼叫均清空；不保存座標、peer、green mask或proof。

`reuse-red.log`重現110次重複分類，`reuse-green.log`2/2通過並驗證第二次相同搜尋重新計算。原最慢影格新執行1772次（completed1674＋orange98），證據 `artifacts/geometry-reuse-20261102-01/ranking-repeats.json`；量測runner原「No cache enabled」描述僅指其wrapper，已保留原檔並附更正，production local reuse實際啟用。45張再次逐欄一致，局部p95=3609.22ms，不能當原193張驗收。

新版本 `74ad37d85e3aef134d0631e0ce6a799bcb4dbe3d`、214檔，Node127/127、Python245/245（377.961秒）通過，pre-unit snapshot與提交後SHA一致。31／41／42聚焦560張新鮮分析／0 raw cache／三組PREVIEW_CONFIRMED／三次虛擬點擊／0 native已全數通過，IoU分別.9358738154／.9325455452／.9575602462，margin19.1081／25.0781／28.4973px，與353b2c9一致；完整560張語義逐欄亦一致。正在前42組及全部必要回歸；原193張隔離基準亦須重跑。新namespace的 `source-freeze.json`、`unit-validation.json`、`qualification.json`與完整日誌不覆寫c235f6a或353b2c9。既有整支分支審查保留為歷史，未冒稱新分類修正已重新做整支審查。


74ad37d前42組完整回歸已完成：42/42、2114張新鮮、0 raw cache、42次各單次虛擬點擊／0 native，全部PREVIEW_CONFIRMED。完整2114張語義逐欄一致；minimum IoU與margin見geometry-reuse namespace的prefix42-summary.json。正在原生20組回歸，尚非全部必要閘門完成，G4仍OPEN。

### 補充比對工具的錯誤紀錄

原生來源本身含歷史analysis的packet路徑。分析清單逐張更新時，尚未處理的影格仍保留歷史指向。補充incremental語義比對器原只檢查檔案存在，錯將未完成影格的舊packet也讀入，誤報已比較1551張及大量差異。原始錯誤報告、修改前腳本與第一項差異追查均保留在geometry-reuse namespace（`native20-incremental-invalid-unprocessed-references.json`、`*-before-output-path-guard.py`、`native-diagnostic-first-difference.json`）。

確認清單當時只有694個本輪路徑、857個歷史路徑，例如S3的46108仍指向`p4c-development-20-v3-analysis-01`。修正補充工具，必須packet實際路徑位於該分片本輪analysis目錄才讀取；未產出的僅標示未比較，不計入新鮮結果。修正後701個實際本輪packet全部語義一致，0差異；另重核已完成的560與2114張。這是診斷工具的路徑／進度錯誤，未修改正式回歸執行器、沒有依它授權點擊或產生正式通過標記。完整原生20組結果仍等待當版執行完成。


74ad37d原生20組亦已完整通過：20/20、1551張新鮮、0 raw cache、20次單次虛擬點擊／0 native，全部PREVIEW_CONFIRMED；完整1551張語義逐欄一致（已加本輪路徑檢查）。minimum IoU／margin見native20-summary.json。開始固定15組，候選稽核及效能等必要閘門尚未完成。


74ad37d固定縮放15組完整通過：15/15、381張新鮮、0 raw cache、0 native；381張語義逐欄一致。前42＋原生20＋固定15的必要正例已完成，仍須負例／評分器控制、1551與七張候選稽核、證據完整性、取整壓力及193張隔離效能。


74ad37d負例30及兩個評分器控制已實際通過，0虛擬／0native；formalNegativeGateComplete仍false，不冒稱G4正式負例完成。1551稽核中30個變動影格、30精確群組、46差異卡與七張完整疊圖及46045均已由主代理實際檢視，0新增錯誤候選／0原有效候選遺失／0anchorLoss。46045仍4候選、原有效battle框[792,512,74.67,81.33]保留，absolute=false。S3-46047仍可見左側battle未框出，已知缺陷保持OPEN；不宣稱全圖召回。綁定本輪auditSHA的manual marker已保存，檢查點舊錯誤／日誌保留於manual-review-checkpoint-before-resume，無新程式修改即接續驗證。

新增分類重用的獨立primitive成本：12真實done切片，預熱10輪、100組交錯hit／freshMiss，含key RGB bytes、dictionary操作與miss時精確分類，排除crop／gray。各切片p50之中位數hit=.0010ms、freshMiss=.0887ms；是primitive，不能代替完整193張效能。證據classification-cache-cost.json，production沒有跨影格重用。
