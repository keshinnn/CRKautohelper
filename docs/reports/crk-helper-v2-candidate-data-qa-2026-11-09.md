# CRK Helper V2：新來源取得與20張邊界QA結果

2026-11-08～09（Asia/Taipei）。本輪接續A0資料准入，**取得兩部新訓練候選影片、20張原尺寸QA圖及兩份獨立定性邊界判讀**。解決三張圖的標註規則歧義；沒有把定性判讀或舊模板框升格成已認證訓練標籤。A1訓練仍未開始，A2正式外緣證據仍OPEN，P5未執行。

## 1. 新來源與split預留

來源搜尋、公開影片metadata及下載紀錄在[本輪工件目錄](../../artifacts/candidate-data-20261108-02/)。先預留來源，再抽QA，未依模型表現改split。四個新YouTube ID均不同於既有四來源；兩部已下載影片的bytes SHA也不在原凍結來源hash中。這是來源身分／bytes檢查，**不是已完成全layout或視覺近重複稽核**。

|來源|用途預留|本輪實際狀態|
|---|---|---|
|[9Rl9H7hen5Y](https://www.youtube.com/watch?v=9Rl9H7hen5Y)，YummyCookieEater，Season5|train|已下載1080p／60fps、無音軌影片串流，1,022,289,723 bytes；SHA `74883295407afa01a4a98201579a70db36e2f9179f0650190f910996b8cb9320`|
|[O_exp3MHbw8](https://www.youtube.com/watch?v=O_exp3MHbw8)，8bahtz，Season1|train|已下載1080p／30fps、無音軌影片串流，180,636,755 bytes；SHA `c7c22cda1bcc6e9e2521e1690019f53b96953047009a73ef5192c4d31df3b4d2`|
|[1nFmD_Ah8V0](https://www.youtube.com/watch?v=1nFmD_Ah8V0)，AEK CH，Season7|val|只保存公開metadata，未下載或檢視畫面|
|[bc2-fdOFrDw](https://www.youtube.com/watch?v=bc2-fdOFrDw)，Info Tools，Season2|test|只保存公開metadata，未下載或檢視畫面；完整來源預留為獨立測試|

資料依據：[source-split-lock.json](../../artifacts/candidate-data-20261108-02/source-split-lock.json)、兩份`train-source*-acquisition.json`及各影片`.metadata.json`。標題／作者／賽季是來源metadata與已檢視train畫面提供的資訊；不能單憑標題宣告未剪輯或獨立run。兩部train片含講解／字幕／剪輯，本輪只把實際保留的原畫面作候選標註QA，不拿剪輯自然跳轉當A3自主操作的因果驗證。

首次一般網路路徑DNS失敗，保留`source-fetch.log`；改用獲允許的公開來源讀取後成功。不登入帳號、不接觸遊戲。1GB來源下載約105.17秒，第二來源約27.64秒；不是模型推論時間。

## 2. 20張QA材料如何產生

每個train來源各10張，全部1920×1080。逐張記錄source影片SHA、精確frameIndex、decoder PTS、PNG SHA、解碼RGB SHA及來源fps；不改大小、不去水印、不修改原始像素。PNG只重新編碼來源解碼後的RGB。

- [qa-recipe.json](../../artifacts/candidate-data-20261108-02/qa-recipe.json)保存具體抽樣影格，可從原影片重跑。
- [qa-frames.json](../../artifacts/candidate-data-20261108-02/qa20/qa-frames.json)及`qa20/raw/`保存20張原圖及來源綁定。
- [prepare_qa.py](../../experiments/candidate_poc/prepare_qa.py)提供可重跑抽取：先驗來源hash，拒絕保護來源ID、跨split同ID及不同ID同bytes；驗實際解碼index，既有輸出不覆寫。

資料scouting先以固定時間抽樣及簡單紅背景覆蓋率縮小檢視範圍，再由實際畫面選QA場景。這個前篩**不是節點辨識器、不產生訓練框或遊戲authority**。其false positives（戰鬥、獎勵、片頭）留在contact及shortlist中，沒有冒稱合格地圖。

既有模板程式只協助定位每張一個代表性物件附近的review crop。`boundary-proposals.json`保留原始候選數與框、cropRect及`automaticProposalOnly=true`。舊候選框未被認定為標籤；本輪沒有用它們訓練，也沒有用凍結真值選輪廓或縮框。原始全圖始終保留。

![20個train-only代表性邊界crop；不是正式候選或已認證標註](../../artifacts/candidate-data-20261108-02/qa20/boundary-contact.jpg)

## 3. 兩份判讀與一次有界規則澄清

兩份分開判讀逐項一致：**13張CLEAR_COMPLETE、4張PARTIAL_OCCLUDED、3張POLICY_AMBIGUOUS、0張NOT_NODE**。獨立review者未讀primary判讀稿，也未檢視val/test畫面。這是兩個AI視覺判讀pass，不冒稱真人標註或具有外部真值；相同判讀仍可能有共同偏差。

|QA index|v1問題|處理|
|---|---|---|
|02、07、11、12|進度／難度／大字覆蓋外框|保留partial，禁止補出被遮住的完整六角框|
|01、09、10|綠色選定／完成外圈與藍色本體，原準則沒有指定哪一層|在模型訓練與測試前澄清新標註準則，再對三張重查|
|其餘13張|代表物件外框可見|僅確認代表物件的定性邊界可判讀，未認證全圖所有框|

原v1判讀、v2有界重查及摘要均在`qa20/boundary-review-*.json`、[qa-summary.json](../../artifacts/candidate-data-20261108-02/qa20/qa-summary.json)。

新準則`visible_outer_solid_extent_v2`：以**屬於該節點的最外層實體著色封閉邊圈**為範圍，包括附著的實體綠色選定／完成外圈；排除連線、擴散光暈、分離箭頭、內部勾號及文字。採「當前可見物件範圍」，不要求不同狀態下虛構相同藍色本體尺寸。遮住外緣就標partial，不從上一影格補形。

澄清後，三張均被獨立重查為可分辨的可見範圍；合計**16張代表性外緣可定性判讀、4張partial**。這是標註層選擇的解決，**不是數值bbox已驗證、不是物理外緣演算法已完成，也不是55～57正式IoU已改善**。準則只作用於新資料，不改任何凍結真值、正式scorer、IoU要求或Verifier。

[annotation-protocol.md](../../experiments/candidate_poc/annotation-protocol.md)及research metadata閘門已更新；舊v1標註不得自動繼承為v2合格標註。全圖仍記`reviewed=false`、`independentReviews=0`、`trainingAdmitted=false`，因為目前每張只做一個代表物件的定性QA，沒有完成全部物件的逐框雙review。

## 4. 工程驗證、成本與版本

- 新增6項來源／抽圖RED→GREEN：重編碼仍不能繞過保護ID、同ID跨split、同bytes不同ID、PNG與原解碼RGB逐byte一致、拒絕覆寫、非法影格拒絕。
- 新增1項舊邊界policy拒絕RED→GREEN；連同既有research測試，**35/35通過**。[all-green.log](../../artifacts/candidate-data-20261108-02/all-green.log)
- 20張原圖抽取約6.03秒；20張既有模板輔助定位約21.18秒。這些是資料準備成本，沒有計作新模型速度或G4 producer p95。
- 正式223檔及141依賴重新核對；結果與新檔／工件hash見本輪`version.json`、`evidence-index.json`。沿用`codex/candidate-poc-a0-a2`；不假稱有新commit，Git作者未設定的原限制仍在。

本輪只新增／修改research資料工具及標註準則，正式程式、原模型、正式測試與凍結輸入不變。未重跑60組、正式負例或保留集；35是research單元結果，不能代替既有48/60完整閉環紀錄。

## 5. 目前Go／No-Go

|項目|決策與尚缺事項|
|---|---|
|新來源搜尋／取得|局部GO：2個新train完整媒體取得；val/test來源已預留，只有metadata|
|20張QA材料／層準則|局部GO：原圖及代表性定性雙review完成，3個層歧義澄清，4個遮擋維持partial|
|資料與layout完整准入|NO-GO：未完成全部run/layout及跨集近重複稽核|
|全框監督標註|NO-GO：目前20張原圖不等於20份完整標註，更不等於400份；已認證完整train／val／test仍0／0／0|
|A1一次訓練|未啟動，預算使用0次；完整資料、隔離train/export環境及算力仍是前置|
|A2／A3|原外緣證據與預覽定位未新增通過；A3尚未開始|

接下來資料工作的明確順序：以已澄清準則對新train全圖逐框標註並獨立QA；取得已預留val/test媒體，完成source/run/layout及近重複稽核後擴至240／80／80。測試來源不能參與模型或標註規則挑選。只有整體准入通過才建立隔離訓練環境並執行既定一次訓練；不因已有影片就跳過標註品質。

**沒有新模型效果數據，沒有新增完整閉環成功；48/60保留，G4未完成，P5未授權／未執行。**
