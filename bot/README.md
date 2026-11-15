# CRK 冥界試煉執行器（MuMu / ADB）— Claude 2026-11-16

## 為什麼舊版一直暫停
V1 `lib/map-observation.cjs` 把所有地圖節點強制設為 `reachable:false`，`lib/flow.cjs` 只點 `reachable` 節點，
唯一例外 `lib/map-resume.cjs` 只限第 1 層續打。第 2 層以後必定暫停，與模型準確度無關。
V2 改用兩幀節點證明（`lib/node-selector.cjs`），但需要絕對層數錨點、當前位置與連線證據，第 2 層以後常缺。

## 做法：點選後核對，並對齊 V2 的安全契約
- 地圖：攻略指定「層＋欄」→ V1 `map_vision` 的欄／列 → 連續兩次一致觀察才點（`navigator.plan_map_tap`）。
  入口不可見時，用「…第N層進行中」標題＋「進行中」標籤定位當前節點。
- 預覽：OCR 層數＋節點類型（戰鬥／王／裂縫）都符合攻略、連續兩張一致才按 進入／確認。
- 每次點擊前重新擷取，點擊處畫面若已改變就放棄重看（`runner.patch_changed`）。
- 同一層地圖點兩次仍無預覽就暫停；失敗達上限寫入 halt，所有可提交動作都會被擋下。
- 換隊：隊伍設定 → 全部解除 → 用本季 15 張實機卡模板選角（遮掉打勾區），每隻重新找到並確認打勾（`team.py`）。
- 寶物：開寶物格 → V1 `TreasureModel` 在格子中定位 → OCR 詳情標題核對 → 點空格並確認已填入（`treasure.py`）。

## 相依
需要 V1 樹（`ml/`、`data/`、`.venv`）。預設 `F:/CRK helper`，可用環境變數 `CRK_V1_ROOT` 指定。

## 執行
1. 把 `bot/` 放進 V1 根目錄（`F:/CRK helper/bot`），`bot/launchers/*.cmd` 放到 V1 根目錄，雙擊 `start-bot-agent.cmd`（只會執行 `bot/` 內的腳本）。
2. 寫入工作：`bot/jobs/<編號>.json` = `{"script":"runner.py","args":["bot/strategy.json","--steps","500"]}`
3. 停止：建立／更新 `bot/jobs/STOP_RUN`。進度存於 `run-state.json`；逐步截圖與決策在 `runs/<時間>/`。

## 自我檢查（離線，見 `selfcheck/REPORT.md`）
- `selfcheck/test_contracts.py`：安全契約單元測試。
- `selfcheck/map_v2_corpus.py <V2路徑>`：Codex 凍結 60 組地圖案例（保留集）。
- `selfcheck/decision_replay.py`：存檔畫面上的決策重播（需本機 `runs/`、`shots/` 畫面，未上傳）。
- `selfcheck/cards_treasures.py`：角色卡／寶物。
- `selfcheck_suites.py`：Codex 既有 V1/V2 測試＋兩節點回放重現。
- `selfcheck/video_shadow.py`：整段影片逐 N 秒判斷畫面類別（涵蓋率）。

## 限制
- 解析度固定 2560×1440（MuMu）；換隊／寶物／按鈕後備座標依此尺寸。
- `strategy-s8-draft.json` 是測試用轉抄草稿，不是正式攻略。
