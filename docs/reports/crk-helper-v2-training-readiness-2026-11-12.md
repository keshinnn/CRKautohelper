# CRK Helper V2 — 2026-11-12 訓練啟動準備與實際准入結果

## 結論

**A1真正的CRK模型訓練尚未啟動，訓練次數仍為0。** 本輪已建立可運行的隔離模型環境、有限訓練入口，並將完整雙覆核標註由7張推進到52張；400張原圖不等於400張合格標註。依原已批准的資料條件，現在仍是DATA_NOT_READY，不消耗唯一的訓練機會。

未修改正式辨識器或Verifier。當版223個正式檔案、141個外部依賴與保留的48/60基準hash一致；未重跑60組，不宣稱新模型改善閉環。G4未完成，P5未執行。

## 實際產出

|項目|本輪實測結果|證據|
|---|---|---|
|隔離環境|Python3.12.14、Ultralytics8.4.189、torch2.15.0+cpu、ONNX1.23.2、ONNX Runtime1.31.1；安裝與載入成功|[environment.json](../../artifacts/candidate-training-20261112-01/environment.json)、[完整鎖定清單](../../artifacts/candidate-training-20261112-01/environment-lock.txt)、[安裝日誌](../../artifacts/candidate-training-20261112-01/install.log)|
|原生硬體讀取|登錄資料可見AMD Radeon RX7700XT及AMD內顯；本環境CUDA=false|這不是已建立AMD GPU訓練支援的證明；本入口固定CPU，不自行更換運算框架|
|官方預訓練模型|從Ultralytics assets v8.4.0下載yolo26n.pt；SHA256 `9b09cc8bf347f0fc8a5f7657480587f25db09b34bf33b0652110fb03a8ad4fef`|[pretrained.json](../../artifacts/candidate-training-20261112-01/pretrained.json)、[下載／匯出日誌](../../artifacts/candidate-training-20261112-01/environment-smoke.log)|
|架構核對|checkpoint的yaml_file=yolo26n.yaml、scale=n、task=detect；載入後end2end=false，如實保留|[model-architecture-check.json](../../artifacts/candidate-training-20261112-01/model-architecture-check.json)|
|ONNX匯出與執行|FP32、640、opset17、batch1，onnx.checker與CPU session成功|[environment-smoke.json](../../artifacts/candidate-training-20261112-01/environment-smoke.json)|
|原始資料|維持原240train／80val／80test，沒有重選或刪除難圖|[raw-corpus-v2.json](../../artifacts/candidate-labeling-20261109-03/raw-corpus-v2.json)|
|完整雙AI覆核|52/400張；21張正例共269框、31張空標註負例；仍未通過整體資料准入|[reviewed-annotations-batch02.json](../../artifacts/candidate-training-20261112-01/reviewed-annotations-batch02.json)|
|新研究單元|68/68，1.391秒；其中訓練入口12項|[all-green.log](../../artifacts/candidate-training-20261112-01/all-green-final.log)|
|真實資料啟動准入|DATA_NOT_READY；未建立training-attempt.json；消耗次數0|[admission-result.json](../../artifacts/candidate-training-20261112-01/admission-result.json)|
|正式程式保護|223正式檔案、141依賴，hash差異均0|[baseline-verification.json](../../artifacts/candidate-training-20261112-01/baseline-verification.json)|

CPU smoke使用全零合成tensor、3次暖機與20次執行，p50=11.745ms、p95=13.100ms。這只證明預訓練模型的執行環境能工作，不包含CRK前處理、候選品質、proof、交易，也不是本專案G4或新鮮CRK影格效能驗收。模型仍是官方預訓練權重，未用CRK資料學習。

## 本輪標註證據與失敗處理

對train前48筆中的46張未完成原圖，各做兩個獨立的完整原圖視覺pass；另外兩張早已在前批完成，不重複計數。新增45張一致覆核，加上原7張為52張。

- 原始第一pass：[primary-train00-23.json](../../artifacts/candidate-training-20261112-01/primary-train00-23.json)、[primary-train24-47.json](../../artifacts/candidate-training-20261112-01/primary-train24-47.json)。
- 原始獨立pass：[independent-train00-23.json](../../artifacts/candidate-training-20261112-01/independent-train00-23.json)、[independent-train24-47.json](../../artifacts/candidate-training-20261112-01/independent-train24-47.json)。
- 分歧前結果：[第一批](../../artifacts/candidate-training-20261112-01/annotation-before-reconciliation.json)、[第二批](../../artifacts/candidate-training-20261112-01/annotation24-before-reconciliation.json)；沒有覆蓋掉原始估計。
- train索引2/3：字幕掩住下緣節點，獨立初稿誤將不可見的y1020區域納入。原圖放大確認可見外框約從y1046開始，修訂保留partial。未重建完整六角形。[有界重查](../../artifacts/candidate-training-20261112-01/independent-train00-23-recheck.json)。
- train35：Tap-to-continue面板邊線跨過節點外框，第一pass的complete改為partial。train46：Hard標籤遮住上框；最底首領徽章使用原圖外側深色實體邊，而非內側藍色切面。[有界重查](../../artifacts/candidate-training-20261112-01/independent-train24-47-recheck.json)。
- train0：嚴重轉場變形，獨立pass無法確認完整性，保持OPEN；沒有當成空白負例、沒有刪出400張分母。
- [來源像素核對後結果](../../artifacts/candidate-training-20261112-01/annotation-after-reconciliation.json)。這些仍是雙AI視覺標註覆核，不是假稱外部人工真值或正式runtime外緣proof。

## 訓練入口與本輪修正

新增研究入口[train_export.py](../../experiments/candidate_poc/train_export.py)與[測試](../../experiments/candidate_poc/test_train_export.py)，沒有匯入正式Verifier或送鍵路徑。

入口檢查固定400原圖清單、source/frame/split/RGB綁定、來源媒體hash、run/layout准入文件、兩份來源綁定標註及完整PNG解碼；不得以任意ready=true、舊模板框或零標註覆蓋未覆核資料。source框保留浮點規則，非法框拒絕，不clamp。test影像／標註不複製到訓練資料夾，訓練yaml只有train和val。

固定單一YOLO26n／seed20261108／640／FP32／最多50epochs；CPU採更嚴格的4小時wall上限，不把CPU時間偽報為GPU時數。正式設定保留原G4期限，這個4小時只限制模型訓練程序。

資料全部檢查成功後才消耗一次專案共用exclusive attempt（更換output目錄不重置預算）；失敗或中斷不自動重跑。子程序需綁定父程序、recipe hash、一次性啟動收據，重新驗證資料與模型；直接--worker及recipe重播不能繞過准入。Windows venv額外launcher只允許同一解譯器且父鏈吻合的一層跳轉。

獨立review發現兩項重要問題，已在單次修正中以RED→GREEN處理：原worker可繞過主入口、原caller可自行指定其他模型與hash。現在鎖定本次官方權重hash並核對實際架構。另測到Ultralytics time模式會覆蓋epochs設定的風險，採固定epochs=50、time=None，加父程序14400秒hard timeout，避免為了時間限制反而擴張epoch數。

RED／GREEN：[初始RED](../../artifacts/candidate-training-20261112-01/train-entry-red.log)、[review RED](../../artifacts/candidate-training-20261112-01/train-review-red.log)、[epoch／launcher RED](../../artifacts/candidate-training-20261112-01/epoch-cap-red.log)、[入口11項GREEN](../../artifacts/candidate-training-20261112-01/train-entry-final-green.log)。68項研究測試不等於合格400張的實際訓練、完整閉環或實機驗收；合格資料happy path尚未實際fit。專案預算亦以[跨output RED](../../artifacts/candidate-training-20261112-01/project-budget-red.log)重現後修正，最終全套68項GREEN。

## 未完成的具體缺口與下一步

1. **348張仍需完整標註覆核／分歧處理**；目前新增覆核全部來自train，不將val/test視為已完成。來源與持續layout的資格文件也未完成，所以完整准入計數仍為0，而不是52。
2. 需逐來源完成run/layout隔離證據；歷史400新圖對2668保護圖的exact重複檢查與一組pHash人工式判讀，不能單獨證明整部影片的地圖獨立性。本輪沒有以舊稽核冒充重新跑過。
3. 把已完成雙覆核與來源資格實證綁定到[training-admission-candidate.json](../../artifacts/candidate-training-20261112-01/training-admission-candidate.json)；目前該檔明確不是合格訓練manifest。其餘素材已在本機，不需要再下載相同四部影片，也不需要用舊保留集補數。
4. 只有完成上述資料門檻，才以已建好的隔離環境消耗一次正式PoC訓練；再依原64張篩選、凍結焦點／成功控制／負例及新test流程評估。一次無改善即停止，不自動換模型重訓。

本輪沒有全面改架構、沒有修改原真值／安全門檻、沒有改善48/60的實測新證據。現況是**訓練環境與受限入口已備妥，資料仍未准入**；不能據此交付「已完成訓練」的模型。

## 版本與依據

基準HEAD仍為`74ad37d85e3aef134d0631e0ce6a799bcb4dbe3d`，branch=`codex/candidate-poc-a0-a2`。未建立新commit；既有作者身分未設定，不代填。研究版本以檔案hash、staged patch和原364檔封存追溯。工作區原有其他修改／報告刪除保持原樣。

Ultralytics API與epoch/time語義依本輪查得的[官方README](https://github.com/ultralytics/ultralytics/blob/main/README.md)、[官方設定](https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/default.yaml)；實際套件版本依環境鎖定檔。上述連結不能替代本機68項測試與實測產物。
