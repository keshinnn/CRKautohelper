# CRK Helper V2：60組開發測試階段報告（M1有限實作）

**當版41通過、1失敗、18未測試／60；停止於第42組，43～60與30保留集未開始。** 本輪M1已完成第41組與全部指定必要回歸；第42組出現M1啟動條件涵蓋不到的局部漏候選。未擴大啟動條件、未降低門檻、未修補Selector或安全規則。這是部分報告，不能宣稱60組、正式G4或P5完成。

功能／測試commit `9944a9dca7ee5edb1b0a0afc5e4d2da1c8e31543`；181個專案來源／測試／資料檔、141外部依賴、runner與runtime hash綁定每個run。後續文件提交不變更這些功能hash。原凍結60開發變換與30保留變換來自20／10段互動、四個來源，**並非60段獨立影片**；manifest SHA256 `189b37115b1d08b0c245306bb727b13759d00aa0efb76a30e74b85acc6038e60`，分母與資料未改。只有離線影片、新鮮Python推論、因果回放與虛擬點擊；原生操作0，P5未授權。

## 通過率與歷史

- 當版總分母通過率41/60=68.33%；已測42組中41/42=97.62%。18組仍未測試。
- M1版本已測42組均保留第一輪結果：41組通過、第42組失敗；不能外推剩餘案例。
- 歷史首筆可追溯通過15/42=35.71%；歷史紀錄未必是絕對第一次執行，不能冒稱絕對首次成功率。表格歷史欄「／數字」沿用舊報告的失敗紀錄數，**不代表修正次數**；平均修正次數無法確認。
- 第41組原版本完整266張但3張觀察後ANCHOR_MISSING；M1當版266 fresh、250張因果觀察、1虛擬點擊、PREVIEW_CONFIRMED，IoU .932545545、margin25.0781px。保留舊失敗與新通過紀錄。

## M1修改範圍及驗證

生產只修改`ml/fast_map_candidates.py`，新增五項聚焦測試。RED五項中兩項實際失敗，最小修改後五項GREEN；原fast matcher等價測試與一次整體獨立審查（0 Critical／0 Important／0 Minor）完成。原204個模板尺寸搜尋項目、原候選與NMS輸出前綴完整保留；只有原NMS少於4個才補掃至多51個標準尺度floor/ceil項目。同一Canny，匹配門檻.48、原NMS、IoU、三peer及source／geometry／identity驗證均不變；不是第二次完整255掃描。未改校準器、raster、Node Selector、Click Transaction、Preview Verifier，未更換模型。

|當版驗證|結果|證據（本輪artifact根目錄：`artifacts/m1-20261027-01/`）|
|---|---|---|
|第41組|266/266 fresh，完整閉環通過|`case41-fresh-01/report.json`|
|前40組|40/40，1583/1583 fresh，0 raw cache|`prefix40-current-01/report.json`|
|原生20組|20/20，1551/1551 fresh|`native20-current-01/report.json`|
|固定倍率15組|15/15，381/381 fresh；75%/100%/125%|`fixed15-current-01/report.json`|
|開發負例30＋評分器對照|30/30、57 fresh、0點擊，兩對照正確評分，3張首個UNKNOWN直接停|`negative30-current-01/report.json`、`negative30-current-integrity.json`|
|完整Node|127/127、0失敗|`node-full.log`|
|完整Python|213項：211通過＋2既有S3 expectedFailure|`python-full.log`|
|原生1551與七張稽核|1551覆蓋、0候選變動、0錨點退步，七張均已補查|`native1551-seven-current-01/report.json`、`seven-current-pixel-review.json`|
|取整邊界壓力|28衍生model輸入、3觸發，base保留、S2新增候選定位／類別檢查通過|`rounding-stress.json`|

正例完整性稽核3781 fresh封包、2894束五檔證據／14470檔。第42失敗另有265 fresh及3束／15檔失敗證據，已通過來源、畫面、封包及bundle hash核對。上述76項正例閉環包含重複來源與變換，不能稱76種地圖。負例報告`formalNegativeGateComplete=false`；開發負例及評分器對照不自動升格正式G4。1551比較與七張目視核對亦不等於1551張都有完整逐節點像素真值。

第41組266封包比較有27張校正後mapReview變動，239張未變、0原始V1 map輸出變動；27張疊圖總覽及關鍵全尺寸影格已補查，未見明顯UI誤框。這是補充目視核對，非全266逐節點真值。

## 第42組失敗：候選總數足夠，但指定節點缺漏

來源S2／`L0ktY5qUppI`、區域5／第1層／第1欄、post-change變換；前兩張35929與35935均1466×1087，實際model raster960×712。**失敗發生在後段尺寸切換之前**。兩張均MAP verified、zone5、anchor verified，但第一排第一欄目標匹配數為0。`selectNode`的`MAP_AMBIGUOUS`在此表示未找到唯一目標，並非重複節點。

|前置影格|原204候選|M1候選／觸發|目標ROI最高原分數|NMS前／後目標數|
|---|---:|---|---:|---|
|35929|11|11／不觸發|.4759610593|0／0|
|35935|11|11／不觸發|.4750573039|0／0|

以同張實際像素、既有Lanczos與Canny、原204 kernel逐項量測；基準matcher與M1結果完全等價，實測未呼叫補強bank。目標分數在.48之前已不足，故是**候選生成失敗**，沒有證據指向NMS排除、比例跳動、座標投影或預覽身份驗證。GT ROI只用於診斷評分，不回饋辨識器或操作授權；未使用未來影格、舊座標或跳過UNKNOWN。未重跑舊版完整Producer閉環，不能把同幀matcher對照冒充舊版第42完整驗收。

當版完整265/265 fresh；回放消費2張、0虛擬點擊、0原生操作、transaction=null，沒有預覽確認。三束失敗證據保留。修復這類「總量≥4但局部缺漏」需要超出本次M1的觸發範圍；本輪不擴大條件、不增加單圖特判、不修改Selector來繞過拒絕。需另行設計與批准後再改。

證據：`case42-fresh-01/report.json`、`case42-fresh-01/replay/.../transaction.json`、`case42-root-cause.json`、`trace-case42.py`／`.log`、`case42-trace-35929/`、`case42-trace-35935/`、`case42-failure-integrity.json`。追溯的程式版本、原圖與封包SHA均保存。

## 效能（正式G4仍未達標）

配對微基準每圖15次、模板bank暖機、每次重算Canny與matching。S2使用第41組pre-change實際model，並非第42組同編號的不同變換；S3使用原生實際model：

|輸入|M1觸發|原matcher p50/p95 ms|M1 p50/p95 ms|新增掃描critical p50/p95 ms|
|---|---|---|---|---|
|35929|否|495.02/561.31|491.51/547.17|無|
|35935|是，2→12|486.15/528.15|609.36/681.35|130.04/149.91|
|46047|否|396.72/424.50|399.17/445.85|無|
|46057|否|396.59/428.63|394.48/432.14|無|

template bank miss單次呼叫另記441.82／618.57／412.33／407.62ms；底層asset已暖，只有各kernel bank清除，n=1，**不是完整冷啟動p95**。額外掃描只掃新kernel，同一Canny執行一次；沒有重掃原204。微基準不含OCR／Producer／Node。

單worker隔離完整193 fresh，同既有來源與runtime指紋、暖機10張：

|整體量測|樣本|p50 ms|p95 ms|
|---|---:|---:|---:|
|Producer|183|1718.68|2292.35|
|Node因果路徑|124|2.30|4.29|
|Producer＋Node因果CPU|124|1688.88|2374.09|

同幀中間結果98 hit／343 miss、p95成本4.24／347.72ms，crossFrame=false。最慢暖機影格57942為2557.45ms，aspect_geometry佔1579.21ms。主要模組p95：aspect_geometry1360.61ms、v1_observation1033.40ms、preview_registration366.11ms；各模組p95不能相加。

舊同來源Producer p95 2713.02ms／183張，整體p95 2743.67ms／127消費張；新整體消費124張，兩輪非逐項交錯配對且消費母體有差異，不能把全部差值歸功於M1。無嚴重退步證據，但**2374.09仍大於1500，G4未完成**。離線CPU合計不含live capture／IPC；畫面送出年齡≤2500及真實15秒結果未驗收，不以PTS或同幀重用冒稱實機效能。

## 60組逐項結果

歷史詳細失敗與修補原文保存於[修補前報告快照](../../artifacts/m1-20261027-01/historical-pre-m1-development60-report.md)，舊記錄不搬成當版成績。

|編號|凍結案例|實際客戶區尺寸|M1當版|歷史首筆可追溯／失敗紀錄數|失敗或修補紀錄|當版證據|
|---|---|---|---|---|---|---|
|01|zone-1-first-battle-random-fixed|2290×1293|通過|失敗／3|地圖／預覽；見 F01|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/zone-1-first-battle-random-fixed/summary/result.json)|
|02|zone-1-first-battle-random-pre-change|1643×723 → 1557×948|通過|失敗／1|證據適配；見 F02|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/zone-1-first-battle-random-pre-change/summary/result.json)|
|03|zone-1-first-battle-random-post-change|2345×1064 → 1651×969|通過|失敗／2|穩定性／預覽；見 F03|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/zone-1-first-battle-random-post-change/summary/result.json)|
|04|zone-2-first-battle-random-fixed|1471×777|通過|失敗／3|點前穩定性；見 F04|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/zone-2-first-battle-random-fixed/summary/result.json)|
|05|zone-2-first-battle-random-pre-change|2094×948 → 1568×1008|通過|失敗／2|點前重取／G2；見 F05|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/zone-2-first-battle-random-pre-change/summary/result.json)|
|06|zone-2-first-battle-random-post-change|1196×631 → 2065×1233|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/zone-2-first-battle-random-post-change/summary/result.json)|
|07|zone-3-first-battle-random-fixed|2481×1347|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/zone-3-first-battle-random-fixed/summary/result.json)|
|08|zone-3-first-battle-random-pre-change|2345×1420 → 2041×920|通過|失敗／2|預覽 OCR／精度回歸；見 F08|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/zone-3-first-battle-random-pre-change/summary/result.json)|
|09|zone-3-first-battle-random-post-change|2071×1132 → 1058×577|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/zone-3-first-battle-random-post-change/summary/result.json)|
|10|zone-8-first-battle-random-fixed|2009×1010|通過|失敗／2|候選／預覽；見 F10|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/zone-8-first-battle-random-fixed/summary/result.json)|
|11|zone-8-first-battle-random-pre-change|1103×553 → 2225×1336|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/zone-8-first-battle-random-pre-change/summary/result.json)|
|12|zone-8-first-battle-random-post-change|1677×1051 → 2252×1434|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/zone-8-first-battle-random-post-change/summary/result.json)|
|13|zone-9-first-battle-random-fixed|996×541|通過|失敗／1|G2 外框品質；見 F13|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/zone-9-first-battle-random-fixed/summary/result.json)|
|14|zone-9-first-battle-random-pre-change|1469×792 → 1366×1074|通過|失敗／3|OCR／近原生比例；見 F14|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/zone-9-first-battle-random-pre-change/summary/result.json)|
|15|zone-9-first-battle-random-post-change|1805×1401 → 1315×546|通過|失敗／1|比例共識／錨點；見 F15|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/zone-9-first-battle-random-post-change/summary/result.json)|
|16|dev-primary-zone2-floor2-col3-higher-random-fixed|1342×552|通過|失敗／1|比例／前置完成位置；見 F16|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/dev-primary-zone2-floor2-col3-higher-random-fixed/summary/result.json)|
|17|dev-primary-zone2-floor2-col3-higher-random-pre-change|2467×1302 → 2543×1050|通過|失敗／1|入口／列距；見 F17|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/dev-primary-zone2-floor2-col3-higher-random-pre-change/summary/result.json)|
|18|dev-primary-zone2-floor2-col3-higher-random-post-change|1997×1146 → 2196×1287|通過|失敗／2|連線／peer 身份；見 F18|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/dev-primary-zone2-floor2-col3-higher-random-post-change/summary/result.json)|
|19|dev-primary-zone3-floor3-col1-higher-random-fixed|1873×1370|通過|通過／1|後續回歸的座標 schema；見 F19|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/dev-primary-zone3-floor3-col1-higher-random-fixed/summary/result.json)|
|20|dev-primary-zone3-floor3-col1-higher-random-pre-change|1255×689 → 1941×1265|通過|失敗／1|完成狀態／目前位置；見 F20|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/dev-primary-zone3-floor3-col1-higher-random-pre-change/summary/result.json)|
|21|dev-primary-zone3-floor3-col1-higher-random-post-change|1734×1187 → 1772×817|通過|失敗／3|配準來源／預覽地圖；見 F21|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/dev-primary-zone3-floor3-col1-higher-random-post-change/summary/result.json)|
|22|dev-primary-zone4-floor2-col3-random-fixed|2383×1372|通過|失敗／1|跨層幾何證據適配；見 F22|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/dev-primary-zone4-floor2-col3-random-fixed/summary/result.json)|
|23|dev-primary-zone4-floor2-col3-random-pre-change|1101×668 → 1734×1018|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/dev-primary-zone4-floor2-col3-random-pre-change/summary/result.json)|
|24|dev-primary-zone4-floor2-col3-random-post-change|2275×1203 → 1448×1072|通過|失敗／1|原生預覽外框；見 F24|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/dev-primary-zone4-floor2-col3-random-post-change/summary/result.json)|
|25|dev-primary-zone6-floor1-col2-random-fixed|1145×721|通過|失敗／1|投影取整；見 F25|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/dev-primary-zone6-floor1-col2-random-fixed/summary/result.json)|
|26|dev-primary-zone6-floor1-col2-random-pre-change|2105×871 → 1056×635|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/dev-primary-zone6-floor1-col2-random-pre-change/summary/result.json)|
|27|dev-primary-zone6-floor1-col2-random-post-change|2275×1186 → 1349×580|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/dev-primary-zone6-floor1-col2-random-post-change/summary/result.json)|
|28|dev-primary-zone10-floor1-col2-random-fixed|1203×864|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/dev-primary-zone10-floor1-col2-random-fixed/summary/result.json)|
|29|dev-primary-zone10-floor1-col2-random-pre-change|1187×703 → 1389×615|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/dev-primary-zone10-floor1-col2-random-pre-change/summary/result.json)|
|30|dev-primary-zone10-floor1-col2-random-post-change|1217×625 → 1725×1256|通過|失敗／1|原生預覽外框；見 F30|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/dev-primary-zone10-floor1-col2-random-post-change/summary/result.json)|
|31|dev-L0-zone6-floor1-col2-select-1773-random-fixed|966×740|通過|失敗／2|小比例／幾何一致性；見 F31|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/dev-L0-zone6-floor1-col2-select-1773-random-fixed/summary/result.json)|
|32|dev-L0-zone6-floor1-col2-select-1773-random-pre-change|1152×597 → 2015×850|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/dev-L0-zone6-floor1-col2-select-1773-random-pre-change/summary/result.json)|
|33|dev-L0-zone6-floor1-col2-select-1773-random-post-change|1486×1014 → 1218×564|通過|失敗／1|OCR 分行；見 F33|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/dev-L0-zone6-floor1-col2-select-1773-random-post-change/summary/result.json)|
|34|dev-L0-zone6-floor1-col2-resume-1781-random-fixed|1781×915|通過|失敗／1|目前位置外環；見 F34|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/dev-L0-zone6-floor1-col2-resume-1781-random-fixed/summary/result.json)|
|35|dev-L0-zone6-floor1-col2-resume-1781-random-pre-change|1168×594 → 1938×1263|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/dev-L0-zone6-floor1-col2-resume-1781-random-pre-change/summary/result.json)|
|36|dev-L0-zone6-floor1-col2-resume-1781-random-post-change|1457×1035 → 1227×571|通過|失敗／3|候選／OCR／預覽時序；見 F36|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/dev-L0-zone6-floor1-col2-resume-1781-random-post-change/summary/result.json)|
|37|dev-L0-zone6-floor3-col3-select-1932-random-fixed|1256×645|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/dev-L0-zone6-floor3-col3-select-1932-random-fixed/summary/result.json)|
|38|dev-L0-zone6-floor3-col3-select-1932-random-pre-change|2137×1241 → 2552×1391|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/dev-L0-zone6-floor3-col3-select-1932-random-pre-change/summary/result.json)|
|39|dev-L0-zone6-floor3-col3-select-1932-random-post-change|1786×1227 → 2053×1191|通過|失敗／1|點後預覽證據；見 F39|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/dev-L0-zone6-floor3-col3-select-1932-random-post-change/summary/result.json)|
|40|dev-earlier-L0-zone5-floor1-col1-random-fixed|1885×793|通過|失敗；run01–04失敗，run05通過|高分定位框重疊、重讀重複、同季拼法衝突、普通字跨比例裁切；已修補並完整通過|[結果](../../artifacts/m1-20261027-01/prefix40-current-01/replay/dev-earlier-L0-zone5-floor1-col1-random-fixed/summary/result.json)|
|41|dev-earlier-L0-zone5-floor1-col1-random-pre-change|2481×1135 → 1751×963|通過|失敗|M1候選補強後完整通過；歷史第41曾ANCHOR_MISSING|[結果](../../artifacts/m1-20261027-01/case41-fresh-01/replay/dev-earlier-L0-zone5-floor1-col1-random-pre-change/summary/result.json)|
|42|dev-earlier-L0-zone5-floor1-col1-random-post-change|1466×1087 → 1729×1350|失敗|失敗／1筆凍結版本紀錄|候選生成漏指定節點，MAP_AMBIGUOUS，0點擊；詳見下文|[結果](../../artifacts/m1-20261027-01/case42-fresh-01/replay/dev-earlier-L0-zone5-floor1-col1-random-post-change/summary/result.json)|
|43|dev-earlier-L0-zone8-floor1-col4-random-fixed|2249×1408|未測試|無法確認／未測試|保持原順序，未開始|—|
|44|dev-earlier-L0-zone8-floor1-col4-random-pre-change|1706×785 → 1009×632|未測試|無法確認／未測試|保持原順序，未開始|—|
|45|dev-earlier-L0-zone8-floor1-col4-random-post-change|1958×1107 → 1813×945|未測試|無法確認／未測試|保持原順序，未開始|—|
|46|dev-earlier-0Q-zone4-floor1-col4-random-fixed|1697×1075|未測試|無法確認／未測試|保持原順序，未開始|—|
|47|dev-earlier-0Q-zone4-floor1-col4-random-pre-change|1886×1065 → 1753×1326|未測試|無法確認／未測試|保持原順序，未開始|—|
|48|dev-earlier-0Q-zone4-floor1-col4-random-post-change|1209×730 → 1315×560|未測試|無法確認／未測試|保持原順序，未開始|—|
|49|dev-LX46-zone1-floor1-col1-resume-random-fixed|1590×1079|未測試|無法確認／未測試|保持原順序，未開始|—|
|50|dev-LX46-zone1-floor1-col1-resume-random-pre-change|1796×1384 → 1801×1057|未測試|無法確認／未測試|保持原順序，未開始|—|
|51|dev-LX46-zone1-floor1-col1-resume-random-post-change|1709×1097 → 1448×693|未測試|無法確認／未測試|保持原順序，未開始|—|
|52|dev-LX46-zone2-floor1-col2-select-random-fixed|1710×1229|未測試|無法確認／未測試|保持原順序，未開始|—|
|53|dev-LX46-zone2-floor1-col2-select-random-pre-change|1290×1005 → 1466×713|未測試|無法確認／未測試|保持原順序，未開始|—|
|54|dev-LX46-zone2-floor1-col2-select-random-post-change|1475×640 → 1962×1238|未測試|無法確認／未測試|保持原順序，未開始|—|
|55|dev-LX46-zone3-floor1-col4-select-random-fixed|1446×854|未測試|無法確認／未測試|保持原順序，未開始|—|
|56|dev-LX46-zone3-floor1-col4-select-random-pre-change|2167×1141 → 1268×662|未測試|無法確認／未測試|保持原順序，未開始|—|
|57|dev-LX46-zone3-floor1-col4-select-random-post-change|1462×690 → 1449×1151|未測試|無法確認／未測試|保持原順序，未開始|—|
|58|dev-LX46-zone4-floor2-col1-select-random-fixed|2306×1417|未測試|無法確認／未測試|保持原順序，未開始|—|
|59|dev-LX46-zone4-floor2-col1-select-random-pre-change|1067×752 → 2399×1182|未測試|無法確認／未測試|保持原順序，未開始|—|
|60|dev-LX46-zone4-floor2-col1-select-random-post-change|1329×732 → 1437×853|未測試|無法確認／未測試|保持原順序，未開始|—|

## 未完成與下一步邊界

- 43～60未執行；30保留變換未開始；S3／S4隨機變換尚未完整驗證。原生S3/S4通過不能外推跨來源隨機尺寸泛化。
- S3 46047戰鬥、46057治療與S2 35929局部漏候選仍OPEN。35929在第41變換下最終12節點仍漏右側第二排戰鬥；與第42同編號的不同變換不能混用。
- 第42目標候選缺漏OPEN，需要另案評估總候選≥4時的覆蓋補強，先保持M1與安全規則不變。
- 正式保留集、正式負例、G4效能／即時畫面年齡及P5未完成。不得以單元、離線閉環或中間里程碑代替正式G4或實機驗收。
- 現階段不全面重寫、不導入YOLO、不修改凍結資料，不宣稱M1解決所有重採樣缺陷。
