# CRK Helper V2：400張原圖與首批全圖數值標註結果

2026-11-09。**已建立240／80／80原圖池；首批7張完成雙AI全圖視覺覆核，其中4張地圖共46框、3張明確背景負例。**這比上輪代表性crop定性QA前進到數值標註，但不是400張已標完、不是訓練准入，更不是新模型或G4通過。A1訓練次數仍0。

工件根目錄：[candidate-labeling-20261109-03](../../artifacts/candidate-labeling-20261109-03/)。正式辨識／Verifier／原凍結資料不變，未進行P5。

## 1. 完成來源取得及原圖池

延續先前source split預留，不在看到模型表現後改分割。本輪取得：

|來源|split|實際媒體|
|---|---|---|
|1nFmD_Ah8V0|val|1920×1080／30fps、731,995,508 bytes；SHA `e1733ef8f6e17bf30903d9443e4a96c698134e2cd15fdba76007a0e861eee8ee`|
|bc2-fdOFrDw|test|1920×1080／30fps、1,030,772,416 bytes；SHA `55df3cde3da2da7b33684d5d106a4b06a8097deb070ed53d0834de0345a971af`|

兩份acquisition.json保存來源與成本，下載約88.61／169.11秒。不登入、不操作遊戲。兩個train媒體仍使用前輪9Rl9H7hen5Y與O_exp3MHbw8原檔，不改SHA。

[raw-corpus-v2.json](../../artifacts/candidate-labeling-20261109-03/raw-corpus-v2.json)含400張自然原圖：160張9Rl9＋80張O_exp＝240train、80val、80test；全數保留來源解碼尺寸1920×1080及RGB像素，沒有以增強圖補原圖數量。每張有影片SHA、source frame index／PTS、PNG／RGB SHA及split。原先20張train QA影格全部保留在集合中。

400張是400個影格，不是400張獨立地圖或400個獨立run。框／可見性／場景分布與source/run/layout仍需逐張標註及完整稽核；影片時間間隔和不同YouTube ID本身不足以認證獨立性。val/test像素只用於預定資料抽取及重複稽核，未拿來選標註規則、調模型或改正式測試。

### 抽樣失敗已保留，沒有默默換測試

初稿從2倍密度的網格由前往後填滿quota，造成部分來源只涵蓋前約47～50%，O_exp因既有QA pins可到約79%。這是新資料抽取工具的覆蓋錯誤，尚未進入訓練。

[sampling-coverage-failure.json](../../artifacts/candidate-labeling-20261109-03/sampling-coverage-failure.json)、舊raw-corpus.json、原400張及log全部保留。先建立3項RED測試，再修正[sampling.py](../../experiments/candidate_poc/sampling.py)：保留既有pins、覆蓋整條來源時間軸、拒絕非法index與不足quota。v2重新抽取約85.26秒，來源頭尾及四分區有明確覆蓋；manifest綁定sampler／materializer hash。

原正式60組、保留集及真值沒有重選或刪減。v1只是尚未准入的新資料草稿；此修正發生於任何模型訓練前。

## 2. 從定性QA進入全圖數值標註

兩份數值草稿分開產生，標註人員均為AI視覺pass，未冒稱真人真值。範圍是原圖所有可辨認的可見map_node／entry_gate：灰色、完成及首領徽章也計入；右側樓層標號、頭像、寶物、對話框header圖示不計。被文字／裁切遮住則partial，不補出隱藏完整框或dialog後的節點。

初稿root列45框，獨立pass列46框。對帳定位到QA14頂端少一個被裁切的節點、兩個partial範圍與首領徽章extent差異。重新看[原圖頂端](../../artifacts/candidate-labeling-20261109-03/qa14-top.png)及[徽章](../../artifacts/candidate-labeling-20261109-03/qa14-boss.png)，只做一次有界原像素修正；不平均兩份框，不使用凍結真值，不任意縮放到門檻。舊45框草稿、獨立46框草稿及修正版均保留。

|train QA圖|框數|complete／partial|兩份數值標註最小IoU|
|---|---:|---|---:|
|03，9Rl9來源|14|10／4|0.906243|
|08，9Rl9來源|15|12／3|0.927230|
|14，O_exp來源|10|6／4|0.935519|
|16，O_exp來源|7|6／1|0.962612|
|合計|46|34／12|各圖逐框一對一比對均達.90|

**此IoU是兩份新標註間的一致性，不是模型對真值IoU，也不保證物理外緣演算法正確。**框由原圖視覺估計，保留AI共同偏差及數值不確定性風險。獨立最後覆核確認四張可辨認物件未發現具體剩餘遺漏，見`final-four-review.json`。

另對3張train原尺寸全圖分別覆核：隊伍配置、寶物視窗、泰文配置。兩份pass均確認沒有實際地圖節點；其六角形物件屬裝備槽或寶物UI，記空annotations與hardNegativeReviewed，而不是看到六角形就標節點。這3張是新增訓練資料負例，不是正式負例30組的新驗收。

總交付：[reviewed-annotations-batch01.json](../../artifacts/candidate-labeling-20261109-03/reviewed-annotations-batch01.json)：**7張全圖覆核、46個正物件框、3張空標註hard negatives，剩393張全圖覆核。**其中正物件為45個map_node與1個entry_gate，類別覆蓋仍不足以推定整個資料池平衡或可訓練。

每張仍`trainingAdmitted=false`、source/run/layout資格未最終認證。全圖標註覆核完成與整體資料准入是兩個狀態，不因數值一致就自動啟動訓練。

## 3. 重複與保護資料稽核

[duplicate-audit.json](../../artifacts/candidate-labeling-20261109-03/duplicate-audit.json)以當版程式重新讀取400張新圖及2668張保護圖，驗PNG hash、完整解碼RGB及尺寸；同RGB不同PNG壓縮也能識別。

|檢查|結果|
|---|---:|
|新資料跨train／val／test完全相同RGB＋尺寸|0對|
|新資料對保護圖完全相同RGB＋尺寸|0對|
|同split完全相同RGB＋尺寸|0對|
|全圖pHash距離≤4的跨集／保護相似對|1對，未截斷|
|低資訊量新圖|1張|

95.46秒是此資料稽核成本，不是producer或模型p95。沒有以「零完全相同圖」宣布所有來源或layout獨立。

唯一相似對為新train的O_exp影格7982與保護資料LX46的2262。獨立資料review確認畫面分支位置、節點類型排列不同，屬共同遊戲背景／UI造成全圖相似，不能僅由pHash隔離整個來源。也不能由這一對的判讀推論整部影片獨立。見[duplicate-pair-review.json](../../artifacts/candidate-labeling-20261109-03/duplicate-pair-review.json)。

低資訊圖為O_exp影格0，接近白色背景與游標。獨立pass視為可作背景負例候選，但尚未納入本輪3張完成雙review的負例，不能暗增標註數。

## 4. 可執行工程與RED／GREEN

- [annotation_audit.py](../../experiments/candidate_poc/annotation_audit.py)：以實際RGB PNG綁定兩份標註，要求不同reviewer與全圖覆核聲明；一對一比對類別、complete／partial及.90一致性，不允許兩框對同一物件或平均差異。永不自動給training admission或操作authority。
- [duplicate_audit.py](../../experiments/candidate_poc/duplicate_audit.py)：exact RGB需同尺寸，pHash僅建review queue；低資訊不假稱可證獨立。
- [sampling.py](../../experiments/candidate_poc/sampling.py)：保留原QA索引，修正新資料全來源時間覆蓋。

新增標註一致性10項、PNG完整解碼2項、抽樣3項、重複稽核5項與尺寸1項RED→GREEN；合計當前research **56／56**通過。[all-green.log](../../artifacts/candidate-labeling-20261109-03/all-green.log)

獨立code review發現research標註audit只查header可能接受自洽hash的41-byte截斷PNG，已先重現RED，再要求完整RGB decode。也以RED驗證相同RGB buffer但不同寬高不能稱完全相同圖。兩者都是本輪研究工具修正，正式Verifier未改。

沒有重跑原60／20／15或正式保留集，沒有以research單元替代它們；沒有把原Python264／Node133歷史結果說成這次新測。版本、source hash、原圖與失敗紀錄以`version.json`／`evidence-index.json`綁定。Git作者未設定，未假稱建立新commit。

## 5. Go／No-Go與下一個工程工作

|項目|判定|
|---|---|
|四個原定來源媒體取得／400原圖|GO：原檔及來源hash鎖定，v2時間覆蓋經測|
|首批數值標註與負例流程|局部GO：7張完成雙AI視覺review；不是400張完成|
|跨集精確重複檢查|GO：本集合未見完全相同RGB；相似對完成有限人工式AI判讀|
|完整資料／layout／標註准入|NO-GO：393張全圖覆核未完成、完整source/run/layout稽核仍待補齊|
|A1一次有界模型訓練|未啟動；次數0，未消耗50 epochs／4 GPU小時訓練預算|
|A2新外緣proof、A3連續自主閉環|沒有新增正式通過，尚未達前置條件|

後續接續剩餘全圖標註與來源layout稽核，保留門、灰色／完成節點、預覽遮擋與UI hard negatives的類別覆蓋；不能只以簡單空背景補齊400張標註。資料全部合格後，才鎖隔離train/export環境與算力並執行一次訓練；單次實驗無改善仍依原停止條件結束。

**既有48/60與所有失敗證據保留；正式223檔及141依賴未改。G4未完成，P5未授權／未執行。**
