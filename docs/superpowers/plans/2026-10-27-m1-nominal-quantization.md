# M1有限實作與離線驗證計畫

授權：2026-10-27使用者正式批准分析報告第七節。基準功能2aeae97，HEAD a68f745；沿用既有V2專用分支codex/v2-minimal-loop及本機凍結artifact，不建立會遺失忽略資料的新checkout。禁止實機、校準器／raster／Selector／Transaction／Preview修改。

## Task 1：RED、增量補強、聚焦GREEN

- 生產只改`ml/fast_map_candidates.py`；新測試`tests/test_nominal_quantization.py`。
- 先以35935實際model PNG重現2候選，要求新增合格battle／IoU≥.90、完整保留base前綴。35929保持8候選，4候選邊界不觸發；同一Canny只執行一次；掃描kernel由204+至多51構成，沒有第二次255全掃描；不合格／被遮除圖不取得額外權威。
- RED日誌後才加入標準尺度floor/ceil新kernel helper。原base groups、_match_group、分數、倍率、Canny及NMS公式不變，base NMS<4才掃新groups，附加候選不得置換base。
- 量化壓力案例從現有模板metadata推導整數邊界及已批准影格的額外衍生尺寸；另存來源／變換，不更改凍結60/30。
- 聚焦測試及原fast matcher等價測試GREEN；AST graph update；最終整體patch一次獨立審查，Critical/Important僅一輪TDD修正、Minor記錄。

## Task 2：凍結候選版本，第41完整新鮮

- 提交source，綁code/model/runtime/data/runner hash。使用convergence-regression.py、case41原source，NEW run02，不傳cache；266fresh完整分析與回放。
- 若新錯誤候選／嚴重效能退步／需擴大架構，保留全部證據停止；一般回放失敗先分析，不增加單圖規則。

## Task 3：依序當版回歸

第41通過後：prefix40新鮮1583 → native20新鮮1551 → fixed15新鮮381 → negatives30+兩對照 → 完整Node/Python → native1551+seven audit → 額外取整壓力。所有run保持同source；不將舊2ae成績冒充新版本。

## Task 4：效能與證據

獨立artifact量測baseline204、M1未觸發／觸發、新增kernel增量、cache hit/miss；精確同幀重用與新鮮Producer分開，與既有隔離集合比較。不能合計stage p95充整體，G4依舊1500ms／age2500ms／15秒結果。新鮮來源與五檔bundle逐一hash稽核。S3 46047/46057及35929局部缺陷保持OPEN除非另有新獨立證據。

## Task 5：42～60與報告

41及所有必要回歸穩定後按凍結順序42～60；每個失敗保存／分析，遵守stop條件。全60通過才按先前授權處理保留集。報告區分單元、離線閉環與實機，G4不足不宣稱完成。P5始終未批准。

## Interfaces / review focus

matcher仍回傳list[box,center,score,template]；FrameIntermediates依同幀／像素／raster／資產綁定，禁止新增跨來源權威快取。補強前綴順序保留base而非全域重新排序。

五項易漏條件：base數量恰4；低候選圖無新合格kernel；新高分重疊base不可置換；模板尺寸已存在不可重掃；模型像素／來源／資產不同不能混用既有證據。聚焦測試與既有FrameIntermediates／Node負例共同覆蓋。
