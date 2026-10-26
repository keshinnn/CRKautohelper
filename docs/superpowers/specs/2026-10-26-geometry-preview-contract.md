# V2 座標與點後等待契約 v1

本文件實作2026-10-26使用者批准的局部收斂，不變更G0–G5。保留V1資料與輸入後端，停在第39組及必要回歸，不執行實機。

## 座標

|空間|權威尺寸／內容|轉換|
|---|---|---|
|source|capture PNG的實際整數寬高、RGB與PNG hash|本輪離線client與source相同；不包含桌面原點|
|rectified|由當張像素比例量測建立的實際resize尺寸；保持Y不變|source→rectified；X/Y均以實際整數尺寸比計算|
|analysis|模型實際960×H tensor，H獨立量化|rectified→analysis；不能把960/寬同時當Y比例|
|client|原始客戶區物理像素|反向analysis→rectified→source；同尺寸離線source→client為identity|
|screen|client加當次物理原點|沿用Geometry；DPI不可再倍乘，尚待P5真實驗證|

Python `geometry_contract.resize_point/resize_box`與JS `geometry-contract`各自實作並驗證。矩形採半開區間端點投影，寬高由右減左／下減上；保持float64，不在中間四捨五入至.01px。V2自有raster採half-up；沿用V1模型的analysis raster由集中 `analysis_raster` 保留其 `round(height*(960/width))` 的實際ties-even及運算順序。JS獨立重算同一分階段政策，不以±半像素代替實際尺寸。這不是增加容差或改模型。真正裁切與最終輸入各自是明確邊界，不能偷偷量化或clamp。

新 `aspectRectification.coordinateContract` 記錄version=1、四個空間的實際尺寸、source capture ID、PNG／RGB hash與rounding／analysisRounding政策。當前分析manifest／capture邊界帶observerContractVersion=1，由回放載入器放入FrameEnvelope，JS不因packet移除certificate而降級；舊不可變fixture使用無新版本的相容入口。JS獨立重算並以既有1e-9浮點檢查精度核對新契約，沒有提高容差。尺寸、原點、視窗、來源或geometryVersion變更仍使舊proof失效。

歷史 `analysisBox/analysisCenter` 是rectified raster的量測，名稱沿用作相容欄位；不是960 tensor座標。新契約將其空間明訂為rectified。`pixelProposal.injectedAnalysisBox`才是模型analysis空間。新producer只透過集中投影建立這些欄位；completed/heal候選與完成外框修復同樣適用。既有V1 native輸出、不可變舊packet的舊.01規約保留在明確舊路徑，不把舊資料偽裝成新證據。

## 預覽控制、身份與操作權限

`preview_context.py`只從本張原像素驗證區域、普通預覽文字、03:00及綠色Enter控制。抽自原preview_identity邏輯，後者重用結果而不重複OCR。低信心時間標籤只定位裁切，新的原像素OCR仍須達原.75標籤門檻；時間數字仍須.95，沒有把低分直接升高。

|觀察|允許已送出交易等待|允許選點／新操作|可確認預覽身份|
|---|---|---|---|
|完整可驗證MAP|是|仍須兩幀選擇proof|否|
|只有獨立普通預覽控制|是，`PREVIEW_PENDING`|否|否|
|同一節點獨立PREVIEW|進入穩定對判斷|否|兩張相隔≥200ms且幾何一致才可|
|UNKNOWN／無有效控制／錯區域／篡改來源|否，拒絕|否|否|

JS `preview-context.cjs`獨立核對來源、區域、原始OCR列會員關係、衍生timer／時間標籤裁切來源及控制幾何／文字分數後，以private WeakMap授予僅限等待能力。複製／修改觀察不能繼承；待確認狀態沒有selectedNode與map root，不可交Selector取得點擊權限。

PreviewSession驗證原觀察的私有權威，再複製進trace；每張等待影格仍經frame/時間／window驗證，清空先前穩定預覽對，原15秒deadline不重設，不新增點擊。完整身份確認仍沿用原來源配準、格點與選中節點驗證，不能用等待控制替代。57947本張只等待，不借後續圖預測身份；後續幀按原序到達後才可形成預覽證據。

## 回歸版本

`scripts/convergence-regression.py`只跑明確提供的manifest，不自動向後推進。凍結Git commit、工作樹狀態、所有ml/lib/scripts/tests/data關鍵檔hash（含圖片）、外部V1程式／map與flow模板／OCR資產、控制器hash與資料manifest；運行中若檔案改變即判失敗，各分片runtime指紋也須一致。新報告區分fresh推論與已核對runtime的raw V1 cache，所有V2契約／交易均重新執行，不借舊pass結果。當前最終回歸採無cache新鮮分析。
