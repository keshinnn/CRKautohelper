# 原 CRUMB 網頁（V1 `F:\CRK helper`）的自動通關整合

原網頁不在這個 repo 裡，所以這裡放「新增檔案」＋「對原檔的修改 patch」。套用方式（在 V1 根目錄）：

1. 複製新檔：`lib/bot-runner.cjs`、`web/bot-runner.js`、`web/bot-runner.css`、`tests/bot-runner*.test.cjs`
2. 套用 patch：`git apply bot/console-integration/v1-console.patch`（或 `patch -p1 < …`），修改 `server.cjs`、`web/config.js`、`web/app.js`、`web/index.html`
3. `start.cmd` 重新啟動。

功能
- 總覽頁「自動通關」：開始／繼續、從第一層重新開始、停止、清除失敗鎖定、手動關卡接手區塊與「我已完成這關，交還程式」、最近動作、實機畫面。
- 攻略配置：每層可設「本關由玩家手動遊玩」＋提示（設定格式新增 `manualPlay`、`manualPlayNotes`）。
- 起始 15 隻頁：角色卡片對應（名稱完全相同才自動對應，其餘由使用者指定，存於 `bot/cards/character-map.json`）。
- 伺服器 `/api/bot/*`：把網頁攻略轉成 runner 格式後啟動 `bot/runner.py`；需 `CRK_ENABLE_CONTROL=1`；與辨識頁本機控制互斥。

驗證：`node --test tests/bot-runner.test.cjs tests/bot-runner-ui.test.cjs`（8 項）；原有 V1 node 測試全數通過；2026-11-16 實機從原網頁啟動、手動交接、交還、停止皆已驗證。
