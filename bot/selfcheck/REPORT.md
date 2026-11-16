# 離線自我檢查報告（2026-11-16 03:55）

範圍：全部離線執行，不連 ADB、不操作遊戲。「模型操作」指 `runner.Runner.decide()`（執行器自身的決策）＋各辨識模組，對存檔畫面自行給出動作，再與真值比對；過程中沒有人工介入。

## 1. Codex 既有自我檢查（Windows 原環境，`selfcheck_suites.py`）
| 項目 | 結果 |
|---|---|
| V1 Node 測試 | 192/192 通過 |
| V1 Python 測試 | 149/149 通過 |
| V2 Node 測試 | 133/133 通過 |
| V2 研究測試（candidate_poc） | 14/14 通過 |
| 交接文件指定的兩節點裂縫回放重現 | `PASS_RESEARCH_TWO_NODE_REPLAY`，result.json 與 run-sealed 完全相同，80 個狀態序列一致（`run-claude-20261116-035150`） |

這些是契約／單元測試與既有錄影回放，不是辨識準確率。

## 2. 地圖選點（保留集：Codex 凍結的 60 組案例，`map_v2_corpus.py`）
真值＝Codex 人工核對的 expectedBox；輸入＝當時保存的 V1 觀察封包；規劃器只拿攻略的「層／欄」。
這 60 組含 4 個來源影片、隨機裁切變形、不同比例，我開發時從未看過。

| 結果 | 數量 |
|---|---|
| 點中正確節點 | **56/60** |
| 點錯節點 | **0** |
| 不決策（安全停下） | 4（案例 49、50、54、59：入口不在畫面且沒有當前位置證據） |

對照：Codex 正式證明流程歷史基準 48/60。

## 3. 決策重播（MuMu 2560×1440，`decision_replay.py`）
38 張本次實機存下的全解析度畫面（26 張非戰鬥＋12 張戰鬥抽樣）。
真值點擊＝當時遊戲實際接受的位置（由下一張畫面驗證）。

- 結果 **38/38**。
- **注意：這是開發集**，執行器規則是看著這些畫面修出來的，數字偏樂觀，不能當泛化能力。
- 自我檢查本身抓到 1 個真錯：地圖捲到入口看不見、V1 沒給出當前位置時會暫停。已改成用「…第N層進行中」標題加「進行中」標籤定位，修正後 60 組保留集結果不變（56/0/4）。
- 另抓到 1 個我自己標錯的真值，已更正。

V1 狀態辨識（`flow_vision`）在 26 張非戰鬥畫面中有 12 張是 UNKNOWN，包括：讀取畫面、BOSS 登場動畫、逾時動畫、「隊伍未滿」確認、季節大廳。這些目前靠執行器補的文字規則處理，或歸類為「等待」。

## 3b. 安全契約（2026-11-16 04:15 補上，對齊 V2 設計）
`selfcheck/test_contracts.py` 8/8 通過：
- 地圖：同一目標需連續兩次一致觀察（位移 ≤6px、間隔 ≤8s）才點；同一層最多點 2 次仍沒有預覽就暫停，不盲目重點。
- 預覽：層數＋節點類型都要和攻略相符（戰鬥／王／裂縫），並且連續兩張預覽一致，才按「進入」或「確認」。
- 新鮮度：每次點擊前重新擷取，點擊位置周圍畫面若和分析時不同（灰階平均差 >12），就放棄這次點擊、重新觀察。實測：同畫面差 0.0，捲動後 50.8，戰鬥動畫 58.2。
- 失敗上限的 halt 狀態會擋住預覽的「進入」。
- 離線重播時第二次觀察是用同一張存檔模擬（結果檔標記 `secondObservationSimulated`），不等於實機的兩次獨立擷取。

## 4. 角色卡（`cards_treasures.py`）
- 真值：遊戲內名單順序固定（依稀有度）。可見卡片必須是名單中連續的一段、間距 280px，並且全部被找到。
- 用來切模板的 2 張圖不計入。其餘 8 張不同時間、不同捲動位置、含已選取打勾的畫面：**8/8 全對**，最低比對分數 0.987。
- V1 原卡片模型（wiki 圖訓練）在同一畫面：0 張通過，例如芒果認成藍莓派。判定為不適用於 MuMu 實機卡片。

## 5. 寶物（V1 `TreasureModel` 原模型）
- 裝備寶物視窗第一頁實際畫面 3 張：12/12、12/12、11/11 支援且名稱正確（11 張那張有一件「裝備中」，正確排除）。
- 秘笈、紅哨、時鐘三件在實機由此模型找到，詳情標題 OCR 也核對相符。
- 未完成：第 2 頁以後沒有保存的整頁畫面。我用單格裁切做的測試無效（捲動後裁切位置偏掉），不計入，也不代表模型錯。

## 6. 尚未涵蓋（沒有資料就不宣稱）
- 補血節點、裂縫的其他事件（恢復活力、加入餅乾、特別獎勵）、區域王、區域過關獎勵、區域 2 以後、深層地圖捲動。
- MuMu 保留集：目前所有 MuMu 畫面都來自今天的開發過程。
- 隊伍設定畫面以外的角色辨識（戰鬥中、待戰畫面角色本體），以及 V1 actor model。

## 判斷：各模型的訓練程度
| 模組 | 程度 |
|---|---|
| V1 地圖節點偵測＋欄位／層數 | 可用，保留集 56/60 且 0 誤點 |
| V1 寶物模型 | 第一頁可用，其餘頁未測 |
| 自建角色模板 | 本季 15 隻可用，換季或換造型要重新擷取 |
| V1 卡片模型（wiki） | 在 MuMu 上不可用 |
| V1 狀態辨識（OCR 語意） | 涵蓋不足，約一半非戰鬥畫面是 UNKNOWN，需要補類別 |

## 下一步（取得 MuMu 保留集）
由使用者手動玩（程式不操作），`record.py` 只錄全解析度畫面；人工標註後再跑本報告的決策重播。

重跑方式：
- 地圖保留集：`python bot/selfcheck/map_v2_corpus.py <V2路徑>`
- 決策重播：`python bot/selfcheck/decision_replay.py bot/selfcheck/decision_truth.json bot/strategy-s8-draft.json`
- 角色／寶物：`python bot/selfcheck/cards_treasures.py`
- 既有測試＋回放：`python bot/selfcheck_suites.py`

## 7. 保留集影片影子測試（2026-11-16 04:40，`video_shadow.py` + `shadow_reclassify.py`）
來源：`buAwy1zf2LI`（季4、中文、1440×1080，與 MuMu 季8 不同版本），每 4 秒 1 張，共 809 張；執行器規則開發時從未看過。

| 類別 | 修正前 | 修正後 |
|---|---|---|
| 節點預覽被當成「地圖」（危險：會在預覽後方規劃點擊） | 29 張 | **0** |
| 待戰畫面（激戰／BOSS 戰鬥）未辨識 | 49 張 UNKNOWN | 辨識為 BATTLE_READY |
| 讀取畫面 | 22 張 UNKNOWN | LOADING（只等待） |
| UNKNOWN 總數 | 199 | 129（剩餘：配料視窗、無字讀取／結算動畫、BOSS 資訊、戰鬥暫停選單） |

變更樣本人工核對 27/27 正確。修正途中回歸抓到 1 個退步（確認視窗壓在預覽上被誤判為預覽），已修並加測試。
注意：此影片的預覽標題 OCR 讀不到層數，執行器在這種情況會暫停（不會按進入）。

## 8. 效能（Windows，38 張決策重播，`bench_ocr.py`）
| OCR 前處理 | 正確 | 觀察 p50 | 觀察 p95 |
|---|---|---|---|
| V1 原始 | 38/38 | 2215 ms | 5394 ms |
| V2 有界 960（採用為預設） | 38/38 | **1344 ms** | 4984 ms |
| V2 有界 736 | 35/38 | 1784 ms | 4983 ms |

p95 尾端來自 V1 對 UNKNOWN 畫面的多尺度模板比對（大廳、讀取畫面約 5 秒），尚未處理。

## 9. 推送前自我審查
- 有改善（量測）：地圖保留集 56/60、0 誤點；保留集影片危險誤判 29→0；UNKNOWN 199→129；觀察 p50 -39%；安全契約 11 項測試。
- 未改善／未達成：p95 延遲幾乎未變；尚未實機驗證新契約；尚未完成任何一整區自動通關。
- 刪除的死碼：寶物單格校準（裁切位置錯誤，結果無效）。未上傳：除錯腳本 `cards.py`、`tmodal.py`、`timeline.py`、實機畫面、錄影、執行狀態。

## 10. 第二輪（2026-11-16 05:00–05:55）：延遲尾端與保留集面板誤判
**延遲根因（cProfile）**：V1 `flow_vision.inspect_frame` 對 UNKNOWN 畫面做 11 個模板 × 多尺度 `matchTemplate`，單張約 3.5 秒，占觀察時間約 80%。
**是否有用**：70 張真實 UNKNOWN／讀取畫面（季4影片＋MuMu）中，模板只在 3 張「失敗」畫面超過 0.9，這 3 張改由文字規則 `result_state()` 判定（「區域Z第F層」或結算時間 `00:51.82` ＋ 勝利／失敗）。
**等價性驗證**：關掉模板後重跑整段保留集影片（v3，809 張），執行器分類與開模板時 **809/809 完全相同**。

| 量測 | 修正前 | 修正後 |
|---|---|---|
| 保留集影片 觀察 p50 / p95 | 1049 / 3004 ms | **722 / 2206 ms** |
| MuMu 38 張 觀察 p50 / p95（Windows，兩次量測） | 2215 / 5394 ms | **783–956 / 2540–3181 ms** |
| MuMu 38 張 決策正確 | 38/38 | 38/38 |

**撤回 V2 有界 OCR 960 預設**：第一輪在 MuMu 38 張上無損，但保留集影片（v2 執行）有 38 張勝利畫面漏讀小字「區域Z第F層」與「離開」。已改回預設關閉（`CRK_OCR_BOUND=960` 可手動開啟）。第一輪報告第 8 節的 960 結論不再適用。

**保留集新發現並修正的危險誤判**（V1 都判為 MAP，執行器會在面板後方規劃地圖點擊）：
| 畫面 | 張數 | 現在的處理 |
|---|---|---|
| 裂縫面板（標題讀不到層數） | 7 | 暫停（無法核對層數） |
| 補血面板「選擇恢復方式」 | 4 | 暫停（尚未自動化） |
| 招募「發現新夥伴」 | 1 | 點「加入」（無選項） |
| 遠征選單「繼續／前往大廳／結束探險」 | 1 | 暫停 |
規則：右側面板一律含「危險度」，地圖本身沒有；有面板就不規劃地圖點擊。目前保留集剩下的 51 張 MAP 抽查 18 張，全是真正的地圖。
契約測試增至 15 項，全部通過；地圖保留集 56/60、0 誤點不變。

## 11. 第二輪自我審查
- 改善（量測）：觀察延遲 p95 約 -27%（影片）／-41%～-53%（MuMu），分類結果完全等價；新增 13 張危險誤判的防護。
- 退步與撤回：960 OCR 在保留集造成勝利畫面漏讀 → 已撤回，並更正第 8 節結論。
- 仍未完成：補血節點與裂縫事件的實際操作、實機驗證新契約、自動通關一整區。

## 12. 補血節點（離線實作，尚未實機）
來源：保留集影片 681–698 秒逐秒畫面。補血面板預設已勾「恢復所有餅乾（所有餅乾 +20）」，面板底部按鈕為「15/15 恢復」。
規則：攻略該步必須是 heal，且地圖上剛點的就是這一層（pending）；畫面若有層數也必須相符；連續兩次觀察一致才點底部「恢復」，之後進到下一步。
契約測試 16 項通過（新增：不在攻略上的補血面板會暫停；符合時兩次觀察後點底部按鈕）。
未驗證：MuMu 季8 的補血面板是否同樣版面、點完後的畫面。

## 13. 模型辨識（2026-11-16 07:00，畫面狀態／地圖／寶物／裂縫）

### 資料集：`selfcheck/screens/`（765 張 MuMu 實機畫面，全部人工逐張核對）
- 513 張今天實戰紀錄＋252 張早上手動錄影（錄影全是冥界以外的王國／選單／登入畫面＝OTHER，用來測「不是冥界就不能亂判」）。
- 標註流程：先用當時 runner 的決策（已被下一張畫面驗證）自動建議，再以縮圖表逐類目視檢查，修正 33 張（`labels_fix.json`）。
- 分割：dev＝區域 1 實戰＋錄影前半；held＝區域 2–3 實戰（060954／061928／063633）＋錄影後半。影像模型只用 dev 訓練。

### 畫面狀態（`screens_eval.py --model`）
| 辨識器 | held 正確 | held 判錯 | held 不判 |
|---|---|---|---|
| V1 flow_state（舊模型） | 170/240＊ | 18 | 52 |
| 文字模型（screen_model.text_class） | 362/365 | 0 | 3 |
| 影像模型（kNN，numpy） | 285/365 | 42 | 38 |
| 融合（文字優先，衝突＝不動作） | 334/365 | 30 | 1 |
＊舊數字是錄影後半加入 held 前的計算。

- V1 舊模型的危險錯誤：恢復面板 6、裂縫面板 6、獎勵提示 7、招募 1 被當成「地圖」（會在面板後面規劃點擊）。新文字模型全部改正。
- 融合的 30 個錯全是「沒見過的非冥界畫面（登入、標題）被影像判成讀取／戰鬥」。所以影像單獨判斷只允許「只等待、不點擊」的三類（戰鬥、BOSS 登場、讀取），而且讀取 60 秒、BOSS 登場 30 秒、戰鬥 240 秒沒變化就暫停。
- 注意：文字規則是在看過全部資料的文字統計後寫的，held 的文字成績偏樂觀；影像模型 held 成績是乾淨的。
- 新增：面板按鈕顏色（綠＝可按、紫＝裂縫結果確認中、灰＝已完成），裂縫「確認結果中」不再暫停，改為等待。

### 地圖選點（`map_live_eval.py`）：今天 30 張實機地圖（區域 1–3，含 BOSS 層）重新辨識＋規劃，**30/30 點中**，0 錯。Codex 60 組保留集不變（56／0／4）。

### 寶物：V1 圖示模型單張正確 14/25。裝備流程新增「讀標題掃描」後備：圖示模型掃完沒找到時，逐一點圖示讀遊戲的寶物標題（遊戲文字＝真值），找到才裝；每次讀到的標題＋圖示存到 `treasures/learned/`，之後可擴充模型。離線流程測試 `test_treasure_equip.py` 通過。

### 裂縫：裂縫轉成恢復節點時，攻略類型「隨機」也允許恢復（之前會暫停）。裂縫的其他結果（激戰、特殊獎勵）尚未在實機遇到，沒有資料可評估。

### 回歸
- `test_contracts.py` 16/16、`test_manual.py` 11/11、`test_treasure_equip.py` 通過。
- `decision_replay.py` 37/38：唯一不同是 023437 失敗畫面，真值是 retryLimit 0 時按「離開」，攻略草稿目前 retryLimit=1，所以按「再一次」，符合設定。

## 14. 實機驗收（2026-11-16 07:15–07:59，新模型＋網頁控制台啟動）
- 從冥界大廳重新入場（入場券 20→19，只扣一次），區域 1–3 共 15 層**全自動通關**，328 步。
- 途中只暫停 1 次：「區域 1 第 2 層裂縫→加入餅乾」結果面板沒有被認得（之前沒見過的畫面）。補上「裂縫結果面板＝該層完成，關閉面板」後重新開始，此後一路到區域 4 才因為沒有攻略資料而停止（預期）。
- 畫面模型在實機上：13 次「V1 認不出、畫面模型判為戰鬥／讀取 → 等待」，原本會累積成暫停；裂縫「確認結果中」1 次改為等待；裂縫→恢復（區域 3 第 2 層）照常恢復。
- 區域 3 BOSS 第一次失敗 → 自動「再一次」（重試上限 1）→ 勝利。
- 每場戰鬥寶物 3 件都有裝上並逐格驗證（共 30 次 verified=True）；寶物讀標題後備沒有被觸發（預設寶物都由圖示模型找到）。
- ADB 卡住自動恢復：程式現在會重開 adb 服務並等裝置上線；但這次 MuMu 內部 adbd 卡死，需重啟模擬器才恢復。

## 15. 全角色辨識（2026-11-16 09:00–）
### Codex 的 180 類卡片模型（`models/cards`，ResNet18＋模板＋SIFT 幾何閘）在 MuMu 隊伍卡片上
資料：27 張 MuMu 隊伍設定畫面、210 張卡片（S8 的 14 位可對應角色；身分由 S8 卡片模板＋實機勾選驗證，再與 wiki 圖目視核對）。`card_codex_eval.py` → `cards_codex_eval.json`。

| 指標 | 結果 |
|---|---|
| top-1 正確 | 115/210（55%） |
| top-5 含正確 | 126/210（60%） |
| 模型自評「可採用」且正確 | 99 |
| **模型自評「可採用」但認錯** | **7**（巴斯克起司→麻辣 6 次、芒果 1 次） |
| 判為未知 | 104 |

結論：Codex 模型是在 wiki 官方圖上訓練（合成擴增 98%），沒有 MuMu 實機準確度；造型（costume）卡與官方圖差異大，且它的接受閘仍會認錯。**不能直接用來自動選角。**

### 新做法：確認過的遊戲內卡片庫＋不認得就停
- `bot/cards/bank.json`：以角色目錄 id（cookie-NNN，與網頁設定相同）為鍵，只收「確認過」的 MuMu 卡片截圖。S8 的 14 位已遷入（氣泡 card12 尚未能對應到目錄角色，保留舊名）。
- 執行時只用卡片庫比對（遮罩模板，≥0.90），並新增**差距規則**：同一位置若有另一位角色分數在 0.10 內就不認。210 張實測：正確者最低 0.956、他人最高 0.805；新規則下 27 張畫面結果與原本完全相同（0 遺失、0 多認）。
- 隊伍設定時遇到卡片庫沒有的角色：程式不猜、停下，並把畫面上不認得的卡片存到 `cards/inbox/`。
- 網頁「遊戲內角色卡片」：列出起始名單哪些已有確認卡片；待確認的新卡片可按「產生辨識建議」（Codex 模型 top-3，僅供參考、不預先選取），由使用者選角色確認後才入庫。
- 測試：`tests/bot-runner*.test.cjs` 9 項通過（含：模型建議不預選、未選角色不能確認、檔名不可跳出 inbox）。

對應（我依 wiki 圖目視判斷，使用者 2026-11-16 確認並更正）：百合＝聖百合（造型）、船長＝艦長、水母＝蕾絲水母、莫札＝默茲瑞拉（造型）、木乃伊＝義大利寬麵、茉莉＝小花茉莉餅乾、**奶油蘇打＝Cream Soda（cookie-092；目錄中文名誤作「氣泡水」）**、**氣泡＝遊戲中的「氣泡水餅乾」，是目錄 180 位之外的新角色** → 放入待確認區，需在網頁新增角色後確認。
注意：目錄（Codex 從 wiki 取得）的中文名可能與台版遊戲不同，身分以使用者確認為準。

## 16. 改進後的角色辨識模型 `bot/card_model2.py`（2026-11-16 09:20–）
問題根源：Codex 模型把 MuMu 卡片當成另一種版面裁切（GPG 版），臉部位置對不上 wiki 圖，再交給 ResNet；在 MuMu 上 top-1 只有 55%。

改法（不需要 torch，沿用 Codex 的 180 位角色、550 張參考圖）：
1. **對齊**：量測 14 張 S8 卡片得出 MuMu 卡片＝wiki 卡圖下移 47 px、比例 1.01；使用者提供的實機卡圖另有對應裁切。
2. **遮罩**：等級字、職業圖示、星星、外框不參與比對；被勾選卡片的綠勾也遮掉。
3. **比對**：逐色頻正規化的遮罩相關（被選取時整張變暗也不影響），加小幅位移搜尋。
4. **幾何檢查**：SIFT＋RANSAC 對勝出角色的參考圖要有 ≥4 個一致特徵點。
5. **判定閘**：分數 ≥0.40、與第二名角色差距 ≥0.06、幾何點 ≥4、卡片未被勾選，任一不符就「不判定」。

| 測試 | 正確 | **認錯** | 不判定 |
|---|---|---|---|
| MuMu 實機 210 張（**不含**卡片庫，模型沒看過這些角色的 MuMu 圖） | 188 | **0** | 22（21 張是被勾選的卡） |
| 只限遠征名單時 | 188 | **0** | 22 |
| 目錄外角色（氣泡水餅乾 6 張） | — | **0** | 6 |
| 開放集壓力測試：550 張參考圖逐一當成「沒看過的造型」查詢 | 134 | **0** | 416 |
| 對照：Codex 原模型（同 210 張） | 115 top-1 | **7** | 104 |

說明：Codex 的 ResNet 嵌入在對齊後的 MuMu 圖上 top-1 只有 21/189，加入後只會降低召回、不會提升安全，所以沒有採用；SIFT 幾何檢查是去除壓力測試中 23 個誤認的關鍵。

使用方式
- 選角優先用已確認的卡片庫（同 §15）；卡片庫沒有的角色才交給 card_model2，且只在判定閘通過時才點選；點選後以「同一張卡、已打勾」再確認。
- 網頁待確認卡片的建議改由 card_model2 提供：通過判定閘時標示「模型判定」，否則說明為何不判定（相似度不足／與其他角色太接近／細節對不上）。
- 回歸：卡片庫比對在 27 張畫面上結果不變（0 遺失、0 多認）；`test_contracts` 16、`test_manual` 11、`test_treasure_equip`、node 9 項全通過。
- 尚未實機驗證「卡片庫沒有、由模型選角」的路徑（目前 S8 角色都已在卡片庫）。

## 17. 全角色＋造型實測（2026-11-16 10:35–11:10）
資料：從王國「餅乾」清單逐一點開每位角色的詳細頁，讀遊戲顯示的名字當真值（`collect_cookies.py`，只讀、不按任何升級/購買）。收到 168 位（擁有 193 位），每位都是**目前套用的造型**；名字對應目錄有 56 筆由我人工核對（`list_truth_fix.json`），2 筆無法確定而排除。卡片版面與隊伍設定不同，另外量測對齊（清單卡＝wiki 卡圖 385 px、下移 8 px）。

| 測試 | 正確 | **認錯** | 不判定 |
|---|---|---|---|
| 清單卡：目錄內角色 152 位（套用中的造型） | 149 | **0** | 3 |
| 　其中靠「造型／活動卡圖」認出 | 91 | | |
| 　其中靠官方卡圖認出 | 39 | | |
| 　其中靠 Codex 收錄的實機卡圖認出（同一畫面來源，偏樂觀） | 19 | | |
| 清單卡：目錄外角色 14 位（BTS、索尼克/塔爾斯、米拉/魯米、佐依、艾法芭、氣泡水餅乾…） | — | **0** | 14 |
| 隊伍設定卡（§16 同一批，改良勾選偵測後） | 192 | **0** | 18（勾選中的卡） |
| 開放集壓力測試 550 張（造型不在庫中） | 161 | **0** | 389 |

本輪修正
- 勾選偵測：原本把綠色系角色（薄荷糖、萊姆）誤當成「打勾」→ 改為只認中央一大塊綠勾；清單卡不做勾選偵測。
- SIFT 不再遮掉所有綠色像素（綠色角色因此沒有特徵點）。
- 一筆「認錯」查證後是我的真值錯：遊戲中的「甜辣醬餅乾」就是 wiki 的 Chili Pepper（同一張圖、30 個幾何點），已更正。

仍無法自動辨認（會停下請使用者確認，不會認錯）
- 目錄沒有的角色：連動角色與最新角色（上表 14 位）；需在網頁「待確認的新卡片」確認一次後加入卡片庫。
- 目錄沒有收錄該造型時：月兔、可可目前的造型 → 不判定；萊姆的相似度很高（0.80）但細節特徵點對不上 → 不判定。
- 沒辦法實測「所有造型」：服裝清單只顯示全身小人像，不是卡片；要逐一套用造型才能拍到卡片（會改動使用者設定，未做）。造型不在庫中的情況已由壓力測試涵蓋（0 認錯）。
- 注意：目錄中文名有多處與台版不同（例：氣泡水＝Cream Soda／遊戲叫奶油蘇打；辣椒＝遊戲的甜辣醬；抄時空＝超時空），身分以 id 為準；可用本次讀到的遊戲名稱建立對照表。

## 18. Taiwan names and 氣泡水餅乾 (2026-11-16)

- User confirmed: 奶油蘇打 = sailor art = cookie-092 (Cream Soda; the catalog's Chinese name 氣泡水 was wrong). 氣泡水餅乾 (EPIC support, veil) is not in Codex's catalog → new id **cookie-184**; S8 card12 confirmed into the bank (alias 氣泡).
- `data/name-overrides-tw.json`: 27 catalog names replaced with in-game names read from each cookie's detail page (typos such as 抄時空/袙夫洛娃/千層蘇, wrong identities 氣泡水/辣椒, other translations such as 巫師→魔法師). 6 names left as they were because the OCR was not clean enough (listed under `unsure`). Codex's `models/cards/model.json` is integrity-hashed and was not edited; `card_model2` applies the table on top. Applied to `runtime/config.json` (console) and `bank.json` (catalogName kept). Backup: `backups/claude-20261116/names-034319/`.
- Re-check after the change: list 149/0 wrong/3 abstain, out-of-catalog 14 abstain; team 192/0/18. S8 strips: cookie-092 and cookie-184 both found 6×, no conflict.

## 19. Live zones 4-6 and the pre-release check (2026-11-16)

Live (S8 strategy from the PDF, started from the CRUMB console): zone 4 (with one user-confirmed strategy fix: 4-5 is slot 3), zone 5 with no intervention, zone 6 floors 1-3 (6-2 team chosen by the user after a tower boss timed out). Fixes found on the way: fixed-lattice map read when V1 cannot see four columns (zone start), boss icon template (>=0.98 present / <=0.69 absent), reward-box notice, heal on any non-boss slot + wait for 已恢復 + stop on a grey (unreachable) heal button, stray heal preview closed (twice at most), 900 px strip steps (a 1600 px swipe hid the 9th of 17 cards), status.json rename retried on Windows, plain-language pause reasons. The "N-th node of the row" reading of route digits was tried and rejected: zones 1-3 live frames prove fixed slots (30/30).

Pre-release check:
- V1 node tests: 202/202 (all 49 files). V1 Python tests on the Windows venv: 34/34 files OK.
- Bot: test_contracts 18/18 (2 new: heal slot on a battle step, reward-box notice; heal-preview contract now "close twice, then pause"), test_manual 11/11, test_treasure_equip PASS — on Linux and on the Windows venv.
- Map planner live frames 30/30. Screen model unchanged (text 362/365 held, 0 wrong; model file hash unchanged).
- Cards: team 192/0 wrong/18, list 149/0/3 (+14 out-of-catalog abstain), stress 161/0. Two recruits seen live (Pavlova, Agar Agar) are not in the bank; card_model2 names them correctly.
- Console config -> runner strategy: 0 errors, default treasures carried to every step without its own.

## 20. Every owned cookie as a reference; cookies outside the catalog; docs (2026-11-16)

- `bot/cards/owned.json` (built by `cards_owned_build.py` from the kingdom cookie-list recording): 165 cookies, 168 list cards in their equipped costume, ids from the in-game name. card_model2 loads them as references (list layout); nothing is trained.
- 14 cookies outside Codex's catalog got ids: cookie-184 氣泡水 (earlier) and cookie-185..197 (BTS ×7, 佐依, 艾法芭, 索尼克, 塔爾斯, 米拉, 魯米; names from the game's detail page, Latin spellings by OCR). Added to `data/name-overrides-tw.json` and the console config. Two former "SKIP" cards resolved where OCR and model agree (星塵 cookie-014, 蘋果糖 cookie-135).
- Cross-layout check (`selfcheck/card_owned_eval.py`, live S8 team cards, bank excluded): Codex only 192 right / 0 wrong / 24 abstain; Codex+owned 199 / 0 / 17; owned list card as the ONLY reference for the S8 cookies 199 / 0 / 17 -> one list card per cookie is enough to find it on the team screen. Stress (Codex refs with the exact costume removed, owned added): 392 right / 0 wrong.
- Future cookies: the inbox can create a character ("新增角色（輸入名稱）"): new cookie-NNN, saved config + name table + bank card. Console `modelIds` = catalog + owned, so those characters no longer block a strategy.
- Docs: Claude Docs "CRK Helper 冥界自動通關 操作說明"; in-page help on the auto-run card and the card page.
- Checks: node 203/203; test_contracts 18/18, test_manual 11/11, treasure PASS (Linux + Windows venv); map 30/30.
