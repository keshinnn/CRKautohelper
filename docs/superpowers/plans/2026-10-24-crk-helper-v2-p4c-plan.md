# CRK Helper V2 P4-C 正式集合與隨機壓力測試

> **For agentic workers:** Use superpowers:executing-plans, systematic-debugging and test-driven-development. P4-A與P4-B已實際通過；本階段連續執行，P5仍須另行批准。

**Goal:** 保留原G0–G5，完成30個不同普通戰鬥互動、20個開發／10個保留、每張三次可重現隨機尺寸／比例／裁切、正式負例與實際效能驗證。

**Architecture:** 持續使用獨立V2；保留V1辨識資產與輸入模組、正式流程不變。真值與變換只給評分器／虛擬dispatcher；不讓辨識器讀取標註。每個失敗先保存再修，不能跳過或縮分母。

## Tasks and gates

1. **來源資格與分組。** 從整部來源影片核對真正的閉合地圖→人工普通節點點擊→預覽互動，排除只有隊伍設定、已開預覽直接改點、Boss／精英及重複計數。逐秒JPEG、色彩與關閉圖示僅作導航，正式來源必須原MP4逐幀PNG。核對至少3區域、2樓層、2路線欄位，先凍結30個不同互動再分20/10。資料不夠就明列缺口，不能假稱30完成；保留未處理的資料缺口。
2. **可操作證據補強（測試先行）。** 正式負例須拒絕灰色不可用節點，即使其形狀／連線像普通戰鬥。更高層的current必須由獨立已完成像素證據與唯一完成路徑成立，不能只將V1 completed候選升成verified。無入口／絕對樓層證據時拒絕；若需跨幀保留語意錨點，必須另有可追溯的像素配準、視窗／區域連續性與唯一性測試，不沿用舊物理點位。
3. **效能瓶頸與等價優化。** 已量測的診斷p95約3.1秒，不算G4通過。profile顯示廣域多尺度環形模板搜尋是主要耗時。優先做可證明等價的重複計算消除／快取，不降低分數門檻、不拿真值縮小搜尋範圍。先對實際原圖測試候選框、分數及拒絕結果不變，再測隔離暖機耗時；不將虛擬時鐘或重用packet耗時當完整辨識性能。
4. **三次隨機虛擬客戶區變換。** 每張畫面記seed、實際輸出尺寸、非等比縮放、裁切與真值轉換。正例保留必要錨點；負例刻意裁掉節點／連線／身份。固定布局、點擊前變更、點擊後變更分成三條序列；辨識器只收新圖片與真實擷取同型欄位，不收逆矩陣或標註。另保留分析前處理逆轉換的獨立測試。
5. **正式回放與總評。** 30個原始互動及三組變換全過，10個保留獨立列出；保留集若用來修正，必須更換保留互動並留紀錄。真正UNKNOWN／錯誤身份立即保存並停該案例，修正後重跑，不能沿用成功人工分支。正例、負例、效能分開計；全部門檻符合才可顯示G4完成。程式／模型／來源／標註／變換／事件／結果均有hash。

## Current evidence

- P4-A：`artifacts/p4a-acceptance-03-versioned/report.json`，5/5。
- P4-B：`artifacts/p4b-acceptance-02/report.json`，15/15。
- 目前所有已驗收來源僅第一層；不能假裝已涵蓋更高層。
- `artifacts/p4c-*-navigation*`是未核對導航候選，不是30個合格互動。
- `artifacts/p4c-observer-profile.txt`為診斷，不是G4效能報告。
- P5沒有批准；不啟動任何原生點擊、技能輸入或正式遠征。

## Task 2追加實作 brief：預覽自動捲動後的身份

真實開發影格23730有入口，23745已自動捲出入口；既有`register_map_images`找到唯一361個內點與跨列節點一致配對。原獨立預覽辨識因沒有入口而拒絕，不能直接省掉入口檢查。

1. 先寫原始兩張PNG與packet測試：配準後恢復正確的絕對層數；錯誤區域、超過2500ms、不同視窗／幾何、不同像素及錯誤／多解配準均拒絕。
2. 在V2新增薄介面，只讀呼叫既有像素配準。需要原圖雜湊、四欄幾何、至少5個唯一節點對且跨兩列、單一層數偏移、原入口及一致高信心區域；不能讀intent或測試標註。
3. 只將已證實的對應關係用於預覽確認；不賦予新點擊、捲動或跨區域權限。Node Selector仍要求當張可見入口。
4. 保留最早仍新鮮的可見入口觀察作直接來源，不作無限歷史鏈接。預覽觀察須帶配準來源PNG SHA與frameId；交易驗證器要求來源是該次選點的兩張原圖之一，防止別次交易的歷史入口混入。
5. 原始raw mapReview不改寫，另存追蹤證據、配準對與恢復樓層。當張綠框、普通預覽與啟用進入按鈕仍要獨立像素驗證。
6. 純單張可見入口路徑不變；補上實際完整逐幀序列、錯來源交易反例與A/B回歸。完成只算P4-C開發能力，不能取代30段正式驗收。

第一版配準只接納相同客戶區幾何；隨機點後改比例仍須另證，不能因單一捲動測試通過而宣稱跨比例完成。

## Task 3追加實作 brief：有尺寸證據的OCR前處理

完整暖機診斷144樣本p95=4433.98ms，不能宣稱效能合格。實驗發現現有OCR的min模式不縮小大型輸入，而max模式會自動覆寫設定的上限；必須檢查實際送入模型的tensor，而非只記設定值。只改執行緒沒有解決問題。

- 在V2離線子程序內建立可還原的OCR runtime，沿用原模型、文字辨識與精修函式、原閾值。預設仍為原V1；以明確的`--bounded-ocr 960`實驗模式啟用實際最長邊上限，V1檔案與正式流程不改。
- 每次文字偵測記實際輸入大小、32倍數取整後tensor大小及獨立X/Y比例。輸出文字框仍由現有模組還原到原圖；PNG／RGB雜湊不更換。
- 960上限實驗的6張原圖均有高信心區域證據，但兩張因「剩余時間」與「剩餘時間」字形差異變UNKNOWN。只正規化這個已讀出的同義正字詞，保留recognizerText、原score、原box；不補遺失的字、不猜遊戲標籤、不提升信心。
- 先寫實際tensor上限、取整後獨立比例、上下文還原、正字詞保留原證據測試，再接批次入口。不同OCR模式或runtime版本的快取不得冒稱新鮮辨識，需重新跑原圖。
- 原5段／15縮放與高層／配準開發案例須重跑；遇到UNKNOWN立即保存、停止該案例並修正。只有目前模式與版本的完整測試、功能回放和獨立實際耗時全過，才可推薦為V2模式；仍不能把局部效能實驗當G4。

## Task 4追加實作 brief：點擊前重新取得穩定畫面

離線runner目前遇到第一對移動畫面或幾何變更立即結束，不能驗證點前變更後重新穩定的正例。保留selector原有200ms、相同視窗／幾何與像素穩定門檻；runner只對同視窗的短間隔、幾何變更或MAP_MOVING重新等待。每次拒絕記完整影格ID／錯誤碼；移動／幾何變更後舊候選作廢，從新圖重新累積200ms。視窗改變、未知、不可用、缺身份／連線等仍立即拒絕。先以連續33ms影格、移動後停止、點前尺寸變更、跨視窗反例TDD；實際影片負例仍不得點擊。

## G0追加實作 brief：實際OCR資產與runtime可追溯

初始2384檔快照未包含venv內的OCR ONNX。正式C之前，在離線analysis記錄Python／Pillow／NumPy／OpenCV／RapidOCR／ORT版本、RapidOCR程式／設定檔及三個實際ONNX的SHA與大小。綁成可重現fingerprint；快取若缺fingerprint或不一致，即使OCR模式與V2程式相同仍須重新辨識。保留OCR模式變更拒絕優先順序。先測實際模型清單／雜湊及偽造runtime快取必須失效，不改任何V1／套件檔。舊報告維持當時證據，不追溯冒稱已記錄。

## Task3新增實際失敗：原生960px區域小字漏偵測

L0zone6resume原圖53427的完整OCR漏掉實際可見「區域6進行中」，造成UNKNOWN；保存並停該案例。由已讀出的唯一高信心剩餘時間行，定位其下方有限原圖區域做3倍OCR重讀，只接受實際讀出的完整區域進行中詞與>=.9分數，座標還原原圖；不讀intent、不補數字、不沿用歷史zone。僅明確bounded模式啟用；有可解析區域時不覆寫，衝突交由既有header拒絕。原字被遮掉的反例仍無區域。先實際影格及遮字反例RED->GREEN，再重跑完整三段與固定縮放。

## G2評分器校正與開發報告

G2規定距人工可點擊區邊界至少目標短邊5%，舊評分器卻用了可點擊區短邊5%。以較小人工安全框先重現誤接受，改用人工目標真值短邊；不改選點位置。原固定縮放須回歸。另提供明確development grade供不同原生尺寸開發案例核對IoU／落點；與A/B里程碑嚴格入口分開，永遠不能產生G4true。

## Task2新增實際失敗：只有區域文字的進行中節點

L0原生resume兩張地圖已讀到區域6與節點旁「進行中」，但V1current helper要求舊式header中的lastEnteredFloor，加上完整模板精確比對，故CURRENT_POSITION_UNPROVEN且0點擊。不得把真值resume改成select避開。新增V2獨立證據：當張可見唯一入口／絕對層數、唯一>=.95的精確進行中標籤、鄰接唯一未完成可用普通節點、四象限黃色外框與上方唯一向下三角。樓層來自當張格線，不填入progress或intent；缺標籤／三角、重複標籤、錯像素均拒絕。保留既有嚴格模板路徑；Node須核對新證據綁定、框、分數與形狀數值再允許resume。先實際兩張與負例Python RED->GREEN，生成實際packet，再Node橋接RED->GREEN，再三段完整回放。

## P3回放分支補強：沒有有效點擊不得讀取人工後續

加入點前移動等待後，runner可能在未發送操作時繼續讀到原影片人工操作後的地圖／預覽；即使最後拒絕，也不符合虛擬dispatcher契約。先測移動兩幀後的人類分支不得交給observer、虛擬點擊0，再在無交易且來源PTS已到previewFrom屏障時停止，保留前一次拒絕及未釋放分支事件。合法新穩定對須在屏障之前形成，不能讀人類結果等它穩定。重跑真實移動畫面負例及既有正例。

## Task2實際區域10解析失敗

原始95313PNG已被OCR讀出完整「區域10進行中」且flow=MAP，但V1header及多個V2界限寫死1..9，使zone=null。核准設計只要求有效區域，沒有排除實際UI的第10區；修正為1..10，不將此可辨識正例改標負例。保留V1檔案，建立離線作用域內的header擴充：既有1..9解析不變、只合併實際完整10區詞，和既有區域或樓層衝突仍拒絕；不接受11/100或遺漏字。原分數不升級、低分不給權限。Node selector/adapter、Python預覽/配準/current界限同步；單張與批次入口一致，快取從同張原始文字重新解析。先實際95313與衝突/邊界/作用域還原RED->GREEN，再Node區域10/11邊界及實際原始閉環。


## G0多來源影格與快取隔離 brief

正式C將使用不同原生影片；目前batch frameId只讀manifest頂層videoSha256，快取key也只有frameIndex/PNG SHA。即使兩個來源有完全相同PNG及影格編號，也必須保有各自影片身份，不得跨片重用packet。先以真實PNG建立兩個明確來源雜湊的入口測試：沒有全域videoSha時仍能逐案例建立不同frameId；同runtime快取只能命中同來源，來源不同必須新鮮辨識。沿用既有單片frameId公式與頂層fallback，驗證SHA格式及同案例source/direct聲明衝突；未知歷史快取來源不能給權限。記錄來源綁定與拒絕原因，維持PNG/RGB/尺寸檢查。這是資料身份契約測試，不將相同測試PNG計入30個影片互動。

### English source development repair brief (2026-10-25)

Real LX46original2194 fails UNKNOWN with fragmented Zone/1inl/Progr despite actual English title and time labels. Permanently development-assigned before inference, original watermark retained. First RED tests require exact full English zone phrases, conflict rejection across languages, no watermark/reward/partial text as zone authority; independently bounded original crop next to unique actual Ends in label must reread missing full zone. Erased original zone pixels must remain unknown. Do not concatenate speculative OCR fragments or fabricate/translate English text into Chinese evidence. Preserve scores/boxes/source references and existing V1 behavior. Subsequent semantic/current/preview support needs its own failing tests; no inference on pending holdout. This repair alone is not a closed-loop pass or formalG4.

### Sparse native map geometry failure brief
Actual LX46zone4floor2col1 development replay rejects ANCHOR_MISSING with0virtual clicks. Original detector sees visible exit + five ordinary/heal/completed nodes on three X clusters; V1 requires four present clusters and discards all column/floor IDs. V2 recovery may infer the single missing column only from same-frame visible gate centered between columns2/3, unique spacing within existing radius bounds, >=3actual columns, >=5actual normal nodes across>=2aligned rows. Require real pixel binding and rerun original map detector/line evidence with independently computed geometry; no intended column, annotated coordinates or cached historical positions. Missing/duplicate/erased gate, two clusters, ambiguous solutions reject; completedpath and .85line/.8check thresholds remain. Preserve original mapReview separately. First real positive+negative tests RED before implementation.

### Actual native map-title OCR truncation repair brief
Earliergate L0zone5 frame36163 fails UNKNOWN while actual image remains MAP, timer and zone5 both independently high-confidence. Original OCR only returns 冥界 from full visible 冥界試煉; do not accept the partial word as scene authority. In bounded runtime, only a unique high-confidence partial title in upper-left adjacent to a unique remaining-time label may locate a small original-pixel reread. Exact original-parser-supported 冥界試 or 冥界試煉>=.9 must actually be read, preserving original row, raw variants/scores/crop/analysis size. Erased trailing glyphs and absent/duplicate/time-mismatched context must not fabricate the title. Same V1 scene parser remains unchanged. First actual failed PNG and missing-title pixel negative RED, then minimal scoped reread, then full earliergate native replay and fixed regressions.

### Task4 sequence-freeze implementation constraints

Original30 source freeze remains immutable. Three transformed sequences must have distinct deterministic layouts for every original source frame, not share the same initial layout across fixed/post-change variants. Derive seeds from frozen annotation SHA + case id + mode/phase; save every crop, size, per-axis scale, matrix and original PNG SHA for evaluator only. Observer receives only actual new PNG and capture-like binding fields.

Pre-click geometry change needs an old-layout observation followed by a wholly new stable200ms pair BEFORE the human branch barrier. The two-frame original source contract cannot supply this by changing only its second frame. Extend only the pre-change variant with the actual immediately preceding native source frame (preFrames[0]-1), from the SHA-verified video, preserving real PTS; do not duplicate a PNG, invent source time, shift the human gate, reuse stale proof or loosen200ms. Review the added original frame's map context and include its SHA/version in a separate immutable transform manifest. If real pixels fail qualification, save and repair/requalify honestly before claiming this positive. Fixed and post-change variants retain original source frames. All three release human post-click pixels only after evaluator-gated virtual click. Post-change preview needs fresh independent identity or explicitly verified registration; geometry changes must never reuse old physical coordinates.

Required crop anchors need reviewed real-image boxes across the entire actual sequence (zone/title/time, visible selection gate, selected node/link evidence, preview identity/enter). Annotation may constrain transformation generation, never recognition. Negative variants intentionally remove required evidence and must reject without a wrong click. Layout planning or generator unit tests are not formalC replay acceptance.

### Actual watermarked Chinese title context repair brief
Third earliergate source0Q46021/46033 has genuine visible gate/four-column lattice, but rawsceneMAP confidence0 because PonPonLin watermark is merged with primary game title. Cropping primary title still yields low-confidence actual reads: do NOT strip the watermark string or raise those scores. The independent season line and remaining-time line are visible. Scoped V2 fallback may accept exact actually read 冥界試季N or 冥界試煉季N plus exact remaining-time duration plus unique actual progress-zone, each>=.9, only after bounded original-pixel reread with real crop/size/raw scores. Existing parser already permits 冥界試 as game title; never fabricate missing 煉. Context crops require unique aligned upper-left season/timer original boxes, no intent/history or watermark text. Preserve non-MAP recognized scenes and high-confidence existingMAP. Missing/erasedseason, timer orzone, conflicting/duplicate labels must not gain trustedMAP authority. First actual failure and freshpixel negatives RED before implementation; old rawMAP0 remains visible in original failed packet. This is new independent evidence, not lowering scene confidence.

### Task4 implementation step: pure three-sequence layout planner

First implement/test a pure planner before any large pixel generation. Inputs are frozen case, explicitly reviewed anchor boxes, separately native-decoded/reviewed prefix(preFrames[0]-1), annotationSHA. It must validate sourceFPS/size/sourceSHA/nativePTS/prepair/gate/prefix/anchor bindings, derive reproducible per-case/per-phase seeds, create five distinct nonuniform client layouts. Sequence fixed usesA; pre-change usesB only on actualprefix thenC for originalframes; post-change usesD for originalprepair thenE afterward. Every original frame receives three different output sizes and positive crops. Preserve real frameindices/PTS; explicit previewFromPtsMs is ORIGINALthirdframe, not transformedlistindex2 (pre-change index2 is the dispatchframe). Transform expected/safe boxes using dispatchlayout only. Drop old packet/binding products, preserve input case unmodified. No image reading/model inference or G4 claim in planner; later renderer must verify actual original PNG SHA/size and freeze outputs before observer use. Unitfixtures are protocol data, not additional real-video positives.

Task4 renderer step: exclusive new output directory, exact plan snapshot/hash, verify each original PNG SHA/size and render from those same hashed bytes. Freeze all three sequences with actualoutputPNG SHA/dimensions/transform/inputSHA and realPTS. Atomic progress manifest stays pixelsRenderedfalse until alloutputs complete; preserve failure reason/case/frame onchangedsource, never overwrite previousrun. No recognizer or inputadapter call. Changing bytes between sourcehash and image decode must not create a mislabeled output (actual RED reproduced blue output bound to red inputSHA; transform_png now decodes the same read bytes viaBytesIO). These protocol/PILfixture tests are not real-video positives.

Task4 native-prefix step: verify actual source-video SHA once per source, nativeFPS/size, exact preceding frame preFrames[0]-1 and actualdecoderPTS. Freeze originalPNG and its SHA with annotationSHA/codeSHA. Newly decodedprefix defaults reviewedfalse and modelInferenceRunfalse; no automatic claim that it is a validMAP. Subsequent visual qualification must bind this exactSHA before planner can use it. Reject wrong video/native specs/unsafe paths/annotation or non-reviewed originalcase; exclusive outputs preserve previousruns. Synthetic short-video tests only prove decoder/protocol behavior, never count as real game positives.

Task4 development runner step: reusable source-loader and gate builder must derive the first human post-branch frame from actual index preFrames[1]+1, not arrayindex2. Explicit branch override must agree; prefix cannot skip gate or dispatchlate. Verify sourcePNG hash, manifest/packet dimensions and source-derived frameId=SHA(videoSHA+frameindex+PNG SHA) before adaptation. New committed developmentCLI preserves five evidence bundles for everyconsumedframe/summary and alwaysG4false; old A/B script restrictions stay. Random nonuniform grades must report scale=null + transformMode, not falsely claim isotropic1.0. TDD gate-prefix, incorrect branch/time, wrongsource/hash/dimensions plus real control-loop before random pilot.

### Task2/4 actual anisotropic zero-candidate failure brief

Real fixed-random2290x1293 firstframe returns0V1nodes; nativecontrol works. V1normalizes width960 but still matches isotropic kernels. Read-onlyexperiment estimates actual orangecircle X/Yratio~1.342 from closed convex ellipse contours and unique>=3circle consensus with distinct rows/columns; no case metadata/intent/transformmatrix. Xrectification to1706x1293 restores9nodes,4columns,visiblegate,10actualpixel-supported edges.

Implement a V2-only postprocessor from actualsourceimage + boundrawpacket. Verify image/pixel/frame binding first. Estimate intrinsiccircle deformation from originalpixels only (CV analysis size/scales/contours/ratios/consensus recorded); refuse absent/ambiguous evidence and native near1.0 is a no-op. Reuse unchanged V1map detector on rectifiedpixels, require actualunique four-column structure; project boxes/centers/columns back with explicit inverse, keep floor/edge proof from that same actualnormalizedimage. Preserve originalmapReview and record source/rectified pixel hashes, actualsizes, forward/inverse transforms and modelanalysisreferences. No thresholds/scores changed, no truth/history inputs. Missinggate cannot gain absolutefloors; noiseellipses withoutactualmap/lattice reject, wrongpixels reject. First real transformedbboxIoU>=.90 +nativeChinese/English no-op +gateerasure/noise/ambiguous ratio/binding tests RED beforecode. Integrate bothsingle/batch observer, restore originalraw map before cachedpostprocessing and recordnewcodeSHA. Then run actualfirstsequence closedloop; preview/current/registration may need explicitaxisgeometry support if realfailures expose remainingisotropic assumptions. This brief does not authorize wholeexpedition or P5.


### Task2/4 actual preview and inner-circle followup

Actual115PNGpilot exposed three distinct failures; retain all prior outputs. First fixed geometry selected correctly but preview selected-node recovery used sourceX spacing forY; deriveY spacing as sourceX spacing * rectifiedWidth/sourceWidth on bound same-frame proof. Icon template recovery may test only actual same-frame detected outer sizes within10%median, with original.9score/.08winner margin and node-orange restriction. Python actual2556 +freshimage erasedgreen negative, Node actual PREVIEW-state assertion andwrongfloor negative.

Second pre-change actual2541 shows nonexit panelheadericon above unique visible topgate, causing spurious extra column. In aspect normalization only, retain excluded candidates at/above measuredgate, then run unchanged existing sparse-lattice solver and actual connecting-line checks on same normalizedimage. No map history/intent/annotation, no OCRconfidence promotion. Record candidateScope and originalnormalizedpixelSHA.

Third post-old pair2514/2520 has identical measured orange inner ellipse while exhaustive outer-template boxes jitter (IoU.92282358). Do not lower selector .95IoU/2%center tolerance. For a battle candidate, permit center refinement only from one enclosed orange-circle consensus member in that same frame, within5%shortside of original model center; preserve original width/height, original analysisbox/center, candidateindex. No temporal smoothing or copiedpriorcoords. Node validates consensusmembership/sourcecirclecenter/enclosure/originalsize/displacement plus existing sourcebinding/inverseprojection. Actualpixelstablepair RED->GREEN, corruptedcircleindex rejects. Originalnative near1 unchanged. Full current115framepilot andfullsuites must be rerun; neither thispilot nor anysubset equalsG4.
