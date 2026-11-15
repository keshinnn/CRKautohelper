# CRK Helper V2：A0准入與A2離線proof工程結果

2026-11-08（Asia/Taipei）。**已產出可重跑工程工具與實驗；A0訓練准入No-Go，A1未訓練；A2原圖／幾何研究取得局部有效結果，完整新proof仍未成立。**不是新模型的正面／負面效果評估，不新增閉環通過數。48/60基準、G4未完成及P5未授權維持。

## 1. 實際完成與版本邊界

研究位於`codex/candidate-poc-a0-a2`，從原`codex/v2-minimal-loop`分出，保留其dirty基準。產品修改0；新增工程只在`experiments/candidate_poc/`，另有本報告、工件及AST圖更新。舊dirty產品檔不是本輪變更。

基準HEAD `74ad37d85e3aef134d0631e0ce6a799bcb4dbe3d`不足以單獨識別當版；使用[基準鎖定](../../artifacts/candidate-poc-20261108-01/baseline.json)及既有verification的逐檔hash。已封存**223個產品／測試／資料檔＋141個依賴，共364檔**，ZIP逐檔重新解壓讀取驗證，16,253,526 bytes。ZIP SHA256：`e71aa9f143d0cc511cc7652b21b4a05835c19e0419f62b87a29a1415e6026dc2`。

[baseline.zip](../../artifacts/candidate-poc-20261108-01/baseline.zip)內`restore-index.json`列出原始路徑、封存位置及hash；可在獨立目錄復原比對，本輪未覆寫正式檔案。既有60組結果及失敗工件留在原處，沒有刪除或替換。新的版本及工件索引見本輪工件目錄中的`version.json`、`evidence-index.json`。

凍結manifest SHA仍為`189b37115b1d08b0c245306bb727b13759d00aa0efb76a30e74b85acc6038e60`。沒有重跑60組來冒稱新的48/60結果。

Git作者身分未設定，研究commit建立失敗，未自行替使用者設定姓名／email。新研究檔僅已暫存；以base HEAD、364檔封存、新研究逐檔hash與`research.patch`重現，`version.json`明示`researchCommitCreated=false`，不假稱有新commit。

## 2. A0資料、環境與訓練決策

### 2.1 實際來源盤點

四部已使用來源均重新核對影片SHA，全部相符。[資料盤點](../../artifacts/candidate-poc-20261108-01/data-readiness.json)

|來源|尺寸|約長度|新訓練准入狀態|
|---|---|---:|---|
|buAwy1zf2LI|1440×1080|3232.3秒|歷史已曝光；未有新run/layout隔離與候選框QA|
|L0ktY5qUppI|960×720|3464.2秒|同上|
|0QxozULx_SQ|1280×720|2976.1秒|同上|
|LX46_2XTfJg|1920×1080|2882.8秒|同上，含浮水印，不去除原像素|

現有影片像素不是零，但**符合新來源隔離、可見外緣標註及獨立QA的已認證資料為0張**：train缺240、val缺80、獨立test缺80。此結論限於已盤點來源與提供的PoC資料，不聲稱整部電腦沒有其他可用影片。現有框、偵測輸出及凍結真值沒有被轉成訓練標籤。

目前採保守整來源排除，直到未使用片段能證明不同run/layout及未與凍結互動重疊；不是永久禁止這四部所有未用片段。資料取得方案：先盤點可獨立的新原始來源／run；或為現有未用train/val片段補齊完整互動、layout及近重複稽核，再取得至少一個未用於訓練／驗證的新測試來源。建議至少三個分割來源群組，最好另有訓練來源增加多樣性。20張新圖先做雙獨立標註QA，通過才擴到400張。

可直接執行的[准入檢查](../../experiments/candidate_poc/freeze_inputs.py)會拒絕跨split source/run/layout、重複圖、保護來源、缺少lineage、未review及外緣未定義資料。它是**metadata閘門，不是光靠JSON勾選就認證實體標註**；未來訓練必須另核對原圖、尺寸、框、近重複與review紀錄。[外緣及資料操作準則](../../experiments/candidate_poc/annotation-protocol.md)已落檔，但實際20張雙標註尚未開始，不能算已達A0資料Go。

### 2.2 環境實測

[環境輸出](../../artifacts/candidate-poc-20261108-01/environment.json)：Python3.12.14、12 logical CPU；torch2.14.1+cpu，CUDA build=null、cudaAvailable=false、deviceCount=0、torch CPU threads=6；ONNX Runtime1.31.0、OpenCV5.0.0.93、Pillow13.0.0。未安裝ultralytics與onnx，未建立隔離訓練環境。

`nvidia-smi`不在命令路徑、CIM讀取被環境拒絕。**不能據此斷言沒有實體GPU**，也沒有量測CPU完成50 epochs需多久。現有torch無CUDA可用；沒有啟動無期限CPU訓練或偷偷更改正式環境。資料未過准入前，不花時間安裝整套訓練依賴。

|A0關卡|結果|
|---|---|
|基準封存與可恢復性|GO：364檔hash及ZIP讀回驗證|
|原始來源完整性|GO：4部影片SHA相符|
|新資料隔離／外緣QA|NO-GO：認證資料0／400；20張初始QA未完成|
|隔離train/export環境與算力|NOT READY：缺套件與隔離環境；GPU資源未認證|
|A1一次訓練|NOT STARTED：0訓練次數，0新模型推論；未動用50 epochs／4 GPU小時預算|

## 3. 已鎖定的評估資料，不等於已執行模型評估

[evaluation-lock.json](../../artifacts/candidate-poc-20261108-01/evaluation-lock.json)固定焦點52、53、55、56、57、58、59（1035張），成功控制1、8、19、25、31、39、40、41、42、46、47、51（1573張）。正例合計2608張；64張篩選規則在訓練前寫入清單：焦點各4張均分索引、控制各首末2張、原排序負例前12組各首張。不使用模型結果選容易圖。

30負例原manifest實際共**60張計畫圖**，本輪全部納入鎖定，與正例合計2668張逐檔驗SHA及PNG尺寸。[圖像hash索引](../../artifacts/candidate-poc-20261108-01/evaluation-image-hashes.json)。之前負例報告的**57張是實際分析數**，3個缺區域標籤案例當時各在首張拒絕；兩個數字意義不同，不能拿57當原manifest完整張數，也沒有修改原始分母。評分器對照2組保留原證據。

上述是來源鎖定／完整性稽核，不是新模型precision／recall、外框IoU或閉環結果；A1未訓練，因此這些效果數據均**尚無法評估**。55～57及52／53等既有失敗狀態不變。

## 4. 訓練前proof相容性實測

[可重跑探針](../../experiments/candidate_poc/proof_compatibility.cjs)在13組既有同幀packet中，選首張及存在時第一張既有verified預覽，共21張；每張做3種schema診斷，共63個變體。不是新模型候選生成，不讀GT，不將後段畫面資訊輸入前段測試。

|變體|實際結果|正確解讀|
|---|---|---|
|拿掉aspect／ellipse相關欄位，加confidence=1|16/21在ASPECT_RECTIFICATION_UNBOUND拒絕；5張其他路徑仍產生MAP／PREVIEW觀察|模板證據確有硬耦合，但不是每條路徑都相同；保留下來的舊觀察／身份欄位不可冒充新模型證據|
|只有同幀舊候選框作schema測試，去掉絕對地圖與預覽authority|21/21沒有絕對anchor，也沒有verified PREVIEW；部分仍可識別MAP，部分僅PREVIEW_PENDING等待|畫面分類通過不等於可選點；沒有建立新模型授權橋接|
|改錯source pixel SHA|21/21拒絕OBSERVATION_BINDING_INVALID|來源綁定拒絕仍有效；不是完整負例套件驗收|

5張未因第一變體拒絕的是19組地圖／預覽、31組預覽、58／59地圖；58／59本來沒有合格anchor。沒有執行任何新點擊或完整交易，所以也不能把這些觀察解讀成新增完整成功。逐筆原packet／PNG hash、時間及結果在[proof-compatibility.json](../../artifacts/candidate-poc-20261108-01/proof-compatibility.json)。

**結論：NO-GO直接替換；GO繼續研究獨立證據。**原始建構器若確實從同幀像素產生合法proof仍可重用，但不能假定NN框天然符合橘色橢圓／模板畫布等物理假設。confidence不是模板相關性。原Node Adapter／Selector／交易／Verifier全部未改。

## 5. A2：已實作的獨立研究原型及未證明部分

新增[Python witness producer](../../experiments/candidate_poc/research_evidence.py)與[Node研究驗證器](../../experiments/candidate_poc/verify_research.cjs)，與正式Verifier無載入連線。Node直接解碼獨立取得的原RGB PNG（CRC、filter及尺寸檢查），重新算RGB SHA、source→640 letterbox浮點矩陣／框及64個固定原圖梯度取樣；不信任producer自行宣告verified。

僅支援8-bit、RGB、非交錯PNG，其餘拒絕。極端比例造成縮放某維度四捨五入為0時也拒絕，不能接受不可逆矩陣。研究context由離線執行器另提供，不從witness讀來源路徑；**正式可信capture store尚未實作**。研究clock使用原離線PTS＋1ms，絕非實機新鮮度驗收。

在焦點7組各首張，以既有同幀observer第一個完整在界內框執行一次測量；不是模型、不是GT選框。6組產生`RESEARCH_GEOMETRY_ONLY`，59組沒有可用當前框，直接`NO_CURRENT_OBSERVER_BOX`，不從別張補框。[逐例與原始witness](../../artifacts/candidate-poc-20261108-01/research-result.json)

|新契約部分|本輪證據／狀態|
|---|---|
|來源PNG／RGB與幾何|局部GO：6張真實PNG兩語言重算一致；原型契約與變造負例已測|
|邊界原始量測|局部GO：64點原圖梯度可重現；只證明讀到同一像素，不證明是唯一正確外緣|
|外緣唯一性與框品質|OPEN：沒有通用可驗證測量法；55～57仍OPEN，不報新IoU改善|
|絕對地圖定位|UNPROVEN：沒有新增入口／三peer／連線／位置證據|
|預覽配準與身份|UNPROVEN：未新增當前5對跨2行、身份或兩張一致預覽；52／53未修復|
|正式Node授權|NO-GO：研究成功／拒絕都固定select=false、confirm=false、dispatch=false；不產生正式authority|

這個原型回答「Node能否不依賴模型confidence而重算來源與幾何基本證據」，尚未回答「能否證明完整可點擊節點／預覽身份」。下一份正式Verifier提案仍須補物理外緣與語義、可信capture來源、地圖及配準證明，再申請批准。把同一模型跑兩次不屬此種獨立驗證。

### 5.1 成本

本輪A0完整來源與圖像hash盤點執行約15.77秒，包含4部影片、2668張圖與原封存核對，不是畫面推論延遲。6張研究witness producer單次約22.91～80.04ms；Node獨立解碼／核對約49.30～120.17ms，中位67.64ms。樣本只有6張、未做正式暖機與隔離，**不列p95、不與舊4033ms完整producer比較、不宣稱達G4**。逐張原始時間在research-result.json，未包括模型／OCR／地圖／身份。

## 6. RED／GREEN、審查與失敗保存

新增隔離單元**28/28通過**：資料准入12、基準／真實負例清單5、研究來源／幾何／變造拒絕11。它們是新研究工具的單元結果，不取代原Python264／Node133同版歷史結果。完整日誌：[all-green.log](../../artifacts/candidate-poc-20261108-01/all-green.log)。

RED保留：資料准入15個斷言失敗（12方法含subtest）、基準3個斷言失敗、真實負例schema與檔案布局重現、新證據11個失敗／錯誤（9方法含subtest）、極端比例2個失敗。先有可重現失敗再寫對應實作，沒有以import錯誤當功能RED。

過程中發現並修復的**研究工具**問題：

- 系統臨時目錄不可寫，初次基準測試為環境錯誤，不算有效RED；改用研究目錄內隔離臨時檔，重新取得有效RED。
- 負例summary用resultsCount且按案例分manifest，不能套正例results／單manifest假設；保存兩次失敗log並以真實布局加測。
- 負例計畫60張與原執行57張的差異已核對來源，不改真值來迎合測試。
- 獨立只讀審查重跑26測試無阻塞發現，指出極端寬窄比例可產生零維letterbox；新增2項RED並在Python／Node同時拒絕，最終28/28。沒有因研究原型允許不可逆幾何而修改正式契約。

本輪未跑新的60／20／15／正式負例／保留集或完整影片；沒有可訓練模型或有效正式補丁，不反覆耗時全量回歸。原1551及七張候選變動後續問題不因此宣稱完成。實際ML效果、完整閉環與G4狀態不從單元數推導。

## 7. Go／No-Go與下一步

|項目|決策|
|---|---|
|已知穩定版可回復、資料清單可重跑|GO|
|A0整體訓練准入／A1|NO-GO：0／400認證資料；未做外緣雙標註QA；隔離train/export與資源未就緒|
|A2來源／幾何研究|PARTIAL GO：可重現獨立驗證，但沒有外緣／定位／身份authority|
|直接把NN框換進模板proof|NO-GO|
|正式Verifier修改／P5|未授權，未執行|
|A3最小自主閉環|仍是下一產品里程碑；尚未滿足候選及proof前置，不冒稱已可連續操作|

下一個實質工作是**補齊來源與標註准入**，不是再切換模型或逐影格補丁。按操作準則先取得20張新且來源隔離的樣本完成雙review，再擴到400張；同時確認可用訓練資源並鎖隔離環境，才啟動一次既定訓練。若一次模型實驗不能改善，仍按原停止條件交負面結果，不自動重訓。

A2下一個可判定關卡是「可唯一測量的實體外緣」及「當前可見配準對」；尚無方法時保持OPEN，不用取樣一致性偽裝成外緣真實性。A0／A1／A2取得有效前置後才轉A3的連續≥2節點、0人工確認路線，正式Verifier改動仍先另批。

重跑入口與限制見[工程README](../../experiments/candidate_poc/README.md)。本輪訓練0次、新模型推論0次、正式修改0、原生輸入0；**沒有宣稱G4或全自主完成**。
