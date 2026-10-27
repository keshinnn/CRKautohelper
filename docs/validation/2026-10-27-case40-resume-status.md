# 第40組修復進行狀態（接續High評估）

最新狀態：第40組與當版75項正例回歸、30負例＋兩對照均已通過。第41組另遇候選恢復不足，依使用者界線停止於High評估；參見[第41組交接](2026-10-27-case41-high-handoff.md)。下方保留本輪修復過程，早期「待完成」文字是歷史進度。

本文件接續fb20475的歷史中止報告；不是60組完成或G4驗收。

候選修補只改既有OCR/context模組：季別與倒數原像素重定位／新鮮重讀，共用原行分離門檻；保留同一函式內已合格的行；以既有允許文字格式解析同一季號／完整時間值，真正矛盾拒絕。普通字裁切使用來源綁定的實際rectified X比例，Node獨立驗證矩陣／certificate／裁切公式。未換模型、未改IoU／.90／.95／TTL／deadline／兩預覽200ms／單次點擊，無影格ID分支。沒有重做效能基準，p95仍以舊2743.67ms標示未解決。

第40組先前四輪完整新鮮265張：run01在37consumed拒絕；run02在236consumed拒絕；run03全265後PREVIEW_TIMEOUT；run04在55consumed拒絕。皆1virtualclick、0native、IoU.9375；所有失敗證據保留。run04原因是同一季號4的既有允許拼法被當成衝突；現在以解析後的語意鍵歸組，季4/季5仍拒絕。原始36066單張全管線新鮮確認：MAP.95449，沒有先前重複重讀副作用。這些診斷不計完整case通過。

聚焦TDD：14項context重讀／擦除／衝突等測試，5項普通aspect／來源變更／舊格式測試；語意與legacy相容組28項已通過。Node新普通crop2項+既有pending3項通過，原扭曲selected-preview回歸已通過。未完成新的完整單元／當版40組回歸，不能沿用舊39當新版本通過。

舊無版本標記且沒有certificate的資料，僅保留原scale1普通文字裁切，完全不使用其舊比例資料。正式V2版本1缺失／錯誤certificate仍拒絕。保留原有空白字變體及格點恢復測試斷言，沒有以放寬binding解決。

OCR修補獨立審查3Important已RED->GREEN處理（季號、缺字clock一致性、測試作用域），普通新模組審查0Critical/0Important，1Minor是專門的Node低分legacy無比例證明＋fractional ties-even正例尚未增加；保留為deferred minor，不能冒稱已測盡所有邊界。Node驗證來源一致性，不重新跑OCR，維持既有producer信任邊界。

下一步：候選功能commit凍結後，run05完整265fresh與完整Node/Python；通過才跑當版prefix40／native20／fixed15／negative30+controls，綁code/runner/data/runtime hash。所有必要回歸穩定後才依序41..60；全60通過後保留30。P5未授權、原生操作0、G4未完成。持續ledger .superpowers/sdd/2026-10-27-development-40-60/progress.md。

## 2aeae97 當版完整結果

第40組run05已完整通過：265/265新鮮推論、0 raw cache；PREVIEW_CONFIRMED，1次虛擬點擊、0原生操作，IoU .9375148747、最小邊界距離20.5679px。來源／執行器／180個專案檔案／141個外部依賴與runtime指紋在run-05/report.json綁定。此前四次失敗全部保存，不能稱首次通過。

完整Node第二輪127/127通過；Python第二輪208項＝206通過＋2項已知S3 expectedFailure，未當成208個通過。證據：high-resume-01/node-full-02.log、python-full-02.log。前40組全量當版新鮮回歸已啟動，完成前不宣稱當版40/40。後續原生20、固定15、負例30＋對照及1551張／七張候選核對依序執行；未進入41～60與保留集。效能仍未達標，G4/P5未完成。


當版prefix40-current-01已完整通過40/40；1583/1583FRESH、0rawcache，所有案例PREVIEW_CONFIRMED、各1次virtualclick、0native。這是2aeae97當版全重算，不沿用舊39結果。native20-current-01已開始全量新鮮分析；其餘回歸仍待完成，未進41。


2aeae97當版正例回歸75/75完成：隨機prefix40、原始native20、固定縮放fixed15。全部3515張新鮮推論0rawcache，2651束五檔證據來源及SHA核對通過。native1551稽核24張候選變動、絕對錨點遺失0、七張覆蓋完成；逐張檢視記錄seven-current-pixel-review.json，仍非1551張全像素真值驗收。46047戰鬥與46057治療漏候選OPEN，CURRENTfresh封包Node Selector以ANCHOR_MISSING拒絕、0virtual。負例30與正負對照仍執行中，G4效能未達標／P5未授權。
