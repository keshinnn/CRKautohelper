# CRK Helper V2 座標與預覽證據收斂 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 統一現有座標投影責任、修復第39組且同版本回歸穩定後停止。
**Architecture:** 沿用Python量測、JavaScript獨立驗證、Selector與單次交易。新增小型有版本的幾何／等待證據契約，遷移相關重複轉換；不改V1，不全面重寫。
**Tech Stack:** Python/Pillow/OpenCV、Node內建test；既有本機venv。
**Spec:** 使用者2026-10-26「下一階段開發與架構收斂指令」及 docs/superpowers/specs/2026-10-24-crk-helper-v2-design.md；背景 docs/reports/crk-helper-v2-progress-review.md。

## Global Constraints

- IoU≥0.90、原安全邊距／分類／連線／身份門檻不變；不clamp、不增加容差。
- 畫面年齡≤2500ms、15秒結果、兩張獨立一致預覽≥200ms、每交易≤1點擊。
- 凍結資料／分母不變，不按影片／影格ID分支，不使用未來影格。
- 本輪只完成第39組與必要回歸即停止，不執行40–60／保留集／實機；其完整驗收責任保留。
- 舊失敗證據不覆寫；每次修改先RED→GREEN，再歷史聚焦與完整既成功回歸。
- 所有新結果綁commit、工作樹hash、runner與資料manifest；隔離基準先建立，功能穩定前不作效能優化。

## Review Focus

1. 非等比高度取整與右／下邊界：端點投影不產生越界。
2. 原生框不得帶rectified欄位；舊幾何／不同PNG證據必拒絕。
3. 可見預覽但地圖候選空缺：最多等待，不可授予點擊或身份。
4. 等待中出現錯區域／未知／不相干面板：仍拒絕；等待不延長deadline。
5. 第39組後續幀必須按序處理，等待會清空先前穩定預覽，不以未來成功修飾中間失敗。

## 根因位置與方案

- 已證實：#8雙重取整、#19原生框混rectified analysisBox、#25端點加法浮誤差；涉及ml/map_aspect.py、lib/observer-adapter.cjs及Python其他投影生產者。
- #39直接失敗鏈：57947原mapReview候選0→aspect恢復未建立→配準無節點對→預覽identity未證→MAP stateVerified=false→交易EVIDENCE_UNVERIFIED。同尺寸直接根57931–44存在，不能歸因完全缺root。需以單幀量測與順序回放確認最底層原因。
- 採用已批准的局部契約收斂。只添單張特殊候選會延續原問題；全面改偵測器／YOLO超出本次且不解決權限契約。

## Task 1：根因重現、契約與聚焦測試

**Files:** docs/superpowers/plans/本文件；artifacts/convergence-20261026/；新增tests/test_geometry_contract.py、tests/geometry-contract.test.cjs及預覽上下文聚焦測試。
**Interfaces:** 定義 source=原始擷取PNG／client本輪同尺寸；rectified=去像素非等比之輸入；analysis=實際模型tensor；不把桌面/DPI當同一空間。source→rectified→analysis，反向走逆序；實際整數resize尺寸權威，浮點box保持半開端點，僅裁切/輸入邊界量化。
- [ ] 保存當前HEAD／hash／舊失敗manifest，baseline Node＋Python全套。
- [ ] 分離57947來源觀察、配準、身份與狀態判斷；保存診斷，列已證實與未知原因。
- [ ] RED：X/Y異倍率、padding/裁切、負原點、右下邊界、明確round-half-up、幾何失效與來源篡改案例。
- [ ] RED：真實57947具有獨立普通預覽控制項時只能等待；無控制／錯zone／偽造來源不得等待或點擊。

## Task 2：最小幾何契約

**Files:** 新ml/geometry_contract.py；擴充lib/geometry.cjs或獨立lib/geometry-contract.cjs；修改ml/map_aspect.py與lib/observer-adapter.cjs必要部分；相關投影producer按調查結果納入。
**Interfaces:** Python resize投影point/box以端點為單位；幾何證據schema版本、sourceSize/rectifiedSize/analysisSize及來源binding。JS自行重算矩陣／端點驗證，不相信producer verified布林。
- [ ] GREEN：集中尺寸量化及點／框投影，移除對應重複取整；舊已保存packet走明確舊契約驗證，不能假裝新契約。
- [ ] 執行#8／19／25歷史反例＋新鮮聚焦回放；被動補丁不能只更新fixtures。
- [ ] 確認既有38組全量回歸，不挪用舊碼結果；綁定版本。
**Acceptance:** 對應焦點／完整單元通過，舊PNG／尺寸／矩陣／越界仍拒絕，G1/G2不降。
**Risk:** 舊schema兼容分支、round策略與peer外框精度影響分類；先局部量測再全量回歸。

## Task 3：預覽控制／身份與等待能力分離

**Files:** ml/preview_identity.py（抽出控制項證據）、必要的新ml/preview_context.py；lib/observer-adapter.cjs、lib/preview-verifier.cjs；必要scripts/回放觀察接線。
**Interfaces:** 從本張原像素取得普通預覽控制上下文（區域、timer、ordinary、綠Enter、來源）；僅形成WAIT_ONLY能力，不授予map anchor／selection／preview identity。既有selected-node身份證據保持原要求。
- [ ] RED→GREEN：按根因選擇最小修正，保持未知拒絕；明確記錄本幀等待原因與能力。
- [ ] 使用#39原45張完整按序推論／回放，不跳57947；兩張獨立預覽確認前不得宣告成功。
- [ ] 驗證等待不更新dispatch／deadline、不保留先前穩定對、不接受錯身份／舊root。
- [ ] Node／Python全套，既有38組新鮮完整回歸及現有正式負例子集。
**Acceptance:** #39一次虛擬點擊、0原生、PREVIEW_CONFIRMED且G2合格；所有負例／來源篡改／逾時拒絕。
**Risk:** 讓不相關綠按鈕成為等待理由；因此共用已有高信心完整文字＋像素控制驗證，JS獨立檢查，不使用raw confidence單獨授權。

## Task 4：同版本回歸、稽核與停止交付

**Files:** 新scripts/版本化回歸控制器（不再只放忽略區）；結果寫artifacts/convergence-20261026/；docs/validation/2026-10-26-convergence-status.md。
**Interfaces:** controller指定不可變source manifest、critical source hashes、runner hashes、Git/worktree版本；輸出每案例完整五類工件、交易、grade；任一失敗保存停止，不掩蓋。
- [ ] 全部原成功38＋39同版本回歸。
- [ ] 原生1551新鮮候選稽核、七張差異逐項語意／後續閉環核對；原生20與固定15閉環同版本全跑。
- [ ] 現有負例完整執行，區分未推論與拒絕；不宣稱G4正式完成。
- [ ] 建立單worker、暖機、分模組與整體p50/p95的可重現基準；不改TTL，不在本輪進行效能優化。
- [ ] 更新Graphify、獨立分支審閱、版本hash與工作樹檢查。
**Acceptance:** 所列回歸全過；有實測而非歷史借用。效能未達標如實列出，不用功能成功宣稱G4/P5。
**Risk:** 計算成本、既有原生資料的潛在新缺陷；若失敗先定位共通原因，不補單圖例外。
**Stop:** #39修復＋座標契約統一＋必要回歸穩定後回報並停止，不自動續40–60。

## 執行紀錄

採既有獨立V2 repo與codex/v2-minimal-loop分支就地執行，保留報告未提交檔，不另複製大型忽略區資料。使用者已明確要求計畫後直接執行、小修改不等批准，覆蓋技能通常的再次計畫批准步驟。功能修改分階段提交；不merge/push，不操作V1／遊戲。Task2與Task3共用來源／幾何綁定，先定契約再接等待權限，最後統一版本全回歸；沒有衝突的輸出規約。

