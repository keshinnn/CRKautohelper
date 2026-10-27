# CRK Helper V2：60組離線閉環階段報告（第40組停止，待High評估）

**這不是60組驗收完成報告。** 凍結分母60組，目前39通過、1失敗、20未測試；本輪僅新測第40組。第41～60與30組保留集未開始，P5未授權，G4仍未完成。

## 版本與測試口徑

- 本輪執行commit：`af30157`；功能版本：`c9559e14f97cdbdefd9c07ddfe00a9f305a3dc0a`。

- 第1～39組引用`artifacts/performance-20261027/random39-current-01/report.json`的實際同功能版本回歸，不宣稱本輪重新執行；177個專案檔案及141個外部依賴逐檔hash均一致。任何未來功能修改，都需要重新建立當版回歸證據，不能直接沿用此結果。

- 本輪265張全部新鮮推論，無raw V1封包快取。使用原凍結`data/p4c/random-source-v1.json`所指的90序列manifest，前60開發、後30保留；原影片、標註、排序、種子、裁切及安全門檻均未更改。原生影片與隨機客戶區的點擊均為虛擬回放，原生操作0。

- 本輪未重做效能分析；沿用上輪p95=2743.67ms作**未解決紀錄**，不是本輪新速度結果。未延長2500ms TTL／15秒deadline。

## 數量、通過率與首次成功率

|口徑|數量／比率|限制|
|---|---:|---|
|已知同凍結功能版本正例通過／全部分母|39/60＝65.00%|包含前回合明確標示的39組，20組未測試|
|已測試組通過率|39/40＝97.50%|不能當60組完成率|
|本輪新測首次通過率|0/1＝0%|第40組run-01失敗，無第二次完整閉環|
|歷史首個可追溯結果通過|15/39＝38.46%|不是可證明的第一次執行；其餘24組首筆為失敗|
|加入本輪第40組的首個可追溯通過|15/40＝37.50%|第41～60未知；絕對首次成功率無法確認|
|保留集驗證|0/30|未啟動；不以開發資料代替|

歷史數字從`docs/reports/crk-helper-v2-progress-review.md`逐列擷取並綁定文件SHA，保存於`historical-first-results.json`。歷史「失敗版本數」不是修正次數，不換算成平均修正次數。

## 第40組：實際失敗與根因

- S2影片`L0ktY5qUppI`，區域5／第1層／第1欄普通戰鬥，固定隨機變換；客戶區1885×793，來源960×720，邊緣裁切[3,5,12,1]，sx=1.994708995、sy=1.110644258。

- 265/265張完成當版新鮮分析；選點、座標及測試入口檢查通過，IoU=.9375148747、最小邊界距離20.5679px。只發出1次虛擬點擊，未重送。

- 消耗37張因果觀察後，在原影格35970／PTS1199000ms，以`EVIDENCE_UNVERIFIED`拒絕。點擊回執PTS1197833.333333ms，僅過1166.67ms；deadline1212833.333333ms，故不是15秒逾時，也不是2500ms TTL到期。

- 該影格仍是捲動中的地圖：入口已離開畫面、絕對錨點未知、flow=`MAP`但confidence=0。`adaptMap`產生stateVerified=false／verified=false；Preview Verifier依原規則拒絕。`v2TrackedMap.verified=true`僅是previewOnly的像素配準，不能拿來冒充新點擊或完整畫面身份權威。

- 季別與倒數文字的全圖OCR框重疊6.9px，超過原獨立行重疊上限5.295px，必須重新量測文字框。`ml/bounded_ocr.py:163`附近的既有重試呼叫V1 `refine_map_title`，該函式只接受score<.9的弱標題；此處季別定位score=.957，無法觸發其重讀。`lib/observer-adapter.cjs:584`及`lib/preview-verifier.cjs:10`維持拒絕，是缺少必要證據的結果。

- 使用同一原PNG、相同現有OCR／模型做唯讀診斷：重新偵測文字框後，季別可由既有line variants讀到.921480584；但倒數行的新鮮完整重讀最高.896664027，低於原.90，並出現`13：19:00`的全形冒號。不能改分數、把舊全圖高分當新重讀，或只做文字替換就宣稱證據通過。

## 未採用修補與停止界線

先新增實際來源綁定的3項測試：正例先RED（scene confidence0），刪除季別像素及重複季別定位兩個負例通過。嘗試只銜接既有偵測器與line recognizer以收緊高信心定位框；季別恢復，但正例仍RED，倒數證據未過原門檻。因此**沒有接受任何功能修正，也沒有宣稱第40組修復**。

草稿patch、草稿測試與所有RED／失敗GREEN嘗試日誌已移到artifact，不留在生產模組或正式測試目錄。`git restore`還原原換行格式後，177+141個hash逐項一致；沒有未驗證功能流入凍結版本。

下一步涉及通用跨比例OCR文字重定位／完整行重讀與來源證據契約的設計，超出這次已證實可用的小銜接修補。依使用者「需重新設計辨識演算法／重大問題則停下改High」的界線，已停止修改與後續序列，供High評估。**尚未證明需要全面重寫架構或更換模型**；也不把此停止描述成整體架構已判定失敗。

High接續時先讀`docs/validation/2026-10-27-case40-high-handoff.md`；不要直接套用未通過的草稿，不降低.90、行獨立性、IoU或來源檢查。

## 回歸、剩餘缺陷與證據

本輪沒有新接受程式變更，因此未重跑整套單元／74項回歸。前回合同功能版本的Node125通過、Python187通過＋2項S3已知expectedFailure、74/74回歸及30負例＋2對照，只以原日期／原版本引用，不冒稱本輪新成績。新案例失敗不表示舊39組退步，但證明泛化尚未完成。

剩餘缺陷：本次S2跨比例MAP等待證據鏈；S3影格46047戰鬥與46057治療漏候選仍OPEN；G4效能p95仍超1500ms；第41～60、保留30與正式G4／P5尚未驗收。

第40組已保存並核對38束／190檔證據（37張觀察＋summary，各含input、observation、overlay、events、result），全部265原PNG與新鮮packet來源綁定核對。根目錄`artifacts/development-20261027-medium-01/`；詳細hash索引`case40-causal-diagnosis.json`、`qualification.json`。

## 60組逐項狀態

尺寸為實際渲染客戶區；箭頭為同條序列的幾何切換。前39「通過」明確是先前同功能版本回歸；本輪第40以後不使用舊測試結果填補。

|編號|凍結案例／區・層・欄|尺寸|目前結果|首個可追溯結果|失敗原因／證據|
|---|---|---|---|---|---|
|01|zone-1-first-battle-random-fixed／1・1・2|2290×1293|通過（前回合，同功能hash）|失敗／3|歷史：地圖／預覽；見 F01；當版IoU=0.94323；[交易](../../artifacts/performance-20261027/random39-current-01/replay/zone-1-first-battle-random-fixed/transaction.json)|
|02|zone-1-first-battle-random-pre-change／1・1・2|1643×723 → 1557×948|通過（前回合，同功能hash）|失敗／1|歷史：證據適配；見 F02；當版IoU=0.95353；[交易](../../artifacts/performance-20261027/random39-current-01/replay/zone-1-first-battle-random-pre-change/transaction.json)|
|03|zone-1-first-battle-random-post-change／1・1・2|2345×1064 → 1651×969|通過（前回合，同功能hash）|失敗／2|歷史：穩定性／預覽；見 F03；當版IoU=0.94558；[交易](../../artifacts/performance-20261027/random39-current-01/replay/zone-1-first-battle-random-post-change/transaction.json)|
|04|zone-2-first-battle-random-fixed／2・1・2|1471×777|通過（前回合，同功能hash）|失敗／3|歷史：點前穩定性；見 F04；當版IoU=0.95924；[交易](../../artifacts/performance-20261027/random39-current-01/replay/zone-2-first-battle-random-fixed/transaction.json)|
|05|zone-2-first-battle-random-pre-change／2・1・2|2094×948 → 1568×1008|通過（前回合，同功能hash）|失敗／2|歷史：點前重取／G2；見 F05；當版IoU=0.95443；[交易](../../artifacts/performance-20261027/random39-current-01/replay/zone-2-first-battle-random-pre-change/transaction.json)|
|06|zone-2-first-battle-random-post-change／2・1・2|1196×631 → 2065×1233|通過（前回合，同功能hash）|通過／0|歷史：未見該組失敗紀錄；當版IoU=0.96775；[交易](../../artifacts/performance-20261027/random39-current-01/replay/zone-2-first-battle-random-post-change/transaction.json)|
|07|zone-3-first-battle-random-fixed／3・1・2|2481×1347|通過（前回合，同功能hash）|通過／0|歷史：未見該組失敗紀錄；當版IoU=0.94491；[交易](../../artifacts/performance-20261027/random39-current-01/replay/zone-3-first-battle-random-fixed/transaction.json)|
|08|zone-3-first-battle-random-pre-change／3・1・2|2345×1420 → 2041×920|通過（前回合，同功能hash）|失敗／2|歷史：預覽 OCR／精度回歸；見 F08；當版IoU=0.95593；[交易](../../artifacts/performance-20261027/random39-current-01/replay/zone-3-first-battle-random-pre-change/transaction.json)|
|09|zone-3-first-battle-random-post-change／3・1・2|2071×1132 → 1058×577|通過（前回合，同功能hash）|通過／0|歷史：未見該組失敗紀錄；當版IoU=0.95077；[交易](../../artifacts/performance-20261027/random39-current-01/replay/zone-3-first-battle-random-post-change/transaction.json)|
|10|zone-8-first-battle-random-fixed／8・1・4|2009×1010|通過（前回合，同功能hash）|失敗／2|歷史：候選／預覽；見 F10；當版IoU=0.95299；[交易](../../artifacts/performance-20261027/random39-current-01/replay/zone-8-first-battle-random-fixed/transaction.json)|
|11|zone-8-first-battle-random-pre-change／8・1・4|1103×553 → 2225×1336|通過（前回合，同功能hash）|通過／0|歷史：未見該組失敗紀錄；當版IoU=0.94516；[交易](../../artifacts/performance-20261027/random39-current-01/replay/zone-8-first-battle-random-pre-change/transaction.json)|
|12|zone-8-first-battle-random-post-change／8・1・4|1677×1051 → 2252×1434|通過（前回合，同功能hash）|通過／0|歷史：未見該組失敗紀錄；當版IoU=0.95228；[交易](../../artifacts/performance-20261027/random39-current-01/replay/zone-8-first-battle-random-post-change/transaction.json)|
|13|zone-9-first-battle-random-fixed／9・1・4|996×541|通過（前回合，同功能hash）|失敗／1|歷史：G2 外框品質；見 F13；當版IoU=0.97312；[交易](../../artifacts/performance-20261027/random39-current-01/replay/zone-9-first-battle-random-fixed/transaction.json)|
|14|zone-9-first-battle-random-pre-change／9・1・4|1469×792 → 1366×1074|通過（前回合，同功能hash）|失敗／3|歷史：OCR／近原生比例；見 F14；當版IoU=0.95697；[交易](../../artifacts/performance-20261027/random39-current-01/replay/zone-9-first-battle-random-pre-change/transaction.json)|
|15|zone-9-first-battle-random-post-change／9・1・4|1805×1401 → 1315×546|通過（前回合，同功能hash）|失敗／1|歷史：比例共識／錨點；見 F15；當版IoU=0.94842；[交易](../../artifacts/performance-20261027/random39-current-01/replay/zone-9-first-battle-random-post-change/transaction.json)|
|16|dev-primary-zone2-floor2-col3-higher-random-fixed／2・2・3|1342×552|通過（前回合，同功能hash）|失敗／1|歷史：比例／前置完成位置；見 F16；當版IoU=0.94032；[交易](../../artifacts/performance-20261027/random39-current-01/replay/dev-primary-zone2-floor2-col3-higher-random-fixed/transaction.json)|
|17|dev-primary-zone2-floor2-col3-higher-random-pre-change／2・2・3|2467×1302 → 2543×1050|通過（前回合，同功能hash）|失敗／1|歷史：入口／列距；見 F17；當版IoU=0.93890；[交易](../../artifacts/performance-20261027/random39-current-01/replay/dev-primary-zone2-floor2-col3-higher-random-pre-change/transaction.json)|
|18|dev-primary-zone2-floor2-col3-higher-random-post-change／2・2・3|1997×1146 → 2196×1287|通過（前回合，同功能hash）|失敗／2|歷史：連線／peer 身份；見 F18；當版IoU=0.93670；[交易](../../artifacts/performance-20261027/random39-current-01/replay/dev-primary-zone2-floor2-col3-higher-random-post-change/transaction.json)|
|19|dev-primary-zone3-floor3-col1-higher-random-fixed／3・3・1|1873×1370|通過（前回合，同功能hash）|通過／1|歷史：後續回歸的座標 schema；見 F19；當版IoU=0.92476；[交易](../../artifacts/performance-20261027/random39-current-01/replay/dev-primary-zone3-floor3-col1-higher-random-fixed/transaction.json)|
|20|dev-primary-zone3-floor3-col1-higher-random-pre-change／3・3・1|1255×689 → 1941×1265|通過（前回合，同功能hash）|失敗／1|歷史：完成狀態／目前位置；見 F20；當版IoU=0.94454；[交易](../../artifacts/performance-20261027/random39-current-01/replay/dev-primary-zone3-floor3-col1-higher-random-pre-change/transaction.json)|
|21|dev-primary-zone3-floor3-col1-higher-random-post-change／3・3・1|1734×1187 → 1772×817|通過（前回合，同功能hash）|失敗／3|歷史：配準來源／預覽地圖；見 F21；當版IoU=0.94604；[交易](../../artifacts/performance-20261027/random39-current-01/replay/dev-primary-zone3-floor3-col1-higher-random-post-change/transaction.json)|
|22|dev-primary-zone4-floor2-col3-random-fixed／4・2・3|2383×1372|通過（前回合，同功能hash）|失敗／1|歷史：跨層幾何證據適配；見 F22；當版IoU=0.94645；[交易](../../artifacts/performance-20261027/random39-current-01/replay/dev-primary-zone4-floor2-col3-random-fixed/transaction.json)|
|23|dev-primary-zone4-floor2-col3-random-pre-change／4・2・3|1101×668 → 1734×1018|通過（前回合，同功能hash）|通過／0|歷史：未見該組失敗紀錄；當版IoU=0.94612；[交易](../../artifacts/performance-20261027/random39-current-01/replay/dev-primary-zone4-floor2-col3-random-pre-change/transaction.json)|
|24|dev-primary-zone4-floor2-col3-random-post-change／4・2・3|2275×1203 → 1448×1072|通過（前回合，同功能hash）|失敗／1|歷史：原生預覽外框；見 F24；當版IoU=0.94494；[交易](../../artifacts/performance-20261027/random39-current-01/replay/dev-primary-zone4-floor2-col3-random-post-change/transaction.json)|
|25|dev-primary-zone6-floor1-col2-random-fixed／6・1・2|1145×721|通過（前回合，同功能hash）|失敗／1|歷史：投影取整；見 F25；當版IoU=0.96864；[交易](../../artifacts/performance-20261027/random39-current-01/replay/dev-primary-zone6-floor1-col2-random-fixed/transaction.json)|
|26|dev-primary-zone6-floor1-col2-random-pre-change／6・1・2|2105×871 → 1056×635|通過（前回合，同功能hash）|通過／0|歷史：未見該組失敗紀錄；當版IoU=0.97524；[交易](../../artifacts/performance-20261027/random39-current-01/replay/dev-primary-zone6-floor1-col2-random-pre-change/transaction.json)|
|27|dev-primary-zone6-floor1-col2-random-post-change／6・1・2|2275×1186 → 1349×580|通過（前回合，同功能hash）|通過／0|歷史：未見該組失敗紀錄；當版IoU=0.95434；[交易](../../artifacts/performance-20261027/random39-current-01/replay/dev-primary-zone6-floor1-col2-random-post-change/transaction.json)|
|28|dev-primary-zone10-floor1-col2-random-fixed／10・1・2|1203×864|通過（前回合，同功能hash）|通過／0|歷史：未見該組失敗紀錄；當版IoU=0.94989；[交易](../../artifacts/performance-20261027/random39-current-01/replay/dev-primary-zone10-floor1-col2-random-fixed/transaction.json)|
|29|dev-primary-zone10-floor1-col2-random-pre-change／10・1・2|1187×703 → 1389×615|通過（前回合，同功能hash）|通過／0|歷史：未見該組失敗紀錄；當版IoU=0.93462；[交易](../../artifacts/performance-20261027/random39-current-01/replay/dev-primary-zone10-floor1-col2-random-pre-change/transaction.json)|
|30|dev-primary-zone10-floor1-col2-random-post-change／10・1・2|1217×625 → 1725×1256|通過（前回合，同功能hash）|失敗／1|歷史：原生預覽外框；見 F30；當版IoU=0.94140；[交易](../../artifacts/performance-20261027/random39-current-01/replay/dev-primary-zone10-floor1-col2-random-post-change/transaction.json)|
|31|dev-L0-zone6-floor1-col2-select-1773-random-fixed／6・1・2|966×740|通過（前回合，同功能hash）|失敗／2|歷史：小比例／幾何一致性；見 F31；當版IoU=0.93587；[交易](../../artifacts/performance-20261027/random39-current-01/replay/dev-L0-zone6-floor1-col2-select-1773-random-fixed/transaction.json)|
|32|dev-L0-zone6-floor1-col2-select-1773-random-pre-change／6・1・2|1152×597 → 2015×850|通過（前回合，同功能hash）|通過／0|歷史：未見該組失敗紀錄；當版IoU=0.91750；[交易](../../artifacts/performance-20261027/random39-current-01/replay/dev-L0-zone6-floor1-col2-select-1773-random-pre-change/transaction.json)|
|33|dev-L0-zone6-floor1-col2-select-1773-random-post-change／6・1・2|1486×1014 → 1218×564|通過（前回合，同功能hash）|失敗／1|歷史：OCR 分行；見 F33；當版IoU=0.92853；[交易](../../artifacts/performance-20261027/random39-current-01/replay/dev-L0-zone6-floor1-col2-select-1773-random-post-change/transaction.json)|
|34|dev-L0-zone6-floor1-col2-resume-1781-random-fixed／6・1・2|1781×915|通過（前回合，同功能hash）|失敗／1|歷史：目前位置外環；見 F34；當版IoU=0.90944；[交易](../../artifacts/performance-20261027/random39-current-01/replay/dev-L0-zone6-floor1-col2-resume-1781-random-fixed/transaction.json)|
|35|dev-L0-zone6-floor1-col2-resume-1781-random-pre-change／6・1・2|1168×594 → 1938×1263|通過（前回合，同功能hash）|通過／0|歷史：未見該組失敗紀錄；當版IoU=0.90635；[交易](../../artifacts/performance-20261027/random39-current-01/replay/dev-L0-zone6-floor1-col2-resume-1781-random-pre-change/transaction.json)|
|36|dev-L0-zone6-floor1-col2-resume-1781-random-post-change／6・1・2|1457×1035 → 1227×571|通過（前回合，同功能hash）|失敗／3|歷史：候選／OCR／預覽時序；見 F36；當版IoU=0.91218；[交易](../../artifacts/performance-20261027/random39-current-01/replay/dev-L0-zone6-floor1-col2-resume-1781-random-post-change/transaction.json)|
|37|dev-L0-zone6-floor3-col3-select-1932-random-fixed／6・3・3|1256×645|通過（前回合，同功能hash）|通過／0|歷史：未見該組失敗紀錄；當版IoU=0.95069；[交易](../../artifacts/performance-20261027/random39-current-01/replay/dev-L0-zone6-floor3-col3-select-1932-random-fixed/transaction.json)|
|38|dev-L0-zone6-floor3-col3-select-1932-random-pre-change／6・3・3|2137×1241 → 2552×1391|通過（前回合，同功能hash）|通過／0|歷史：未見該組失敗紀錄；當版IoU=0.93451；[交易](../../artifacts/performance-20261027/random39-current-01/replay/dev-L0-zone6-floor3-col3-select-1932-random-pre-change/transaction.json)|
|39|dev-L0-zone6-floor3-col3-select-1932-random-post-change／6・3・3|1786×1227 → 2053×1191|通過（前回合，同功能hash）|失敗／1|歷史：點後預覽證據；見 F39；當版IoU=0.93916；[交易](../../artifacts/performance-20261027/random39-current-01/replay/dev-L0-zone6-floor3-col3-select-1932-random-post-change/transaction.json)|
|40|dev-earlier-L0-zone5-floor1-col1-random-fixed／5・1・1|1885×793|失敗（本輪run-01）|失敗／1個完整閉環嘗試|MAP等待權威不足→EVIDENCE_UNVERIFIED；[交易](../../artifacts/development-20261027-medium-01/case-40/run-01/replay/dev-earlier-L0-zone5-floor1-col1-random-fixed/transaction.json)|
|41|dev-earlier-L0-zone5-floor1-col1-random-pre-change／5・1・1|2481×1135 → 1751×963|未測試|無法確認|第40組停止，未執行；來源已凍結|
|42|dev-earlier-L0-zone5-floor1-col1-random-post-change／5・1・1|1466×1087 → 1729×1350|未測試|無法確認|第40組停止，未執行；來源已凍結|
|43|dev-earlier-L0-zone8-floor1-col4-random-fixed／8・1・4|2249×1408|未測試|無法確認|第40組停止，未執行；來源已凍結|
|44|dev-earlier-L0-zone8-floor1-col4-random-pre-change／8・1・4|1706×785 → 1009×632|未測試|無法確認|第40組停止，未執行；來源已凍結|
|45|dev-earlier-L0-zone8-floor1-col4-random-post-change／8・1・4|1958×1107 → 1813×945|未測試|無法確認|第40組停止，未執行；來源已凍結|
|46|dev-earlier-0Q-zone4-floor1-col4-random-fixed／4・1・4|1697×1075|未測試|無法確認|第40組停止，未執行；來源已凍結|
|47|dev-earlier-0Q-zone4-floor1-col4-random-pre-change／4・1・4|1886×1065 → 1753×1326|未測試|無法確認|第40組停止，未執行；來源已凍結|
|48|dev-earlier-0Q-zone4-floor1-col4-random-post-change／4・1・4|1209×730 → 1315×560|未測試|無法確認|第40組停止，未執行；來源已凍結|
|49|dev-LX46-zone1-floor1-col1-resume-random-fixed／1・1・1|1590×1079|未測試|無法確認|第40組停止，未執行；來源已凍結|
|50|dev-LX46-zone1-floor1-col1-resume-random-pre-change／1・1・1|1796×1384 → 1801×1057|未測試|無法確認|第40組停止，未執行；來源已凍結|
|51|dev-LX46-zone1-floor1-col1-resume-random-post-change／1・1・1|1709×1097 → 1448×693|未測試|無法確認|第40組停止，未執行；來源已凍結|
|52|dev-LX46-zone2-floor1-col2-select-random-fixed／2・1・2|1710×1229|未測試|無法確認|第40組停止，未執行；來源已凍結|
|53|dev-LX46-zone2-floor1-col2-select-random-pre-change／2・1・2|1290×1005 → 1466×713|未測試|無法確認|第40組停止，未執行；來源已凍結|
|54|dev-LX46-zone2-floor1-col2-select-random-post-change／2・1・2|1475×640 → 1962×1238|未測試|無法確認|第40組停止，未執行；來源已凍結|
|55|dev-LX46-zone3-floor1-col4-select-random-fixed／3・1・4|1446×854|未測試|無法確認|第40組停止，未執行；來源已凍結|
|56|dev-LX46-zone3-floor1-col4-select-random-pre-change／3・1・4|2167×1141 → 1268×662|未測試|無法確認|第40組停止，未執行；來源已凍結|
|57|dev-LX46-zone3-floor1-col4-select-random-post-change／3・1・4|1462×690 → 1449×1151|未測試|無法確認|第40組停止，未執行；來源已凍結|
|58|dev-LX46-zone4-floor2-col1-select-random-fixed／4・2・1|2306×1417|未測試|無法確認|第40組停止，未執行；來源已凍結|
|59|dev-LX46-zone4-floor2-col1-select-random-pre-change／4・2・1|1067×752 → 2399×1182|未測試|無法確認|第40組停止，未執行；來源已凍結|
|60|dev-LX46-zone4-floor2-col1-select-random-post-change／4・2・1|1329×732 → 1437×853|未測試|無法確認|第40組停止，未執行；來源已凍結|
