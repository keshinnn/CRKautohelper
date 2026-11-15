# CRK Helper V2 — Claude 接手摘要

> 先讀本文件，再按「目前基準／限制／下一步」工作。這是精簡入口，不取代程式、測試輸出與原始證據。只引用已存在的證據；遇到未知就標示未知。

## 目標與目前狀態

- 產品目標：自主完成 Cookie Run: Kingdom 冥界遠征。這是長期目標，不代表目前已能全自動。
- 最新可執行成果：一次**同一原始影片、兩節點離線研究回放**，結果 `PASS_RESEARCH_TWO_NODE_REPLAY`。證據：`artifacts/rift-episode-20261113-01/RESULTS.md`、`run-sealed/result.json`、`run-sealed/states.json`。
- 實際計數：2次虛擬節點點擊、2次預覽確認、2次結果確認、2次地圖狀態更新；0次原生電腦操作。
- 重要限制：隊伍、進入關卡、技能與戰鬥操作由錄影提供，未自主產生。僅一個已知來源，辨識只取樣階段影格，沒有驗證整段影片每一影格或跨來源泛化。故不是全自主遠征、正式A3、G4或P5通過。
- 正式歷史基準仍48/60；G4整體暖機p95≤1500ms未達/未確認。研究YOLO26n有一次小規模訓練，但不應把它稱為正式A1模型或正式驗收通過。

## 必讀檔案（由近至遠）

1. `artifacts/rift-episode-20261113-01/RESULTS.md`：最新實際結果、事件時間線、限制、重現命令。
2. `artifacts/rift-episode-20261113-01/verification-final.json`：本次研究程式及證據SHA256、基準比較、Git HEAD。
3. `artifacts/rift-episode-20261113-01/run-sealed/result.json` 與 `states.json`：最終機器結果及逐狀態證據。
4. `experiments/candidate_poc/progress.md`：累積進度與被否決/未完成事項；內容較長，讀最新尾端即可。
5. `README.txt`：既有專案使用說明。Repo沒有根目錄README.md。
6. `artifacts/concentrated-repair-20261103-02/verification.json`：既有223正式程式檔+141依賴檔雜湊基線（本次比較0差異）。

## 架構與研究成果

- 正式辨識/交易在`ml/`、`lib/`。正式Node Selector、Geometry、Click Transaction及Verifier本次未修改。
- 最新裂縫支援是研究隔離擴充：`experiments/candidate_poc/rift-proof.cjs`、`rift-transaction.cjs`、`rift-context.cjs`、`rift-completion.cjs`、`converted_current.py`、`analyze_waiting.py`；`episode-replay.cjs`只在傳入研究資料夾時啟用。
- 根因：原可用性只收橘色battle，紫色rift不會進規劃；rift選取時綠框，轉戰鬥後變黃框並出現進行中標籤/向下三角。新研究契約保留來源、RGB、座標、期限、兩張獨立預覽、單次操作及私有能力；不能產生正式battle proof。
- 測試：`focused-final.log` 14/14；`legacy-core.log` 20/20；`check-rift-sealed.log`正例成功、14負例拒絕。這不是全repo或60案例完整回歸。
- 本次連續來源在manifest標示2514–8130影格（83.8–271.0秒，1440×1080，30fps）；成功actor於269.0秒結束。270.2秒UNKNOWN保留於`second-return-wait-v2.log`，不宣稱整窗100%可辨識。

## 絕對不變的安全/資料規則

- UNKNOWN、來源/身份/幾何不足、過期或互相矛盾證據 → 等待或拒絕；不得猜點、強制送出或靜默略過。
- 不改凍結真值、既有門檻或正式Verifier；不以模型confidence冒充模板分數。
- 不用影格ID特例、未來影格、舊畫面/座標、拼接影片或錄影中的後續選擇來授權當下動作。
- 每個操作需當下新鮮來源及私有一次性能力；預覽身份需兩張獨立一致影格。研究能力不得跨成正式權限。
- P5實機操作未授權。需要修改正式Verifier、降低安全條件、重訓或改正式驗收分母時，先停止並向使用者取得明確批准。
- 保留現有失敗紀錄與凍結資料，不刪除測試來提高通過率。不要宣稱60/60、G4、A3或全自動已完成。

## 建議 Claude 直接接續的工作

1. 從本次`run-sealed`重現一次研究回放（用新的輸出資料夾，證據PNG是write-once）；確認結果、狀態數與證據hash一致。命令見`RESULTS.md`。不要重跑模型訓練或60組完整回歸。
2. 做一個有限的裂縫研究契約獨立驗證：挑現有不同來源/不同UI狀態及負例，檢驗typed-rift來源權威、轉換配準、期限與拒絕路徑。先列樣本清單和預期結果，再執行；若缺資料只報明確缺口，不偽造來源。
3. 研究如何以新的、可獨立驗證的狀態與操作證據補上目前由錄影提供的隊伍/進場/戰鬥階段。維持離線/研究隔離；任何正式Verifier整合與實機操作須另行授權。
4. 每次報告以實際命令、結果檔和證據位置為準。不要再寫大型架構文件；先交付可重現的最小工程結果與阻塞原因。

## 重現最新研究結果

於repo根目錄PowerShell：

```powershell
$env:PYTHONUTF8='1'
$env:TEMP=(Resolve-Path artifacts/rift-episode-20261113-01/tmp).Path
$env:TMP=$env:TEMP
node experiments/candidate_poc/episode-replay.cjs artifacts/rift-episode-20261113-01/episode artifacts/rift-episode-20261113-01/run-claude-NEW artifacts/result-repair-20261113-01 artifacts/rift-episode-20261113-01
```

需要已存在的`F:/CRK helper/.venv/Scripts/python.exe`原生OCR環境及repo現有Node相依。這是離線錄影虛擬時間回放，不操作遊戲或電腦輸入。

## 對 Claude 的工作提示

請遵守本交接文件，先核對最新機器結果及hash，再直接完成一項範圍有限且可驗證的工程工作。除非觸及上述需另行批准事項，不要停下來反覆詢問。回報只區分：已驗證事實、未驗證事項、實際阻塞；附命令與證據路徑。
