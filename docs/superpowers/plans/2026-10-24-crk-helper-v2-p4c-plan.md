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

- P4-A歷史原生里程碑5/5；P4-B最新比例回歸`artifacts/p4c-aspect-fixed-15-acceptance-01/report.json`15/15，保留實際分析版本。
- `artifacts/p4c-aspect-native-20-replay-01/report.json`原生開發20/20，含更高樓層及四部影片；1551張地圖與原本新鮮核心結果完全一致，重用核心證據不算新鮮效能。
- `artifacts/p4c-random-pilot-replay-08/report.json`首段三種變換3/3；仍只有一個原始互動。
- 完整90組／9042張來源PNG已產生，雜湊／尺寸／來源／座標變換獨立核對通過（`data/p4c/random-source-v1.json`）。開發60組逐組辨識並立即回放，遇第一失敗停該輪；保留30組尚未推論。
- 第一輪60組已在第4組`zone-2-first-battle-random-fixed`因入口外框模板切換而停止，0點擊；前3組通過不構成60組完成。入口像素與預覽假設修正後，該組目前已通過；最新首段3組回歸亦通過。第3輪開發回放核對相同圖片與當前程式雜湊後沿用這4組證據，從第5組接續，分母仍為60。
- 正式負例與最新隔離暖機p95尚未驗收，G4false。V1正式流程不變，P5未批准。

## Task 2追加實作 brief：預覽自動捲動後的身份

真實開發影格23730有入口，23745已自動捲出入口；既有`register_map_images`找到唯一361個內點與跨列節點一致配對。原獨立預覽辨識因沒有入口而拒絕，不能直接省掉入口檢查。

1. 先寫原始兩張PNG與packet測試：配準後恢復正確的絕對層數；錯誤區域、超過2500ms、不同視窗／幾何、不同像素及錯誤／多解配準均拒絕。
2. 在V2新增薄介面，只讀呼叫既有像素配準。需要原圖雜湊、四欄幾何、至少5個唯一節點對且跨兩列、單一層數偏移、原入口及一致高信心區域；不能讀intent或測試標註。
3. 只將已證實的對應關係用於預覽確認；不賦予新點擊、捲動或跨區域權限。Node Selector仍要求當張可見入口。
4. 保留最早仍新鮮的可見入口觀察作直接來源，不作無限歷史鏈接。預覽觀察須帶配準來源PNG SHA與frameId；交易驗證器要求來源是該次選點的兩張原圖之一，防止別次交易的歷史入口混入。
5. 原始raw mapReview不改寫，另存追蹤證據、配準對與恢復樓層。當張綠框、普通預覽與啟用進入按鈕仍要獨立像素驗證。
6. 純單張可見入口路徑不變；補上實際完整逐幀序列、錯來源交易反例與A/B回歸。完成只算P4-C開發能力，不能取代30段正式驗收。

第一版配準只接納相同客戶區幾何；隨機點後改比例仍須另證，不能因單一捲動測試通過而宣稱跨比例完成。

## Actual glowing-edge candidate and precision repair brief

Run05 actual zone8fixed source64878/64884 loses outer-edge proposals while the source orange ellipse and ordinary icon remain visible. Supplement only missing centers using same-frame aspect-consensus ellipses, median measured peer sizes and original node-orange RGB evidence. Preserve original detector, unique visible-gate lattice and connecting pixels as the authority for IDs, columns and floors. The source PNG/RGB/frame, actual analysis image/size, injection coordinates, ellipse, original template SHA and actual icon scores must accompany every supplement. Scoped hooks restore on success or exception; near-native aspect remains an unchanged no-op.

Actual64890 may use the existing preview core comparison (58x58 normalized crop, inner[12,12,34,34], original .90 score and .08 winner margin, bounded2% alignment). Ellipse-derived physical geometry remains independent of that alignment. Store original circle score and core ranking/crop separately; erased icon, unbound source, missing proof, modified crop/alignment/margin/template must reject. Do not change source intervals, seeds, stable duration or score thresholds.

Actual development control20224 exposed .0111947px disagreement after the legacy lattice rounds normalized candidate coordinates and source projection rounds them again. Retain original measured candidate precision through lattice assignment and round only at final source output; do not widen adapter tolerance. Add the actual Node preview bridge RED->GREEN, rerun all ten current controls and complete suites before resuming the unchanged60-case denominator. Prior failed replays remain preserved and cannot seed current-code reuse.

## Actual case14 original text and near-native recovery brief

Original78306 global OCR reads a partial remaining-time label with one missing glyph. Treat only a unique high-score complete day/clock suffix with that narrowly defined partial label as a locator. Existing independent season/zone/line-layout gates stay required; only a new original-pixel crop that actually reads the full remaining-time label and clock at>=.90 grants map context. Preserve original text/score and new crop/reading. Missing/duplicate locator or erased original timer must reject; do not insert a glyph into text or raise its confidence. OCR-code changes invalidate historical cache; same-core cache tests must build genuine fresh current-runtime baselines.

The same pre-change sequence has1366x1074 preframes and measured pixel-aspect.9437703. Existing8% no-op suppressed needed normalization. Preserve no-op for all<=3% deviations. For3–8% inputs, normalize using the existing unique circle consensus and original gate/line checks, and explicitly bind anchored/unanchored purpose to the same-frame prior raw map's actual boolean anchor status and pixel frame ID. Initially limiting this repair to unanchored maps fixed selection but still timed out: real78306/78308/78318 already had an anchor yet their uncorrected icon aspect prevented preview identity. Those three actual frames also require pixel normalization, with independent original icon and green-outline checks unchanged. Missing/mismatched prior map or purpose rejects. Scores, geometry tolerances, G2 and preview duration remain unchanged. Actual positives and binding negatives first RED->GREEN, then entirecase14 and current13 controls/suites before continuation.

Exact equality with old native V2 map output is a diagnostic, not a user requirement to freeze V2 predictions. The new near-native path changes relative candidates in actual native0Q46047 (old and new absolute anchors bothfalse); preserve that difference and audit it, do not silently call all1551maps unchanged or alter thresholds merely to pass an equivalence check. Any lost previously valid absolute anchor stops the audit; current full native replay must pass before G4. V1 files/assets and formal expedition remain untouched.

## Actual second-floor case16 pixel evidence brief

The1342x552 source14530/14540 has only two orange battle circles. Keep minimumthree, originalellipse/statistical/spatial gates and existingambiguity refusal. Only when no original qualified group exists, verify orange circles against original battle icon>=.9 and add exactlyone cyan gate validated by existing original arrow RGB>=.9. Atleasttwo verifiedbattlecircles plusone verifiedgate must form one median-closed consensus. OriginalHUDcoin fails the battleicon; erasedarrow fails the gate. Bind each additionalcircle's sourcepixel/template/innergeometry/score proof in Node before normalization grantsauthority. Existing three-orange path and genuine conflictingaspect groups remainunchanged.

Actualheader sourcexindent33.5px versusrowheight24.5px is physically explained by measuredpixelaspect1.83, so the old isotropic horizontal-spacing check falsely blocks originalseason/time reread. Scale only that failing horizontal limit using independently validated same-frame pixelaspect>1, preserveall verticalseparation/overlap/uniqueness/crop/score rules andrecordposition evidence. Requireactualfreshfullseason/time labels>=.9; erasedtimer stillrejects. No sceneconfidence promotion.

The completedfirst-row predecessor is missing from originaledgeproposals. A separate sourcepixel candidate may use actual greencheckcomponent, originaldone templates and onlysame-frame measuredpeer sizes; require doneRGB>=.9, gapagainstotherfamilies>=.08 and unchangedcheckmaskIoU>=.8. Recordsource/component/template/crop/alignment/peer/source-normalized-analysis geometry. Originalclassifier/lattice/connectingpixels assignIDs andfloors; independently rerun existing availability/completedpath masks afterward. Node validatesallbindings/peer geometry/scores, missingorcorruptedproof rejects. Do notinfercompletionfromstrategy, currentzone, intendedtarget or weakV1completedflag. Erasedoriginalcheck mustnotbereplacedbyrewardpanelcheck. Onlyminimumloop higherfloorcurrentproof is added; noexpedition orP5input.

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


### Task2/4 actual gate variant failure

First full-development randomrun01 stops on case4 zone2fixed1471x777 MAP_MOVING withzero clicks. Actual12318/12324 target orange geometry is stable, but exit template switches node-live-exit (119.52x91.10) to node-b-exit (113.40x79.42); gateIoU.82715. Do not relax selector or change frozen prepair. A unique cyan inner component of the measured same-frame exit candidate has identical actualsourcebox[732,262,83,59]. Original node-exit template innerextent[9,9,40,41] over58x58 yields canonical sourceouterbox[713.325,249.04878,120.35,83.46341]; actualindependent innerRGB scores.96948/.96961. New aspect-only refinement requires unique centered cyancomponent, candidate-size limits, actualoriginaltemplate arrow match>=.9 and outerdimension within15%originalmodel box. Store originalmodel analysisbox/center, sourceinnerpixelbox, templateSHA/size/innerextent and actualscore. Node must recompute geometry and reject wrongpixelproof. Actual stablegate RED->GREEN and erased-arrow cyanblob negative; targetIoU/line/scene/current gates unchanged. Re-run failedcase and previous3pilot cases, fullsuites before continuing60. Native near1 remainsno-op. Never count source rendering as inference or G4.


### Task4點前換尺寸順序與G2外框修正

實際case5舊前綴2094x948只有MAP場景／無入口，新1568x1008地圖有入口。runner在檢查幾何前先驗舊錨點而拒絕；同視窗幾何變更須先作廢舊候選、記STALE_GEOMETRY，再從新圖取得完整兩張有效錨點與200ms。selector、不同視窗、UNKNOWN及人工分支屏障不放寬。兩個RED->GREEN測試覆蓋重新取得與新畫面仍缺錨點必須拒絕。

順序修正後已確認預覽，但G2實際IoU.896281<.9，仍判失敗。新增aspect-only普通節點外框量測：由當張唯一共識圈對應的原始高解析度橙色凸輪廓擬合橢圓，用同張實際內圖RGB匹配原node-orange模板>=.9，再依原模板實際內框／尺寸換算外框，僅接納原模型尺寸±15%內且完整在圖內的解。保留原模型score與box，記來源橢圓／整數實際裁切／參考PNG SHA／尺寸／匹配分數；Node重新核對綁定、幾何與共識。純橙色無戰鬥圖示反例拒絕，沒有新增模板、修改真值或降低門檻。

當前case5IoU.954465、margin31.999px閉環通過；前4組當前程式回歸亦全過。最新Node77／Python101全過。僅5/60開發變換案例通過，仍非G4。後續沿用證據必須逐一核對相同PNG／PTS／幾何／intent／真值與全部當前ML/lib/scripts雜湊；不作效能證據，分母仍60。


### Task2實際計時圖示合併

實際case8zone3pre-change的20226/28/29/30/31影格包含弱讀值@03:00，圖示與數字合併使既有精確時間門檻拒絕，最短片段未累積200ms。新增限定裁切重讀：唯一弱圖示時間只作定位，需同張唯一鄰接限制時間／TimeLimit標籤與Enter及普通／Difficulty上下文；裁切範圍只有限移除左側圖示，對原數字實際OCR，只有同裁切三種讀法中無衝突的03:00>=.95才可用。保留原token／score、實際crop與analysis尺寸、鄰接標籤，不補字、不直接剝除前綴或提升舊信心。刪數字／重複／衝突／無標籤反例拒絕，非bounded模式不猜。

當前第8組回放通過、前7組回歸通過，Node77／Python104全套通過。接續第9組前須保存當前程式並核對前8組相同sourcePNG／PTS／幾何／intent／真值與當前codeSHA；保留集及G4仍未完成。

### Task2/4 missing gate candidate and independently measured row pitch

Actual development case17 (2543x1050 pre-change pair14530/14540) has two original-RGB verified orange nodes and one verified cyan gate arrow, but normalized Canny omits the gate and only three map columns remain visible. Permit the already independently verified cyan gate to enter the scoped candidate producer using its actual source inner/template outer extent; keep original classifier, unique lattice and line-pixel checks. Bind full source PNG/RGB/frame and normalized raster/analysis coordinates, and require the arrow proof to equal the unique chosen cyan calibration candidate at the Node boundary. Missing/altered evidence must reject. When this establishes actual peer IDs, permit one bounded completed-candidate pass; no unbounded recovery loop or target-driven candidates.

The same pair showed x-derived floors [1.02768,3.08693,3.07799,3.07799,2.05281,2.05618] despite valid <=4% pixel-aspect consensus. Do not widen the .08 row residual. With >=3 distinct observed rows, derive actual adjacent vertical pitch, require all gaps within4% of their median and that median within4% of measured horizontal pitch, then apply the unchanged floor residual, first-row=1 and original full detector/line-pixel rerun. Two-row path retains prior spacing. This separates measured x/y pitches and avoids accumulating calibration error down each row; annotations and evaluator transforms remain outside inference.

Focused real33-frame case17 passed one virtual click followed by independent preview confirmation, native0; Node missing/tampered gate-proof RED->GREEN. Current first16 regression and full suites are required before continuing case18. This remains P4-C development evidence, not G4 or P5 approval.

### Task2 completed candidates without geometric rescaling; supplemental gate independent of aspect consensus

Actual native-like negative completed-node-random-2 (measured aspect1.025) omitted the first-row completed node while already having a visible-gate four-column anchor. The original provider independently obtains doneRGB .95186/checkIoU .85106. For <=3% aspect only, preserve original dimensions and allow a completed-only candidate pass on an already anchored four-column map. Orange/gate supplementation and rescaling remain disabled there. Reuse one completedGeometry validator for physical/native inverse1 and aspect coordinates, retaining every original source, raster, check, icon-family, peer-size and alignment check. Actual two-frame Python/Node regressions and altered/missing-source-proof negatives required; do not accept MAP_AMBIGUOUS for a known completed node by broadening expected negative reasons.

Actual heal-not-battle-random-1 first frame78294 lacks an exit candidate despite a valid orange-only aspect consensus1.53807. Independent existing source search verifies exactly one gate arrowRGB .93431 with ratio1.54493 (within4%). When no exit candidate exists, permit this measured gate outside the unchanged orange consensus, retaining its separately marked candidate index, original gate proof, shape/ratio/center/source and injection binding. It does not alter the chosen aspect members/median or normalization. Second frame78300 already has a gate. Actual Python/Node RED->GREEN requires both anchors and correct heal identity; removed/altered supplemental membership or source/index/ratio/box/score/proof must reject. Continue full positive and negative replay with unchanged thresholds and denominators.

### Task2/4 line reference dimensions and physical peer identity

Case18 post-change prepair14530/14540 at1997x1146 fails original line40sample support .85/.825 despite actual continuous highlighted line. Measured nodes exceed58px in the960 model raster, while original transverse6px band staysfixed. Scoped V2 reference_line_geometry reuses unchanged original color/40sample kernel at58px per-pair median-shortside reference, independently rounded x/y raster scales. It runs only for original .5<=support<.85 and measurednode>58, accepts only reference support>=.85, preserves every original passing edge and rejection if fallback fails. Evidence binds source/frame/PNG/RGB, actual analysis raster, actual node boxes/centers, reference58 raster/scale andbothscores. Node validates projection/source/refinement geometry and rejects missing/corrupt proof. Erased actual line stem while retaining arrow center must reject; reference scaling is not evidence that an arrow alone proves a link. No V1 edits or threshold decrease.

Full first new-size frame14542 then exposed relative peer IDs renumbering after inserting missing first row. Resolve peer by unique unchanged same-frame sourcebox within existing.011 coordinate tolerance before setting final peer ID; original source/size/score/check validations remain. Actual first transition frame stays MAP, rather than being promoted to PREVIEW. Focused full32-frame case18 current replay passes one virtual click and independently confirmed preview. Current88Node/125Python/negative30 and full18 regression gates precede continuation19; G4false/P5unapproved.

### Task2 detected-completed extent geometry after verified peer measurements

Actualcase20 raw detected row2col1 has original completedTrue but independent source checkIoU.766<.8. Raw peer boxes cannot produce a valid source candidate; final independently orange-refined same-frame peers do yield originaldoneRGB.959/familygap>=.08/checkIoU.855. Add a separate final source-space stage for already detected completed hypotheses only; remove that hypothesis only in the provider view, require unique original-pixel solution within15%old dimensions/5%oldshortside center, retain its ID/type/template/rawmodelscore/completedflag and record previous geometry. Never promote rawmodelscore or infer completion from that flag. Source original check/appearance/peer/alignment/geometry bindings remain unchanged. Recompute affected adjacent line pixels with original lattice rules and scoped58-reference algorithm; explicitly validate final-geometry line provenance. Erased actual green with retained oldcompletedflag must not gain newgeometry/currentauthority.

ActualPython/Node RED->GREEN and source/oldbox/score/check/peer/missingproof negatives precede full current89Node/127Python/negative30/current20 regressions. Focused24frame case20 passes one virtual click followed by independent preview confirmation; still development only, no G4/P5.

### Native coordinate convention regression

Actualsource23736 undercase19 uses no aspect normalization. Completed extent recovery must retain physical source node fields and put normalized measurement details only in its explicitly bound proof; node.analysisBox/analysisCenter require a real aspectRectification. Adding those markers to a native map incorrectly triggered the existing unbound-geometry rejection. Actual regression RED->GREEN by preserving the original coordinate convention, while deliberate marker injection stillrefuses. Focusedcase19fullpasses; current90Node/127Python/negative30 and full20regression gates precede case21. No guard relaxation or P5activation.

### Task3 transaction-local directly observed semantic roots

Actualcase21 postclick resize has genuine independently anchored MAP23731 in the SAME successful click transaction; subsequent preview's existing SIFT proof references it rather than the old-client selectionpair. Internaloriginal-pair-only source guard rejects it despite correctG2/previewidentity. Keep finalG0-G5 criteria. Accept additional roots only through adapter-minted unforgeable direct visiblegate/unique lattice pixel authority, actually observed aftersentreceipt, samewindow/zone and validfreshmonotonicframes. Session's private root registry grants semantic registration reference only, no clickauthority. Direct anchored preview can become a reference only after expected identity matches; registered anchors cannot chain. Extra sourceid/SHA must match, currentpreviewgeometry/dims/origin/window must agree, sourceage>0<=2500ms; two200ms previews, original15sdeadline and oneclick remain unchanged. Wrong/unseen/copied/weak/mismatched-zone/window sources mustreject. Actualcase21 and oldwrong-source negative tests first; then fullNode/current21replay. Pythonvision andinput modules stayunchanged, so reuse model analyses only after exactallML/runtime/sourcehash checks, neverasfreshperformance.

### Task2/3 next isolated defect: offscreen-gate ordinary preview scope

After transaction-local semantic-root repair, actualcase21 accepts two genuine previews23738/39 but23740-51 have no detected mapcolumns. Source23740 normalized detector retains a large ordinary-battle illustration inside the previewpanel as a fifth map column; gate is offscreen, so visible-gate exclusion cannot run. A source-only diagnostic excluding that illustration using actual contextualtext boundary yields5 real nodes/4 relativecolumns; registration must still independently recoverfloor. Implement bounded scope ONLY after actual unique ordinary/03:00/Enter OCR + unique enabledgreenbutton originalpixels; no intent/annotation/click coordinates. Bind new candidateScope to PNG/RGB/frame/dimensions/actual OCR boxes/buttonpixelgeometry, preserve excluded measurements. No absolute anchor/selectionauthority granted. Apply only uncalibrated rectified maps, reuse original template/lattice/line and SIFT checks, verify source/score/controls/scope bindings in Node. RED actual23740 relativecolumns/registration/selected-ring test first; missing controls/erasedbutton/wrongsource/missingproof negatives, complete case21, fullcurrentNode/Python/negative30/current21regression before advancing22. Existing G4false/P5unapproved.

Task2 source-only ruling for laterpreview23741: prefer recovering the actually visible missed healnode rather than introducing ambiguous3column hypotheses. Originalgreencomponent exists atsource[1024,310,92,58], with independentoriginal innerRGB heal-family score>.9 andnonheal gap>.08 atsameframe measuredpeer sizes. Add bounded heal candidate producer only for ordinarypreview-scoped uncalibratedmaps: actualgreencomponent, >=4actual peer boxes, peer dimensions/centeralign withinexisting2%, actualsourcecrop RGBfamily evidence>=.9/.08, source/frame/rasterproof and no nearby duplicate. Original classifier/lattice/line/SIFT still decide; heal remains uncompletedheal and neverordinarytarget. Node validatesallsource/size/peer/green/score/projectionproof, rejectsmissingproof. Actual23741 RED plus erasedgreen/nonheal/differentbinding negatives first. This avoids guessedcolumns/floors andcrossframe-derived detection. Ifgreen/RGBproof fails, reject; never fall back to3column guess to pass.

### Task3 historical measured peer geometry provenance

Actualvariant22 source30119 completedcandidateuses a real same-frame rawpeer measurement that is later independently refined byorange sourceellipse. Require exactoldmeasurement binding topeer.orangeRefinement.originalAnalysisBox afterXprojection, with existingfull source/class/score/ellipse proof validated. This is sizesourceprovenance, nevernewclickauthority or stalepointreuse. Keepactualcheckcrop/box/score and.011 tolerance, no rewritinglabels/proofs tofinalgeometry. ActualframeRED->GREEN and missing/altered/sourcewrongpeer negatives, fullNode, actual22 andcurrent21modelregrade, negative30currentNodegrade precede nextvariant. MLunchanged: verifyallMLhashes andsource/runtime, reuseexistingcurrentanalysiswithoutclaimingfreshinference/performance.

### Task2 native preview source size references

Native/near-native frames also need theexistingmeasuredsameframepeer-size hypotheses, notonlymedian. Actual24/30138 missestargetCanny undergreenoutline; actualpeer116.14x116.1 clearsordinaryRGB.9528/gap.2448 whilemedian110.11x110.06fails. Extendexistingwithin10%observedpeer-size search andper-crop.9/.08 checks toallimages, sameboundedalignment. EmitactualsourcePNG/RGB/frame/peerbox identity/size proof; Node validatesexactsameframepeer andbounds, rejects missing/alteredproof. No fakeaspectnormalization or scorepromotion. ActualREDtestfirst, thencompletecase24, fullcurrentNode/Python/negative/current23regressionbeforeadvancing25.

### Task2 raster interval endpoints

Actual25/46303 boundarycalibrationcandidate projectedtop+height overshoots721 by1e-13. Preserve strictcoordinatebounds; projectbothmeasuredrasterendpoints with integerproduct/source-dimension division andderiveextent. No clipping/tolerance/threshold/consensus changes. ActualsourceboundarytestRED->GREEN, NodeactualMAPbinding andallnewsourcecropped/pixelguards, full25/current24/negative/suites beforeadvance26.

### Task2 original source ellipse extents for native outlines

Actual30/95343 no peerextent clearsordinary.9/.08 though actualsourceellipseextentdoes(.9440 vs.7804). Add source-original ellipseextent hypothesis toexistingboundedoutlinecrop search, within10%median, same2%alignment andscores; do notnormalizeanear-nativeframe. Existingactualellipse/template geometryproof isretained andNodebound tosource/frame/box/score; missing/alteredproofreject. ActualREDandorange-erasednegative, full30/current29regressions/fullNode/Python/negative before31.

### Task2 source-bound small-aspect sparse recovery

Actual31firstpreframe hasuniqueexit/6normalnodes/3Xclusters andtruepixelratio.9751886; prior<=3%skip preventsnormalizationandabsoluteanchor. PermitnontrivialactualnormalizationONLYforrawunanchored/no-column/uniquegate/>=5normal/3clustercontexts, withsourceboundsmallAspectSparseRecovery proof validatedbyNode andalloriginalqualityconstraintsunchanged. Existinganchorednative framesretaincurrentcoordinateconvention. ActualRED/source-topology-negative tests first; thenfull31/current30/negative/fulltests before32.

### Task2 separate weak remaining-label and actual clock crop locator

Actualvariant33source53172hasweakexactremaininglabel .7025 plusseparateclock .9658, soexisting.85locatorgate cannotrereadfulltimerandMAPremainsUNKNOWN. Permitonlyoneexactweaklabel .65..85 andoneclock>=.9 withboundedbaseline/overlap/gap tolocateoriginalunioncrop. Preservebothrawtokens/scores/boxes; requirefreshcompleteexactremainingtimer>=.9 andexistingseason/zonecontext beforeMAP. No inferredglyphs/scorepromotion/thresholddecrease. ActualRED->GREENpluserasedlabel/clock/missing/duplicate/misalignmentnegatives. OCRhashchangesrequirefreshfullpipeline(current32andnegatives), notlegacycacheinferenceclaim. Complete33loopandsuites/sourceartifactauditsbefore34.
