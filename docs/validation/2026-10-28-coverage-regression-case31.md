# Coverage 當版回歸：第31組幾何退步

本輪來源版本 `5e2c740fcce2fb0f43127ccff5e87adc1f3d44b4`。第42組完整通過後，前41組1849張新鮮分析完成，但原批次在第31組的G2評分失敗，退出碼1。未進入第43組、保留集或實機。**不能宣稱原有40組已保持通過，也不能宣稱本輪60組完成。**

## 已執行與分母

來源仍為凍結90變換manifest，SHA256 `189b37115b1d08b0c245306bb727b13759d00aa0efb76a30e74b85acc6038e60`；60開發／30保留分母未變。功能183檔、外部141檔與runtime指紋均核對。

- 前41組1849/1849 fresh、0 raw cache。原整批評分：1～30通過，第31失敗，後續停止。
- 為完成失敗範圍分析，另以同一批已新鮮產生、版本相同的封包，逐一評分32～41，10/10通過。這是明示的診斷補查；**不把失敗的整批改成通過**，未跳過失敗來授權新組別。
- 第42組另有265/265 fresh、完整因果閉環通過。合計當版已評42組，41通過、1失敗、18未測；2114 fresh、0 raw cache、0原生操作。
- native20、fixed15、negative30、原生1551／七張及新增候選稽核、壓力與效能尚未在本版本完成。完整Node127/127通過；Python220項有218通過、2項歷史frame-context語義相等失敗，不能搬用M1完整回歸。

## 可重現的根因

案例 `dev-L0-zone6-floor1-col2-select-1773-random-fixed`，966×740。來源53163、53169為當前診斷索引，未寫入辨識演算法。兩版本的點擊proof都使用相同53169來源PNG與geometryVersion。原M1來源版本 `9944a9dca7ee5edb1b0a0afc5e4d2da1c8e31543`。

|量測|M1歷史正常版本|當版coverage|
|---|---|---|
|原始地圖節點|7|10|
|原始絕對樓層／四欄|false／null|true／四欄|
|比例恢復路徑|unanchored_near_native_recovery|原始結果返回，未執行該恢復|
|相同比例估計|0.9751886127920794|同張像素，診斷中共用原演算法|
|最終proof外框|[411.9270,353.0846,80.3186,82.3843]|[414.57,355.4,74.46,74.5]|
|凍結GT外框|[413.7067,354.7368,76.9926,81.0526]|相同|
|IoU|0.9358738154|**0.8889215162，低於0.90**|
|點擊內縮margin|19.1081px|18.9658px，符合內縮要求|
|預覽身份|通過|通過|
|結果|通過|G2外框品質失敗|

`ml/analyze_cases.py:41` 將coverage matcher安裝至共用的V1 `map_vision.node_candidates`，因此它同時改變初始V1觀察與後續比例恢復的候選。原始matcher的M1候選前綴完整保留，**但最終幾何路徑並未因此保持**。

`ml/map_aspect.py:425` 起，在比例偏差≤.03時，`_small_aspect_sparse_evidence`依原始觀察的未錨定／欄位狀態決定是否恢復。新增候選使原始觀察可建立四欄，這條件不再成立；429～432行改走已錨定結果返回，只補完成狀態。舊版曾經執行的rectification與橘色圖示外框精修未再發生。新增候選把指定目標辨識為battle，但保留了74.46×74.5的較小框，影響G2品質。

以兩張相同來源PNG，在隔離程序只切換M1／coverage matcher，重新執行原始地圖觀察及未修改的`recover_map_aspect`，均重現7／未錨定→10／已錨定的路徑差異。不是利用未來影格、改GT或重用舊座標；診斷模式明示，不當作正式當版推論成績。

分類上是**候選增補引起的幾何路由耦合與外框品質退步**。沒有證據顯示這次是座標取整誤差、錯節點點擊或錯預覽身份；虛擬點位仍位於正確實體節點內。因果交易本身達到PREVIEW_CONFIRMED，但獨立GT評分失敗，兩者必須區分。

另查第42組原失敗兩張35929／35935，本來就是已錨定、無aspectRectification。因此「一律把M2延後到rectified輸入」會讓第42組再次漏候選，不能當成完整修法。

## 最小下一步設計（尚未實作）

應將**基礎幾何路由證據**與**同幀補強候選**明確分開：

1. 同幀產生並保存原base／M1結果，以原有規則決定source或rectified工作空間；候選增加不能暗中取消既有必要的恢復與精修。
2. 在已選定的同幀工作空間內，增量掃描M2整數尺寸帶。已錨定source路徑也必須能補漏，才能維持第42組修復。保留完整原候選與各階段來源／尺寸／pixel hash，不用舊幀資料授權。
3. 使用明確的Observer呼叫參數或階段介面，代替把兩種用途綁在一個全域matcher指標。框投影仍由既有Geometry負責一次；Node Selector、Click Transaction、Preview Verifier及獨立JS驗證不改。
4. 同幀快取身份加入實際候選backend／階段，保留已修好的跨backend拒絕機制。共用Canny及已驗證的中間結果，避免把「解耦」做成兩遍完整匹配。

預計觸及 `ml/analyze_cases.py` 的安裝邊界、`ml/map_observer.py` 的明確backend介面，以及`ml/map_aspect.py`的呼叫整合；matcher銀行可保留。不改圈比例估計演算法、raster策略、匹配／IoU／peer門檻，不引入模型。**但這已超出只改matcher銀行的範圍，且涉及先前要求不修改的比例恢復呼叫邊界，因此先停止生產修改，待明確批准。**

### 驗收與風險

- RED：本次53163／53169須重現目前路由差異與IoU失敗，再驗證修復後兩張均維持原比例恢復及外框品質；不能改GT或放寬0.90。
- 第31完整29張與閉環、第41完整266張、第42完整265張重跑，均fresh，單次虛擬點擊、兩張獨立一致預覽。
- 保留第8／19／25座標歷史回歸、S3 46047／46057實體候選斷言、35929局部候選新證據，不以整段通過取代局部檢查。
- 整批前42、native20、fixed15、negative30＋評分器對照、完整單元、1551／七張／新增候選、取整壓力、同環境效能均重新綁定新版本。穩定後才43～60。
- 主要風險：兩階段候選身份混用、同幀快取鍵不足、source／rectified投影重複、額外掃描拖慢效能。必須以來源hash與實際階段耗時驗證；不能用TTL或安全門檻補償。

## 證據索引

根目錄 `artifacts/coverage-20261028-01/`：

- `prefix41-current-01/report.json`：完整1849張新鮮分析與原整批失敗；`replay/.../transaction.json`及`summary/result.json`保存31組失敗。
- `prefix41-suffix-diagnostic/report.json`：32～41個別診斷結果；不取代原批次。
- `current42-aggregate.json`：明示合併方法、原分母、41通過／1失敗／18未測。
- `prefix41-failure-integrity.json`：1849來源、654束／3270檔證據完整性通過，語義驗收仍失敗。
- `prefix41-suffix-integrity.json`：32～41補查的692束／3460檔hash完整性通過；不將失敗批次升格。
- `trace-case31.py`、`trace-case31.log`、`case31-counterfactual-trace.json`：同像素、只切matcher的兩幀可重現分析，包含runner及來源／packet hash。
- `case31-regression-proof.json`、`case31-regression-overlay.png`、`case31-regression-crop.png`：新舊框與凍結GT對照。已目視核對局部框包含同一戰鬥節點，coverage框較小。
- `case42-fresh-02/`、`case42-final-integrity.json`：第42組當版通過證據，未與M1舊失敗混淆。
- `s2-35929-local-current-proof.json`及overlay／crop：另處原漏候選已於當版恢復，距原手動中心2.938px；沒有完整獨立外框IoU標註，不能外推全圖。
- `continuation.json`：失敗即停，`GATE_FAILED:prefix41-current-01`，必要回歸未完成，43～60及heldout未啟動。

本輪不宣稱G4完成。M1舊p95=2374ms是歷史基準，coverage當版完整隔離基準尚未執行；P5未授權。

## 使用者後續批准及更窄可行方案

使用者已批准局部整合調整並繼續驗證。後續同像素可行性探針保留當幀新鮮M1原始觀察在既有v2OriginalMapReview欄位，覆蓋觀察作為工作mapReview；未修改map_aspect即可恢復原unanchored路徑，53163／53169的IoU為.9388055951／.9358738154。證據case31-phase-separation-feasibility.json只屬診斷，不冒充新版本閉環。依[新實作計畫](../superpowers/plans/2026-10-28-phase-observation.md)使用明確coverage階段、後端快取身份與增量共用工作實作；先RED再修改。原5e2批次失敗不變。
