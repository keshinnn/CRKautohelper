# V2 座標／預覽收斂驗證紀錄

狀態：進行中。此文件不宣稱G4／G5完成；不執行40–60、保留集或實機。

## 基準與範圍

基準f38af719cfe90b3da59abe74f629e9d0e282c380；實作計畫位於 `../superpowers/plans/2026-10-26-geometry-preview-convergence.md`。新結果保存在 `artifacts/convergence-20261026/`，舊報告／失敗圖未覆寫。

基準Node113/113、Python150/150；本次基準日誌 `baseline-node.log`／`baseline-python.log`。所有閉環均是離線虛擬點擊。

## 第39組根因

57947的原始候選為0。比例量測成功（ratio1.30414724468），校正1574×1191後有9個候選，但無唯一四欄格點；recover_map_aspect保留原始空地圖，配準無節點對，身份未證，adapter的MAP stateVerified=false導致EVIDENCE_UNVERIFIED。不是單純缺少新尺寸根：57931–57944已有直接根。

原程式將控制項驗證放在地圖錨點驗證之後，因此「控制項足夠等待、地圖暫不足確認」的能力無法表達。拆出普通預覽控制時，另確認57947時間標籤舊OCR=.7305低於既有.75門檻；本張原像素裁切重讀=.83113566637，時間數字另以原.95門檻重讀。沒有提升舊分數或降低門檻。

修正引入source-bound PREVIEW_PENDING：只可在既有已送出交易等待，不可選點、確認身份或建立map root。等待清空穩定預覽對，不重設deadline。57947未跳過，後續影格按原序到達後才確認。

聚焦 `case39-analysis-02` 共45張分析（raw V1 cache有明示，V2當前重算）；`case39-replay-02` 通過，29張消費影格、IoU=.93916365618、邊距29.52312021116px、虛擬點擊1、原生0。這不是最終完整回歸。

## 已發現並處理的迴歸

新全精度投影先使完成外框修復的獨立.01取整暴露，Node完整測試118/119；`completed extent refinement keeps model score and independently binds source pixels`失敗。完成producer改走新契約投影後聚焦轉綠。Python完整測試曾有4個相容性錯誤（診斷packet沒有capture frameId、舊timer helper匯入）；保留明確非權威診斷與helper別名後，相關17個比例與3個timer測試轉綠。舊失敗日誌保留。

## 獨立審查與修正清單

首輪範圍f38..7891116；審查未執行模型或遊戲，沒有Critical，四項Important須在最終驗證前修正：

1. V1實際模型尺寸採Python ties-even；新raster half-up不可宣稱為V1的實際analysis尺寸。需集中、分階段明訂量化，JS獨立要求實際尺寸。
2. 等待上下文需核對原始OCR列及timer-label衍生裁切來源，不可只看context內分數。
3. 新契約certificate移除時不可自動降級舊容差；由外部觀察封包版本決定規約。
4. 回歸快照需納外部V1辨識程式、PNG模板及OCR資產，並比較分片runtime指紋。

目前尚未完成全部同版本回歸、1551稽核、原生20、固定15及隔離效能基準；最終結果需另填實測證據，不能引用舊版本通過。
