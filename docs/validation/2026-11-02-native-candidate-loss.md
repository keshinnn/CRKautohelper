# 原生候選稽核：閉環通過但局部候選退步

## 實際完成結果

版本 `24bfb2a5eb6ef4143c4574d02d2d93493e2e7f61`：前42組42/42、原生20組20/20、固定倍率15組15/15閉環通過。新鮮分析分別2114、1551、381張，raw cache為0；Node127、Python236通過。30組開發負例及評分器對照通過，`formalNegativeGateComplete=false`，不能改稱正式負例G4完成。

證據根目錄 `artifacts/phase-routing-20261028-01/`；來源188個專案檔、141外部依賴、runtime與各報告hash綁定。這些是24bfb2a的結果，不能當作後續修正版通過。

1551張與原M1的候選／錨點對照：31張最終候選發生變動，沒有錨點遺失；七張原候選變動影格已逐張看疊圖。代理檢視31組54項差異裁圖、四張完整差異表，以及46045、14546、57947的上下文後，發現**一個原本合法的戰鬥候選遺失**。沒有在差異中觀察到新增錯誤物件，但這不足以讓候選稽核通過。沒有產生會放行控制器的`native-candidate-changes-reviewed.json`。控制器在必要候選稽核閘門停止；43～60、保留集、效能測量均未啟動。

## 46045 根因

原圖1280×720，PNG SHA256 `2cbdc12a5820b74618251719d9bd683bd08480fa0afd5cea9482b893eca40886`。原圖右側橘色戰鬥節點清楚可見，舊M1中心 `[829.33,552.67]`，box `[792,512,74.67,81.33]`，匹配分數0.494630456。這個節點確實不在新版最終結果中；不是配對器的ID變動誤報。

|階段|M1／基準|24bfb2a補強|
|---|---|---|
|原圖候選|4|4|
|原圖稀疏恢復後|4|4|
|比例恢復|未接受另一份地圖，保留原圖4個|接受校正圖7個，替換原圖|
|最終右側指定戰鬥節點|存在|消失|
|絕對樓層錨點|false|false|

估計比例1.039984236，校正raster1231×720，模型raster960×561。補強候選改變校正結果能否建立四欄並被接受；只保存原始M1欄位，不能隔離完整的幾何接受路徑。原圖候選的前綴保留也無法保證另一raster的最終候選不遺失。

當版實際兩次同像素重算（共用開／關）皆4→4→7且結果一致，排除中間結果快取誤用。這是**候選在不同raster重採樣後的可用性與幾何結果接受邊界耦合**，不是點擊、座標取整或預覽身份失敗。沒有假稱已定位到某一模板的完整NMS前分數；本輪邊界證據足以定位最終替換造成的遺失。

## 本輪最小修正

沿用已批准的Observer／比例恢復呼叫邊界調整，僅改`ml/map_pipeline.py`：先在同幀明確M1 backend跑既有幾何接受路徑，再處理補強。補強不得引入M1未接受的校正raster；M1有校正時，來源、校正與分析尺寸、來源身份及正反矩陣必須完全一致。不同時保留同幀合法基準／source工作結果，保存被拒絕地圖及原因。最終currentPosition仍按當前像素重新測量。

不修改比例估計器、raster函式、候選銀行、Canny／匹配／NMS／IoU／三peer閾值、JS proof、Selector、Transaction或Preview Verifier；不拷貝上一幀座標，也不將被拒絕地圖用於點擊。

`tests/test_phase_route_parity.py`：先兩項真實46045測試RED（原有候選集合遺失），修正後GREEN；再以外層coverage scope重現基準backend不明確的RED，明確指定M1後三項全GREEN。共用／停用模式一致，46045原4個候選保留、絕對樓層仍false。既有phase相關9項、legacy current兩項、S3六項聚焦檢查亦通過；phase9是在第三項加入前的實際套件數，不能當作最後完整套件成績。

只讀反事實9張試驗保持31／41／42目標IoU≥.90及S3兩張獨立GT通過，僅支撐設計選擇，不能冒充生產完整閉環。第一版試驗錯將轉換前35928對比轉換後GT而失敗，原始腳本／日誌保留；第二版使用凍結preFrames35929、35935，沒有修改正式測試資料。

## 待驗證與風險

修正版尚須綁定新commit／檔案hash，完整Node／Python、560聚焦、42組、原生20、固定15、負例30、1551／七張與全部候選差異、取整壓力、配對matcher及193張隔離效能都須重新驗證。不得使用上述24bfb2a結果填補新版空白。

新增基準幾何步驟有額外CPU成本，雖可共用當幀原始匹配，仍須實測。G4 p95≤1500ms、畫面年齡≤2500ms與15秒結果條件保持不變。若需要新融合演算法、修改估計器／raster或降低安全條件，停止並回報。P5仍未授權。

## 證據

- `native1551-seven-current-01/report.json`：1551與七張覆蓋、31張候選變動。
- `native-review-prep/report.json`、`sheet-001.png`～`sheet-004.png`、`0022/context.png`：54項實際像素差異。
- `native-candidate-review-failure.json`：已檢視、0個新增錯誤物件、1個合法候選遺失、gatePassed=false。
- `native46045-loss-01/boundary-trace.json`：同幀兩模式重算階段輸入／輸出。
- `route-parity-study-01.log`、`study-route-parity.py`：首版診斷錯誤完整保留。
- `route-parity-study-02/report.json`：九張只讀反事實，不是完整閉環驗收。
- `route-parity-red.log`、`route-parity-green.log`、`route-parity-explicit-backend-red.log`、`route-parity-explicit-backend-green.log`：實際RED→GREEN。
- `route-parity-phase-tests.log`、`route-parity-legacy-tests.log`、`route-parity-s3-tests.log`：聚焦驗證日誌。
- `local-defects-current-01/report.json`、`pixel-review.json`：24bfb2a S3兩張IoU0.95114559／0.93100102，S2 35929恢復局部戰鬥候選；不是全圖召回率或新版驗收。
