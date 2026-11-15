# Agent / skill 使用紀錄

用途：讓後續 Claude/Codex 知道自動化代理曾使用哪些工作流程；這是專案層級摘要，不包含模型內部推理、私人對話全文或使用者電腦上的 skill 原始檔。

## 可追溯紀錄

- Superpowers 工作流程：`using-superpowers`、`systematic-debugging`、`test-driven-development`、`verification-before-completion`、`requesting-code-review`。相關計畫/結果位於 `docs/superpowers/`、`artifacts/`；該工作流程只記錄於代理工作脈絡，沒有完整獨立稽核日誌可供匯出。
- Serena：用於工作區符號/程式脈絡檢查；本 repo `.serena/` 是本機狀態，不上傳。
- Graphify：依專案規範先查詢程式圖，修改後執行 `graphify update .`。輸出在 `graphify-out/`。
- 研究隔離候選模型及證據契約：執行摘要見 `experiments/candidate_poc/progress.md`；本次使用的研究隔離裂縫證據和兩節點離線回放見 `artifacts/rift-episode-20261113-01/RESULTS.md`。
- 多代理：歷史任務曾使用限定範圍的審查代理；目前無可匯出的完整逐工具紀錄。此文件不虛構各代理呼叫時間或隱藏對話內容。

## 邊界

本文件記錄工具/技能名稱與可查證輸出位置。`C:/Users/...` skill 安裝檔、Serena session、`.superpowers/` 私人狀態與模型思考內容不納入公開 repo。後續若要完整稽核，應在專案內為每次代理工作新增日期、技能名稱、命令和輸出檔案的簡短紀錄。

## 2026-11-16 Claude（Opus 5.5）工作紀錄

| 時間（UTC+8） | 工作 | 使用的工具／技能 | 輸出 |
|---|---|---|---|
| 01:36–02:10 | 讀 V1/V2 程式與紀錄；找出地圖暫停根因（`map-observation.cjs` 強制 `reachable:false`） | 遠端裝置 shell、本機 graphify 圖譜 | `bot/README.md` |
| 01:45–02:40 | MuMu ADB 橋接、執行器（地圖→預覽→進入→換隊→戰鬥→結算） | ADB（MuMu `127.0.0.1:16384`）、V1 辨識模組 | `bot/*.py`；實機：區域1第1層勝利、第2層裂縫轉戰鬥失敗（測試隊 1 隻、無配料） |
| 03:20–03:40 | 寶物裝備改用 V1 `TreasureModel`，OCR 詳情標題核對 | V1 `ml/treasure_model.py` | `bot/treasure.py` |
| 03:41–04:00 | 離線自我檢查；重現 Codex 回放與既有測試 | Windows job agent（`bot/agent.py`） | `bot/selfcheck/REPORT.md` |
| 04:06–04:45 | 對齊 V2 安全契約、保留集影片影子測試、OCR 效能比較 | 本機 graphify 圖譜（`graphify-out/graph.json`）、V2 `bounded_ocr.py` | `bot/selfcheck/test_contracts.py`、`shadow-buAwy1zf2LI/`、`decision_replay_result-win*.json` |

說明：Graphify 雲端工作區目前沒有已啟用的 repo，改查本機 `graphify-out/`。實機截圖、錄影、執行狀態未上傳。推送前於 `2e24683` 建立回溯點 tag `rollback/pre-claude-20261116`。
