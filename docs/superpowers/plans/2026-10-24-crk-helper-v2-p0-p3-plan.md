# CRK Helper V2 P0–P3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. 使用者已要求核對計畫後直接進入 P0–P3，無需再次詢問是否開始；P5 必須另行批准。

**Goal:** 建立獨立、可離線測試的地圖→唯一節點→一次虛擬點擊→同一節點預覽確認核心，不接入 V1 正式自動遠征。

**Architecture:** 在獨立 V2 目錄實作純 Node.js 座標、證據選擇及交易狀態機；Python 只讀重用既有影像辨識模組。時鐘、畫面與輸入皆可注入；預設只有虛擬輸入，不建立實機呼叫入口。

**Tech Stack:** 現有 Node.js 內建 node:test、Python／Pillow／OpenCV 既有環境；不安裝新依賴、不訓練模型。

**Spec:** [已修訂設計](C:/Users/User/Documents/Codex/2026-10-24-crk-helper-v2-design.md)

## Global Constraints

- V1 `F:/CRK helper` 的正式流程、設定、模型與輸入後端不變；以hash前後對照驗證。
- Git工作樹存取目前回報權限錯誤；獨立開發位置 `C:/Users/User/Documents/Codex/CRK-Helper-V2`，不對V1 master寫入；此位置是新增獨立套件，不冒充已合併到正式專案。
- P0–P5與G0–G5最終標準保留。P4-A=5段原始解析度；P4-B=同5段×75/100/125%=15序列；P4-C=30段、20/10分組、每張3次隨機變換及正式負例。A/B通過不得顯示G4通過。
- 每里程碑存原始／錯誤畫面、辨識輸出、座標疊圖、狀態事件與結果。尚未實際辨識的候選不得標註通過。
- 最小閉環只普通戰鬥節點；不按進入、不戰鬥、不施放技能、不自動遠征。P5仍禁止。
- 新鮮度2500ms、預覽deadline15000ms、雙幀間隔至少200ms；座標誤差及最終驗收門檻照設計。
- 真正UNKNOWN立即停止案例；明確可辨識轉場／等待只讀後續幀；送出不確定絕不重點。
- 第一輪原始像素不變；第二輪才固定等比例縮放；第三輪才隨機比例、裁切與正式影像負例。P1–P3錯誤契約單元測試不受此排序限制。

## Review Focus

1. 點擊後resize不應使用舊點位或重點，也不能僅因幾何版本不同就丟失交易身份（T4）。
2. 兩個同層戰鬥節點不能僅靠相同樓層標題誤認成同一預覽（T4）。
3. 影片兩張相同PTS、舊frameId或錯誤hash不能充當兩張獨立證據（T1、T3、T5）。
4. 負桌面原點與非整數縮放高度不能造成多乘DPI或clamp掩蓋越界（T2）。
5. 任一中間里程碑不得寫出G4正式通過；缺少任一失敗工件不能算完整結果（T1、T5）。

## 固定資料介面

所有可變資料進入核心時複製，輸出不可由呼叫者修改後改變交易。時間為注入單調時鐘的ms，不混用來源影片PTS或Date.now。

- `Frame`: `{id,sha256,atMs,windowKey,geometryVersion,width,height,origin:[x,y]}`；PNG由觀察adapter綁定，SHA為64位hex。`windowKey`包含視窗與process身份；跨視窗必拒。
- `MapObservation`: `{frame,state:'MAP',verified,zone,anchorVerified,nodes,edges,current}`。node=`{id,floor,column,type,box:[x,y,w,h],score,completed}`，box在客戶區。edge=`{from,to,pixelSupport}`。current=`{nodeId,verified,inProgress}`或null。`anchorVerified`由影像定位證據導出，不接受測試人工框注入。
- `Intent`: `{zone,floor,column,event:'battle',mode:'select'|'resume'}`，來自獨立攻略測試輸入。
- `SelectionProof`: `{kind:'node-selection',frame,previousFrameId,intent,nodeId,box,point,connection}`，只由T3建立。
- `PreviewObservation`: `{frame,state:'PREVIEW'|'TRANSITION'|'MAP'|'UNKNOWN',verified,zone,floor,event,selectedNode:{verified,zone,floor,column},controlsVerified}`。selectedNode證據必須從後續畫面獨立產生，不能從pending補上。缺失就不能確認。
- `Receipt`: `{status:'sent'|'not_sent'|'uncertain',transactionId,frameId}`；送出成功只保留交易，不算預覽成功。

## T1 / P0：基準凍結與里程碑結果契約

**Files:** 新增 `lib/evidence.cjs`、`tests/evidence.test.cjs`、`scripts/freeze-baseline.cjs`；生成 `artifacts/baseline.json`、`artifacts/video-candidates.json`。路徑皆在獨立V2根目錄下。

**Interfaces:** `snapshotFiles(root,relativePaths)->{files:[{path,sha256}]}`；`compareSnapshot(root,snapshot)->{unchanged,changed,missing}`；`milestoneResult(stage,cases)->{stage,passed,g4Complete:false,...}`（只有未來正式G4總評器可判G4，不讓本函式宣稱正式驗收）。

- [ ] 寫測試：建立臨時真實檔案，變更一個位元後compareSnapshot必回報changed；缺檔回報missing；`../`與絕對路徑拒絕。
- [ ] 執行 `node --test tests/evidence.test.cjs`，應因缺少所述功能而失敗，保存RED輸出。
- [ ] 實作檔案雜湊、前後比對與中間里程碑結果，不接遊戲。
- [ ] 寫／跑測試：5個A案例或15個B案例全過仍`g4Complete:false`；缺少`input,observation,overlay,events,result`任一工件，整份中間結果不完整。
- [ ] 跑完整V2測試套件，保存GREEN。凍結V1的lib/ml/web/scripts、server與辨識metadata／參考圖，排除runtime個資與大影片切片；影片以現有manifest的來源hash記錄。
- [ ] 生成五段原始影片候選區間：84–104、410–430、475–495、535–555、895–915秒；標記`reviewed:false`，是P4-A待核對候選，並非完成標註或通過。保存目前真實失敗PNG及packet的來源與hash清單。
- [ ] Ledger記錄測試命令、結果、資料缺口與選擇；V1原始測試若因寫入權限不能跑，明列不能稱其已通過。

## T2 / P1：統一可逆座標

**Files:** 新增 `lib/geometry.cjs`、`tests/geometry.test.cjs`。

**Interfaces:** `createGeometry({frame,contentRect,analysisSize,padding})->Geometry`；`analysisToClient(point,g)`、`clientToAnalysis(point,g)`、`clientToScreen(point,g)`。實際分析尺寸包含補邊，sx=(analysisWidth-left-right)/contentWidth，sy獨立計算。

- [ ] 寫獨立算好的字面值案例：content=[100,50,1000,500]，analysis=[520,270]，padding=[10,10,10,10]，analysis(260,135)必回client(600,300)；origin(-1920,200)必回screen(-1320,500)。DPI不得再次相乘。
- [ ] 跑 `node --test tests/geometry.test.cjs` 驗證RED，再實作最小轉換。
- [ ] 新增2275×981→960×414的非整數高案例；分析(480,207)還原為(1137.5,490.5)，取整只在輸入邊界。
- [ ] 寫越界、NaN、零尺寸、內容框越界、舊geometryVersion測試；不可將錯點clamp進框。測點與四角的往返每軸≤0.5px。
- [ ] 執行完整V2測試並記錄GREEN；此處不做正式影片縮放里程碑。

## T3 / P2：兩幀地圖到唯一節點證明

**Files:** 新增 `lib/node-selector.cjs`、`tests/node-selector.test.cjs`、`tests/fixtures.cjs`。

**Interfaces:** `selectNode(previous,current,intent,{nowMs})->SelectionProof`；不可選擇時丟出帶`code`的明確錯誤。`validateProof(proof)`核對來源與不可偽造的發行身份；將影像候選與可操作證明分開。

- [ ] 寫select正例：第一層指定第4欄，兩幀差200ms，有可見exit→node邊且support≥.85；同時存在其他節點仍只選意圖欄位。字面值框[400,200,100,100]落點應為[450,250]。
- [ ] RED後實作唯一意圖匹配、兩幀穩定度、邊證據及安全落點。
- [ ] 寫resume正例：第2層指定欄位有當張verified current/inProgress，不得硬寫floor=1；不將普通未到達節點當resume。
- [ ] 逐個拒絕：重複frameId、未滿200ms、過期／未來時間、不同視窗或前點幾何、缺錨點、錯區域、重複欄位、多解、缺連線、低support、目標框越界、兩幀節點移動。
- [ ] 更高層select必須有已核對前置位置；V1僅有綠勾候選而無verified完成證據時拒絕，不偷升權限。
- [ ] 完整套件GREEN並在ledger記錄；不修改V1的reachable欄位或map-resume特殊分支。

## T4 / P3：單次交易與獨立預覽確認

**Files:** 新增 `lib/preview-verifier.cjs`、`lib/preview-session.cjs`、`tests/preview-session.test.cjs`。

**Interfaces:** `verifyPreview(proof,observation)->{kind:'match'|'wait'|'reject',code?}`；`new PreviewSession({clock,dispatch,trace})`；`await session.start(proof)`；`session.observe(observation)`；`session.snapshot()`。dispatch是注入的虛擬後端，無預設本機輸入。

- [ ] 先寫正常閉環測試：真實selector產生proof，虛擬後端回sent，先TRANSITION再兩張預覽（間隔200ms）；最後PREVIEW_CONFIRMED，發送次數恰為1且沒有enter。
- [ ] 驗證RED後實作，輸入前保留交易與來源；前點畫面過期則零輸入；not_sent與uncertain各保留不同結果，皆不重點。
- [ ] 寫同層錯欄位、錯樓層、缺selectedNode、控制項不完整、UNKNOWN、舊幀、重複PTS／ID、倒序時間、視窗身份變更測試；不能將pending nodeId抄成後續辨識結果。
- [ ] 寫點後resize：新幾何版本與重新定位的同一語意selectedNode可成功；舊點位不再使用、不得二次送出。
- [ ] 14999ms仍可等待、15000ms逾時，且snapshot／observe重入不重點；兩張預覽不同身份不能湊成穩定確認。成功後任何後續observe不得輸出新操作。
- [ ] 完整V2套件GREEN；結束在預覽，不建立正式自動遠征接線。

## T5 / P3：只讀辨識adapter、trace與核心整合

**Files:** 新增 `ml/observe.py`、`lib/observer-adapter.cjs`、`lib/artifact-writer.cjs`、`tests/observer-adapter.test.cjs`、`tests/artifact-writer.test.cjs`；新增唯讀診斷CLI `scripts/observe-image.cjs`。

**Interfaces:** Python以既有`.venv/Scripts/python.exe`呼叫V1 `inspect_capture`，輸入必為PNG且按真實bytes產生binding；Node `adaptMap(frame,packet)`與`adaptPreview(frame,packet)`回傳固定契約。缺少獨立selected-node像素證明則`verified:false`，不能補成已確認。`writeCaseArtifacts(directory,{png,observation,overlays,events,result})`保存五類資料與PNG座標疊圖。

- [ ] 寫adapter測試：真實留存packet配實際PNG來源，binding mismatch拒絕；來源框錯空間拒絕；沒有預覽selectedNode證據不能成功。觀察adapter不得呼叫capture_window／execute_action。
- [ ] 寫artifact測試：臨時目錄實際生成PNG疊圖（可用既有Python/Pillow）；五類工件均存在且有hash；缺任一不完整，不准覆寫舊run。
- [ ] RED後實作薄adapter與工件寫入；明確保留V1尚未能提供的證據缺口，P4-A必須以真實畫面驗證和補足，不能以契約單元測試冒充5段通過。
- [ ] 跑既有真實PNG的只讀診斷與V2完整測試；檢查輸入來源hash與baseline未變。此診斷不是影片閉環驗收，不顯示G4完成。
- [ ] 記錄實際執行的測試數、失敗／待驗證的分項，執行一輪獨立程式審閱；重要缺陷以RED→GREEN修正，再跑完整套件。

## 技術衝突核對與執行紀錄

- P4三輪是累積的調試階梯；100%固定縮放沿用原始像素時保留原圖bytes，不無意重新編碼。不同長寬比與裁切只於正式第三輪測。
- P0僅建立5段候選而非宣稱五段真值已核對；完整人工標註及影像閉環在P4-A入口補齊。若區間選不到真實完整互動，換成其他原始區間並留選擇紀錄，不偽造。
- P0–P3的程式完成證據是契約與核心整合測試；P4影像與模型的實際表現仍可能暴露adapter證據缺口，必須修復後再過該里程碑。
- V1工作樹權限／無法提交時使用本目錄progress.md與RED/GREEN log保存紀錄，不捏造commit，也不為通過測試更改正式V1檔案。
- 初次執行採本執行緒逐項實作；只在最後做一次獨立程式審閱，不用多代理同時修改共用狀態。

### 驗證命令與結果名稱

獨立目錄執行 `node --test tests/*.test.cjs`；成功為0失敗、非0退出即未完成。每個任務單獨保留RED與GREEN輸出，完整套件作為任務出口，不以單一測試取代。

本次結束的狀態須分別列出：設計修訂、P0–P3程式／測試進度、P4-A/P4-B/P4-C未執行或實際結果、G4正式未通過、P5未批准。
