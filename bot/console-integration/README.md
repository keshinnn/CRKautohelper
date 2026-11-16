# 原 CRUMB 網頁（V1 `F:\CRK helper`）的自動通關整合

原網頁不在這個 repo 裡，所以這裡放「新增檔案」＋「對原檔的修改 patch」。套用方式（在 V1 根目錄）：

1. 複製新檔：`lib/bot-runner.cjs`、`web/bot-runner.js`、`web/bot-runner.css`、`tests/bot-runner*.test.cjs`、`data/name-overrides-tw.json`
2. 套用 patch：`git apply bot/console-integration/v1-console.patch`（或 `patch -p1 < …`），修改 `server.cjs`、`web/config.js`、`web/app.js`、`web/index.html`
3. `start.cmd` 重新啟動。

功能
- 總覽頁「自動通關」：開始／繼續、從第一層重新開始、停止、清除失敗鎖定、手動關卡接手區塊與「我已完成這關，交還程式」、最近動作、實機畫面。
- 攻略配置：每層可設「本關由玩家手動遊玩」＋提示（設定格式新增 `manualPlay`、`manualPlayNotes`）。
- 起始 15 隻頁「遊戲內角色卡片」：已確認的卡片庫（`bot/cards/bank.json`，以角色 ID 對應）；組隊時遇到不認得的卡片會存進「待確認的新卡片」，由使用者指定角色後才加入卡片庫；「產生辨識建議」用 `bot/card_model2.py` 給建議（不確定時不判定，不會預選）。
- 角色名稱：`data/name-overrides-tw.json` 把目錄裡錯字／不同譯名改成台版遊戲名稱，並新增目錄沒有的 氣泡水餅乾（cookie-184）；Codex 的 `models/cards/model.json` 有完整性雜湊，不修改。`runtime/config.json` 的角色名稱需同步套用（見 bot/selfcheck/REPORT.md §18）。
- 伺服器 `/api/bot/*`：把網頁攻略轉成 runner 格式後啟動 `bot/runner.py`；需 `CRK_ENABLE_CONTROL=1`；與辨識頁本機控制互斥。

驗證（2026-11-16 r6）：V1 node 測試 203 項、V1 Python 測試 34 個檔案全部通過；組隊卡辨識 199 對／0 錯／17 不判定（Codex 參考圖＋擁有角色清單卡）；地圖選點 30/30。
「待確認的新卡片」可直接新增目錄外的角色（建立 cookie-NNN、寫入攻略設定與 data/name-overrides-tw.json）。
舊驗證（r5）：V1 全部 node 測試 201 項通過；角色辨識 清單 149 對／0 錯／3 不判定、組隊卡 192／0／18、壓力測試 161／0。
舊驗證：`node --test tests/bot-runner.test.cjs tests/bot-runner-ui.test.cjs`（9 項）；原有 V1 node 測試全數通過；2026-11-16 實機從原網頁啟動、手動交接、交還、停止皆已驗證。
