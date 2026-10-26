# CRK Helper V2 — 閉環測試階段性技術審查報告

審查日期：2026-10-26（Asia/Taipei）  
審查版本：`f38af719cfe90b3da59abe74f629e9d0e282c380`，分支 `codex/v2-minimal-loop`。  
工作目錄：`C:/Users/User/Documents/Codex/CRK-Helper-V2`。  
性質：**現存程式、Git、測試紀錄及證據的唯讀審查；不是新一輪測試結果。**

**結論：C．需要局部架構調整。** 最小閉環的核心交易與拒絕機制已有實質證據，但座標規約、觀察證據適配及預覽時序仍反覆失敗。應保留現有辨識／輸入與測試集合，先釐清這些共通介面，再繼續剩餘案例。沒有證據支持全面重寫或立即重訓模型，也不能宣布可進入實機驗收。

本次未修改程式、未新增或執行測試、未操作遊戲。原本執行中的測試已在第39組遇到失敗後依既有規則自然停止，控制器亦已結束；未強制中斷或重新啟動。本次唯一新增專案檔案為本報告。

## 0. 審查方法與證據解讀

以[設計](../superpowers/specs/2026-10-24-crk-helper-v2-design.md)、[P0–P3計畫](../superpowers/plans/2026-10-24-crk-helper-v2-p0-p3-plan.md)、[P4-C計畫](../superpowers/plans/2026-10-24-crk-helper-v2-p4c-plan.md)、[進度紀錄](../../progress.md)，對照當前程式與保存工件。使用已可運作的 Graphify 查詢模組關係；Serena 唯讀核對沿用的 V1 `ml/observation.py:inspect_capture`，確認地圖觀察仍受舊畫面分類前置條件影響。未安裝、修復或更新工具／索引。

主要結論依據：

- [當前60組執行報告](../../artifacts/p4c-random-development-60-run-25/report.json)及逐組交易，並非只採用進度文字。
- [36組彙總](../../artifacts/p4c-sparse-peer-controls-thirtysix-replay-01/report.json)、[35組完整新鮮辨識稽核](../../artifacts/p4c-sparse-peer-current35-fresh-audit-01.json)、[版本／單元閘門](../../artifacts/p4c-sparse-peer-continuation-01/gates.json)。
- 本次重新讀取38個成功交易：均為 `PREVIEW_CONFIRMED`、一次虛擬點擊、零原生操作。重新核對其856份工件 manifest 所列4280個檔案 SHA；這是檔案完整性稽核，沒有重新執行辨識。
- 版本閘門所列42個關鍵檔案雜湊與審查時工作樹一致。主執行報告的 commit 欄位可能仍指向提交前的 `37cfaad`；本報告以實際檔案 hash 對應 `f38af71`，不竄改舊報告。
- 歷史「首次結果」僅納入能對上凍結案例的完整影格索引、PNG hash、尺寸及意圖的紀錄。部分記錄缺少逐次補丁對照，因此修正次數不能精確還原。

本文「通過」必須附範圍：單元通過、某次版本的離線閉環通過，或實機驗收通過。沒有保存紀錄者寫「無法確認」；未執行不等於失敗，也不等於通過。大量工件位於 Git 忽略的 `artifacts/`；本機路徑可追溯不代表乾淨 clone 自動包含它們。

## 一、開發進度總覽

### 1.1 目前完成與未完成

已實作獨立 V2 流程：帶來源的畫面封包、地圖觀察適配、兩幀唯一節點選擇、座標換算、單次虛擬點擊交易、獨立預覽身份確認、逾時／不確定拒絕，以及逐幀輸入圖、辨識輸出、疊圖、事件及結果保存。既有辨識與輸入模組仍沿用；沒有改成完整自動遠征，也沒有全面重訓模型。

尚未完成：60組開發隨機變換閉環、保留集、當前版本完整原生回歸、最終負例矩陣及正式效能驗收。真實布局、DPI、工具列／黑邊、原生點擊及跨尺寸操作尚未由 P5 證明。選角、隊伍／寶物變更、戰鬥技能、戰後進度及跨區域遠征均不屬於本次最小閉環，不能因本階段進展宣稱完成。

與批准方向整體一致：保留 V1，V2 停在關卡預覽，不按「進入」。主要偏差是原先期望的「薄觀察介面＋統一可逆座標鏈」已逐漸變成多處座標投影與較厚的證據適配層；需要局部收斂。

### 1.2 「60組」的正確分母

|集合|數量與當前狀態|可以證明／不能證明|
|---|---|---|
|凍結真實原始互動|30段：20開發、10保留；4部來源影片；3004張原生影格（1551開發／1453保留）|互動片段及標註已備齊；不是30部不同影片|
|三種隨機變換|90條序列、9042張渲染圖：開發60條4673張，保留30條4369張|固定、點前變更、點後變更各一；圖片準備不等於模型或閉環通過|
|本次所稱60組|**38成功、1失敗、21未測試**|成功占分母63.33%；已嘗試39組中38成功（97.44%），是多輪修正後結果，非首次／未知資料準確率|
|目前38成功的來源覆蓋|13段來源互動：12段三變換全過、另一段過兩種；目前涉及S1、S2兩部影片|不是38張不同地圖；同一節點選取與續開也不能算不同物理節點|
|保留集30條變換|尚未完成模型推論／閉環；只有來源審閱與渲染|不得拿來補足開發成功數，也不能稱完全未經人眼接觸|
|實機驗收|**0組 V2 G5驗收**|原始錄影有人操作；V2回放使用虛擬輸入|

來源清單見附錄A。[凍結集合](../../data/p4c/corpus-30-v3.json)、[原生manifest](../../artifacts/p4c-frozen-native-30-v3/manifest.json)、[變換圖片manifest](../../artifacts/p4c-random-native-30-v3-pixels-01/manifest.json)。

### 1.3 P0～P5狀態

|階段|目前狀態|證據及限制|
|---|---|---|
|P0 基準凍結|有界基準與失敗集已建立|2384檔初始快照、後補10檔；[P0–P3狀態](../validation/2026-10-24-p0-p3-status.md)。不是全V1所有路徑的永久不變證明|
|P1 Geometry|核心契約／單元實作完成；跨模組整合仍有技術債|[geometry.cjs](../../lib/geometry.cjs)、當前單元紀錄；實際DPI、多螢幕與原生布局未驗|
|P2 Map→Selector|核心實作完成，影像穩定性驗證未全面完成|[node-selector.cjs](../../lib/node-selector.cjs)、38條當前成功序列；仍不能代表所有正例|
|P3 Click→Preview|核心交易／確認已實作，當前正例仍有缺口|[preview-session.cjs](../../lib/preview-session.cjs)、第39組點後拒絕；不能把模組存在視為全場景完成|
|P4-A 原始5段|**歷史中間里程碑5/5**|[版本化報告](../../artifacts/p4a-acceptance-03-versioned/report.json)；非當前版本完整重新驗收|
|P4-B 同5段三縮放|**歷史中間里程碑15/15**|[原報告](../../artifacts/p4b-acceptance-02/report.json)、[較後比例修正版15組](../../artifacts/p4c-aspect-fixed-15-acceptance-01/report.json)；關鍵檔案已有變更|
|P4-C 正式回放|**進行中，未完成**|當前38/60；第39組失敗；保留集、完整原生回歸、最終負例及效能未閉合|
|P5 有限實機|**未開始、未獲另行批准**|本次不進行遊戲操作；沒有30/30實機證據|

### 1.4 G0～G5狀態：維持原標準

|閘門|原要求摘要|判定與證據|
|---|---|---|
|G0 可追溯|來源、標註、模型／程式及變換hash完整|大量已具備，當前42關鍵檔案及成功工件可核對；最終集合尚未全跑，部分忽略區控制腳本未納同一版本閘門。**正式全集未完成**|
|G1 座標|往返每軸≤0.5px，最終每軸≤1px；跨DPI／負原點；舊幾何0次|數學契約與對應單元通過；真實DPI／布局尚未驗。**不能宣稱實機全面通過**|
|G2 正確選擇|身份全對、框IoU≥0.90、邊距≥max(3px,短邊5%)、負例零誤點|最新38成功均符合；IoU 0.906364～0.975288，最小邊距14.8325px。**全矩陣未完成**|
|G3 狀態銜接|回條不等於確認；兩張獨立相同節點預覽；交易≤1點擊；後續操作0|核心單元與38條離線序列有證據；第39組無法確認預覽。**全集未通過**|
|G4 離線閉環|30原始＋三組變換（含10保留）；正例UNKNOWN／錯選／逾時／救援0，負例全拒絕|**未完成／不合格於最終出口**，不可用P4-A/B或38組成功替代|
|G4 效能／重現|暖機p95≤1500ms，送出畫面年齡≤2500ms；15秒內明確結果；相同版本與seed可重現|沒有當前版本隔離、完整、暖機後合格效能報告；現有診斷偏慢。**未通過**|
|G5 有限實機|≥3真實布局各10次，30/30；誤點／重點／救援／越過預覽0|**未執行**；P5仍需使用者另行批准|

## 二、60組測試詳細分析

### 2.1 表格讀法與逐組證據

下表全部目標均為最小閉環支援的**普通戰鬥節點**；「選點／續開」為意圖，不是兩種不同地圖模式。欄號依凍結標註。

尺寸為渲染後實際客戶區寬高；`sx/sy` 是相對該段**裁切後來源**的實際X/Y倍率，四位小數，並非固定縮放的75/100/125%或Windows DPI。箭頭表示同條序列前後尺寸。隨機裁切僅為邊緣約1～12px的小裁切，不證明任意嚴重裁切也可辨識。

「失敗版本數」是本次能找到的、每組按程式指紋去重的失敗版本數，**不是修正次數**；0只表示未找到該組失敗紀錄，不能證明從未受其他組修正影響。

- E編號指向最新 `transaction.json`，其同目錄有逐幀 `frame-NNNN/`，各含 `input.png`、`observation.json`、`overlay.png`、`events.json`、`result.json`、`manifest.json`；上層 `report.json` 提供評分。
- S編號指向全部渲染來源影格，尚未測試者只列S，沒有虛構日誌。
- #01–35最新交易來自35組全量回歸；#36來自聚焦修復後的第03版回放；#37–39來自主執行run-25。各次版本關鍵hash已對照。
- 失敗歷史的 `replay/report.json` 所屬執行目錄一般另有 `analysis.log`、`replay.log`、`analysis/manifest.json` 與逐影格 packet；聚焦／舊pilot目錄格式不同，以實際保存檔案為準。

|編號|來源／目標／變換模式|實際虛擬尺寸及 sx/sy（依序）|當前結果／框 IoU|首個可追溯結果／失敗版本數|失敗階段與原因|修正方式|最新版本回歸|日誌、影格與工件|
|---|---|---|---|---|---|---|---|---|
|01|S1／區1・層1・欄2／選點／固定|2290×1293 @ 1.6059/1.1994|通過／0.94322|失敗／3|地圖／預覽；見 F01|見 F01|本輪35組全量回歸|[E01](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/zone-1-first-battle-random-fixed/transaction.json>) · [S01](<../../artifacts/p4c-random-native-30-v3-pixels-01/zone-1-first-battle/zone-1-first-battle-random-fixed>)|
|02|S1／區1・層1・欄2／選點／點前變更|1643×723 @ 1.1546/0.6763<br>→ 1557×948 @ 1.0843/0.8969|通過／0.95354|失敗／1|證據適配；見 F02|見 F02|本輪35組全量回歸|[E02](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/zone-1-first-battle-random-pre-change/transaction.json>) · [S02](<../../artifacts/p4c-random-native-30-v3-pixels-01/zone-1-first-battle/zone-1-first-battle-random-pre-change>)|
|03|S1／區1・層1・欄2／選點／點後變更|2345×1064 @ 1.6341/0.9981<br>→ 1651×969 @ 1.1529/0.9022|通過／0.94559|失敗／2|穩定性／預覽；見 F03|見 F03|本輪35組全量回歸|[E03](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/zone-1-first-battle-random-post-change/transaction.json>) · [S03](<../../artifacts/p4c-random-native-30-v3-pixels-01/zone-1-first-battle/zone-1-first-battle-random-post-change>)|
|04|S1／區2・層1・欄2／選點／固定|1471×777 @ 1.0366/0.7275|通過／0.95925|失敗／3|點前穩定性；見 F04|見 F04|本輪35組全量回歸|[E04](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/zone-2-first-battle-random-fixed/transaction.json>) · [S04](<../../artifacts/p4c-random-native-30-v3-pixels-01/zone-2-first-battle/zone-2-first-battle-random-fixed>)|
|05|S1／區2・層1・欄2／選點／點前變更|2094×948 @ 1.4592/0.8943<br>→ 1568×1008 @ 1.0957/0.9474|通過／0.95447|失敗／2|點前重取／G2；見 F05|見 F05|本輪35組全量回歸|[E05](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/zone-2-first-battle-random-pre-change/transaction.json>) · [S05](<../../artifacts/p4c-random-native-30-v3-pixels-01/zone-2-first-battle/zone-2-first-battle-random-pre-change>)|
|06|S1／區2・層1・欄2／選點／點後變更|1196×631 @ 0.8381/0.5892<br>→ 2065×1233 @ 1.4522/1.1459|通過／0.96774|通過／0|未見該組失敗紀錄|無該組專屬修正紀錄|本輪35組全量回歸|[E06](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/zone-2-first-battle-random-post-change/transaction.json>) · [S06](<../../artifacts/p4c-random-native-30-v3-pixels-01/zone-2-first-battle/zone-2-first-battle-random-post-change>)|
|07|S1／區3・層1・欄2／選點／固定|2481×1347 @ 1.7313/1.2672|通過／0.94491|通過／0|未見該組失敗紀錄|無該組專屬修正紀錄|本輪35組全量回歸|[E07](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/zone-3-first-battle-random-fixed/transaction.json>) · [S07](<../../artifacts/p4c-random-native-30-v3-pixels-01/zone-3-first-battle/zone-3-first-battle-random-fixed>)|
|08|S1／區3・層1・欄2／選點／點前變更|2345×1420 @ 1.6456/1.3333<br>→ 2041×920 @ 1.4303/0.8598|通過／0.95592|失敗／2|預覽 OCR／精度回歸；見 F08|見 F08|本輪35組全量回歸|[E08](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/zone-3-first-battle-random-pre-change/transaction.json>) · [S08](<../../artifacts/p4c-random-native-30-v3-pixels-01/zone-3-first-battle/zone-3-first-battle-random-pre-change>)|
|09|S1／區3・層1・欄2／選點／點後變更|2071×1132 @ 1.4585/1.0560<br>→ 1058×577 @ 0.7388/0.5382|通過／0.95075|通過／0|未見該組失敗紀錄|無該組專屬修正紀錄|本輪35組全量回歸|[E09](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/zone-3-first-battle-random-post-change/transaction.json>) · [S09](<../../artifacts/p4c-random-native-30-v3-pixels-01/zone-3-first-battle/zone-3-first-battle-random-post-change>)|
|10|S1／區8・層1・欄4／選點／固定|2009×1010 @ 1.4128/0.9501|通過／0.95296|失敗／2|候選／預覽；見 F10|見 F10|本輪35組全量回歸|[E10](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/zone-8-first-battle-random-fixed/transaction.json>) · [S10](<../../artifacts/p4c-random-native-30-v3-pixels-01/zone-8-first-battle/zone-8-first-battle-random-fixed>)|
|11|S1／區8・層1・欄4／選點／點前變更|1103×553 @ 0.7730/0.5159<br>→ 2225×1336 @ 1.5614/1.2568|通過／0.94515|通過／0|未見該組失敗紀錄|無該組專屬修正紀錄|本輪35組全量回歸|[E11](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/zone-8-first-battle-random-pre-change/transaction.json>) · [S11](<../../artifacts/p4c-random-native-30-v3-pixels-01/zone-8-first-battle/zone-8-first-battle-random-pre-change>)|
|12|S1／區8・層1・欄4／選點／點後變更|1677×1051 @ 1.1777/0.9822<br>→ 2252×1434 @ 1.5815/1.3465|通過／0.95229|通過／0|未見該組失敗紀錄|無該組專屬修正紀錄|本輪35組全量回歸|[E12](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/zone-8-first-battle-random-post-change/transaction.json>) · [S12](<../../artifacts/p4c-random-native-30-v3-pixels-01/zone-8-first-battle/zone-8-first-battle-random-post-change>)|
|13|S1／區9・層1・欄4／選點／固定|996×541 @ 0.6941/0.5104|通過／0.97315|失敗／1|G2 外框品質；見 F13|見 F13|本輪35組全量回歸|[E13](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/zone-9-first-battle-random-fixed/transaction.json>) · [S13](<../../artifacts/p4c-random-native-30-v3-pixels-01/zone-9-first-battle/zone-9-first-battle-random-fixed>)|
|14|S1／區9・層1・欄4／選點／點前變更|1469×792 @ 1.0258/0.7367<br>→ 1366×1074 @ 0.9552/1.0103|通過／0.95697|失敗／3|OCR／近原生比例；見 F14|見 F14|本輪35組全量回歸|[E14](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/zone-9-first-battle-random-pre-change/transaction.json>) · [S14](<../../artifacts/p4c-random-native-30-v3-pixels-01/zone-9-first-battle/zone-9-first-battle-random-pre-change>)|
|15|S1／區9・層1・欄4／選點／點後變更|1805×1401 @ 1.2631/1.3155<br>→ 1315×546 @ 0.9248/0.5141|通過／0.94844|失敗／1|比例共識／錨點；見 F15|見 F15|本輪35組全量回歸|[E15](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/zone-9-first-battle-random-post-change/transaction.json>) · [S15](<../../artifacts/p4c-random-native-30-v3-pixels-01/zone-9-first-battle/zone-9-first-battle-random-post-change>)|
|16|S1／區2・層2・欄3／選點／固定|1342×552 @ 0.9385/0.5183|通過／0.94033|失敗／1|比例／前置完成位置；見 F16|見 F16|本輪35組全量回歸|[E16](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/dev-primary-zone2-floor2-col3-higher-random-fixed/transaction.json>) · [S16](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-primary-zone2-floor2-col3-higher/dev-primary-zone2-floor2-col3-higher-random-fixed>)|
|17|S1／區2・層2・欄3／選點／點前變更|2467×1302 @ 1.7216/1.2248<br>→ 2543×1050 @ 1.7846/0.9831|通過／0.93889|失敗／1|入口／列距；見 F17|見 F17|本輪35組全量回歸|[E17](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/dev-primary-zone2-floor2-col3-higher-random-pre-change/transaction.json>) · [S17](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-primary-zone2-floor2-col3-higher/dev-primary-zone2-floor2-col3-higher-random-pre-change>)|
|18|S1／區2・層2・欄3／選點／點後變更|1997×1146 @ 1.3946/1.0740<br>→ 2196×1287 @ 1.5443/1.2085|通過／0.93670|失敗／2|連線／peer 身份；見 F18|見 F18|本輪35組全量回歸|[E18](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/dev-primary-zone2-floor2-col3-higher-random-post-change/transaction.json>) · [S18](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-primary-zone2-floor2-col3-higher/dev-primary-zone2-floor2-col3-higher-random-post-change>)|
|19|S1／區3・層3・欄1／選點／固定|1873×1370 @ 1.3107/1.2876|通過／0.92476|通過／1|後續回歸的座標 schema；見 F19|見 F19|本輪35組全量回歸|[E19](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/dev-primary-zone3-floor3-col1-higher-random-fixed/transaction.json>) · [S19](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-primary-zone3-floor3-col1-higher/dev-primary-zone3-floor3-col1-higher-random-fixed>)|
|20|S1／區3・層3・欄1／選點／點前變更|1255×689 @ 0.8795/0.6415<br>→ 1941×1265 @ 1.3545/1.1934|通過／0.94456|失敗／1|完成狀態／目前位置；見 F20|見 F20|本輪35組全量回歸|[E20](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/dev-primary-zone3-floor3-col1-higher-random-pre-change/transaction.json>) · [S20](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-primary-zone3-floor3-col1-higher/dev-primary-zone3-floor3-col1-higher-random-pre-change>)|
|21|S1／區3・層3・欄1／選點／點後變更|1734×1187 @ 1.2109/1.1062<br>→ 1772×817 @ 1.2400/0.7693|通過／0.94602|失敗／3|配準來源／預覽地圖；見 F21|見 F21|本輪35組全量回歸|[E21](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/dev-primary-zone3-floor3-col1-higher-random-post-change/transaction.json>) · [S21](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-primary-zone3-floor3-col1-higher/dev-primary-zone3-floor3-col1-higher-random-post-change>)|
|22|S1／區4・層2・欄3／選點／固定|2383×1372 @ 1.6746/1.2895|通過／0.94646|失敗／1|跨層幾何證據適配；見 F22|見 F22|本輪35組全量回歸|[E22](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/dev-primary-zone4-floor2-col3-random-fixed/transaction.json>) · [S22](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-primary-zone4-floor2-col3/dev-primary-zone4-floor2-col3-random-fixed>)|
|23|S1／區4・層2・欄3／選點／點前變更|1101×668 @ 0.7689/0.6237<br>→ 1734×1018 @ 1.2109/0.9514|通過／0.94611|通過／0|未見該組失敗紀錄|無該組專屬修正紀錄|本輪35組全量回歸|[E23](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/dev-primary-zone4-floor2-col3-random-pre-change/transaction.json>) · [S23](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-primary-zone4-floor2-col3/dev-primary-zone4-floor2-col3-random-pre-change>)|
|24|S1／區4・層2・欄3／選點／點後變更|2275×1203 @ 1.5976/1.1180<br>→ 1448×1072 @ 1.0126/1.0113|通過／0.94497|失敗／1|原生預覽外框；見 F24|見 F24|本輪35組全量回歸|[E24](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/dev-primary-zone4-floor2-col3-random-post-change/transaction.json>) · [S24](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-primary-zone4-floor2-col3/dev-primary-zone4-floor2-col3-random-post-change>)|
|25|S1／區6・層1・欄2／選點／固定|1145×721 @ 0.8018/0.6815|通過／0.96860|失敗／1|投影取整；見 F25|見 F25|本輪35組全量回歸|[E25](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/dev-primary-zone6-floor1-col2-random-fixed/transaction.json>) · [S25](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-primary-zone6-floor1-col2/dev-primary-zone6-floor1-col2-random-fixed>)|
|26|S1／區6・層1・欄2／選點／點前變更|2105×871 @ 1.4762/0.8217<br>→ 1056×635 @ 0.7349/0.5957|通過／0.97529|通過／0|未見該組失敗紀錄|無該組專屬修正紀錄|本輪35組全量回歸|[E26](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/dev-primary-zone6-floor1-col2-random-pre-change/transaction.json>) · [S26](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-primary-zone6-floor1-col2/dev-primary-zone6-floor1-col2-random-pre-change>)|
|27|S1／區6・層1・欄2／選點／點後變更|2275×1186 @ 1.5898/1.1094<br>→ 1349×580 @ 0.9453/0.5390|通過／0.95435|通過／0|未見該組失敗紀錄|無該組專屬修正紀錄|本輪35組全量回歸|[E27](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/dev-primary-zone6-floor1-col2-random-post-change/transaction.json>) · [S27](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-primary-zone6-floor1-col2/dev-primary-zone6-floor1-col2-random-post-change>)|
|28|S1／區10・層1・欄2／選點／固定|1203×864 @ 0.8454/0.8136|通過／0.94989|通過／0|未見該組失敗紀錄|無該組專屬修正紀錄|本輪35組全量回歸|[E28](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/dev-primary-zone10-floor1-col2-random-fixed/transaction.json>) · [S28](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-primary-zone10-floor1-col2/dev-primary-zone10-floor1-col2-random-fixed>)|
|29|S1／區10・層1・欄2／選點／點前變更|1187×703 @ 0.8289/0.6582<br>→ 1389×615 @ 0.9693/0.5732|通過／0.93461|通過／0|未見該組失敗紀錄|無該組專屬修正紀錄|本輪35組全量回歸|[E29](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/dev-primary-zone10-floor1-col2-random-pre-change/transaction.json>) · [S29](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-primary-zone10-floor1-col2/dev-primary-zone10-floor1-col2-random-pre-change>)|
|30|S1／區10・層1・欄2／選點／點後變更|1217×625 @ 0.8522/0.5836<br>→ 1725×1256 @ 1.2071/1.1738|通過／0.94140|失敗／1|原生預覽外框；見 F30|見 F30|本輪35組全量回歸|[E30](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/dev-primary-zone10-floor1-col2-random-post-change/transaction.json>) · [S30](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-primary-zone10-floor1-col2/dev-primary-zone10-floor1-col2-random-post-change>)|
|31|S2／區6・層1・欄2／選點／固定|966×740 @ 1.0266/1.0526|通過／0.93586|失敗／2|小比例／幾何一致性；見 F31|見 F31|本輪35組全量回歸|[E31](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/dev-L0-zone6-floor1-col2-select-1773-random-fixed/transaction.json>) · [S31](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-L0-zone6-floor1-col2-select-1773/dev-L0-zone6-floor1-col2-select-1773-random-fixed>)|
|32|S2／區6・層1・欄2／選點／點前變更|1152×597 @ 1.2203/0.8408<br>→ 2015×850 @ 2.1278/1.1905|通過／0.91749|通過／0|未見該組失敗紀錄|無該組專屬修正紀錄|本輪35組全量回歸|[E32](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/dev-L0-zone6-floor1-col2-select-1773-random-pre-change/transaction.json>) · [S32](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-L0-zone6-floor1-col2-select-1773/dev-L0-zone6-floor1-col2-select-1773-random-pre-change>)|
|33|S2／區6・層1・欄2／選點／點後變更|1486×1014 @ 1.5659/1.4383<br>→ 1218×564 @ 1.2944/0.7932|通過／0.92852|失敗／1|OCR 分行；見 F33|見 F33|本輪35組全量回歸|[E33](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/dev-L0-zone6-floor1-col2-select-1773-random-post-change/transaction.json>) · [S33](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-L0-zone6-floor1-col2-select-1773/dev-L0-zone6-floor1-col2-select-1773-random-post-change>)|
|34|S2／區6・層1・欄2／續開／固定|1781×915 @ 1.8708/1.2942|通過／0.90943|失敗／1|目前位置外環；見 F34|見 F34|本輪35組全量回歸|[E34](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/dev-L0-zone6-floor1-col2-resume-1781-random-fixed/transaction.json>) · [S34](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-L0-zone6-floor1-col2-resume-1781/dev-L0-zone6-floor1-col2-resume-1781-random-fixed>)|
|35|S2／區6・層1・欄2／續開／點前變更|1168×594 @ 1.2269/0.8366<br>→ 1938×1263 @ 2.0530/1.7789|通過／0.90636|通過／0|未見該組失敗紀錄|無該組專屬修正紀錄|本輪35組全量回歸|[E35](<../../artifacts/p4c-sparse-peer-controls-thirtyfive-replay-01/dev-L0-zone6-floor1-col2-resume-1781-random-pre-change/transaction.json>) · [S35](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-L0-zone6-floor1-col2-resume-1781/dev-L0-zone6-floor1-col2-resume-1781-random-pre-change>)|
|36|S2／區6・層1・欄2／續開／點後變更|1457×1035 @ 1.5369/1.4849<br>→ 1227×571 @ 1.2929/0.8122|通過／0.91215|失敗／3|候選／OCR／預覽時序；見 F36|見 F36|本輪獨立完整重驗|[E36](<../../artifacts/p4c-sparse-peer-case36-replay-03/dev-L0-zone6-floor1-col2-resume-1781-random-post-change/transaction.json>) · [S36](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-L0-zone6-floor1-col2-resume-1781/dev-L0-zone6-floor1-col2-resume-1781-random-post-change>)|
|37|S2／區6・層3・欄3／選點／固定|1256×645 @ 1.3207/0.9136|通過／0.95067|通過／0|未見該組失敗紀錄|無該組專屬修正紀錄|同版續跑完整通過|[E37](<../../artifacts/p4c-random-development-60-run-25/dev-L0-zone6-floor3-col3-select-1932-random-fixed/replay/dev-L0-zone6-floor3-col3-select-1932-random-fixed/transaction.json>) · [S37](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-L0-zone6-floor3-col3-select-1932/dev-L0-zone6-floor3-col3-select-1932-random-fixed>)|
|38|S2／區6・層3・欄3／選點／點前變更|2137×1241 @ 2.2518/1.7678<br>→ 2552×1391 @ 2.7178/1.9619|通過／0.93453|通過／0|未見該組失敗紀錄|無該組專屬修正紀錄|同版續跑完整通過|[E38](<../../artifacts/p4c-random-development-60-run-25/dev-L0-zone6-floor3-col3-select-1932-random-pre-change/replay/dev-L0-zone6-floor3-col3-select-1932-random-pre-change/transaction.json>) · [S38](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-L0-zone6-floor3-col3-select-1932/dev-L0-zone6-floor3-col3-select-1932-random-pre-change>)|
|39|S2／區6・層3・欄3／選點／點後變更|1786×1227 @ 1.8840/1.7209<br>→ 2053×1191 @ 2.1679/1.6870|失敗／0.93914|失敗／1|點後預覽證據；見 F39|見 F39|未通過|[E39](<../../artifacts/p4c-random-development-60-run-25/dev-L0-zone6-floor3-col3-select-1932-random-post-change/replay/dev-L0-zone6-floor3-col3-select-1932-random-post-change/transaction.json>) · [S39](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-L0-zone6-floor3-col3-select-1932/dev-L0-zone6-floor3-col3-select-1932-random-post-change>)|
|40|S2／區5・層1・欄1／選點／固定|1885×793 @ 1.9947/1.1106|未測試|無執行結果|—|未進行|未測|[S40（僅備料）](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-earlier-L0-zone5-floor1-col1/dev-earlier-L0-zone5-floor1-col1-random-fixed>)|
|41|S2／區5・層1・欄1／選點／點前變更|2481×1135 @ 2.6199/1.5919<br>→ 1751×963 @ 1.8393/1.3679|未測試|無執行結果|—|未進行|未測|[S41（僅備料）](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-earlier-L0-zone5-floor1-col1/dev-earlier-L0-zone5-floor1-col1-random-pre-change>)|
|42|S2／區5・層1・欄1／選點／點後變更|1466×1087 @ 1.5530/1.5506<br>→ 1729×1350 @ 1.8238/1.9068|未測試|無執行結果|—|未進行|未測|[S42（僅備料）](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-earlier-L0-zone5-floor1-col1/dev-earlier-L0-zone5-floor1-col1-random-post-change>)|
|43|S2／區8・層1・欄4／選點／固定|2249×1408 @ 2.3649/2.0172|未測試|無執行結果|—|未進行|未測|[S43（僅備料）](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-earlier-L0-zone8-floor1-col4/dev-earlier-L0-zone8-floor1-col4-random-fixed>)|
|44|S2／區8・層1・欄4／選點／點前變更|1706×785 @ 1.8015/1.1166<br>→ 1009×632 @ 1.0666/0.8990|未測試|無執行結果|—|未進行|未測|[S44（僅備料）](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-earlier-L0-zone8-floor1-col4/dev-earlier-L0-zone8-floor1-col4-random-pre-change>)|
|45|S2／區8・層1・欄4／選點／點後變更|1958×1107 @ 2.0589/1.5680<br>→ 1813×945 @ 1.9104/1.3423|未測試|無執行結果|—|未進行|未測|[S45（僅備料）](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-earlier-L0-zone8-floor1-col4/dev-earlier-L0-zone8-floor1-col4-random-post-change>)|
|46|S3／區4・層1・欄4／選點／固定|1697×1075 @ 1.3458/1.5379|未測試|無執行結果|—|未進行|未測|[S46（僅備料）](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-earlier-0Q-zone4-floor1-col4/dev-earlier-0Q-zone4-floor1-col4-random-fixed>)|
|47|S3／區4・層1・欄4／選點／點前變更|1886×1065 @ 1.4921/1.4937<br>→ 1753×1326 @ 1.3946/1.8970|未測試|無執行結果|—|未進行|未測|[S47（僅備料）](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-earlier-0Q-zone4-floor1-col4/dev-earlier-0Q-zone4-floor1-col4-random-pre-change>)|
|48|S3／區4・層1・欄4／選點／點後變更|1209×730 @ 0.9512/1.0443<br>→ 1315×560 @ 1.0362/0.7865|未測試|無執行結果|—|未進行|未測|[S48（僅備料）](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-earlier-0Q-zone4-floor1-col4/dev-earlier-0Q-zone4-floor1-col4-random-post-change>)|
|49|S4／區1・層1・欄1／續開／固定|1590×1079 @ 0.8333/1.0094|未測試|無執行結果|—|未進行|未測|[S49（僅備料）](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-LX46-zone1-floor1-col1-resume/dev-LX46-zone1-floor1-col1-resume-random-fixed>)|
|50|S4／區1・層1・欄1／續開／點前變更|1796×1384 @ 0.9388/1.2959<br>→ 1801×1057 @ 0.9444/0.9925|未測試|無執行結果|—|未進行|未測|[S50（僅備料）](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-LX46-zone1-floor1-col1-resume/dev-LX46-zone1-floor1-col1-resume-random-pre-change>)|
|51|S4／區1・層1・欄1／續開／點後變更|1709×1097 @ 0.8985/1.0224<br>→ 1448×693 @ 0.7585/0.6513|未測試|無執行結果|—|未進行|未測|[S51（僅備料）](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-LX46-zone1-floor1-col1-resume/dev-LX46-zone1-floor1-col1-resume-random-post-change>)|
|52|S4／區2・層1・欄2／選點／固定|1710×1229 @ 0.9000/1.1454|未測試|無執行結果|—|未進行|未測|[S52（僅備料）](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-LX46-zone2-floor1-col2-select/dev-LX46-zone2-floor1-col2-select-random-fixed>)|
|53|S4／區2・層1・欄2／選點／點前變更|1290×1005 @ 0.6779/0.9454<br>→ 1466×713 @ 0.7667/0.6676|未測試|無執行結果|—|未進行|未測|[S53（僅備料）](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-LX46-zone2-floor1-col2-select/dev-LX46-zone2-floor1-col2-select-random-pre-change>)|
|54|S4／區2・層1・欄2／選點／點後變更|1475×640 @ 0.7763/0.6038<br>→ 1962×1238 @ 1.0288/1.1679|未測試|無執行結果|—|未進行|未測|[S54（僅備料）](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-LX46-zone2-floor1-col2-select/dev-LX46-zone2-floor1-col2-select-random-post-change>)|
|55|S4／區3・層1・欄4／選點／固定|1446×854 @ 0.7587/0.8019|未測試|無執行結果|—|未進行|未測|[S55（僅備料）](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-LX46-zone3-floor1-col4-select/dev-LX46-zone3-floor1-col4-select-random-fixed>)|
|56|S4／區3・層1・欄4／選點／點前變更|2167×1141 @ 1.1340/1.0764<br>→ 1268×662 @ 0.6656/0.6210|未測試|無執行結果|—|未進行|未測|[S56（僅備料）](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-LX46-zone3-floor1-col4-select/dev-LX46-zone3-floor1-col4-select-random-pre-change>)|
|57|S4／區3・層1・欄4／選點／點後變更|1462×690 @ 0.7666/0.6425<br>→ 1449×1151 @ 0.7638/1.0869|未測試|無執行結果|—|未進行|未測|[S57（僅備料）](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-LX46-zone3-floor1-col4-select/dev-LX46-zone3-floor1-col4-select-random-post-change>)|
|58|S4／區4・層2・欄1／選點／固定|2306×1417 @ 1.2130/1.3330|未測試|無執行結果|—|未進行|未測|[S58（僅備料）](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-LX46-zone4-floor2-col1-select/dev-LX46-zone4-floor2-col1-select-random-fixed>)|
|59|S4／區4・層2・欄1／選點／點前變更|1067×752 @ 0.5563/0.7061<br>→ 2399×1182 @ 1.2606/1.1088|未測試|無執行結果|—|未進行|未測|[S59（僅備料）](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-LX46-zone4-floor2-col1-select/dev-LX46-zone4-floor2-col1-select-random-pre-change>)|
|60|S4／區4・層2・欄1／選點／點後變更|1329×732 @ 0.6951/0.6899<br>→ 1437×853 @ 0.7539/0.7957|未測試|無執行結果|—|未進行|未測|[S60（僅備料）](<../../artifacts/p4c-random-native-30-v3-pixels-01/dev-LX46-zone4-floor2-col1-select/dev-LX46-zone4-floor2-col1-select-random-post-change>)|


### 2.2 失敗原因與已記錄修正

以下列的是已觀察到的直接原因與對應版本；沒有逐次因果紀錄者不補造。「重新通過」看上表當前結果，不能因歷史補丁存在就算回歸成功。

|索引|已保存失敗階段／直接原因|有紀錄的修正方式與版本|歷史失敗證據|
|---|---|---|---|
|F01・地圖／預覽|pilot 先 ANCHOR_MISSING，後有 PREVIEW_TIMEOUT。非首次就成功。|原圖比例／預覽幾何恢復；10e274a 等。單次補丁歸因非完整。|[原結果](<../../artifacts/p4c-random-pilot-first-replay-01/report.json>)；最新結果見 E01|
|F02・證據適配|pilot 第一次可比結果 EVIDENCE_UNVERIFIED。|尺寸與來源幾何綁定修正後恢復；不能把正式 runner 的首輪成功當零修正。|[原結果](<../../artifacts/p4c-random-pilot-replay-04/report.json>)；最新結果見 E02|
|F03・穩定性／預覽|pilot 有 MAP_MOVING、PREVIEW_TIMEOUT。|入口／預覽外框及比例證據修正；完整 pilot 至 replay-07 才三組均通過。|[原結果](<../../artifacts/p4c-random-pilot-replay-05/report.json>)；最新結果見 E03|
|F04・點前穩定性|入口模板切換導致框 IoU 不穩，MAP_MOVING。|同張原圖青色入口元件與模板外框量測；2436208。|[原結果](<../../artifacts/p4c-random-development-60-run-01/zone-2-first-battle-random-fixed/replay/report.json>)；最新結果見 E04|
|F05・點前重取／G2|最早 ANCHOR_MISSING；其後曾確認預覽但框 IoU 約 0.8963 不達標。|先作廢舊幾何再重取穩定對；量測橙色節點外框；c55174b。|[原結果](<../../artifacts/p4c-random-development-60-run-03/zone-2-first-battle-random-pre-change/replay/report.json>)；最新結果見 E05|
|F08・預覽 OCR／精度回歸|首次 PREVIEW_TIMEOUT；後另有 TRANSITION_UNKNOWN 回歸。|原像素裁切重讀合併計時圖示，保留 .95 門檻；068b58f。另修雙重取整；48c19e1。|[原結果](<../../artifacts/p4c-random-development-60-run-04/zone-3-first-battle-random-pre-change/replay/report.json>)；最新結果見 E08|
|F10・候選／預覽|光暈影響外框候選，最早 ANCHOR_MISSING。|來源橙色橢圓、原圖示核心及有界對齊驗證；713bd6a 等。|[原結果](<../../artifacts/p4c-random-development-60-run-05/zone-8-first-battle-random-fixed/replay/report.json>)；最新結果見 E10|
|F13・G2 外框品質|曾 state=PREVIEW_CONFIRMED，但 IoU=0.8954929，grade=false。|保留小尺寸原圖外框與圖示證據；9f85e04。不能只看狀態名稱判通過。|[原結果](<../../artifacts/p4c-random-development-60-run-06/zone-9-first-battle-random-fixed/replay/report.json>)；最新結果見 E13|
|F14・OCR／近原生比例|原像素計時標籤漏字而 UNKNOWN；另有近原生比例不校正問題。|部分詞只作裁切定位，完整文字重新辨識；有證據的近原生校正；ec7a797。|[原結果](<../../artifacts/p4c-random-development-60-run-07/report.json>)；最新結果見 E14|
|F15・比例共識／錨點|ANCHOR_MISSING，已測比例共識在歧義判斷前未閉合。|對實測群組求閉合共識，保留歧義拒絕；1268f82。|[原結果](<../../artifacts/p4c-random-development-60-run-08/zone-9-first-battle-random-post-change/replay/report.json>)；最新結果見 E15|
|F16・比例／前置完成位置|ANCHOR_MISSING；只有兩個橙色圓、完成前置節點候選不足。|兩個原圖戰鬥圓＋一個獨立入口箭頭形成三個量測；完成勾像素證明與文字位置校正；3e986b9 等。|[原結果](<../../artifacts/p4c-random-development-60-run-09/dev-primary-zone2-floor2-col3-higher-random-fixed/replay/report.json>)；最新結果見 E16|
|F17・入口／列距|ANCHOR_MISSING，缺入口候選且 X 導出的列距累積偏差。|來源入口候選、獨立實測 Y 列距且維持 4% 一致性約束；801186f。|[原結果](<../../artifacts/p4c-random-development-60-run-10/dev-primary-zone2-floor2-col3-higher-random-pre-change/replay/report.json>)；最新結果見 E17|
|F18・連線／peer 身份|CONNECTION_UNPROVEN；原 support 有 .85/.825；補首列後 ID 可能重排。|固定 58px 參考尺度重跑原 40 點／6px 色彩核；保留原門檻並綁同張量測 peer；8e6a057。|[原結果](<../../artifacts/p4c-random-development-60-run-12/dev-primary-zone2-floor2-col3-higher-random-post-change/replay/report.json>)；最新結果見 E18|
|F19・後續回歸的座標 schema|首次完整閉環通過；第20組修正後的回歸出現 EVIDENCE_UNVERIFIED。|原生完成外框誤帶 rectified 的 analysisBox；保持原生欄位規約；3f3fec0。|[原結果](<../../artifacts/p4c-completed-extent-controls-twenty-replay-01/report.json>)；最新結果見 E19|
|F20・完成狀態／目前位置|CURRENT_POSITION_UNPROVEN；舊完成旗標不能替代原圖勾形狀證明。|用原圖完成圖示、勾 mask、量測 peer 外框重新核對，再重算受影響連線；64b5675。|[原結果](<../../artifacts/p4c-random-development-60-run-14/dev-primary-zone3-floor3-col1-higher-random-pre-change/replay/report.json>)；最新結果見 E20|
|F21・配準來源／預覽地圖|最早 PREVIEW_REGISTRATION_SOURCE_MISMATCH；其後預覽面板誤入地圖候選、可見治療節點漏檢。|交易內已觀察直接語意根、面板像素範圍、來源治療候選；aeb6c68、a8b6ab0。|[原結果](<../../artifacts/p4c-random-development-60-run-16/dev-primary-zone3-floor3-col1-higher-random-post-change/replay/report.json>)；最新結果見 E21|
|F22・跨層幾何證據適配|最早 TRANSITION_UNKNOWN；來源完成候選引用後來被修正的 peer 舊量測。|保留歷史量測與新外框的同張來源關係，不改原裁切分數；2c6c1ac。|[原結果](<../../artifacts/p4c-random-development-60-run-17/dev-primary-zone4-floor2-col3-random-fixed/replay/report.json>)；最新結果見 E22|
|F24・原生預覽外框|PREVIEW_TIMEOUT，單用中位數尺寸無法通過原圖圖示核對。|同張已偵測 peer 尺寸作獨立假設，每一裁切仍須 .9/.08；55b80b7。|[原結果](<../../artifacts/p4c-random-development-60-run-18/dev-primary-zone4-floor2-col3-random-post-change/replay/report.json>)；最新結果見 E24|
|F25・投影取整|EVIDENCE_UNVERIFIED；top+height 比 721 大約多 1e-13。|投影量測區間兩端再相減，不 clamp、不放寬越界；385eaad。|[原結果](<../../artifacts/p4c-random-development-60-run-19/dev-primary-zone6-floor1-col2-random-fixed/replay/report.json>)；最新結果見 E25|
|F30・原生預覽外框|PREVIEW_TIMEOUT；既有 peer 尺寸未達圖示門檻。|原圖橢圓外框只作後備假設，仍保留 .9/.08、10% 尺寸界限；364492e。|[原結果](<../../artifacts/p4c-random-development-60-run-20/dev-primary-zone10-floor1-col2-random-post-change/replay/report.json>)；最新結果見 E30|
|F31・小比例／幾何一致性|ANCHOR_MISSING；首次小比例補強後又有 MAP_MOVING。|用原始三欄拓撲決定是否校正，使相鄰幀採同一座標規約；5ab2595。|[原結果](<../../artifacts/p4c-random-development-60-run-21/dev-L0-zone6-floor1-col2-select-1773-random-fixed/replay/report.json>)；最新結果見 E31|
|F33・OCR 分行|分析在 53172 因 UNKNOWN 停止，尚未進入回放。|弱「剩餘時間」標籤＋獨立時鐘只定位裁切；重新讀完整原圖字串；73c1585。|[原結果](<../../artifacts/p4c-random-development-60-run-22/report.json>)；最新結果見 E33|
|F34・目前位置外環|CURRENT_POSITION_UNPROVEN；相鄰幀黃色環覆蓋率 .07902/.08158 跨原 .08 門檻。|僅有來源條件時於 58px 參考尺寸重測；原 .08/.04、標籤與三角條件不變；37cfaad。|[原結果](<../../artifacts/p4c-random-development-60-run-23/dev-L0-zone6-floor1-col2-resume-1781-random-fixed/replay/report.json>)；最新結果見 E34|
|F36・候選／OCR／預覽時序|先 EVIDENCE_UNVERIFIED，局部修正後又於較晚幀拒絕，再有 PREVIEW_TIMEOUT。|三個一致尺寸只定位第四個原圖圖示；補天數／時鐘切分；相同「普通」空白讀值取實際最高分；f38af71。|[原結果](<../../artifacts/p4c-random-development-60-run-24/dev-L0-zone6-floor1-col2-resume-1781-random-post-change/replay/report.json>)；最新結果見 E36|
|F39・點後預覽證據|57947：MAP 信心 .8649、節點0、無錨點、配準未證、預覽身份未證；EVIDENCE_UNVERIFIED。|尚未修正。本次只分析；不得跳過失敗影格或放寬拒絕以宣稱通過。|[原結果](<../../artifacts/p4c-random-development-60-run-25/dev-L0-zone6-floor3-col3-select-1932-random-post-change/replay/report.json>)；最新結果見 E39|


### 2.3 首次結果、修正負擔與回歸趨勢

39組已嘗試案例中，首個可追溯結果通過的為 **15組**：

`06、07、09、11、12、19、23、26、27、28、29、32、35、37、38`。

另24組首個可追溯結果失敗。當前38組成功中，23組是從首敗恢復；#19雖首過，後來也曾退步，因此共有24個當前成功案例留有失敗版本紀錄，其餘14個未見該組失敗紀錄。

不能只看正式runner的第一次執行：最早3組在 pilot 已有相同影格、尺寸及意圖的失敗。若只看主runner，會得到18個首過，漏掉pilot而高估首次成功。本報告使用包含pilot的15組；仍不宣稱掌握任何未保存的更早嘗試。

**每組平均需要幾次修正：無法確認。** 缺乏一對一「案例→失敗→補丁→複驗」完整台帳，單次提交常同時處理多個根因，其他案例也可能因共通補丁受益。有限保存紀錄可數出 **41個案例×失敗程式版本組合**，除以已嘗試39組約1.05；這僅是觀察到的失敗版本密度，不是平均修正次數、完整嘗試次數或成本。

|順序區間|首個可追溯失敗|保存的失敗版本組合|能否證明改善|
|---|---|---|---|
|#20–29|5/10|7|比較基準；資料相依、非隨機抽樣|
|最近#30–39|6/10|9|**未見下降證據**；不能宣稱修正次數減少|

重複出現的是入口／比例錨點不足、原圖外框量測、座標schema／浮點取整、完成狀態與peer來源、分行或合併圖示的OCR、預覽地圖配準／身份證據。這些跨多個案例，並非只有第39組的孤立圖片問題。

已確認存在「修某組導致其他組退步」：

1. #20完成外框補強後，#19在[20組控制回放](../../artifacts/p4c-completed-extent-controls-twenty-replay-01/report.json)退為 `EVIDENCE_UNVERIFIED`；原因是原生框誤帶校正座標的 `analysisBox`，由 `3f3fec0` 修復。最新35組回歸包含#19並通過。
2. #8曾在[候選控制回放02](../../artifacts/p4c-proposal-controls-nine-replay-02/report.json)因重複取整造成約0.0111947的規約差異，成為 `TRANSITION_UNKNOWN`；`48c19e1` 修復後最新回歸通過。
3. #13曾已達 `PREVIEW_CONFIRMED`，但IoU僅0.8954929，因此整體仍失敗。這不是新的誤點結論，而是證明「狀態成功」不能替代G2評分。

## 三、視覺辨識與跨尺寸穩定性

### 3.1 八個關鍵環節

|環節|目前實作與實證|共通問題／尚待驗證|
|---|---|---|
|地圖入口錨點|來源入口候選、青色元件／箭頭、格點與區域文字結合；來源與hash綁定|光暈、裁切、滾動後入口消失均會影響絕對層數；#4、15–17、31反覆觸及。入口不存在時不能猜層|
|節點候選|沿用既有候選，加入原圖圖示核心、橢圓與peer尺寸等受限假設|分析候選與真正原圖外框不同；稀疏圖示、面板遮擋、治療與完成節點仍需不同分支。沒有完整未見集precision/recall|
|比例校準|非等比校正、原圖量測共識、稀疏三點／格距及入口支持|近原生與小比例分支、X/Y格距、相鄰幀是否切換座標規約可反覆失敗；拉伸錄影不等於真實UI重排|
|座標轉換／取整|Geometry核心可逆；來源框與分析框附證據；拒絕越界／舊幾何|Python各模組仍自行做source↔analysis↔rectified↔參考尺寸投影，JS再驗證。#19、25及#8回歸顯示契約未完全統一|
|外框與IoU|G2保留≥0.90；最新38成功最低0.906364|#5、13及後續preview extent修正說明「中心落對」不代表框合格；未測21組與保留集不能推算合格率|
|OCR|現有ONNX OCR＋原像素有界裁切重讀；弱文字／時鐘只定位，再讀完整字串|計時圖示合併、剩餘時間分行、天數／時鐘、等價空白，#8、14、33、36重複；需區分定位提示與語意權威|
|預覽確認|區域／層／欄／事件、綠色按鈕、選中輪廓、直接或可追溯配準；兩張一致預覽≥200ms|原始畫面分類成功不能代替selected-node證明；當前#39仍有可見預覽卻證據鏈斷裂|
|完成狀態／連線|原圖勾形狀、目前位置外環／標籤／三角、前置節點及連線支持；兩幀一致|完成旗標不能代替像素；peer重編號與格距影響線端點。連線支持原門檻0.85保留，非全部候選設reachable|

對應原始碼：[比例](../../ml/map_aspect.py)、[預覽身份](../../ml/preview_identity.py)、[OCR](../../ml/bounded_ocr.py)、[觀察適配](../../lib/observer-adapter.cjs)、[幾何](../../lib/geometry.cjs)、[選擇器](../../lib/node-selector.cjs)。

### 3.2 哪些修正有泛化能力，哪些仍偏局部

具有跨地圖潛力的修正包括：明確區分座標空間、區間端點一致取整、幾何改變後作廢舊proof、由實際原圖量測取得外框、pixel/hash綁定、連線依同張peer重算、OCR只用完整重讀結果確認、輸入回條與預覽確認分離。這些是契約或量測方法，且部分已由35組回歸支持；仍須保留集與當前完整原生集合驗證。

較依賴畫面條件的是：兩橙圓加入口形成三量測、三個同尺寸候選定位第四個圖示、同張peer／原生橢圓後備、特定分行／合併時鐘裁切，以及58px參考尺度的色核重測。它們不是直接按案例ID放行，但每個都增加條件分支；現有成功不足以證明對新語言、遮擋或新美術泛化。

存在硬編碼與過擬合風險：960分析參考、四欄拓撲、區域1～10／層數1～31、58px參考、HSV／色核、0.90與0.08分類規則、0.85連線、0.95穩定性，以及近原生／小比例分段條件。部分是模式規則或安全門檻，不能一概稱錯誤。唯讀搜尋未發現runtime依這四部影片ID或57947等影格ID直接選分支；這不等於排除對開發資料形狀的間接過擬合。

### 3.3 75%、100%、125%目前能說什麼

同5段的歷史固定縮放尺寸為1080×810、1440×1080、1800×1350，15/15曾通過。較後固定15組報告亦通過，但 `map_aspect.py`、`bounded_ocr.py`、`preview_identity.py`、`observer-adapter.cjs` 的hash均與當前不同。

因此，**當前f38版本三個固定倍率是否全部仍穩定：無法確認**。也沒有證據可以指定「75%目前必敗」或「125%目前一定無問題」。隨機變換已暴露的小尺寸外框／OCR、近原生校準、點後尺寸改變與自動滾動之證據空窗，是需要重新覆蓋的條件，不應以其他尺寸成功代替。

目前回放證明的是影像縮放／拉伸／小裁切下的邏輯；未證明模擬器實際重排、額外工具列、內容黑邊、跨螢幕原點或真實DPI都正常。

### 3.4 是否需要YOLO或其他模型

**現階段沒有足夠證據支持立即導入YOLO。** 已保存失敗多數涉及幾何規約、來源權威、OCR及跨畫面確認；換候選偵測模型不能直接修復這些問題。現行系統使用既有OpenCV／模板／配準與OCR模型，不應把啟發式修正稱為重新訓練大型視覺模型。

適合先量測未見集中的入口／節點候選召回率、誤檢率、外框IoU與耗時，按遮擋、尺寸、美術分類。如果候選本身形成主要且無法由一致量測解決的瓶頸，再比較學習式偵測器與現有方案。新模型仍須通過同一幾何、身份與交易驗證，不能用模型信心取代操作證據。本次不實作或訓練。

## 四、回歸測試與安全性

### 4.1 最新可核對測試結果

|類別|保存結果|版本與範圍限制|
|---|---|---|
|Node單元|**113/113**，失敗0、跳過0；84.973秒|[日誌](../../artifacts/p4c-sparse-peer-full-node-03.log)，與當前版本閘門對應；本次未重跑|
|Python單元|**150/150**；393.882秒|[日誌](../../artifacts/p4c-sparse-peer-full-python-03.log)，同上|
|已通過隨機開發案例回歸|最新38個成功案例仍有當前關鍵hash的成功證據|35組全量新鮮分析＋#36聚焦＋#37/38新執行；不是任意歷史集合全過|
|歷史20原生互動|20/20曾通過|[原生20](../../artifacts/p4c-development-20-v3-replay-01/report.json)、[比例修正後20](../../artifacts/p4c-aspect-native-20-replay-01/report.json)；當前關鍵hash已不同|
|全影片／全部模式|**未證明**|只回放標註互動片段；沒有整部無剪輯影片、所有事件／戰鬥操作的完整驗收|
|實機|**未執行V2 G5**|錄影中的原玩家操作不算V2實機成功|

35組新鮮回歸實際重新產生1141個 `fresh_full_pipeline` packet，沒有以舊OCR快取冒充新推論。但「這35組保持通過」不能延伸為「全部歷史固定／原生／1551影格均已對當前版本回歸」。

### 4.2 錯點、重點與錯誤預覽

最新39個已嘗試案例各有一次虛擬點擊；38個完成預覽確認，第39個點後拒絕。保存評分中目標身份／座標均通過，未見本輪錯落點或重複虛擬點擊；但不能據此宣稱真實遊戲零誤點。

特別注意，grader的 `checks.identityPassed` 是選擇proof與標註的比較，**不能單獨證明最終預覽身份**。只有獨立Preview Verifier確認後、整體grade通過才算閉環成功。單元中的故意錯誤輸入是拒絕測試，不是產品已發生誤操作的紀錄；全部未保存歷史是否存在誤點，無法確認。

虛擬dispatcher按人工標註的時間與點位條件釋放後續錄影分支，模型接收PNG與來源綁定，不接收真值意圖作為辨識結果。這是離線反事實操作近似，不能證明原生輸入已送到正確視窗。報告的 `nativeActions:0` 亦是離線runner的固定範圍欄位，不是OS層鍵鼠遙測。

### 4.3 第39組：安全停下，但可用性仍未達標

最新失敗：`dev-L0-zone6-floor3-col3-select-1932-random-post-change`。來源960×720，虛擬尺寸1786×1227→2053×1191。45張已分析；交易實際讀至20張即停止。點位IoU **0.9391386**，安全邊距 **29.5231px**，一次虛擬點擊、零原生操作。

失敗在來源影格 **57947**（PTS 1931566.666667ms）：

|項目|保存輸出|
|---|---|
|raw畫面分類|MAP，信心0.8649|
|mapReview|節點0、absoluteAnchor=false、aspect=false|
|tracked map|`PREVIEW_REGISTRATION_UNPROVEN`|
|preview|`PREVIEW_IDENTITY_UNPROVEN`|
|adapter|`stateVerified=false`、`verified=false`|
|交易|`EVIDENCE_UNVERIFIED`，不再重點／不繼續放行|

已視覺檢視[失敗原圖](../../artifacts/p4c-random-development-60-run-25/dev-L0-zone6-floor3-col3-select-1932-random-post-change/replay/dev-L0-zone6-floor3-col3-select-1932-random-post-change/frame-0019/input.png)：可看見普通戰鬥預覽、03:00、綠色「進入」及選中輪廓；地圖因面板而滾動。因此不能說遊戲未響應，也不能只憑肉眼把機器證據缺口標為通過。

對照[逐幀packet](../../artifacts/p4c-random-development-60-run-25/dev-L0-zone6-floor3-col3-select-1932-random-post-change/analysis/dev-L0-zone6-floor3-col3-select-1932-random-post-change/0057947.packet.json)及[交易](../../artifacts/p4c-random-development-60-run-25/dev-L0-zone6-floor3-col3-select-1932-random-post-change/replay/dev-L0-zone6-floor3-col3-select-1932-random-post-change/transaction.json)：

- 57923／57929為舊尺寸直接入口錨點；57930換新尺寸後暫缺。
- **57931～57944已有新尺寸的直接入口錨點**，所以「換尺寸後完全沒有新根」不是本案成立的根因。
- 57945無候選、57946有10候選但無錨點、57947又無候選且配準未證。
- 57948及57950～57972的預先保存packet之後又有可驗證追蹤，但本次交易已停止，沒有使用它們。不能跳過57947或借未放行的未來資料追認成功。

已定位為轉場候選／配準／預覽證據鏈在短暫空窗斷裂；**造成該空窗的最底層單一根因仍無法確認**。本次不加測或修補。安全拒絕在這裡有效，但仍屬正常正例失敗，不能把頻繁停住解讀成品質合格。

### 4.4 證據不足與負例是否真的執行

核心有私有proof來源、幾何／視窗／時間綁定；兩張穩定地圖至少相隔200ms，前置／目標均需一致；點擊後兩張獨立身份一致預覽才完成。回條不等於確認，發送不確定不重試。現有證據支持這些限制在已測案例生效，不能推廣成所有失效模式已封閉。

負例不是只有準備圖片：

- [negative v13證據](../../data/p4c/negative-random-evidence-v13.json)與[fresh run-30-14](../../artifacts/p4c-random-negative-fresh-run-30-14/report.json)：**10基例×3變換=30/30拒絕**，虛擬點擊0、原生操作0、不計入正例、不碰保留集。
- 共60張準備圖，其中57張真正推論並保存五類工件；另外3張因第一張區域UNKNOWN即停止，沒有繼續推論，不能宣稱60張都經過模型。
- 覆蓋灰節點、完成、治療、裂隙、缺目標、精英及入口／目標／區域／底部裁切等。
- [grader controls](../../artifacts/p4c-random-negative-grader-controls-14/selfcheck.json)：真灰節點應被拒絕；真實可選正例必須不能被負例grader誤當合格。控制自檢通過。
- 證據本身明列 `formalNegativeGateComplete:false`，G4未完成；30項當前局部負例成功不能替代整份正式負例出口。

### 4.5 1551張原生影格與「六張過渡候選變動」

**後續驗證尚未完全完成。**

|稽核|結果|意義|
|---|---|---|
|[aspect native equivalence](../../artifacts/p4c-aspect-native-map-equivalence-01.json)|1551張、當時0變動|歷史版本的候選等價性|
|[near-native audit](../../artifacts/p4c-near-native-native-map-audit-01.json)|1551張、6張候選改變；錨點未新增／遺失|標記需要完整原生回放，不能只因錨點數相同結案|
|[consensus audit](../../artifacts/p4c-consensus-native-map-audit-01.json)／[gate-supported audit](../../artifacts/p4c-gate-supported-native-map-audit-01.json)|仍6張變動|部分後續比較存在，但非當前最終完整驗收|
|[supplemental-gate audit](../../artifacts/p4c-supplemental-gate-native-map-audit-01.json)|1551張、**7張**變動，錨點仍無新增／遺失；`requiresFullNativeReplay:true`|此稽核的程式hash也非當前版本|

最新保存差異為：S1區2層2欄3影格14546候選13→14（錨點仍真）；S3區4層1欄4的46047 15→14、46049 16→16、46051 18→20、46052 20→20、46056 18→17、46057 16→16（錨點均假）。候選數相同也可能位置或身份不同。

沒有找到當前 `f38` 關鍵hash下重新完成的1551張稽核及20原生互動完整閉環；S3對應的隨機開發#46–48也尚未跑。候選改變不必然是退步，但「沒有遺失錨點」不足以證明語意與閉環安全。應把六張後續已完成的說法改為：有中間比較、後來擴為七張，最終當前版閉環複驗仍缺。

## 五、程式架構與技術債

### 5.1 五個核心責任

|模組|責任是否清楚|目前主要問題|
|---|---|---|
|Map Observer|名義上只回傳像素觀察，但實際承擔大量證據修復與權威建立|[observer-adapter](../../lib/observer-adapter.cjs)618行，混合多來源proof驗證；Python亦有比例、候選補充、配準與預覽語意；厚度已超過原先薄介面|
|Node Selector|相對清楚：意圖＋兩幀觀察→唯一選擇proof，不讀圖片／不點擊|[28行核心](../../lib/node-selector.cjs)本身簡潔，但高度依賴adapter生成完整正確證據；上游不完整就頻繁拒絕|
|Geometry|核心純函式清楚|[9行核心](../../lib/geometry.cjs)未統一承接全部ML前處理；多處人工逆投影、同名欄位不同空間是主要技術債|
|Click Transaction|清楚：時鐘、收圖、單次dispatch、回條、確認／失敗與trace|[preview-session](../../lib/preview-session.cjs)114行；直接依賴observer-adapter的私有root讀取，交易層與視覺權威具體實作仍耦合|
|Preview Verifier|外部契約清楚：驗證所選節點，不只驗證樓層或狀態名|[25行核心](../../lib/preview-verifier.cjs)很薄，但[Python身份](../../ml/preview_identity.py)317行混合OCR重讀、綠鈕、輪廓、格點與多尺寸假設，語意能力分散|

行數包含壓縮成單行的JS，不能直接拿來比較複雜度。Selector和Transaction不需要因上游失敗全面重寫。

### 5.2 隱藏耦合、狀態與重複實作

1. **座標規約分散。** `raw`、`v2Original`、`analysisBox`、`aspectRectification`、`v2TrackedMap`跨多層適配。PreviewSession建立的Geometry常是整張client的identity context，而實際校正早在Python完成；數學核心存在不代表所有投影已走單一鏈。#19／25／8是實際後果。
2. **多個布林值承載不同權限。** `verified`、`stateVerified`、`anchorVerified`、`previewOnly`及raw信心各有意義，但跨畫面等待與允許新點擊需要的證據強度不同。應釐清具名能力與拒絕階段，不能一律放寬或把分類成功當操作授權。
3. **兩語言驗證同一量測。** Python生成、JS再驗證本身有安全價值；問題是缺乏單一版本化座標／來源契約，容易改了一側漏另一側。不能為減少重複就刪掉獨立驗證。
4. **配準root與時序。** PreviewAnchorTracker在視窗／幾何／區域變更清根；恢復配準要求同尺寸同幾何、同區域、新鮮根及多個配對／跨列支持，避免鏈式無權威漂移。這些是合理安全約束，但不能證明任意跨布局可恢復。第39組新尺寸root已出現，該案更細根因仍待定位。
5. **舊分類前置。** Serena確認V1 `inspect_capture`主要在flow=MAP才建立mapReview；V2沿用觀察後再補證據，因此舊分類／OCR失敗仍可阻斷幾何觀察。可能需要明確拆開「量測可用」與「畫面語意可操作」。
6. **全域替換。** 沿用 `text_reader` reader／read_text、flow及candidate函式的全域替換，有context／finally還原；子程序分片也提供隔離。這是未來同程序併行風險，**沒有證據可直接宣稱已發生競態**。
7. **可重現性依賴。** 依賴 `F:/CRK helper`及外部venv；部分單元fixture硬綁歷史artifacts或F槽Python。現機能跑不等於乾淨clone可自足重現。
8. **執行器版本化不足。** 如 `artifacts/run_random_development_60_25.py`為Git忽略檔；[version-evidence](../../lib/version-evidence.cjs)主要涵蓋lib/ml/scripts/data，42檔閘門未同等包含所有ad-hoc控制器。核心grader有hash，不能因此說完全無版本控制；但最外層執行順序／續跑政策未完全納入同一封存。

這些支持**局部介面／責任調整**，而非否定整套架構。現有private WeakSet／WeakMap的proof權威、不可拷貝繞過的root、嚴格來源綁定、獨立grader與一次點擊交易應保留。

## 六、最近約兩天的開發效率

### 6.1 可量化工作分布

自2026-10-24 00:00（+08）至審查HEAD共有**46個Git提交**。同期間檔案觸及次數：observer-adapter 27次、map_aspect 17次、bounded_ocr 12次、preview_identity 11次、analyze_cases 10次。這反映修改集中在觀察／幾何／預覽界面，不是46個獨立根因，也不是工時。

主要工作為：凍結30段與變換資料、人工對照來源、失敗定位與反例、來源外框／比例／OCR／配準證據修復、修復後完整前綴回歸及工件hash核對。實際人時、模型token成本、每次使用的推理強度與等待佔比**無法確認**，不能從提交間距推算工作時間。

最大的改善來自三類：

- 原圖實測與幾何規約修正，使原先錨點／IoU失敗可跨多組恢復，而非只改分類名稱。
- 嚴格來源與交易root綁定，避免拿未觀察到的影格／舊proof確認預覽。
- 完整新鮮回歸，實際抓到#19與#8退步，避免只證明新案例成功。

不能給每個補丁增加多少百分點的精確歸因：提交與案例不是一對一，缺少全程配對實驗。

### 6.2 耗時與效能證據

|紀錄|觀察值|限制|
|---|---|---|
|35組1141個fresh packet|elapsedMs中位數3626.6092ms，nearest-rank p95 7397.2173ms，最大15125.0684ms|三並行worker下的實際packet計時；不是隔離G4benchmark|
|同批packet elapsedMs加總|4665113.3602ms，約77.75分鐘|多worker牆鐘區間會重疊，**不是總工時／CPU時間／整批實際經過時間**|
|[fast shadow診斷](../../artifacts/p4c-fast-shadow-timing-diagnostic.json)|中位1862.2914ms、p95 2971.0441ms、最大5175.7031ms|開發併行且未含目前完整MapActions；不能當正式結果|
|[候選階段診斷](../../artifacts/p4c-candidate-performance.json)|單圖各3樣本，中位baseline 1150.0357ms→grouped4 426.7927ms，同為9候選|只證明該候選步驟的局部改善；非整段辨識p95|

以上不足以推論當前隔離效能的精確值，但足以說明**沒有證據達到p95≤1500ms**。真實畫面年齡≤2500ms是另一硬限制；不能用虛擬時鐘或提高TTL掩蓋速度問題。

### 6.3 逐組方式是否有效率

停在首敗保留證據，對定位有效，也符合不跳過UNKNOWN的要求；完整回歸確實抓到退步，必須保留。但目前常見「新組失敗→加條件→重跑長前綴→下一組同類問題」，加上版本失效後全量OCR與外層腳本多版本，成本增加，最近10組也未顯示首敗下降。

建議保留最終全量矩陣與原分母，先按共通失敗族群收斂幾何／證據契約，再用對應小集合快速診斷、同版本完整回歸；統一可追溯執行器與依賴感知快取，避免過期結果混用。這是後續建議，本次沒有更動測試順序或實作。

繼續剩餘測試的最大風險：尚未跑的S3／S4與英文浮水印、美術／比例變化暴露新條件，令條件分支繼續膨脹；舊原生／固定集合沒對當前版本全部複驗；即使離線功能過關，真實延遲、DPI和UI布局仍可能再次失敗。

## 七、最終結論與下一階段建議

### 7.1 技術成熟度

目前屬於**有嚴格證據鏈的離線工程原型，正在驗證核心可靠性**。它比單張分類或只看按鈕名稱完整：已有38條真正經過觀察、選擇、換算、一次虛擬點擊與獨立確認的序列。但仍有正常正例停住、缺乏當前全集回歸與效能證據；不適合以「能自行完整操作」交付，也不能稱實機可用或辨識100%。

### 7.2 明確選項：C．需要局部架構調整

支持C的具體證據：

1. #19／25／8出現跨層座標規約／取整缺陷，直接對應原設計「單一可逆鏈」尚未完全落實。
2. observer-adapter兩天27次觸及；同類候選／OCR／預覽證據問題在多組重現，最近10組首敗6/10，未見收斂。
3. #39點位與身份評分已合格、畫面確有預覽，仍在跨畫面證據層拒絕；增加候選模型不是已證實解法。
4. 1551原生稽核從六張變七張變動且仍要求完整回放；當前版本未閉合該回歸。
5. 現有Selector、單次交易及來源權威仍可重用，38成功與負例拒絕不支持「重大架構全盤失效」的D結論。

因此不選A直接照原逐組補丁繼續；B只修共通bug仍不足以處理已實證的座標schema／權威界面債務；C是限縮的介面與責任調整，**不代表批准全面重寫、重訓或完整遠征**。

### 7.3 最值得優先解決的三個問題

|優先|問題與建議工作|完成證據|
|---|---|---|
|1|統一source／analysis／rectified／client的版本化座標與量測來源契約，明確集中轉換和取整責任|#8／19／25歷史回歸、各縮放／點前點後變更、全部既通過集合保持通過，無靠clamp或門檻放寬|
|2|定位#39短暫候選／配準證據空窗，釐清「允許等待」與「允許新點擊」的能力／狀態；保留獨立身份權威|不跳幀、不用未放行未來資訊、不新增重點；完整45幀與對應負例通過，拒絕原因有階段可追|
|3|收斂可重現回歸與效能出口：把控制器及依賴納版本，補當前1551＋原生20／固定15，最後60開發／30保留／正式負例與隔離profiling|同版本完整報告，三類測試結果分開，正式負例旗標閉合，暖機p95與畫面年齡達原門檻|

以上不是本次已執行的修改。完整60組開發測試**仍應保留並完成**，但宜先解決前兩項共通介面後再續跑剩餘；不得重抽容易案例、刪失敗、縮分母或把中間成功稱G4完成。

### 7.4 是否需要提高Codex推理強度

專案紀錄不足以確認各次模型／effort／token費用，沒有相同任務不同effort的配對證據；因此不能歸因為「推理強度太低」，也不能保證提高設定就能解決。官方將reasoning effort描述為速度、token與推理深度的調整手段；仍需清楚目標、輸出契約與驗證。[OpenAI reasoning指南](https://developers.openai.com/api/docs/guides/reasoning)

較合理的是在根因分析、座標契約及獨立審查上做受控比較，量測返工與驗證結果，再決定是否提高一級。當前優先問題是版本化證據、界面一致性與回歸成本，不應把改effort當進入下一階段的前提。本次未變更模型設定。

### 7.5 何時才適合真實遊戲驗收

必須先取得同一候選版本的完整G0–G4證據：30原始互動、60開發與30保留變換全部合格，正式負例確實執行並拒絕，原生候選變動經語意及閉環複驗，固定倍率／歷史失敗集無退步；重現與暖機p95≤1500ms、送出畫面年齡≤2500ms亦達標。失敗工件、標註、程式／模型／控制器版本需可重現，不得只列通過數。

之後由使用者**另行批准P5**，只做最小地圖→預覽閉環，以至少3種真實布局各10次、30/30驗證。真實大小／比例／核准DPI、工具列及客戶區偏移需有capture／input trace；正常正例人工救援、誤點、重點及越過預覽輸入均為0。批准P5前，本報告不恢復原生遊戲操作。

## 附錄A：來源、證據路徑與hash

### A.1 四部來源影片

|代號|影片ID／原始尺寸／影格率|來源與限制|
|---|---|---|
|S1|`buAwy1zf2LI`／1440×1080／30fps|`F:/CRK helper/data/video-validation/buAwy1zf2LI/buAwy1zf2LI.mp4`|
|S2|`L0ktY5qUppI`／960×720／30fps|`F:/CRK helper/data/map-video/L0ktY5qUppI.mp4`|
|S3|`0QxozULx_SQ`／1280×720／60fps|`F:/CRK helper/data/map-video/0QxozULx_SQ.mp4`；影片內有4:3內容與美術邊欄|
|S4|`LX46_2XTfJg`／1920×1080／60fps|[本地來源目錄](../../artifacts/p4c-new-source-LX46_2XTfJg/)；英文及@chateaw浮水印|

浮水印像素保留，不作節點身份或OCR授權來源。人眼可忽略浮水印，不代表當前尚未執行的S4隨機案例已證明不受影響。

### A.2 指紋登錄

以下影片hash引用凍結來源紀錄，本次未重新雜湊整部多GB影片；報告／manifest雜湊與當前工件讀取核對。雜湊只證明檔案身份，不證明內容判斷正確。

|對象|SHA-256|
|---|---|
|S1影片|`af0edce98d57e893d0051bb710668ba9a4ee8a5352aa363a8f5b097586cd901a`|
|S2影片|`a2a6efb31d39dddace649a1d4c7b4819f6820eeaf7756c5f08d52fe47eb88ab6`|
|S3影片|`df4176658c886958d5218c2ed1fa4c4d6b2798ae9ea5a758265e151cd4709de1`|
|S4影片|`3bfbf01b59055c3c01ff3309be3ffa7846e488938eff69adb6126f70c2ada712`|
|原生30 manifest|`918b5bd7dc4cfc41e78d383f29447ef9760199d914072ab6ee97cb973e4e4e26`|
|corpus-30-v3.json|`ea7c95615338b0601211489e90374bdd5b2e91951458033f50b5f094bc425a3f`|
|三變換90序列manifest|`189b37115b1d08b0c245306bb727b13759d00aa0efb76a30e74b85acc6038e60`|
|run-25 report|`8745181093c4d871e43e560b5a9a4fc14cf9fe371cf0d0d83947ec46d8ed2a02`|
|36組彙總report|`478c1d6af47ae9291b9bded0570e629af5a9e5d5e8edb5c566ee1242462ae915`|
|negative-random-evidence-v13|`a56b3a2baf501575fd0755ee092c7f538df2f51213a1583f0bb620ede7835bd6`|

### A.3 尚不能確認的事項

精確逐案例修正次數／平均修正次數、未保存的更早失敗、每個補丁獨立收益、實際人時／模型成本／歷史effort、當前全部固定倍率穩定性、當前原生1551／20段完整回歸、保留集準確率、整部影片全部內容的辨識率、第39組最底層單一根因、真實DPI／不同模擬器布局與原生輸入可靠性，均沒有充分現存證據，**無法確認**。這些缺口不以推測或中間里程碑代填。

