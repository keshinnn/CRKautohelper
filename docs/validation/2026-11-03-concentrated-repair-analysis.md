# 集中修復：共因、最小修改與驗收

基準74ad37d，原47PASS／13FAIL與所有失敗證據保留於`artifacts/exploration-20261102-01/`；可復原bundle與214檔備份不動。新工件獨立放在`artifacts/concentrated-repair-20261103-01/`。本文件是階段分析，不是60組新版本通過宣告。

## A 英文完整語義

根因：49標點、50拆字／後續影格整個suffix漏偵測、51計時前置括號／後續區域尾端句點；完整字串閘門正確，但缺少合格原圖重讀。保留語義regex及信心門檻；新`english_context_evidence.py`只把原OCR當定位與數值矛盾約束，限定有效標題下的同一header欄與行順序，從當張原圖重讀完整標籤。suffix缺失時使用同幀title/timer界定欄寬，不能拼文字授權。輸出含原locator、實際讀值、score、crop、完整RGB像素SHA與尺寸；無前一幀資料。

RED：`english-red-valid.log`原三張失敗；全段49～51另暴露50/2206與51/2236，保存原失敗後補`english-missing-suffix-red.log`兩個失敗，完成共通欄寬重測後8項通過。17項English相關測試通過。原完整聚焦第一次49分析82張完成但ANCHOR_MISSING，50／51另遇UNKNOWN；沒有冒稱三組閉環已修好。原結果見`english-focus.json`。後續必須以修改後全段新鮮回歸確認。

驗收：原未知boundary的完整語義成立、原文不變、刪除／換圖／矛盾／off-header拒絕；完整閉環結果另列。風險：局部完整標籤的新辨識可能揭露下游候選或current證據缺口，不能當作新誤點或偷偷繞過。

## B 預覽context與身份鏈

已確認共因：舊難度crop的右界`width-labelHeight`會切掉Normal尾端，52／55／57新鮮讀值只剩Norma／Norm；53計時讀成00:0，55讀成00:80@且Enter原score僅0.9019。原.95閘門不可直接放寬。

最小修正：保留已合格舊crop作incumbent；失敗才讀到當張source右界的完整同一文字行，仍要求完整`*{0,2}Normal`及.95。計時可由唯一.95 Time Limit定位右側原圖重偵測，必須重新讀到完整03:00及.95，不能由錯字推算；清楚矛盾clock拒絕。弱Enter只定位crop，再以完整原字與.95重新認證。新增來源、crop、原始讀值與投影證據，由`lib/preview-context.cjs`獨立檢查來源綁定／幾何／唯一標籤。權限仍僅WAIT，不能SELECT或CONFIRM。

RED `preview-line-red.log`4個實際boundary失敗；`preview-independent-red.log`新crop被獨立驗證拒絕；修改後5個實際context均成立，Python3項（含12個擦除子情況）及Node3項新合約通過；包含來源SHA／crop篡改與重複弱標籤拒絕。預覽與pending相關Node共6項通過。新鮮13張boundary分析未跳UNKNOWN：55、57有實際identity成立；52、53、56仍缺幾何／配準，48仍拒絕。**不是完整閉環通過**。

相關但未採用的假設：English普通panel scope目前有中文限制，但`panel-scope-probe.json`隔離實驗即使提供scope仍不能使52／53／56形成有效地圖；所以沒有為此加無效新分支。不能因修完context就宣稱registration、identity完整。

## C 初始診斷（下列C1／C2補證之前）

- 54：原圖入口可見，5候選但無exit。比例calibration存在（ratio1.29524），獨立cyan gate原圖證據實驗未通過；不是把有calibration就當有入口。`gate-boundary-probe.json`排除了「只被orange前置檢查阻擋」的假設。
- 58／59：只有1／0候選，`estimate_pixel_aspect`不能形成合格比例證據；入口與節點肉眼可見不等於已取得三個一致的受驗證參考。不能拿前一幀比例、真值變換或增加容差補上。
- 60：6候選、4列、可見入口成立；完成勾號checkMaskIoU=0.5441176471，低於既有0.80，兩色階補證也不成立，無唯一完成路徑權威；維持CURRENT_POSITION_UNPROVEN。不是簡單沒偵測到節點。
- 48：尺寸變更後calibration=None且候選0；即使可見遊戲，當幀無地圖證據。後續34張identity成立不能反向救援。
- 55～57：點前source-orange ellipse refinement產生外框IoU .88231／.88717／.88844。原始detector框回退的icon試算也未通過既有.90/.08，不能只為GT較接近就採用。模板圓範圍換用fitEllipse也不能直接解釋／消除偏差；不新增任意縮框係數，不改真值。

這些問題不會靠context修正自動消失。根因已定位到候選／比例證據不足、完成形狀證據不足與外框測量三個不同邊界；更底層像素與特徵方案尚未充分驗證。此類本輪不加入未證實的演算法或特殊條件，保留OPEN，在統一回歸中照實計失敗。後續需要獨立可驗證的原圖形狀／範圍證據設計，而非放寬三peer、IoU或完成門檻；若方案超出局部修正再提交批准。

## 驗證順序與剩餘工作

### C1 完成勾號：同一半徑內補齊格點，隔離幾何路由

後續實測證實60不需要降低.80：舊中性覆蓋補證只掃[-2,0,2]，漏掉半徑2內的奇數格點。(-1,+1)同圖／同check模板，saturation80／60的IoU=.83125／.824242，兩個都合格。`completed-grid-red.log`兩個實際失敗→GREEN；空白、超半徑、重複色階及弱證據拒絕。

保留舊9點任何合格incumbent；只在失敗後查另外16個整數位置，半徑／兩色階.80不變，JS獨立核對。歷史10項聚焦曾抓到補強提早通過而略過必要completedRefinement；隔離換回凍結checker即恢復，確認是呼叫邊界。現geometry／candidate使用舊grid，僅最終action proof啟用完整grid。`completed-grid-phase-green.log`4項、`gate-family-historical-green-02.log`10項及`completed-grid-independent-green-02.log`2項通過。C60完整44張曾由CURRENT_POSITION_UNPROVEN推進到一次正確點擊（IoU .959748），但PREVIEW_TIMEOUT，仍不算完整通過。

### C2 現有入口模板家族

`_gate_pixel_geometry`原只讀node-exit.png，未變動catalog早已有node-b-exit.png。58實際primary=.880536，secondary=.905436；59 secondary=.898875仍拒絕。僅primary不合格後嘗試secondary，保留合格舊結果、RGB公式、.90與全部bounds／ellipse／三peer條件；來源、模板hash與尺寸仍獨立驗證，不改比例公式／共識規則。`gate-family-red.log`兩失敗→`gate-family-green.log`3通過；58樣本恢復三peer，59仍拒絕。

中間58～60 group分析133張新鮮，Node在58 ANCHOR_MISSING即止，只評了58；不能把59／60算已閉環。最終改為各例獨立新回歸。48更精確的診斷是兩組歧異的5-peer共識，並非單純少peer；既有icon補證只有1個合格，不能任選一組（`aspect-return-traces.json`、`ambiguous-aspect-icon-probe.json`），未增加猜測式選組。54入口未進入合格cyan候選；58有校準不等於baseline geometry已成立；55～57外框繼續OPEN。

C1／C2複審沒有P1/P2。最終新工件用`artifacts/concentrated-repair-20261103-02/`，與先前220檔版本和16組成功紀錄分開。先跑完整單元，再優先原13失敗以加快回饋，所有60仍以同一最終source hash、原分母／真值計算。

各邊界的實際PNG、原封包、診斷、RED／GREEN已保存。接著凍結本輪修改後完整source/test hash與執行環境，統一執行60、native20、fixed15、開發負例／評分器及完整單元。逐例失敗獨立保留，不跳UNKNOWN或強制點擊。基準HEAD搭配dirty source hash識別當版，絕不冒稱74ad37d未修改。

G4仍OPEN；4033ms是歷史基準而非新版本速度；未啟動效能重構、保留集或P5。若統一回歸發現新誤接受，保留錯誤並先修復該共通回歸，不以增加成功數掩蓋。

## 獨立審查修正

新timer補證最初只選出03:00後計數，會漏掉同次新鮮重讀的合格02:00。審查以原53畫面＋stub重現，Python與JS均有RED記錄；修正為先檢查**全部合格新讀時鐘**且必須唯一，再確認03:00，保留完整讀值供JS獨立拒絕矛盾。`timer-conflict-green.log`與`timer-independent-conflict-green.log`通過，五個實際context仍成立。獨立複審確認此finding closed，未再發現P1/P2。

當時完整Python256單元已在執行，未中斷它；新增RED檔使外層source-freeze在單元安全完成後停止，未啟動後續大回歸。該次256/256歷史紀錄及預期CODE_OR_DATA_CHANGED_DURING_REGRESSION停止封存於`review-stop-before-conflict-01/`，不是新最終版回歸。最終版新增負例後必須重新跑完整單元與大回歸，不沿用舊成功。版本使用base HEAD＋220檔source/test/data雜湊識別（dirty source），未聲稱等同未修改74ad37d。

## 最終回歸進行中：子階段不可當閉環

最終版使用`concentrated-repair-20261103-02`與223檔source/test/data hash；Python264、Node133完整單元exit0。完整回歸尚在執行時不填入最終60組成功數。

實際全段51已通過，IoU=.930488；49／50完成82／83張新鮮分析，英文UNKNOWN消除，但ANCHOR_MISSING，仍FAIL。55預覽交易已PREVIEW_CONFIRMED，IoU=.882310仍不達標；56 PREVIEW_TIMEOUT且IoU=.887166，兩項缺陷分開追蹤。

中文header補證的診斷`-02/complete-header-diagnostic.log`沒有改變任何實際封包（changed=[]），重放仍EVIDENCE_UNVERIFIED。這只是未全新推論的隔離診斷，不列入60組，也未因此修改中文辨識或交易流程。不能把單獨裁切OCR讀值較好推論為完整語義／交易已改善。

後續報告會直接統計原13組當版全部封包的flow／context／identity原始輸出，與JS交易終止分開列示。即使較晚封包identity成立，也不能反向授權交易已拒絕的較早影格。
