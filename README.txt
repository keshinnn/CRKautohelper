CRK Helper V2 — 獨立離線核心
2026-10-24

位置：C:\Users\User\Documents\Codex\CRK-Helper-V2
V1來源：F:\CRK helper（只讀；本套件未接入正式自動遠征）

這份套件做什麼
地圖證據 → 唯一節點證明 → 一次虛擬點擊 → 獨立預覽身份確認。
沒有啟動遊戲、實機輸入或「進入」按鈕入口。
核心測試通過不等於真實影片或實機驗收通過。

驗證核心
在上述V2目錄執行：
node --test tests/*.test.cjs

測試預設讀取既有V1圖片與Python環境；來源改位置時先設定環境變數：
CRK_V1_ROOT = V1根目錄
CRK_PYTHON = 已安裝Pillow的Python完整路徑
未設定CRK_PYTHON時，疊圖工具沿用 F:\CRK helper\.venv\Scripts\python.exe。
不需要安裝新的套件。

單張原始PNG診斷
node scripts/observe-image.cjs "圖片完整路徑.png" "新的輸出目錄"
只讀使用既有本機辨識模組，結果永遠不是P4通過證據。
輸出目錄必須不存在，避免覆蓋舊證據。

已保存序列的只讀診斷
node scripts/replay-saved.cjs "序列manifest.json" "新的輸出目錄"
manifest格式：
{
  "intent":{"zone":1,"floor":1,"column":4,"event":"battle","mode":"resume"},
  "gate":{"windowMs":[1000,1100],"clientBox":[400,200,100,100],"previewFromPtsMs":1200},
  "frames":[
    {"image":"原始PNG完整路徑","packet":"同一PNG的辨識JSON完整路徑",
     "atMs":800,"sourcePtsMs":800,"geometryVersion":"original"}
  ]
}
frames必須按時間排列，使用實際綁定的PNG與packet。每幀包含嚴格遞增的影片PTS；
至少兩張穩定地圖及兩張獨立預覽才能成功。gate是人工標註的操作窗口與可點擊區，
只傳給虛擬dispatcher，不傳給辨識器。錯誤點位或操作時間不會取得影片人工操作後的預覽。
輸出run.json及各幀的原圖、辨識結果、疊圖、事件與結果。這個診斷入口不判P4通過。

目前驗證進度與缺口
P4-A：5段原始1440×1080影片閉環已通過；來源區域1、2、3、8、9，各一次虛擬點擊。
已補上影片普通戰鬥預覽的獨立選中節點像素辨識；舊V1 packet缺少此證據時仍拒絕，
不能拿攻略意圖或pending欄位補成辨識成功。
P4-B固定75/100/125%已通過15/15；P4-C與G4尚未通過。不同真實模擬器布局尚未驗收。
P5實機操作仍須使用者另行批准。

回放時鐘
PreviewSession使用注入時鐘；排程器在沒有新畫面或回條時仍須呼叫tick()。
15秒到期後不重送；不確定或遲到回條不能恢復已結束交易。
虛擬時間處理新鮮度／期限；實際processingMs另外記錄，不代表p95已合格。

詳細報告：docs/validation/2026-10-24-p0-p3-status.md
原始影片結果：docs/validation/2026-10-24-p4a-status.md
固定縮放結果：docs/validation/2026-10-24-p4b-status.md
設計：docs/superpowers/specs/2026-10-24-crk-helper-v2-design.md
實作計畫：docs/superpowers/plans/2026-10-24-crk-helper-v2-p0-p3-plan.md
執行紀錄：progress.md
