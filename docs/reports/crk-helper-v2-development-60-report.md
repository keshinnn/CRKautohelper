# CRK Helper V2：60組離線閉環測試報告

**停止點：第41組待High評估。**依使用者的辨識演算法改動界線，已停止修改及第42組之後；詳見[第41組交接](../validation/2026-10-27-case41-high-handoff.md)。

更新時間：2026-10-27T13:08:20.131750+00:00。功能／測試綁定commit `2aeae973d32fb23541347e026b9f700a30c77e5c`，180個專案檔案hash與141個外部依賴逐次執行保存。

**當版：40/60通過、1失敗、19尚未完成當版驗證。** 這是進行中／部分結果，不能宣稱60組完成。

本輪只有離線影片分析、因果回放與虛擬點擊；原生遊戲操作0、P5未授權。G4效能仍未解決：前輪隔離CPU因果p95=2743.67ms>1500ms，本輪沒有重新量測，不把回放PTS或重用資料當效能成績。

## 版本與資料完整性

原凍結60開發變換／30保留變換，來自20／10段互動、四個來源；不是60段獨立影片。未重新選取容易資料。凍結manifest SHA256=`189b37115b1d08b0c245306bb727b13759d00aa0efb76a30e74b85acc6038e60`。各run/report.json綁定commit、owned/external hash、runtime指紋、執行器及資料manifest SHA；每個新影格均使用fresh pipeline，沒有raw V1封包快取。相同來源影格內的中間結果重用不是跨來源快取。

前39的舊c955結果保存在原歷史文件，不代替本輪修補版本回歸。本輪前40完整重算通過。

## 通過率與首次結果

- 當版全部分母通過率：40/60=66.67%。
- 已有首筆可追溯結果：15/41=36.59%；歷史不是可證明的第一次執行，不能當絕對首次成功率。
- 第40組五輪完整265張分析：run01／02／04為EVIDENCE_UNVERIFIED，run03為PREVIEW_TIMEOUT，run05通過。失敗前完整證據未刪除；每輪僅1次虛擬點擊。修正次數不由失敗版本數推算，未記錄者標示無法確認。

## 修補與回歸

三個runtime模組：bounded_ocr的原像素行重定位／同呼叫新鮮季別保留／合法語意鍵與矛盾拒絕；Python普通字裁切使用來源綁定rectified比例；Node獨立驗證certificate、矩陣、實際raster與裁切公式。沒有更換模型、影格ID分支、降低.90/.95或IoU、修改TTL／deadline／單次點擊／兩獨立預覽規則。舊無版本無certificate資料僅使用原scale1裁切，不信任其aspect；正式V2缺證明仍拒絕。

當版單元測試：Node127/127通過；Python208項＝206通過＋2項已知S3 expectedFailure，後兩項不算通過。新測試先RED後GREEN，舊測試斷言未修改。

|回歸集合|當版結果|證據|
|---|---|---|
|prefix40-current-01|40/40通過|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|native20-current-01|20/20通過|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/native20-current-01/report.json)|
|fixed15-current-01|15/15通過|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/fixed15-current-01/report.json)|
|negative30-current-01|30/30通過|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/negative30-current-01/report.json)|

單元測試通過、離線閉環通過與實機驗收互不替代。負例是否正式驗收，以正式gate欄位為準；30開發負例及兩個評分器對照不自動升格正式G4。1551原生影格與7張候選差異的hash／候選覆蓋稽核，亦不等於每張候選皆有像素語意真值。

## 60組逐項結果

|編號|凍結案例|實際客戶區尺寸|當版結果|首筆可追溯結果|失敗／修補紀錄|當版證據|
|---|---|---|---|---|---|---|
|01|zone-1-first-battle-random-fixed|2290×1293|通過|失敗／3|地圖／預覽；見 F01|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|02|zone-1-first-battle-random-pre-change|1643×723 → 1557×948|通過|失敗／1|證據適配；見 F02|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|03|zone-1-first-battle-random-post-change|2345×1064 → 1651×969|通過|失敗／2|穩定性／預覽；見 F03|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|04|zone-2-first-battle-random-fixed|1471×777|通過|失敗／3|點前穩定性；見 F04|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|05|zone-2-first-battle-random-pre-change|2094×948 → 1568×1008|通過|失敗／2|點前重取／G2；見 F05|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|06|zone-2-first-battle-random-post-change|1196×631 → 2065×1233|通過|通過／0|未見該組失敗紀錄|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|07|zone-3-first-battle-random-fixed|2481×1347|通過|通過／0|未見該組失敗紀錄|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|08|zone-3-first-battle-random-pre-change|2345×1420 → 2041×920|通過|失敗／2|預覽 OCR／精度回歸；見 F08|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|09|zone-3-first-battle-random-post-change|2071×1132 → 1058×577|通過|通過／0|未見該組失敗紀錄|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|10|zone-8-first-battle-random-fixed|2009×1010|通過|失敗／2|候選／預覽；見 F10|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|11|zone-8-first-battle-random-pre-change|1103×553 → 2225×1336|通過|通過／0|未見該組失敗紀錄|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|12|zone-8-first-battle-random-post-change|1677×1051 → 2252×1434|通過|通過／0|未見該組失敗紀錄|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|13|zone-9-first-battle-random-fixed|996×541|通過|失敗／1|G2 外框品質；見 F13|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|14|zone-9-first-battle-random-pre-change|1469×792 → 1366×1074|通過|失敗／3|OCR／近原生比例；見 F14|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|15|zone-9-first-battle-random-post-change|1805×1401 → 1315×546|通過|失敗／1|比例共識／錨點；見 F15|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|16|dev-primary-zone2-floor2-col3-higher-random-fixed|1342×552|通過|失敗／1|比例／前置完成位置；見 F16|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|17|dev-primary-zone2-floor2-col3-higher-random-pre-change|2467×1302 → 2543×1050|通過|失敗／1|入口／列距；見 F17|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|18|dev-primary-zone2-floor2-col3-higher-random-post-change|1997×1146 → 2196×1287|通過|失敗／2|連線／peer 身份；見 F18|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|19|dev-primary-zone3-floor3-col1-higher-random-fixed|1873×1370|通過|通過／1|後續回歸的座標 schema；見 F19|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|20|dev-primary-zone3-floor3-col1-higher-random-pre-change|1255×689 → 1941×1265|通過|失敗／1|完成狀態／目前位置；見 F20|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|21|dev-primary-zone3-floor3-col1-higher-random-post-change|1734×1187 → 1772×817|通過|失敗／3|配準來源／預覽地圖；見 F21|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|22|dev-primary-zone4-floor2-col3-random-fixed|2383×1372|通過|失敗／1|跨層幾何證據適配；見 F22|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|23|dev-primary-zone4-floor2-col3-random-pre-change|1101×668 → 1734×1018|通過|通過／0|未見該組失敗紀錄|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|24|dev-primary-zone4-floor2-col3-random-post-change|2275×1203 → 1448×1072|通過|失敗／1|原生預覽外框；見 F24|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|25|dev-primary-zone6-floor1-col2-random-fixed|1145×721|通過|失敗／1|投影取整；見 F25|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|26|dev-primary-zone6-floor1-col2-random-pre-change|2105×871 → 1056×635|通過|通過／0|未見該組失敗紀錄|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|27|dev-primary-zone6-floor1-col2-random-post-change|2275×1186 → 1349×580|通過|通過／0|未見該組失敗紀錄|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|28|dev-primary-zone10-floor1-col2-random-fixed|1203×864|通過|通過／0|未見該組失敗紀錄|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|29|dev-primary-zone10-floor1-col2-random-pre-change|1187×703 → 1389×615|通過|通過／0|未見該組失敗紀錄|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|30|dev-primary-zone10-floor1-col2-random-post-change|1217×625 → 1725×1256|通過|失敗／1|原生預覽外框；見 F30|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|31|dev-L0-zone6-floor1-col2-select-1773-random-fixed|966×740|通過|失敗／2|小比例／幾何一致性；見 F31|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|32|dev-L0-zone6-floor1-col2-select-1773-random-pre-change|1152×597 → 2015×850|通過|通過／0|未見該組失敗紀錄|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|33|dev-L0-zone6-floor1-col2-select-1773-random-post-change|1486×1014 → 1218×564|通過|失敗／1|OCR 分行；見 F33|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|34|dev-L0-zone6-floor1-col2-resume-1781-random-fixed|1781×915|通過|失敗／1|目前位置外環；見 F34|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|35|dev-L0-zone6-floor1-col2-resume-1781-random-pre-change|1168×594 → 1938×1263|通過|通過／0|未見該組失敗紀錄|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|36|dev-L0-zone6-floor1-col2-resume-1781-random-post-change|1457×1035 → 1227×571|通過|失敗／3|候選／OCR／預覽時序；見 F36|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|37|dev-L0-zone6-floor3-col3-select-1932-random-fixed|1256×645|通過|通過／0|未見該組失敗紀錄|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|38|dev-L0-zone6-floor3-col3-select-1932-random-pre-change|2137×1241 → 2552×1391|通過|通過／0|未見該組失敗紀錄|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|39|dev-L0-zone6-floor3-col3-select-1932-random-post-change|1786×1227 → 2053×1191|通過|失敗／1|點後預覽證據；見 F39|[證據](../../artifacts/development-20261027-medium-01/high-resume-01/prefix40-current-01/report.json)|
|40|dev-earlier-L0-zone5-floor1-col1-random-fixed|1885×793|通過|失敗；run01–04失敗，run05通過|高分定位框重疊、重讀重複、同季拼法衝突、普通字跨比例裁切；已修補並完整通過|[證據](../../artifacts/development-20261027-medium-01/case-40/run-05/report.json)|
|41|dev-earlier-L0-zone5-floor1-col1-random-pre-change|2481×1135 → 1751×963|失敗：REPLAY_FAILED_SEE_REPLAY_LOG|失敗|ANCHOR_MISSING|[證據](../../artifacts/development-20261027-medium-01/case-41/run-01/report.json)|
|42|dev-earlier-L0-zone5-floor1-col1-random-post-change|1466×1087 → 1729×1350|未完成當版驗證|無法確認／尚未測試|無新失敗紀錄|未建立|
|43|dev-earlier-L0-zone8-floor1-col4-random-fixed|2249×1408|未完成當版驗證|無法確認／尚未測試|無新失敗紀錄|未建立|
|44|dev-earlier-L0-zone8-floor1-col4-random-pre-change|1706×785 → 1009×632|未完成當版驗證|無法確認／尚未測試|無新失敗紀錄|未建立|
|45|dev-earlier-L0-zone8-floor1-col4-random-post-change|1958×1107 → 1813×945|未完成當版驗證|無法確認／尚未測試|無新失敗紀錄|未建立|
|46|dev-earlier-0Q-zone4-floor1-col4-random-fixed|1697×1075|未完成當版驗證|無法確認／尚未測試|無新失敗紀錄|未建立|
|47|dev-earlier-0Q-zone4-floor1-col4-random-pre-change|1886×1065 → 1753×1326|未完成當版驗證|無法確認／尚未測試|無新失敗紀錄|未建立|
|48|dev-earlier-0Q-zone4-floor1-col4-random-post-change|1209×730 → 1315×560|未完成當版驗證|無法確認／尚未測試|無新失敗紀錄|未建立|
|49|dev-LX46-zone1-floor1-col1-resume-random-fixed|1590×1079|未完成當版驗證|無法確認／尚未測試|無新失敗紀錄|未建立|
|50|dev-LX46-zone1-floor1-col1-resume-random-pre-change|1796×1384 → 1801×1057|未完成當版驗證|無法確認／尚未測試|無新失敗紀錄|未建立|
|51|dev-LX46-zone1-floor1-col1-resume-random-post-change|1709×1097 → 1448×693|未完成當版驗證|無法確認／尚未測試|無新失敗紀錄|未建立|
|52|dev-LX46-zone2-floor1-col2-select-random-fixed|1710×1229|未完成當版驗證|無法確認／尚未測試|無新失敗紀錄|未建立|
|53|dev-LX46-zone2-floor1-col2-select-random-pre-change|1290×1005 → 1466×713|未完成當版驗證|無法確認／尚未測試|無新失敗紀錄|未建立|
|54|dev-LX46-zone2-floor1-col2-select-random-post-change|1475×640 → 1962×1238|未完成當版驗證|無法確認／尚未測試|無新失敗紀錄|未建立|
|55|dev-LX46-zone3-floor1-col4-select-random-fixed|1446×854|未完成當版驗證|無法確認／尚未測試|無新失敗紀錄|未建立|
|56|dev-LX46-zone3-floor1-col4-select-random-pre-change|2167×1141 → 1268×662|未完成當版驗證|無法確認／尚未測試|無新失敗紀錄|未建立|
|57|dev-LX46-zone3-floor1-col4-select-random-post-change|1462×690 → 1449×1151|未完成當版驗證|無法確認／尚未測試|無新失敗紀錄|未建立|
|58|dev-LX46-zone4-floor2-col1-select-random-fixed|2306×1417|未完成當版驗證|無法確認／尚未測試|無新失敗紀錄|未建立|
|59|dev-LX46-zone4-floor2-col1-select-random-pre-change|1067×752 → 2399×1182|未完成當版驗證|無法確認／尚未測試|無新失敗紀錄|未建立|
|60|dev-LX46-zone4-floor2-col1-select-random-post-change|1329×732 → 1437×853|未完成當版驗證|無法確認／尚未測試|無新失敗紀錄|未建立|

## 尚未解決及下一步

- S3原影格46047仍漏戰鬥節點、46057仍漏治療節點；兩項expectedFailure持續追蹤，不因整段閉環通過而關閉。
- G4 p95門檻尚未達成；本輪不是效能重新驗收。
- 普通裁切新模組審查0Critical／0Important、1Minor：專門Node低分legacy scale1無比例證明／fractional ties-even正例夾具尚未新增，保留為deferred minor。
- 保留集30僅在60開發全部通過後啟動。開發用grader不冒稱正式blind gate；正式負例、跨來源泛化與G4仍需獨立證明。
- P5實機尚未授權，不執行遊戲操作。

更多證據：[第40組250束證據hash稽核](../../artifacts/development-20261027-medium-01/high-resume-01/case40-run05-integrity.json)、[四次失敗597束證據hash稽核](../../artifacts/development-20261027-medium-01/high-resume-01/failed-attempts-audit.json)、[兩張預覽像素檢視](../../artifacts/development-20261027-medium-01/high-resume-01/case40-pixel-review.json)。

本報告產生器SHA256：`5119044aa5fbd029afa502a1a8b7bf9f4e9b8845010404ed7cda0f8e89442dd3`。

## 第41組停止與High接續

第41組全部266張新鮮辨識後，在第三張送出前觀察以ANCHOR_MISSING拒絕，0虛擬點擊。35929與35935的比例量測均成功，但rectified/model raster由1285×963／960×719變為1282×963／960×721；快速與原始V1偵測器均由8候選降為2，框與排序一致。現有恢復前提不足，不是快速版獨有退步，也不是在座標投影驗證階段拒絕；候選在投影前已不足。需要評估候選生成／重採樣穩定性方案，依使用者重大問題／辨識演算法改動須停下轉High的要求，停止修改及第42組以後。未斷言必須全面重寫，也尚未定位到某個單一Canny像素或kernel。

詳細接續與證據：[第41組High交接](../validation/2026-10-27-case41-high-handoff.md)。七張原圖檢視與當版S3拒絕證明另存high-resume-01/seven-current-pixel-review.json、current-s3-refusal.json。負例當版30/30＋兩對照均通過，57張實際新鮮／57束證據SHA核對完成；三組在第一張UNKNOWN安全停止。第42～60、保留30及正式G4未完成，P5未授權。
