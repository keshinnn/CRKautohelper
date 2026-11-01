# CRK Helper V2：60 組開發閉環測試進度

**當版 42 通過、0 失敗、18 未完成／60。** 本頁由完成的當版回歸報告產生；執行中的案例不算通過。

來源提交 `24bfb2a5eb6ef4143c4574d02d2d93493e2e7f61`，188 個專案檔。凍結 60 開發／30 保留變換不變；60 組是 20 個原始互動的三種變換，並非 60 張獨立地圖或影片。全為離線回放與虛擬點擊，P5 未授權，G4 未完成。

## 當版證據與歷史區分

- 完成案例通過率：42/42；全 60 分母：70.00%。尚未完成不得當作失敗或通過。
- Node 127／Python 236 已通過；詳見當版 unit-validation.json 的 commit、檔案、依賴、runtime 與日誌 hash。單元通過不能替代閉環或實機驗收。
- 第 31／41／42 聚焦完整 560 張新鮮分析通過；本頁案例數另取完整前 42 與逐組正式開發回放，不重複計數。
- 舊版本 5e2 的第 31 組 IoU 0.8889 失敗與 41 通過／1 失敗完整保留於歷史快照。階段分離後是否恢復，依下表當版結果判定。
- 歷史首筆可追溯前 42 組為 15/42 成功；不是絕對首次執行率。表內歷史失敗紀錄數不是修正次數，平均修正次數無法確認。新組的當版首輪結果與歷史紀錄分開。
- 原生 20、固定倍率 15、負例 30、1551／七張候選稽核、取整壓力與隔離效能仍須各自核對完成報告；本頁不因控制器已排程就宣稱它們完成。

## 60 組明細

|編號|凍結案例／區域・樓層・欄位|客戶區尺寸|當版結果|歷史首筆／失敗紀錄數|歷史原因（不是當版失敗）|當版證據|
|---|---|---|---|---|---|---|
|01|zone-1-first-battle-random-fixed<br>1・1・2|2290×1293|通過|失敗／3|地圖／預覽；見 F01|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/zone-1-first-battle-random-fixed/summary/result.json)|
|02|zone-1-first-battle-random-pre-change<br>1・1・2|1643×723 → 1557×948|通過|失敗／1|證據適配；見 F02|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/zone-1-first-battle-random-pre-change/summary/result.json)|
|03|zone-1-first-battle-random-post-change<br>1・1・2|2345×1064 → 1651×969|通過|失敗／2|穩定性／預覽；見 F03|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/zone-1-first-battle-random-post-change/summary/result.json)|
|04|zone-2-first-battle-random-fixed<br>2・1・2|1471×777|通過|失敗／3|點前穩定性；見 F04|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/zone-2-first-battle-random-fixed/summary/result.json)|
|05|zone-2-first-battle-random-pre-change<br>2・1・2|2094×948 → 1568×1008|通過|失敗／2|點前重取／G2；見 F05|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/zone-2-first-battle-random-pre-change/summary/result.json)|
|06|zone-2-first-battle-random-post-change<br>2・1・2|1196×631 → 2065×1233|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/zone-2-first-battle-random-post-change/summary/result.json)|
|07|zone-3-first-battle-random-fixed<br>3・1・2|2481×1347|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/zone-3-first-battle-random-fixed/summary/result.json)|
|08|zone-3-first-battle-random-pre-change<br>3・1・2|2345×1420 → 2041×920|通過|失敗／2|預覽 OCR／精度回歸；見 F08|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/zone-3-first-battle-random-pre-change/summary/result.json)|
|09|zone-3-first-battle-random-post-change<br>3・1・2|2071×1132 → 1058×577|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/zone-3-first-battle-random-post-change/summary/result.json)|
|10|zone-8-first-battle-random-fixed<br>8・1・4|2009×1010|通過|失敗／2|候選／預覽；見 F10|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/zone-8-first-battle-random-fixed/summary/result.json)|
|11|zone-8-first-battle-random-pre-change<br>8・1・4|1103×553 → 2225×1336|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/zone-8-first-battle-random-pre-change/summary/result.json)|
|12|zone-8-first-battle-random-post-change<br>8・1・4|1677×1051 → 2252×1434|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/zone-8-first-battle-random-post-change/summary/result.json)|
|13|zone-9-first-battle-random-fixed<br>9・1・4|996×541|通過|失敗／1|G2 外框品質；見 F13|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/zone-9-first-battle-random-fixed/summary/result.json)|
|14|zone-9-first-battle-random-pre-change<br>9・1・4|1469×792 → 1366×1074|通過|失敗／3|OCR／近原生比例；見 F14|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/zone-9-first-battle-random-pre-change/summary/result.json)|
|15|zone-9-first-battle-random-post-change<br>9・1・4|1805×1401 → 1315×546|通過|失敗／1|比例共識／錨點；見 F15|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/zone-9-first-battle-random-post-change/summary/result.json)|
|16|dev-primary-zone2-floor2-col3-higher-random-fixed<br>2・2・3|1342×552|通過|失敗／1|比例／前置完成位置；見 F16|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/dev-primary-zone2-floor2-col3-higher-random-fixed/summary/result.json)|
|17|dev-primary-zone2-floor2-col3-higher-random-pre-change<br>2・2・3|2467×1302 → 2543×1050|通過|失敗／1|入口／列距；見 F17|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/dev-primary-zone2-floor2-col3-higher-random-pre-change/summary/result.json)|
|18|dev-primary-zone2-floor2-col3-higher-random-post-change<br>2・2・3|1997×1146 → 2196×1287|通過|失敗／2|連線／peer 身份；見 F18|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/dev-primary-zone2-floor2-col3-higher-random-post-change/summary/result.json)|
|19|dev-primary-zone3-floor3-col1-higher-random-fixed<br>3・3・1|1873×1370|通過|通過／1|後續回歸的座標 schema；見 F19|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/dev-primary-zone3-floor3-col1-higher-random-fixed/summary/result.json)|
|20|dev-primary-zone3-floor3-col1-higher-random-pre-change<br>3・3・1|1255×689 → 1941×1265|通過|失敗／1|完成狀態／目前位置；見 F20|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/dev-primary-zone3-floor3-col1-higher-random-pre-change/summary/result.json)|
|21|dev-primary-zone3-floor3-col1-higher-random-post-change<br>3・3・1|1734×1187 → 1772×817|通過|失敗／3|配準來源／預覽地圖；見 F21|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/dev-primary-zone3-floor3-col1-higher-random-post-change/summary/result.json)|
|22|dev-primary-zone4-floor2-col3-random-fixed<br>4・2・3|2383×1372|通過|失敗／1|跨層幾何證據適配；見 F22|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/dev-primary-zone4-floor2-col3-random-fixed/summary/result.json)|
|23|dev-primary-zone4-floor2-col3-random-pre-change<br>4・2・3|1101×668 → 1734×1018|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/dev-primary-zone4-floor2-col3-random-pre-change/summary/result.json)|
|24|dev-primary-zone4-floor2-col3-random-post-change<br>4・2・3|2275×1203 → 1448×1072|通過|失敗／1|原生預覽外框；見 F24|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/dev-primary-zone4-floor2-col3-random-post-change/summary/result.json)|
|25|dev-primary-zone6-floor1-col2-random-fixed<br>6・1・2|1145×721|通過|失敗／1|投影取整；見 F25|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/dev-primary-zone6-floor1-col2-random-fixed/summary/result.json)|
|26|dev-primary-zone6-floor1-col2-random-pre-change<br>6・1・2|2105×871 → 1056×635|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/dev-primary-zone6-floor1-col2-random-pre-change/summary/result.json)|
|27|dev-primary-zone6-floor1-col2-random-post-change<br>6・1・2|2275×1186 → 1349×580|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/dev-primary-zone6-floor1-col2-random-post-change/summary/result.json)|
|28|dev-primary-zone10-floor1-col2-random-fixed<br>10・1・2|1203×864|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/dev-primary-zone10-floor1-col2-random-fixed/summary/result.json)|
|29|dev-primary-zone10-floor1-col2-random-pre-change<br>10・1・2|1187×703 → 1389×615|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/dev-primary-zone10-floor1-col2-random-pre-change/summary/result.json)|
|30|dev-primary-zone10-floor1-col2-random-post-change<br>10・1・2|1217×625 → 1725×1256|通過|失敗／1|原生預覽外框；見 F30|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/dev-primary-zone10-floor1-col2-random-post-change/summary/result.json)|
|31|dev-L0-zone6-floor1-col2-select-1773-random-fixed<br>6・1・2|966×740|通過|失敗／2|當版G2外框IoU0.8889；全域候選改變比例恢復路由。歷史：小比例／幾何一致性；見 F31|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/dev-L0-zone6-floor1-col2-select-1773-random-fixed/summary/result.json)|
|32|dev-L0-zone6-floor1-col2-select-1773-random-pre-change<br>6・1・2|1152×597 → 2015×850|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/dev-L0-zone6-floor1-col2-select-1773-random-pre-change/summary/result.json)|
|33|dev-L0-zone6-floor1-col2-select-1773-random-post-change<br>6・1・2|1486×1014 → 1218×564|通過|失敗／1|OCR 分行；見 F33|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/dev-L0-zone6-floor1-col2-select-1773-random-post-change/summary/result.json)|
|34|dev-L0-zone6-floor1-col2-resume-1781-random-fixed<br>6・1・2|1781×915|通過|失敗／1|目前位置外環；見 F34|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/dev-L0-zone6-floor1-col2-resume-1781-random-fixed/summary/result.json)|
|35|dev-L0-zone6-floor1-col2-resume-1781-random-pre-change<br>6・1・2|1168×594 → 1938×1263|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/dev-L0-zone6-floor1-col2-resume-1781-random-pre-change/summary/result.json)|
|36|dev-L0-zone6-floor1-col2-resume-1781-random-post-change<br>6・1・2|1457×1035 → 1227×571|通過|失敗／3|候選／OCR／預覽時序；見 F36|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/dev-L0-zone6-floor1-col2-resume-1781-random-post-change/summary/result.json)|
|37|dev-L0-zone6-floor3-col3-select-1932-random-fixed<br>6・3・3|1256×645|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/dev-L0-zone6-floor3-col3-select-1932-random-fixed/summary/result.json)|
|38|dev-L0-zone6-floor3-col3-select-1932-random-pre-change<br>6・3・3|2137×1241 → 2552×1391|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/dev-L0-zone6-floor3-col3-select-1932-random-pre-change/summary/result.json)|
|39|dev-L0-zone6-floor3-col3-select-1932-random-post-change<br>6・3・3|1786×1227 → 2053×1191|通過|失敗／1|點後預覽證據；見 F39|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/dev-L0-zone6-floor3-col3-select-1932-random-post-change/summary/result.json)|
|40|dev-earlier-L0-zone5-floor1-col1-random-fixed<br>5・1・1|1885×793|通過|失敗；run01–04失敗，run05通過|高分定位框重疊、重讀重複、同季拼法衝突、普通字跨比例裁切；已修補並完整通過|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/dev-earlier-L0-zone5-floor1-col1-random-fixed/summary/result.json)|
|41|dev-earlier-L0-zone5-floor1-col1-random-pre-change<br>5・1・1|2481×1135 → 1751×963|通過|失敗|當版完整266 fresh通過；歷史候選取整失敗由M1修復|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/dev-earlier-L0-zone5-floor1-col1-random-pre-change/summary/result.json)|
|42|dev-earlier-L0-zone5-floor1-col1-random-post-change<br>5・1・1|1466×1087 → 1729×1350|通過|失敗／1筆凍結版本紀錄|舊M1候選分數低於.48；當版coverage完整265 fresh通過，舊失敗保留|[結果](../../artifacts/phase-routing-20261028-01/prefix42-current-01/replay/dev-earlier-L0-zone5-floor1-col1-random-post-change/summary/result.json)|
|43|dev-earlier-L0-zone8-floor1-col4-random-fixed<br>8・1・4|2249×1408|未完成|無法確認／未測試|必要回歸失敗，未開始；保留原順序|尚無當版完成報告|
|44|dev-earlier-L0-zone8-floor1-col4-random-pre-change<br>8・1・4|1706×785 → 1009×632|未完成|無法確認／未測試|必要回歸失敗，未開始；保留原順序|尚無當版完成報告|
|45|dev-earlier-L0-zone8-floor1-col4-random-post-change<br>8・1・4|1958×1107 → 1813×945|未完成|無法確認／未測試|必要回歸失敗，未開始；保留原順序|尚無當版完成報告|
|46|dev-earlier-0Q-zone4-floor1-col4-random-fixed<br>4・1・4|1697×1075|未完成|無法確認／未測試|必要回歸失敗，未開始；保留原順序|尚無當版完成報告|
|47|dev-earlier-0Q-zone4-floor1-col4-random-pre-change<br>4・1・4|1886×1065 → 1753×1326|未完成|無法確認／未測試|必要回歸失敗，未開始；保留原順序|尚無當版完成報告|
|48|dev-earlier-0Q-zone4-floor1-col4-random-post-change<br>4・1・4|1209×730 → 1315×560|未完成|無法確認／未測試|必要回歸失敗，未開始；保留原順序|尚無當版完成報告|
|49|dev-LX46-zone1-floor1-col1-resume-random-fixed<br>1・1・1|1590×1079|未完成|無法確認／未測試|必要回歸失敗，未開始；保留原順序|尚無當版完成報告|
|50|dev-LX46-zone1-floor1-col1-resume-random-pre-change<br>1・1・1|1796×1384 → 1801×1057|未完成|無法確認／未測試|必要回歸失敗，未開始；保留原順序|尚無當版完成報告|
|51|dev-LX46-zone1-floor1-col1-resume-random-post-change<br>1・1・1|1709×1097 → 1448×693|未完成|無法確認／未測試|必要回歸失敗，未開始；保留原順序|尚無當版完成報告|
|52|dev-LX46-zone2-floor1-col2-select-random-fixed<br>2・1・2|1710×1229|未完成|無法確認／未測試|必要回歸失敗，未開始；保留原順序|尚無當版完成報告|
|53|dev-LX46-zone2-floor1-col2-select-random-pre-change<br>2・1・2|1290×1005 → 1466×713|未完成|無法確認／未測試|必要回歸失敗，未開始；保留原順序|尚無當版完成報告|
|54|dev-LX46-zone2-floor1-col2-select-random-post-change<br>2・1・2|1475×640 → 1962×1238|未完成|無法確認／未測試|必要回歸失敗，未開始；保留原順序|尚無當版完成報告|
|55|dev-LX46-zone3-floor1-col4-select-random-fixed<br>3・1・4|1446×854|未完成|無法確認／未測試|必要回歸失敗，未開始；保留原順序|尚無當版完成報告|
|56|dev-LX46-zone3-floor1-col4-select-random-pre-change<br>3・1・4|2167×1141 → 1268×662|未完成|無法確認／未測試|必要回歸失敗，未開始；保留原順序|尚無當版完成報告|
|57|dev-LX46-zone3-floor1-col4-select-random-post-change<br>3・1・4|1462×690 → 1449×1151|未完成|無法確認／未測試|必要回歸失敗，未開始；保留原順序|尚無當版完成報告|
|58|dev-LX46-zone4-floor2-col1-select-random-fixed<br>4・2・1|2306×1417|未完成|無法確認／未測試|必要回歸失敗，未開始；保留原順序|尚無當版完成報告|
|59|dev-LX46-zone4-floor2-col1-select-random-pre-change<br>4・2・1|1067×752 → 2399×1182|未完成|無法確認／未測試|必要回歸失敗，未開始；保留原順序|尚無當版完成報告|
|60|dev-LX46-zone4-floor2-col1-select-random-post-change<br>4・2・1|1329×732 → 1437×853|未完成|無法確認／未測試|必要回歸失敗，未開始；保留原順序|尚無當版完成報告|

## 未完成與已知限制

G4 效能目標仍為暖機 p95 ≤1500ms；舊 M1 2374ms 是歷史值，不能作為當版效能結果。保留集原生 10 與變換 30 尚須等開發 60 全過再執行。保留互動與開發互動沒有重複影格，但共用三個影片來源，不能宣稱是全新影片盲測。負例正式驗收亦不得由開發測試標籤直接改稱完成。

S3 46047／46057 與 S2 35929 的局部候選證據另行追蹤；閉環通過本身不證明整張地圖無漏候選。當版局部修復須綁定新鮮封包、原圖與獨立標註／像素稽核。

本輪階段分離與重新檢查同幀 currentPosition 沒有修改比例估計器、raster、Node Selector、Click Transaction、Preview Verifier 或安全門檻。原始失敗、審查發現與修正測試均保留。

[當版詳細狀態](../validation/2026-11-02-phase-observation-status.md) · [舊版本完整報告](../../artifacts/phase-routing-20261028-01/historical-before-phase-development60-report.md)
