# Python視覺效能優化與泛化驗證（2026-10-27）

狀態：本輪最小優化、完整必要回歸、隔離成對193張測量已完成。**因果CPU p95由3753.45降至2743.67ms（改善26.90%），仍未達1500ms；未開始40–60／保留集／P5，G4未完成。**

## 範圍、版本與計畫

本輪依使用者批准的Python效能方向執行；計畫`../superpowers/plans/2026-10-27-python-vision-performance.md`，規約`../superpowers/specs/2026-10-27-python-vision-performance.md`。基準`a7a05a2`（前版功能8aa1111、基準runner f88cb93），當前功能／測試凍結`c9559e14f97cdbdefd9c07ddfe00a9f305a3dc0a`。只保留一項已證明去重的功能修改；V1磁碟程式／模型、Node Selector／交易／Preview Verifier及所有驗收門檻未改。

證據根目錄：`artifacts/performance-20261027/`。舊基準完整193張單worker暖機10：producer p50/p95=2767.417/4370.174ms、因果CPU=2708.224/4292.450ms；各自183與127樣本，不可相加／相減分位數。

## 1. 操作層量測，而非依名稱判斷

凍結21張診斷圖（原193張中19張，含開圖／較慢／預覽轉換，另兩張S3已知缺陷）。這不是擴充正例分母、完整片段或效能驗收。`profile-before-01`與`unprofiled-before-01`的相同21張、相同順序，在binding、flow、evidence、mapReview、原始mapReview、progress、trackedMap、previewContext、previewIdentity、mapActions等10類內容**完全一致**；`profiler-semantic-check.json`保留逐項比較。剖析加入額外開銷，不能直接當速度基準。

`operation_profile.py`量測OpenCV工作執行緒內的實際呼叫、尺寸、時間，並按StageTiming歸屬到本張影格／模組。保留cProfile明細作導覽，真正的並行呼叫以顯式探針為準；同一函式遞迴、父子包含及平行worker的inclusive時間均不可加成wall time。

|操作／區域|21張實際次數|診斷含括時間／發現|
|---|---:|---|
|raw觀察候選掃描|21|約7.9秒wall；V1 inspect_map的42次含大圖→960的遞迴，不是42次掃描|
|aspect候選掃描|27|約12.1秒wall；其中10次是補候選重跑同張校正圖的基礎候選|
|estimate_pixel_aspect|21（另raw特殊路徑1次）|aspect內共約275ms，約13ms／張；**不是該模組數秒的主因**|
|aspect cv2.matchTemplate|140945|其中133531主執行緒；133382次34×34小圖比對共約2632ms。其餘主要是worker的大圖模板匹配|
|raw cv2.matchTemplate|7045|主執行緒1377次，其餘在worker；不得拿thread inclusive總和當整體耗時|
|raw文字辨識TextRecognizer|78|OCR細分探針共約14780ms inclusive，實際主要成本|
|raw文字偵測|25|約2619ms inclusive|
|raw文字方向分類|25|約451ms inclusive|
|流程inspect_frame|21|約304ms；不是主要瓶頸|

額外核對轉換／複製而非只猜CPU設定：aspect內PIL.resize 7964次／1460ms、PIL.tobytes 9080次／751ms、numpy.asarray 8149次／484ms、numpy.array 2182次／488ms、cv2.cvtColor 9923次／412ms，Canny僅27次／73ms；raw內PIL.resize 480次／883ms、numpy.array 5626次／373ms。多數是小模板／候選圖，不可把呼叫數當整張大圖複製次數。它們各有成本，但相較完整候選掃描與OCR辨識，沒有證據支持先全面改寫資料轉換。以上仍是診斷inclusive數值，不加成推估最終延遲。

數據分別在`bottleneck-analysis.json`、`profile-before-01/operations.json`、`profile-ocr-detail-02/operations.json`；不同剖析輪的時間不能混加。OCR辨識數包含保留規約所需的原像素重讀／字型尺度變體，不任意省略獨立讀取。

## 2. 已保留的最小優化

`FrameIntermediates`只在一張影格生命週期內共用**原始候選量測**；鍵含來源capture／PNG／尺寸、實際模型RGB像素hash、模型尺寸／模式、模板實際內容hash、backend／OpenCV設定及參數。每次返回隔離副本，避免分類／欄列賦值污染後續讀取；8項內的有界快取在結束／例外清空。唯有不可變的模板配置fingerprint跨生命週期保留；模板改變即拒絕並要求新辨識程序，避免沿用底層原有模板LRU的陳舊資料。全域hook由非阻塞scope鎖防止混入巢狀／平行影格。

沒有快取OCR、分類決策、地圖root、節點proof、連線證據或預覽身份。分類／格點／連線及Python／JS獨立來源驗證照常執行。`analyze_cases.py`與`observe.py`均接入，沒有只為跑分啟用。`--disable-frame-reuse`只作明確的離線對照，維持相同演算法而不共用候選，報告記錄該設定。

|前後同21張診斷|raw掃描|aspect掃描|同影格hit／miss|10類語意內容|
|---|---:|---:|---:|---|
|優化前|21|27|不適用|參考|
|優化後|21|17|10／38|全部完全一致|

證據：`profile-after-01`、`frame-reuse-semantic-check.json`。移除10次重掃的預期可回收工作約4.4秒／21張；這是操作數收益，**最終速度改善必須以成對193張新鮮測量判定**。

安全聚焦：8項cache／配置檢查加disabled對照共9項，實際4影格的開／關兩條管線逐欄位相等；所有RED/GREEN保留。新加入的OpenCL狀態查詢曾在本機診斷卡住，已停止兩個自建診斷程序並移除該查詢；目前處理CPU ndarray，不查詢GPU能力。

## 3. 有量測但未採用的方案

- 相同模板kernel去重：960×540為173個kernel、0重複；960×717為204個、17重複。整體回收預期有限，未加入複雜度。
- OCR thread改少：使用3組實際擷取、固定像素／順序的辨識batch，各暖機3、量7次，文字與分數逐值一致。4／2 threads p50為163.40、63.26、23.02ms；2／1為258.16、95.86、27.43；1／1為386.04、147.49、39.53。較少threads更慢，原4／2不改。這是micro診斷，不是完整producer效能。
- 候選worker改8：三種模型尺寸4workers p95為590.22、627.78、670.77ms；8workers為613.56、701.86、604.47。候選／分數／排序逐值一致，但尾延遲不穩且兩例退步，保留4。2workers更慢。

證據：`ocr-thread-micro-01/report.json`、`candidate-workers-micro.json`。未更改模型、辨識解析度、crop規約、.48/.90/.95或IoU門檻，也沒有延長TTL／deadline。

## 4. S3缺陷仍OPEN

獨立測試標註：`data/p4c/s3-scroll-known-defects-v1.json`，來源1280×720原PNG／video／frame／RGB／SHA綁定，**不改原凍結60／30驗收分母**。生產程式沒有影格ID或地圖ID分支。

|影格／物件|定位後根因|原圖分數|校正後分數|狀態|
|---|---|---:|---:|---|
|46047戰鬥（來源框681,578,78,78）|未到NMS即無合格peak；原始正確位置最高值略低於原.48|.479775995|.467131436|OPEN|
|46057治療（來源框461,421,78,80）|raw候選存在（IoU=.9326），校正後未到NMS即缺漏；無預覽panel scope時heal補候選不執行|.517282188|.465661258|OPEN|

當張像素比例估計1.042114843／1.038246547，微幅重採樣改變Canny／模板支援；這是定位到的機制，不能宣稱所有根因或其餘地圖都相同。`s3-candidate-stage-diagnosis.json`保留原始／校正模型大小、NMS前後候選及原kernel在人工框附近的最高分。未把.48降到.479去湊成功，也未猜測可點節點。

`test_s3_scroll_defects.py`先實際RED兩項缺漏，之後明確標記為兩個已知expectedFailure，**不算已通過／已修正**；若將來真的通過會產生unexpectedSuccess，必須重新審閱更新紀錄。source／packet／schema檢查與覆蓋計算在setup或普通測試，只有正確綁定後的缺漏assertion可列known failure。Node測試確認兩張MAP雖可觀察，anchor=false，selectNode仍拋ANCHOR_MISSING。

## 5. 獨立審查與當版回歸

獨立審查範圍a7a05a2..9d1f769：0Critical、1Important、0Minor。Important為expectedFailure掩蓋錯誤來源，已重現「錯SHA仍successful」並以三項普通guard測試RED→GREEN修正；修正commit c9559e1。`independent-review.json`及`review-bad-source-red.json`留存。沒有未處理的審查問題；整體接受仍需下面實際回歸。

單元實測：Node125/125通過（374.706秒）；Python共189項，187通過、2項S3已知缺漏expectedFailure、0非預期失敗（601.735秒）。證據`node-full-01.log`／`python-full-01.log`。

|當版離線回歸|閉環／判分結果|分析影格|證據束／檔案數|最小IoU|
|---|---:|---:|---:|---:|
|已完成39組凍結變換|39/39|1318（raw V1已核准重用；V2全部重算）|876／4380|.906351455|
|原始20段，S1–S4|20/20|1551全部新鮮|1254／6270|.913425769|
|固定75%、100%、125%|15/15|381全部新鮮|273／1365|.991292070|
|30組負例|30/30正確拒絕|57全部新鮮|57／285|不適用|
|負例判分器對照|2/2正確判分|重用當版新鮮正例／灰節點各2張|4／20|不作正例計數|

74是回歸執行數，**不是74張不同地圖**。正例各只發出1次虛擬點擊並完成兩張獨立預覽身份確認；負例0點擊、0錯誤選擇proof、0錯誤預覽確認。負例凍結60張中3組UNKNOWN在首張即安全中止，故實際分析57張，不將缺失的第2張算已推論。eligible-request對照故意能產生合法selection proof，負例grader必須判不合格；gray-request必須正確拒絕，不能把兩者一概「通過負例」。正式負例門檻仍標示未完成，與整體保留集/G4分開。

39組僅重用已核對141外部資產、7個raw依賴與inspect_capture AST相同的raw V1證據，當版V2與交易全部重跑，**不是新鮮效能資料**；`raw-v1-reuse-qualification.json`保留依據。原始20、固定15、30負例皆無raw V1快取。1318張變換、1551張原生、381張固定縮放各自對前版九類語意欄位全部逐值相等（binding/來源影格身份另核對），沒有新增差異；對應`random39-semantic-comparison.json`、`native20-current-01-semantic-comparison.json`、`fixed15-current-01-semantic-comparison.json`。此相等證明未退步，不證明前版所有候選已正確。

`functional-evidence-integrity.json`逐檔核對2403個正例證據束／12015檔、61個負例與對照證據束／305檔，並核對當版code、141外部依賴、來源PNG、來源manifest及replay報告hash；每束皆含input／observation／overlay／events／result。所有正式執行報告保留c9559e14完整commit、runner SHA、code各檔SHA、runtime fingerprint及凍結資料集manifest SHA。沒有原生遊戲操作。

當版原生稽核：1551／1551張來源核對，對原始legacy基線有24張候選差異（與前版稽核數相同），絕對錨點流失0；七張指定畫面均保存當版五項證據／35檔。七張當版的原PNG及九類語意欄位，已逐一與前次實際視覺審閱的packet核對完全一致，`native-audit-current-01/semantic-review.json`綁定前次審閱hash與當版來源／輸出hash，承接先前視覺審閱而非冒稱另做全面像素ground truth。自動audit的`pixelSemanticReviewComplete=false`保留原意；不代表七張後續驗證漏做。兩個局部缺漏仍OPEN。

## 6. 完整成對效能測量

相同原193張、相同順序、single worker、每輪warmup10、無raw V1／跨影格快取，兩輪**各193張全部新鮮推論、各5/5完整閉環通過**。前置125項Node及189項Python已結束，74項功能回歸、負例與重型hash／語意稽核全部結束後，才寫入`functional-audits.complete`，依序執行control→optimized。當版code與依賴相同，只有明示`--disable-frame-reuse`開關不同。兩輪不與其他專案推論／測試並行；未固定CPU親和，也未隔絕Windows系統背景負載；這是一組成對實測，不冒稱多輪統計信賴區間。

|項目（ms）|對照p50|對照p95|優化p50|優化p95|
|---|---:|---:|---:|---:|
|Producer，183暖機後影格|2518.170|3749.654|2159.823|2713.022|
|Node交易路徑，127暖機後因果影格|2.618|5.347|2.543|5.226|
|整體因果CPU，127影格|2405.844|3753.451|2113.624|2743.673|
|aspect_geometry|1280.534|2146.447|877.690|1644.927|
|v1_observation|1132.851|1583.191|969.035|1475.206|
|preview_registration|.016|462.445|.013|441.901|
|preview_controls|8.567|123.012|7.583|98.224|
|decode_binding|31.812|41.772|29.183|38.583|
|preview_identity|9.524|27.384|8.680|26.654|
|map_actions|12.355|16.620|11.439|15.376|
|sparse_geometry|5.323|8.142|4.862|7.615|
|progress|.122|.265|.104|.219|

Producer p95改善27.65%；因果CPU p95改善26.90%。這些分位數不同樣本／模組**不可相加，也不能將各分位數下降直接分配成總體因果貢獻**。前期操作追蹤證明確實少做相同候選掃描；其餘模組的小幅變化仍可能包含執行波動／CPU競爭變化，不宣稱都由快取直接造成。Node只占數毫秒，沒有證據支持改寫Node交易以追求本輪秒級差距。

舊基準因果CPU p95=4292.450ms、producer p95=4370.174ms保留參考，但本次關閉共用的對照也比舊時段快，故**不把4292→2744的全部差額歸因於本次優化**。

同影格命中98次、未命中343次（皆為183張暖機後影格內的候選呼叫）；命中p50/p95=4.198/6.043ms，未命中=382.099/470.053ms。包含來源／像素／配置核對與副本處理，命中不是零成本。兩群輸入不完全相同，不拿兩群分位數相減當每次節省。control完全不掛候選memo hook，所以報告hit=0/miss=0/null代表未記錄hook成本，**不是沒有執行候選推論**。

同影格共用仍標示`freshFullPipeline=true`：每一張來源PNG重新處理、每張首次量測為miss；只有同一張相同像素／尺寸／模板／參數的量測再請求可hit。39組的舊raw V1封包重用則標示false，已排除於此速度測量；絕不混稱兩者。兩輪193張原PNG／frame identity及九類語意欄位逐值一致，證據`paired-performance-semantic-comparison.json`。

最慢producer影格：

- 對照S2影格57943，4400.214ms，最大階段aspect_geometry=2792.647ms；來源video `a2a6efb31d39dddace649a1d4c7b4819f6820eeaf7756c5f08d52fe47eb88ab6`。
- 優化S1影格30117，2998.480ms，v1_observation=1472.446ms、aspect_geometry=1445.791ms；來源video `af0edce98d57e893d0051bb710668ba9a4ee8a5352aa363a8f5b097586cd901a`。兩個階段在同張實際同時偏高，不是相加p95推測。
- 優化S2影格57943仍需2869.521ms，其中aspect_geometry=1897.475ms；較慢階段並未消失。`remaining-bottlenecks.json`保留最慢10張及所有模組分割時間。

版本綁定：Windows-11-10.0.26200-SP0；runtime fingerprint `6de839b9fbfe09baba6f2aeeb41de1ad81c1818e7b6a283b2d4cbefe2bbd5029`；193來源manifest SHA `cd118ade5bb862a2e11225a483d4f95dfadbfe086196e8f87a0fe3eb0e269073`。`paired-control-01/performance.json`與`paired-optimized-01/performance.json`保存每個code／外部依賴／runner hash；`paired-performance-comparison.json`核對上述內容完全相同，僅功能設定不同；`paired-performance-evidence-integrity.json`再核對每輪142束／710檔五項證據與當版code／依賴hash。

## 7. 未達標原因與下一輪有限方案

**G4速度未通過。** 2743.673ms仍超出1500ms約1243.673ms，需再降低約45.33%的當前尾延遲。183張的總wall分割統計（非相加p95）顯示：v1_observation占47.04%，aspect_geometry占42.66%，preview_registration占6.62%；前兩者合計89.71%。候選共用帶來實測收益，保留；拒絕不穩定的threads／workers變更。沒有以放寬門檻、提高TTL、跳影格或沿用過期資料湊成達標。

下一輪按下列順序，**先取得micro實測收益，再改生產路徑**；以下尚未實作，也不保證能達1500ms：

1. **OCR細分到ONNX forward與每個實際ROI／batch。** 已知TextRecognizer 78次／14.8秒inclusive，先記錄各次輸入形狀、批次大小、像素hash、前後處理與session.run各耗時，區分必要獨立ROI、重複請求與padding／dispatch成本。若現有批次邊界產生可證明的重複工作，才嘗試同影格批次合併或共用純量測；保留每個ROI的來源／幾何／文字score核對，不能把兩張獨立預覽合成一次證據。需逐值輸出比較、S3／歷史失敗／完整回歸及193張新鮮基準。先前降低threads已被實測否決，不再盲調。
2. **候選模板掃描的精確演算法micro。** 真正成本是raw／rectified上的大圖matchTemplate與大量小patch分類，不是13ms的比例估計。先按尺寸／模板組統計實際kernel耗時與同像素特徵重算；評估不改score定義／排序的批次化或可證明的搜尋上界裁減，無法證明可排除的區域保留原搜尋。跨不同rectified像素不得直接套raw結果，不能只測快速正例、把新增漏候選當安全拒絕後忽略。模板kernel重複僅0/173或17/204，單純kernel去重沒有足夠證據可彌補45%差距。
3. **preview_registration的同影格純量測介面。** p95仍441.9ms、占總wall6.62%；先追蹤是否與aspect真的重複相同像素／幾何工作，再決定共用。不得把已驗證的身份／anchor權威快取給另一模組；Python各證據來源與JavaScript獨立驗證保持。此項本身不足以填補現有差距，不先全面收斂／重寫Observer。

這三項是有量測依據的調查／試驗範圍，尚無其新性能結果。若要更換OCR／YOLO、全面改寫視覺架構、降低原門檻或實機操作，仍需使用者另行批准。

本次CPU指標只含已量測producer＋Node adapter／selection／transaction／verification，排除capture／IPC／報告I/O；不能冒稱實機端到端。暖機後183張中39張僅producer處理即超過2500ms（180張超過1500ms）；即使尚未加capture／IPC，也無法保證送出年齡要求。此為處理耗時必要下界分析，沒有冒稱量到實機畫面年齡。畫面送出年齡≤2500ms、15秒內明確結果與實際DPI／客戶區點擊尚未實機驗收。即使單次CPU數據達標，也不足以單獨宣稱正式G4完成。

第40–60組與30組保留集變換尚未開始／完成；原凍結分母與困難案例不變。S3／S4目前僅本輪原始尺寸回歸通過，不能以此宣稱所有隨機比例跨來源泛化完成。P5未批准，原生遊戲操作始終為0。

## 8. 執行取捨、審查界限與未完成事項

- 沿用已隔離V2分支與既有忽略資料集；依使用者已批准計畫直接執行小修，不重複要求設計批准。誤判代價是較少額外隔離／人工覆核，透過凍結source與全回歸降低風險；V1與正式遠征流程未改。
- 模板配置指紋變動即拒絕並要求新程序，避免底層legacy LRU持有舊模板；代價是改模板時不支援無縫熱更新。
- 39組只在raw依賴／實際來源一致後重用raw證據；獨立審查要求的完整回歸已實際執行。誤判依賴會造成錯誤相容性判定，因此另有1551＋381＋193＋193全新鮮推論與逐欄位相等核對；raw重用時間不作效能證據。
- 獨立審查不判定尚未跑過的G4／保留集／實機；其風險以實際gate維持，未達就不升級。代價是40–60與最終驗收仍未完成。
- S3兩個人工框由主執行者審閱原PNG並有raw heal IoU .9326佐證，沒有獨立第二次標註覆核；代價是不能宣稱完美ground truth。兩個缺漏保持OPEN。
- 支援受測的process-local proposal注入、模板內容／OpenCV配置變動防護；任意第三方全域hook／kernel替換不是完整支援範圍。代價是這類未受測外掛環境不能保證正確，不能拿本輪回歸概括。
- 本輪不合併、不推送、不發布，保留`codex/v2-minimal-loop`供後續處理；代價是此結果仍是開發分支，不能當已部署版本。

獨立審查0Critical／1Important／0Minor；Important已RED→GREEN並通過當版全套回歸，沒有deferred minor。本輪未完成的產品條件：CPU p95≤1500ms、S3局部候選完整性、其餘21開發變換、30保留集變換、正式負例/G4整體驗收、P5實機驗收。不得將本輪「必要回歸穩定」寫成產品完成或100%辨識。
