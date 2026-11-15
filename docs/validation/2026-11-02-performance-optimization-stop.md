# 74ad37d：功能回歸穩定，效能仍未收斂

日期：2026-11-02（Asia/Taipei）。本輪接續使用者「請繼續修正」，僅執行離線修正與驗證，未操作遊戲。

## 結論與停止點

最新提交 **`74ad37d85e3aef134d0631e0ce6a799bcb4dbe3d`**，214 個專案程式／測試／資料檔、141 個外部依賴。兩項有限修正均保留原分數公式、匹配／IoU／幾何／身份門檻、raster、來源與獨立 JavaScript 驗證、單次點擊、兩張一致預覽、逾時及拒絕規則。

**當版前42組、原生20組、固定15組、負例30組及評分器控制均通過；但原193張隔離重測的整體因果CPU p95=4033.06ms。** 仍高於既有嚴重退步保護線3561.14ms，也高於正式G4的1500ms。控制器依既有條件結束為非零，未產生第43組輸入，未開始43～60或保留集；停止後沒有修改程式。

開發分母仍為 **42通過／0失敗／18未測／60**。這次失敗的是效能閘門，不能將它記成第43組辨識或閉環失敗。G4 OPEN，P5未授權。

既有控制器的條件見 `artifacts/geometry-reuse-20261102-01/continue-phase.py`：暖機整體CPU p95超過M1基準的1.5倍即停止。這是退步診斷保護線，**不是放寬正式1500ms驗收**。亦遵循使用者先前「嚴重效能退步時停止並回報」的要求，本輪不再盲目追加最佳化。

## 實作內容與經證明的收益

### 1. c235f6a：必要家族先算、必定失敗時提前結束

- `ml/icon_ranking.py`；只接入 `ml/completed_node_candidates.py` 與 `ml/map_aspect.py` 的圖示比對內圈。
- 先算必要家族。未達原`.9`、不優於原incumbent、或原`.08`家族差距已無法成立，才提前拒絕。接受候選仍比較全17模板，winner／runner-up及分數完全相同。RGB float64轉換移出模板內圈，不改運算公式。
- 21張舊版實際RGB切片：先RED（4方法、40個subtest assertion），後GREEN4/4；分數精確相等，沒有加epsilon。模板比較357→138次。
- 同完整45張新鮮推論，候選、分數、座標、狀態與proof逐欄一致。只排除計時／程式SHA診斷欄位。
- 當版Node127／Python243通過，原193張5/5閉環通過，整體CPU p95=3519.40ms，比353b2c9的5842.53ms改善39.76%。但仍未達G4；且c235f6a未獨立完成後來74ad37d的全部大回歸，不可挪用後者的通過紀錄。
- 同45張操作剖析的NCC呼叫1026297→207907，完成候選搜尋inclusive34.86→11.87秒、orange15.28→6.64秒；插樁與多執行緒時間非可相加牆鐘，也不能作正式效能。

### 2. 74ad37d：單次完成節點搜尋內的精確分類重用

- 僅在`completed_node_candidates`一次呼叫中建立local dictionary。key含實際RGB bytes、shape、dtype與incumbent；模板與必要家族在該呼叫內固定。
- 最多1024筆，滿後照原計算，不刪候選；每次搜尋重建。沒有跨影格／來源重用，不保存座標、peer、green mask或proof。
- 真實完成前驅測試先重現110個重複分類（RED），修正後2/2通過，並驗證下一次相同搜尋重新計算。
- 原最慢診斷影格57943：四次completed搜尋的分類3988→1674；兩次orange核心共98次不重用。因此整張4086→1772，不能把整張統計說成單一次搜尋。
- 12個真實done切片的獨立primitive量測：預熱10輪、100組交錯hit／freshMiss，各切片p50的中位數hit=.0010ms、freshMiss=.0887ms。含key／dictionary／miss分類，排除crop／gray，**不是完整Producer效能**。
- 全部必要功能回歸通過，卻未證明完整p95收益：比c235f6a的整體p95高14.60%。因此此項目前只能稱為「減少重複分類」，不能稱為已合格的整體效能最佳化。

## 同193張隔離CPU比較

同一來源SHA `cd118ade5bb862a2e11225a483d4f95dfadbfe086196e8f87a0fe3eb0e269073`、執行器SHA、runtime指紋、141個依賴、平台、單worker、暖機10張，所有影格新鮮分析／0 raw cache；量測時沒有其他專案推論或測試並行。

|版本|Producer p50／p95 ms|Node p50／p95 ms|整體因果CPU p50／p95 ms|
|---|---:|---:|---:|
|M1 9944a9d比較基準|1718.68／2292.35|2.30／4.29|1688.88／2374.09|
|353b2c9修正前|3801.97／5015.00|2.82／5.03|3699.63／5842.53|
|c235f6a第一項修正|2797.87／3569.71|2.53／4.35|2780.82／3519.40|
|74ad37d加入局部重用|2795.58／4048.28|2.59／4.25|2676.76／4033.06|

Producer統計暖機後183張；Node及整體因果CPU統計124張實際因果消費影格。不得相加各模組p95推算整體p95。排除capture、IPC與報告I/O，不是實機延遲；CPU頻率、溫度、RSS與OS背景負載未記錄，因此軟體及資料可比不代表已排除所有環境因子。

當版整體p95比353b2c9改善30.97%，但仍超出嚴重退步保護線 **471.92ms**。比c235f6a的整體p50改善約3.74%，p95卻退步14.60%，不能只選中位數宣布改善。

### 新的尾延遲證據

|模組|c235f6a p95 ms|74ad37d p95 ms|
|---|---:|---:|
|v1_observation|1137.58|1297.66|
|baseline_geometry|1002.51|1004.38|
|aspect_geometry|1067.07|1129.63|
|source_coverage|530.70|508.12|
|preview_registration|391.99|376.97|

同193張逐影格比較：**全部語義一致，原始候選呼叫的hit／尺寸／scan-reuse模式也完全相同**。最慢影格為S2 57963，Producer4320.13ms，其中v1_observation1492.42ms。相對c235f6a相同影格，總時間+718.54ms：v1_observation+368.19、baseline_geometry+88.37、aspect_geometry+168.51、source_coverage+52.96ms，其餘為小項。

未修改的v1模組也變慢，且原始候選呼叫模式未增加。這不能證明局部dictionary一定是退步原因，也不能證明它與尾延遲無關；可能涉及記憶體／排程／環境或其他共同成本，**目前無法確認因果**。需要同環境受控A/B，不能再憑微基準或函式名稱猜測。

## 當版驗證與證據

以下均在74ad37d／214檔下實際執行，舊353b2c9結果未當作新通過：

|驗證|實際結果|證據（相對專案根目錄）|
|---|---|---|
|完整單元|Node127/127；Python245/245|`artifacts/geometry-reuse-20261102-01/unit-validation.json`、`unit-execution-provenance.json`|
|31／41／42聚焦|3/3；560新鮮；0 raw cache；各1虛擬點擊|同namespace `focus3-current-02/report.json`|
|前42組完整回歸|42/42；2114新鮮；最小IoU .9063514553、margin14.8325px|`prefix42-summary.json`、`prefix42-current-01/replay.log`|
|原生20|20/20；1551新鮮；最小IoU .9134257694、margin16.6650px|`native20-summary.json`|
|固定15|15/15；381新鮮|`fixed15-current-01/report.json`|
|負例與評分器|30/30；57新鮮／57包；2控制正確；0虛擬點擊|`negative30-current-01/report.json`、`negative30-current-integrity.json`|
|原生候選稽核|1551張；30變動／30群組／46差異；七張完整疊圖及46045已檢視；0新增錯誤／0原有效候選遺失／0anchorLoss|`native1551-seven-current-01/report.json`、`native-review-prep/`、`native-candidate-changes-reviewed.json`|
|正例證據完整性|4606來源紀錄／3654包／18270檔／80交易，雜湊通過；含套件間重複，非80張獨立地圖|`positive-integrity.json`|
|取整壓力|42/42衍生案例，未改60／30分母|`rounding-stress.json`|
|matcher成本|6 raster各15配對，完整舊prefix保留及實際額外掃描成本|`matcher-benchmark.json`、`matcher-benchmark.log`|
|原193張|5/5功能閉環；193新鮮；**效能閘門失敗**|`producer-isolated-01/performance.json`、`performance-comparison.json`、`incremental-performance-tail-analysis.json`|

負例中的三個缺少區域上下文案例，在第一張UNKNOWN便拒絕，不取下一張補過；`formalNegativeGateComplete=false`保留，不冒稱G4正式負例完成。所有測試nativeActions=0。

1551候選稽核沒有證明全圖召回100%。S3-46047仍可見未框出的左側battle；S3-46047／46057、S2-35929保持OPEN，局部已有候選或某段閉環通過不能替代完整獨立GT。46045的原有效battle框[792,512,74.67,81.33]保留，absolute=false，不能猜測授權。

補充incremental比對器曾誤讀原生清單中尚未更新的歷史packet指向。已保留誤報與舊腳本，增加「必須屬於本輪analysis目錄」檢查，再重核560／2114／1551／381張，全部語義一致。這不是正式回歸通過的來源；詳見前一份[過程報告](2026-11-02-geometry-ranking-performance.md)。

## 保存與不可挪用事項

- `source-freeze.json`綁定提交、214檔、141依賴與runtime。`stop-verification.json`確認停止後程式、兩個凍結manifest與HEAD未變。
- 嚴重效能失敗的控制器、日誌、版本與performance已另存 `performance-stop-before-any-next-step/`。先前人工稽核檢查點亦保留於 `manual-review-checkpoint-before-resume/`，不能將檢查點視為案例失敗。
- `qualification.json`／`continuation.json`最後為stopped，原因`SEVERE_PRODUCER_LATENCY_REGRESSION`；不是全部閘門通過。
- c235f6a的3519ms不能當作74ad37d的當版速度；原生／單元通過不能當作實機驗收；新primitive重用成本不能當作新鮮Producer速度。
- 第43～60未執行，保留集未啟動，沒有重挑畫面、降低門檻、延長TTL／deadline、跳過UNKNOWN、沿用舊座標或重訓模型。

## 下一步最小方案（尚未執行）

1. 維持74ad37d與c235f6a各自不可變證據，先做同環境受控交錯A/B；記錄CPU／OS負載、RSS、每影格各階段及NCC／OCR呼叫數，分開比較局部重用開／關。若使用診斷注入，明確標示，不冒稱正式版本驗收。
2. 先用完整效能量測淘汰沒有穩定p95收益的候選，再凍結候選做大回歸。本輪第二項修正先跑完整大回歸才重測193張，增加了等待成本，下一輪應調整順序。
3. 依已量出的共通成本，優先評估原始像素HSV重算與連線採樣（`F:/CRK helper/ml/map_vision.py:104`，45張診斷2690次line_evidence約12.33秒inclusive），及兩幾何階段的必要重複工作。只先驗證數學等價、實際收益，不直接更換模型／全面重寫。現有增加模板的獨立成本仍高，不能用減少必要模板或放寬門檻掩蓋。
4. 局部重用僅在受控完整p95實證穩定後保留；否則撤回該項，再以新實際來源版本重驗。不能把c235f6a的速度與74ad37d的回歸拼接宣稱同一版本合格。
5. 必要回歸與效能穩定後才恢復43～60；60全部通過後才保留集。即使低於3561ms保護線，正式G4仍須1500ms及其他原驗收條件。若確定需要架構重設、換模型或更動原條件，另取使用者批准；P5仍需單獨批准。

目前有可追溯的功能穩定證據及第一項最佳化收益，但整體效能尚未收斂。這是階段結果，**不是60/60完成報告，也不是G4完成或實機通過**。
