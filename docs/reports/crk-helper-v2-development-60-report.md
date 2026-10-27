# CRK Helper V2：60組開發測試階段報告（coverage當版回歸未通過）

**當版41通過、1失敗、18未測／60。** 第42已修復，但原有第31組IoU退步至0.8889；必要回歸未穩定，43～60與保留集未啟動。本報告是完整60項狀態表，並非60組完成或正式G4報告。

來源版本 `5e2c740fcce2fb0f43127ccff5e87adc1f3d44b4`；183個專案檔、141外部依賴及runtime指紋綁定。凍結60開發／30保留變換、20／10原始互動、四個影片來源均未改。這不是60段獨立影片。來源manifest SHA256 `189b37115b1d08b0c245306bb727b13759d00aa0efb76a30e74b85acc6038e60`。本輪全為離線新鮮推論、因果回放及虛擬點擊，0原生操作，P5未授權。

## 已執行結果與首筆紀錄

- 前41組1849/1849 fresh，原整批回放在第31組失敗；前30通過。另對同批已新鮮分析的32～41逐一補查，10/10通過，不改寫原批次失敗。
- 第42完整265/265 fresh，249張因果觀察、一次虛擬點擊、PREVIEW_CONFIRMED，IoU0.9575602462、margin28.4973px。
- 合計2114 fresh、0 raw cache、已評42組41通過／1失敗；全60分母通過率68.33%，已評通過率97.62%。第31為G2外框失敗，身份及點擊內縮通過；無證據顯示選錯實體節點。
- 當版首輪已評42組41組通過，但這不是歷史首次成功率。歷史首筆可追溯仍15/42=35.71%，資料未必是絕對首次執行；修正次數平均無法確認。表內歷史「／數字」是失敗紀錄數，不能當修正次數。
- 第41在當版同批266張新鮮分析與獨立補查中通過；仍不能把整批前41標為通過。

## 本輪修改及新增風險

本輪在獨立coverage模式補掃標準尺度floor−1..ceil+1有界整數模板，保留完整M1輸出前綴、原base204尺寸項目及其合法重複、同張一次Canny、原.48／NMS／IoU／三peer與身份門檻。預設M1 API保持原樣。另經一次審查修復backend/hash未綁定的真實CLI快取問題；完整正式新鮮測試沒有使用raw cache。聚焦4項coverage、5項M1、3項cache及6項S3已通過。後續完整Node127/127通過；Python220項有218通過、2項歷史frame-context語義相等檢查失敗，原始log保留。

但全域matcher安裝同時改變初始V1地圖與後續幾何路由。第31原始觀察7節點／未錨定變成10節點／四欄已建立，略過既有近原生恢復及外框精修；兩張相同像素僅切matcher可重現。完整M1候選前綴保留並不足以保存最終幾何行為。原M1外框IoU0.9358738154退步至0.8889215162。詳見[第31根因與最小調整設計](../validation/2026-10-28-coverage-regression-case31.md)。失敗後未做生產程式修改、未放寬門檻。

建議明確分離基礎幾何路由證據與同幀補強候選，再在已選工作空間增量補漏。這涉及Observer／比例恢復呼叫整合，超出只改matcher銀行的範圍；使用者已批准此局部整合範圍，將依[新實作計畫](../superpowers/plans/2026-10-28-phase-observation.md)繼續；本表仍是修改前5e2版本實際結果。不能只把M2限制在rectified圖，因第42原失敗本來就是已錨定source路徑。

## 回歸、稽核與效能

|當版項目|實際狀態|證據（根目錄artifacts/coverage-20261028-01/）|
|---|---|---|
|前41完整新鮮分析|1849/1849，原批次第31失敗|prefix41-current-01/report.json|
|32～41補查|10/10，使用同批fresh封包，非整批PASS|prefix41-suffix-diagnostic/report.json|
|第42完整閉環|通過，265 fresh|case42-fresh-02/report.json|
|合併42組狀態|41通過／1失敗／其餘18未測|current42-aggregate.json|
|原批次來源及bundle完整性|1849來源、654束／3270檔hash通過；語義仍失敗|prefix41-failure-integrity.json|
|suffix補查bundle完整性|692束／3460檔hash通過|prefix41-suffix-integrity.json|
|第42完整性|265來源、250束／1250檔|case42-final-integrity.json|
|native20／fixed15／negative30＋controls|本版本尚未完成，控制器於前置回歸失敗即停|continuation.json|
|完整Node／Python|Node127/127；Python220項218通過／2失敗，未達全綠|node-full.log、python-full.log|
|1551／七張／新增候選像素稽核|本版本未完成|必要前置回歸失敗，未啟動|
|取整邊界壓力／配對matcher／193完整隔離效能|runner已準備，尚未執行|不得當通過或效能改善證據|

M1舊整體CPU p95=2374ms>1500ms是歷史比較基準；coverage本版本完整隔離p95尚未量測，不能宣稱更快或達標。正式G4效能、即時畫面年齡、正式保留集／負例與P5均未完成。離線PREVIEW_CONFIRMED、GT外框評分、單元測試與實機驗收分開。

## 60組當版狀態

歷史失敗說明中的F編號沿用[完整歷史快照](../../artifacts/m1-20261027-01/historical-pre-m1-development60-report.md)，不是本輪修正次數或當版通過證據。第42舊失敗與M1修復前分析另保存於本輪historical-before-coverage-development60-report.md。

|編號|凍結案例／區域・樓層・欄位|客戶區尺寸|當版|歷史首筆可追溯／失敗紀錄數|失敗階段／歷史原因|當版證據|
|---|---|---|---|---|---|---|
|01|zone-1-first-battle-random-fixed<br>1・1・2|2290×1293|通過|失敗／3|地圖／預覽；見 F01|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/zone-1-first-battle-random-fixed/summary/result.json)|
|02|zone-1-first-battle-random-pre-change<br>1・1・2|1643×723 → 1557×948|通過|失敗／1|證據適配；見 F02|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/zone-1-first-battle-random-pre-change/summary/result.json)|
|03|zone-1-first-battle-random-post-change<br>1・1・2|2345×1064 → 1651×969|通過|失敗／2|穩定性／預覽；見 F03|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/zone-1-first-battle-random-post-change/summary/result.json)|
|04|zone-2-first-battle-random-fixed<br>2・1・2|1471×777|通過|失敗／3|點前穩定性；見 F04|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/zone-2-first-battle-random-fixed/summary/result.json)|
|05|zone-2-first-battle-random-pre-change<br>2・1・2|2094×948 → 1568×1008|通過|失敗／2|點前重取／G2；見 F05|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/zone-2-first-battle-random-pre-change/summary/result.json)|
|06|zone-2-first-battle-random-post-change<br>2・1・2|1196×631 → 2065×1233|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/zone-2-first-battle-random-post-change/summary/result.json)|
|07|zone-3-first-battle-random-fixed<br>3・1・2|2481×1347|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/zone-3-first-battle-random-fixed/summary/result.json)|
|08|zone-3-first-battle-random-pre-change<br>3・1・2|2345×1420 → 2041×920|通過|失敗／2|預覽 OCR／精度回歸；見 F08|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/zone-3-first-battle-random-pre-change/summary/result.json)|
|09|zone-3-first-battle-random-post-change<br>3・1・2|2071×1132 → 1058×577|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/zone-3-first-battle-random-post-change/summary/result.json)|
|10|zone-8-first-battle-random-fixed<br>8・1・4|2009×1010|通過|失敗／2|候選／預覽；見 F10|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/zone-8-first-battle-random-fixed/summary/result.json)|
|11|zone-8-first-battle-random-pre-change<br>8・1・4|1103×553 → 2225×1336|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/zone-8-first-battle-random-pre-change/summary/result.json)|
|12|zone-8-first-battle-random-post-change<br>8・1・4|1677×1051 → 2252×1434|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/zone-8-first-battle-random-post-change/summary/result.json)|
|13|zone-9-first-battle-random-fixed<br>9・1・4|996×541|通過|失敗／1|G2 外框品質；見 F13|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/zone-9-first-battle-random-fixed/summary/result.json)|
|14|zone-9-first-battle-random-pre-change<br>9・1・4|1469×792 → 1366×1074|通過|失敗／3|OCR／近原生比例；見 F14|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/zone-9-first-battle-random-pre-change/summary/result.json)|
|15|zone-9-first-battle-random-post-change<br>9・1・4|1805×1401 → 1315×546|通過|失敗／1|比例共識／錨點；見 F15|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/zone-9-first-battle-random-post-change/summary/result.json)|
|16|dev-primary-zone2-floor2-col3-higher-random-fixed<br>2・2・3|1342×552|通過|失敗／1|比例／前置完成位置；見 F16|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/dev-primary-zone2-floor2-col3-higher-random-fixed/summary/result.json)|
|17|dev-primary-zone2-floor2-col3-higher-random-pre-change<br>2・2・3|2467×1302 → 2543×1050|通過|失敗／1|入口／列距；見 F17|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/dev-primary-zone2-floor2-col3-higher-random-pre-change/summary/result.json)|
|18|dev-primary-zone2-floor2-col3-higher-random-post-change<br>2・2・3|1997×1146 → 2196×1287|通過|失敗／2|連線／peer 身份；見 F18|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/dev-primary-zone2-floor2-col3-higher-random-post-change/summary/result.json)|
|19|dev-primary-zone3-floor3-col1-higher-random-fixed<br>3・3・1|1873×1370|通過|通過／1|後續回歸的座標 schema；見 F19|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/dev-primary-zone3-floor3-col1-higher-random-fixed/summary/result.json)|
|20|dev-primary-zone3-floor3-col1-higher-random-pre-change<br>3・3・1|1255×689 → 1941×1265|通過|失敗／1|完成狀態／目前位置；見 F20|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/dev-primary-zone3-floor3-col1-higher-random-pre-change/summary/result.json)|
|21|dev-primary-zone3-floor3-col1-higher-random-post-change<br>3・3・1|1734×1187 → 1772×817|通過|失敗／3|配準來源／預覽地圖；見 F21|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/dev-primary-zone3-floor3-col1-higher-random-post-change/summary/result.json)|
|22|dev-primary-zone4-floor2-col3-random-fixed<br>4・2・3|2383×1372|通過|失敗／1|跨層幾何證據適配；見 F22|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/dev-primary-zone4-floor2-col3-random-fixed/summary/result.json)|
|23|dev-primary-zone4-floor2-col3-random-pre-change<br>4・2・3|1101×668 → 1734×1018|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/dev-primary-zone4-floor2-col3-random-pre-change/summary/result.json)|
|24|dev-primary-zone4-floor2-col3-random-post-change<br>4・2・3|2275×1203 → 1448×1072|通過|失敗／1|原生預覽外框；見 F24|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/dev-primary-zone4-floor2-col3-random-post-change/summary/result.json)|
|25|dev-primary-zone6-floor1-col2-random-fixed<br>6・1・2|1145×721|通過|失敗／1|投影取整；見 F25|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/dev-primary-zone6-floor1-col2-random-fixed/summary/result.json)|
|26|dev-primary-zone6-floor1-col2-random-pre-change<br>6・1・2|2105×871 → 1056×635|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/dev-primary-zone6-floor1-col2-random-pre-change/summary/result.json)|
|27|dev-primary-zone6-floor1-col2-random-post-change<br>6・1・2|2275×1186 → 1349×580|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/dev-primary-zone6-floor1-col2-random-post-change/summary/result.json)|
|28|dev-primary-zone10-floor1-col2-random-fixed<br>10・1・2|1203×864|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/dev-primary-zone10-floor1-col2-random-fixed/summary/result.json)|
|29|dev-primary-zone10-floor1-col2-random-pre-change<br>10・1・2|1187×703 → 1389×615|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/dev-primary-zone10-floor1-col2-random-pre-change/summary/result.json)|
|30|dev-primary-zone10-floor1-col2-random-post-change<br>10・1・2|1217×625 → 1725×1256|通過|失敗／1|原生預覽外框；見 F30|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/dev-primary-zone10-floor1-col2-random-post-change/summary/result.json)|
|31|dev-L0-zone6-floor1-col2-select-1773-random-fixed<br>6・1・2|966×740|失敗|失敗／2|當版G2外框IoU0.8889；全域候選改變比例恢復路由。歷史：小比例／幾何一致性；見 F31|[結果](../../artifacts/coverage-20261028-01/prefix41-current-01/replay/dev-L0-zone6-floor1-col2-select-1773-random-fixed/summary/result.json)|
|32|dev-L0-zone6-floor1-col2-select-1773-random-pre-change<br>6・1・2|1152×597 → 2015×850|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/coverage-20261028-01/prefix41-suffix-diagnostic/case32/dev-L0-zone6-floor1-col2-select-1773-random-pre-change/summary/result.json)|
|33|dev-L0-zone6-floor1-col2-select-1773-random-post-change<br>6・1・2|1486×1014 → 1218×564|通過|失敗／1|OCR 分行；見 F33|[結果](../../artifacts/coverage-20261028-01/prefix41-suffix-diagnostic/case33/dev-L0-zone6-floor1-col2-select-1773-random-post-change/summary/result.json)|
|34|dev-L0-zone6-floor1-col2-resume-1781-random-fixed<br>6・1・2|1781×915|通過|失敗／1|目前位置外環；見 F34|[結果](../../artifacts/coverage-20261028-01/prefix41-suffix-diagnostic/case34/dev-L0-zone6-floor1-col2-resume-1781-random-fixed/summary/result.json)|
|35|dev-L0-zone6-floor1-col2-resume-1781-random-pre-change<br>6・1・2|1168×594 → 1938×1263|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/coverage-20261028-01/prefix41-suffix-diagnostic/case35/dev-L0-zone6-floor1-col2-resume-1781-random-pre-change/summary/result.json)|
|36|dev-L0-zone6-floor1-col2-resume-1781-random-post-change<br>6・1・2|1457×1035 → 1227×571|通過|失敗／3|候選／OCR／預覽時序；見 F36|[結果](../../artifacts/coverage-20261028-01/prefix41-suffix-diagnostic/case36/dev-L0-zone6-floor1-col2-resume-1781-random-post-change/summary/result.json)|
|37|dev-L0-zone6-floor3-col3-select-1932-random-fixed<br>6・3・3|1256×645|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/coverage-20261028-01/prefix41-suffix-diagnostic/case37/dev-L0-zone6-floor3-col3-select-1932-random-fixed/summary/result.json)|
|38|dev-L0-zone6-floor3-col3-select-1932-random-pre-change<br>6・3・3|2137×1241 → 2552×1391|通過|通過／0|未見該組失敗紀錄|[結果](../../artifacts/coverage-20261028-01/prefix41-suffix-diagnostic/case38/dev-L0-zone6-floor3-col3-select-1932-random-pre-change/summary/result.json)|
|39|dev-L0-zone6-floor3-col3-select-1932-random-post-change<br>6・3・3|1786×1227 → 2053×1191|通過|失敗／1|點後預覽證據；見 F39|[結果](../../artifacts/coverage-20261028-01/prefix41-suffix-diagnostic/case39/dev-L0-zone6-floor3-col3-select-1932-random-post-change/summary/result.json)|
|40|dev-earlier-L0-zone5-floor1-col1-random-fixed<br>5・1・1|1885×793|通過|失敗；run01–04失敗，run05通過|高分定位框重疊、重讀重複、同季拼法衝突、普通字跨比例裁切；已修補並完整通過|[結果](../../artifacts/coverage-20261028-01/prefix41-suffix-diagnostic/case40/dev-earlier-L0-zone5-floor1-col1-random-fixed/summary/result.json)|
|41|dev-earlier-L0-zone5-floor1-col1-random-pre-change<br>5・1・1|2481×1135 → 1751×963|通過|失敗|當版完整266 fresh通過；歷史候選取整失敗由M1修復|[結果](../../artifacts/coverage-20261028-01/prefix41-suffix-diagnostic/case41/dev-earlier-L0-zone5-floor1-col1-random-pre-change/summary/result.json)|
|42|dev-earlier-L0-zone5-floor1-col1-random-post-change<br>5・1・1|1466×1087 → 1729×1350|通過|失敗／1筆凍結版本紀錄|舊M1候選分數低於.48；當版coverage完整265 fresh通過，舊失敗保留|[結果](../../artifacts/coverage-20261028-01/case42-fresh-02/replay/dev-earlier-L0-zone5-floor1-col1-random-post-change/summary/result.json)|
|43|dev-earlier-L0-zone8-floor1-col4-random-fixed<br>8・1・4|2249×1408|未測試|無法確認／未測試|必要回歸失敗，未開始；保留原順序|—|
|44|dev-earlier-L0-zone8-floor1-col4-random-pre-change<br>8・1・4|1706×785 → 1009×632|未測試|無法確認／未測試|必要回歸失敗，未開始；保留原順序|—|
|45|dev-earlier-L0-zone8-floor1-col4-random-post-change<br>8・1・4|1958×1107 → 1813×945|未測試|無法確認／未測試|必要回歸失敗，未開始；保留原順序|—|
|46|dev-earlier-0Q-zone4-floor1-col4-random-fixed<br>4・1・4|1697×1075|未測試|無法確認／未測試|必要回歸失敗，未開始；保留原順序|—|
|47|dev-earlier-0Q-zone4-floor1-col4-random-pre-change<br>4・1・4|1886×1065 → 1753×1326|未測試|無法確認／未測試|必要回歸失敗，未開始；保留原順序|—|
|48|dev-earlier-0Q-zone4-floor1-col4-random-post-change<br>4・1・4|1209×730 → 1315×560|未測試|無法確認／未測試|必要回歸失敗，未開始；保留原順序|—|
|49|dev-LX46-zone1-floor1-col1-resume-random-fixed<br>1・1・1|1590×1079|未測試|無法確認／未測試|必要回歸失敗，未開始；保留原順序|—|
|50|dev-LX46-zone1-floor1-col1-resume-random-pre-change<br>1・1・1|1796×1384 → 1801×1057|未測試|無法確認／未測試|必要回歸失敗，未開始；保留原順序|—|
|51|dev-LX46-zone1-floor1-col1-resume-random-post-change<br>1・1・1|1709×1097 → 1448×693|未測試|無法確認／未測試|必要回歸失敗，未開始；保留原順序|—|
|52|dev-LX46-zone2-floor1-col2-select-random-fixed<br>2・1・2|1710×1229|未測試|無法確認／未測試|必要回歸失敗，未開始；保留原順序|—|
|53|dev-LX46-zone2-floor1-col2-select-random-pre-change<br>2・1・2|1290×1005 → 1466×713|未測試|無法確認／未測試|必要回歸失敗，未開始；保留原順序|—|
|54|dev-LX46-zone2-floor1-col2-select-random-post-change<br>2・1・2|1475×640 → 1962×1238|未測試|無法確認／未測試|必要回歸失敗，未開始；保留原順序|—|
|55|dev-LX46-zone3-floor1-col4-select-random-fixed<br>3・1・4|1446×854|未測試|無法確認／未測試|必要回歸失敗，未開始；保留原順序|—|
|56|dev-LX46-zone3-floor1-col4-select-random-pre-change<br>3・1・4|2167×1141 → 1268×662|未測試|無法確認／未測試|必要回歸失敗，未開始；保留原順序|—|
|57|dev-LX46-zone3-floor1-col4-select-random-post-change<br>3・1・4|1462×690 → 1449×1151|未測試|無法確認／未測試|必要回歸失敗，未開始；保留原順序|—|
|58|dev-LX46-zone4-floor2-col1-select-random-fixed<br>4・2・1|2306×1417|未測試|無法確認／未測試|必要回歸失敗，未開始；保留原順序|—|
|59|dev-LX46-zone4-floor2-col1-select-random-pre-change<br>4・2・1|1067×752 → 2399×1182|未測試|無法確認／未測試|必要回歸失敗，未開始；保留原順序|—|
|60|dev-LX46-zone4-floor2-col1-select-random-post-change<br>4・2・1|1329×732 → 1437×853|未測試|無法確認／未測試|必要回歸失敗，未開始；保留原順序|—|

## 剩餘缺陷與未完成事項

- 第31幾何路由退步OPEN，完整當版回歸失敗；必須先解決候選增補與基礎幾何路由的整合契約。
- 43～60仍未測，S3／S4隨機變換尚未完成，不能外推跨來源泛化。60開發通過後才啟動原始10段保留互動及30保留變換。heldout-protocol.json只預登記，不代表已執行或歷史完全盲測。
- S3 46047／46057已有聚焦實體GT IoU0.9511／0.9310的新證據，但當版native1551及全面候選像素稽核仍未完成，不宣稱整體問題關閉或可點擊。
- S2 35929另一處右側第二排漏候選於當版新鮮封包恢復，來源PNG／RGB綁定及全圖／局部像素已核對，距原手動中心2.938px。只有局部恢復證據，沒有新完整外框IoU標註，不宣稱全圖全幀修復。
- 本輪沒有新的完整效能、正式負例或實機結果。G4未完成，P5未授權。
