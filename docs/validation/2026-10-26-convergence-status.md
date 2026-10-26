# V2 座標／預覽收斂驗證紀錄

狀態：**已完成本輪收斂並停在第39組；功能回歸穩定，效能未達標。**2026-10-26～27執行；停止點維持第39組，不執行40–60、保留集或實機。此文件不宣稱G4／G5完成。

## 基準與範圍

基準f38af719cfe90b3da59abe74f629e9d0e282c380；實作計畫位於 `../superpowers/plans/2026-10-26-geometry-preview-convergence.md`。新結果保存在 `artifacts/convergence-20261026/`，舊報告／失敗圖未覆寫。

基準Node113/113、Python150/150；本次基準日誌 `baseline-node.log`／`baseline-python.log`。所有閉環均是離線虛擬點擊。

## 第39組根因

57947的原始候選為0。比例量測成功（ratio1.30414724468），校正1574×1191後有9個候選，但無唯一四欄格點；recover_map_aspect保留原始空地圖，配準無節點對，身份未證，adapter的MAP stateVerified=false導致EVIDENCE_UNVERIFIED。不是單純缺少新尺寸根：57931–57944已有直接根。

原程式將控制項驗證放在地圖錨點驗證之後，因此「控制項足夠等待、地圖暫不足確認」的能力無法表達。拆出普通預覽控制時，另確認57947時間標籤舊OCR=.7305低於既有.75門檻；本張原像素裁切重讀=.83113566637，時間數字另以原.95門檻重讀。沒有提升舊分數或降低門檻。

修正引入source-bound PREVIEW_PENDING：只可在既有已送出交易等待，不可選點、確認身份或建立map root。等待清空穩定預覽對，不重設deadline。57947未跳過，後續影格按原序到達後才確認。

聚焦 `case39-analysis-02` 共45張分析（raw V1 cache有明示，V2當前重算）；`case39-replay-02` 通過，29張消費影格、IoU=.93916365618、邊距29.52312021116px、虛擬點擊1、原生0。這不是最終完整回歸。

## 已發現並處理的迴歸

新全精度投影先使完成外框修復的獨立.01取整暴露，Node完整測試118/119；`completed extent refinement keeps model score and independently binds source pixels`失敗。完成producer改走新契約投影後聚焦轉綠。Python完整測試曾有4個相容性錯誤（診斷packet沒有capture frameId、舊timer helper匯入）；保留明確非權威診斷與helper別名後，相關17個比例與3個timer測試轉綠。舊失敗日誌保留。

## 獨立審查與修正清單

首輪範圍f38..7891116；審查未執行模型或遊戲，沒有Critical，四項Important須在最終驗證前修正：

1. V1實際模型尺寸採Python ties-even；新raster half-up不可宣稱為V1的實際analysis尺寸。需集中、分階段明訂量化，JS獨立要求實際尺寸。
2. 等待上下文需核對原始OCR列及timer-label衍生裁切來源，不可只看context內分數。
3. 新契約certificate移除時不可自動降級舊容差；由外部觀察封包版本決定規約。
4. 回歸快照需納外部V1辨識程式、PNG模板及OCR資產，並比較分片runtime指紋。

以上為首輪審查當時狀態；後續修正與當版實測如下，不能把首輪或更舊通過當成本輪結果。

## 最終階段結果

辨識／lib功能版本 `8aa11113906b91843dbec7200fcd146503a25a5c`；最終工具版本 `f88cb93c992ce2c17ec88a5eac6c847115e22ce9`，其後修改僅在測試工具與Python工具測試，ML／lib逐byte一致。

|驗證|實測結果|證據|
|---|---|---|
|新增#23的五組聚焦|5/5閉環，193/193新鮮影格|`artifacts/convergence-20261026/focus5-run-01/report.json`；此輪在138da39，當前ML相同，之後補原生JS尺寸與基準統計|
|最新Node全套|124/124，0失敗|`node-final-04.log`，331.843005秒；f017執行，之後Node測試／lib／ML未變，另以f88重新跑74組交易與原grader|
|最新Python全套|168/168，0失敗|`python-final-06.log`，415.139秒；f88執行|
|原成功38＋#39|**39/39當版閉環通過**，39次虛擬點擊、0原生|`random39-final-02/report.json`；1318張當版V2重算，明示raw V1 cache1318張；f88另以byte-identical producer證據重新交易／評分|
|原始尺寸20|20/20閉環；1551/1551新鮮分析|`native20-final-02/report.json`；無cache；f88另重新交易／評分|
|固定75%／100%／125%|15/15閉環；381/381新鮮分析|`fixed15-final-03/report.json`；五片段×三倍率，P4-B原標註／原grader|
|既有負例子集|30/30拒絕；57張實際新鮮分析，另兩項grader對照通過|`negative30-final-04/report.json`；3組在首張UNKNOWN即保存拒絕，未假稱60張全部推論；正式完整負例gate仍false|
|最終當版完整正例回歸|74/74次重新交易與原grader通過|`positive74-current-final-02/report.json`；0原生，非新推論|
|完整五類證據hash稽核|2403份bundle／12015檔／74當版transaction|`release-evidence-check.json`，全部吻合|

39組最小IoU=.9063514552647348，最小安全邊距14.832526346613975px。#39在57945／57946／57947／57949明確等待；57948雖已匹配，57949等待使它無法被用來形成穩定對；57950重新起算、57956相隔200ms後確認。#23在30116至30122形成獨立預覽穩定證據；每交易仍只點一次。

`random39-final-01` 保存本輪第23組退步：全1318張新鮮推論後，22組通過，第23組在第6張消費影格失敗。根因是V1便利縮放先將框與中心獨立取整，來源中心偏差.01271260997超過原.011；新 `map_observer` 取原960量測並保存detectorGeometry。新CJS測試另篡改原模型框.001，必須拒絕；不是把來源中心改成想要的值或提高容差。

快取取捨：只重用上述失敗輪中依賴未變的raw V1輸出，不重用任何舊grade。已比對141個外部依賴、6個本地原始觀察模組及6個校準函式AST；輸入PNG／source index／video／runtime亦核對。證據 `raw-v1-cache-compatibility-v2.json`。所有新的V2候選恢復／兩段座標投影／配準／控制／身份與交易重新執行；此輪耗時不作新鮮性能基準。原始20、固定15及隔離基準另跑新鮮分析。

獨立審查新增4492bac..8aa1111的模型邊界修正後未發現Critical／Important；這是靜態審查，沒有把它當影片通過紀錄。

## 原始1551影格與七張歷史變動的當版核對

`native20-final-02/report.json`：20/20、1551/1551全新鮮分析，0 raw cache；S1–S4均包含。`native-audit-final-02/report.json`逐張比對不可變來源PNG／index／PTS，當版24張候選內容與最早原始分析不同，既有絕對錨點遺失0。24不等於24個錯誤：包含框中心精度差、恢復候選、相對ID重排；逐項欄位差另存`candidate-differences.json`，不能單靠ID比較推論實體類型變更。

|來源／影格|最早候選→當版|當版核對／限制|
|---|---|---|
|S1／14546|13→14|14個可見地圖物件有框，補回完成前驅；exit與選中二層三欄位置正確；PREVIEW確認|
|S3／46047|15→14|滾動模糊，資源列遮住頂部exit；下方x720,y616戰鬥漏框；anchorVerified=false|
|S3／46049|16→16|16個完整可見一般節點有框；底邊部分圖示及被遮gate未當絕對錨點|
|S3／46051|18→20|底列進入畫面後20個一般節點有框；exit仍截斷，沒有絕對錨點|
|S3／46052|20→20|20個一般節點有框；數量相等不表示幾何相同，exit截斷|
|S3／46056|18→17|頂列穿過資源UI，相對節點ID重排；partial boss未當普通節點／絕對錨點|
|S3／46057|16→16|x500,y455可見heal漏框；頂列UI重疊及底邊partial boss不提供絕對錨點|

七張當版input／observation／overlay／events／result及hash位於`native-audit-final-02/{case}-{frame}/`；人工可見位置核對與保留缺陷為`semantic-review.json`，另外以hash綁原始稽核報告。原始report的`pixelSemanticReviewComplete=false`不回寫，後續審閱為獨立附錄。六張S3均可觀察MAP但`anchorVerified=false`；Selector仍明確要求錨點，不能授予新選點。兩個父片段的完整當版離線回放通過，代表本次操作閉環穩定，**不代表七張每個可見節點都辨識完整、或整部影片100%準確**。

## 固定倍率工具相容性修正

`fixed15-final-02`已完整推論381張，但通用development CLI在任何交易前拒絕既有`scale-0.75`名稱，錯誤`CASE_ID_INVALID`。此輪不算15組辨識失敗或閉環成功。改由controller按既有P4-A/P4-B metadata選擇原`accept-replay.cjs`，使用不可變`data/p4a/cases.json`，不改案例ID或放寬路徑規則；固定scale由原P4-B grader核對。

同時補傳FrameEnvelope的外部observerContractVersion；實際v1 envelope搭配移除packet版本／certificate的降級負向測試，舊入口會接受、修正後不送點擊且拒絕。聚焦RED02／GREEN02保存在`fixed-schema-*.log`，Python入口路由聚焦`fixed-runner-*.log`。初版用未定義schema2的測試不符合既有v1契約，已更換成真正降級情境，未把錯誤測試當修正證據。

工具版本`f0170672394de6985371b3af9630e31a70047754`；相較8aa，ml/lib完全未改。`replays-current-03`將再次執行全39＋20組JS交易，綁當版工具、每一packet hash及來源；先證明producer／核心／外部資產逐byte一致才重用既有V2分析。此項不宣稱重新推論；固定15、負例與隔離基準另外新鮮推論。

## 最終工具版本與驗收邊界

`negative30-final-02`的30組新鮮負例都拒絕，但後續對照選到random39的raw cache，grader保留的freshFullPipeline檢查正確阻擋。該彙總仍標失敗，不以30/30子結果宣稱總門檻完成。工具修正`793800af51d7dc2d9731c1c72a367ed668e402f7`加入明確`--control-case`與執行前的新鮮檢查；使用`native20-final-02`同一來源zone-2-first-battle實際新鮮前兩張，原曾假設其第1欄為灰色，但當版對照實際建立proof而使彙總03失敗；這是工具的錯誤意圖，不是Selector退步。最後f88採已凍結且本輪新鮮分析的`neg-native-gray-node-random-1`作gray對照，保留其來源／原意圖／原拒絕條件；原生zone2案例只作eligible對照。沒有改動凍結30負例、ML、lib、IoU或負例評分器。

`positive74-current-final-02/report.json`是工具修正後重新執行的74次完整閉環評分（39隨機變換＋20原始＋15固定；案例互有重疊，**不是74張不同地圖**）。每一組重新執行Observer Adapter→Selector→Geometry／交易→Preview Verifier及原先幾何／身份grader；保存當版交易與其hash，連結之前完整五類證據。僅在當前ml/lib及141個外部依賴逐byte相同時重用producer packet，另外記錄全部packet hash。這不是新推論，也不是搬用舊PASS。

G4／G5仍未完成：第40–60、保留集30變換、完整正式負例門檻、實際capture／IPC畫面年齡／DPI及P5原生點擊均未在這個停止點驗收。原始20包含S3/S4只能證明已測原始片段，不代表其所有隨機變換已通過；不能把中間成功改稱正式G4。實機操作保持0，V1流程未改。

## 本輪明確取捨與剩餘限制

1. 沿用專用V2 repo／分支，保留大型忽略區資料；沒有另複製worktree。若隔離判斷錯，會混入原工作樹內容；以起始基準、逐檔hash與不改V1控制風險。
2. 依使用者已批准的方向直接執行，不另要求小修批准；若方向理解錯會增加工作量，但未越過實機／重構／標準變更的批准界線。
3. 將偶然的peer ID常數斷言改成實體來源框綁定，保留錯peer拒絕。代價是無法靠該常數測出偏好變化；實體綁定與完整回放才是安全條件。
4. raw V1 cache僅在141外部、6本地模組及6函式AST依賴一致時重用；當版V2重算並用193張新鮮聚焦補證。漏列依賴會導致陳舊分類風險，因此不拿此輪當效能證據。
5. 工具專屬修正後的74組回歸重用已證明當版ml/lib完全相同的V2 packet，重新交易／評分；代價是不能稱全新推論。原始1551、固定381、負例與隔離基準分開記錄新鮮來源，避免混淆。

獨立審查範圍至8aa，沒有未處理的審查Critical／Important；之後工具修正由作者以聚焦RED/GREEN與當版完整回歸核對，不宣稱獨立審查已涵蓋所有後續工具。七張核對保留兩張漏候選、正式G4／P5及效能未達標範圍；既有測試依賴忽略區fixture和本機V1／OCR資產，尚不能宣稱乾淨clone可完整自足執行。


## 隔離新鮮效能基準與最後停止結論

`isolated-baseline-final-01/performance.json`，f88、單一project推論worker、無cache、193張全部新鮮，前10張暖機；量測期間沒有其他專案單元／模型推論工作。這是離線CPU基準，並非獨占作業系統或實際capture／IPC端到端延遲；非推論檔案稽核屬一般背景I/O。原5段閉環另外再次通過。

|量測|樣本數|p50 ms|p95 ms|
|---|---:|---:|---:|
|Python完整producer|183|2767.417|4370.174|
|Node因果交易路徑|127|3.549|10.589|
|producer＋Node整體CPU|127|2708.224|4292.450|

producer統計採183張暖機後完整分析；整體採實際消費的127張因果回放影格，兩母體不同，不能直接比較或相減分位數。整體CPU合計包含同張producer與Node觀察／選擇／交易／預覽驗證，不含live capture／IPC、載入及報告I/O。

|Producer模組|p50 ms|p95 ms|
|---|---:|---:|
|aspect_geometry|1431.082|2655.304|
|decode_binding|33.453|45.655|
|map_actions|12.923|18.439|
|preview_controls|8.924|144.413|
|preview_identity|10.830|31.270|
|preview_registration|0.017|490.718|
|progress|0.132|0.311|
|sparse_geometry|5.267|8.604|
|v1_observation|1285.633|1868.693|

**效能未通過：整體p95=4292.450ms > 1500ms；producer本身p95=4370.174ms。** 最大成本在aspect_geometry與v1_observation；各模組p95不能相加。畫面送出年齡≤2500ms及真實15秒內結果未經live驗收，不能因虛擬時序交易通過而宣稱達標。沒有延長TTL／deadline、調低門檻、使用過期畫面或進行效能優化。

本輪停止條件已達：#39完整通過、座標／等待契約收斂、必要功能回歸穩定並保存未達標效能。**停止於39/60，未執行40–60、保留集或P5。** 下階段若另行授權，應先處理已量出的共通效能成本，再恢復剩餘變換；目前不適合宣稱G4完成或進入實機驗收。

最終彙總與各報告SHA：`artifacts/convergence-20261026/checkpoint-summary.json`。所列結果均保留producer／當版交易／工具版本差異，沒有把舊版本PASS搬成當版結果。最後文件／圖譜提交不變更上述功能檔hash；實作保留在`codex/v2-minimal-loop`，不merge／push。
