# 第40組High交接：未接受任何功能修正

使用者要求重大／辨識算法重設計時停止並切High。本輪已停止於40，41–60及保留集未開始；原功能c955完整還原，HEAD起始af30157，177owned+141external hash全相同。不要重新做已完成效能分析；G4p95仍2743.67>1500未解決。禁止P5／實機／改分母／跳UNKNOWN／降低安全標準。

先讀 docs/reports/crk-helper-v2-development-60-report.md。證據根 artifacts/development-20261027-medium-01；continuation-report.json stoppedForFailure=true，session57491已結束，case40session78588已結束，沒有需續等的推論。

第40組來源case-40/source.json；265frames全新鮮、原排序。run-01完整分析，replay失敗37consumed、1virtualclick、IoU.9375148747。失敗35970，MAP confidence0/stateVerifiedfalse、gateoffscreen；當張配準previewOnly不可給新權威。失敗在回執後1166.67ms，非TTL/deadline。38個五證據束／190檔及所有source/codex/assets hashes已檢查。

根因：季別全圖score.957但OCRquad與timer重疊6.9>5.295px，現有V1弱標題重讀只收score<.9，無法收緊strongseason。唯讀diagnostic crop [5,23,265,110]的actual detector為season提供較緊box但文字錯；現有line variants讀原PNG [35,54,232,75]可得.921480584正確季別。不能從這一點就判通過：完整reread timer最高.896664027<.90，含fullwidthcolon。case40-strong-locator-debug.json保存所有實際變體／scores；不新造confidence，不把globalOCR高分當fresh。

未接受草稿：unaccepted-strong-season.patch、draft_bounded_ocr.py、draft_test_strong_season_locator.py；unaccepted-draft.json。strong-season-red.log正例RED＋2negativepass；strong-season-green.log仍正例RED，不是GREEN。草稿僅恢復season，再次MAPcontext仍0；已移出tests/ml並還原，不可直接套回當已完成修復。若採用其中測試，先重新跑RED；先決定能否沿現有架構設計通用、可來源驗證的原像素OCR重定位／完整行重讀，保留行獨立性/.90/重複拒絕/兩預覽/單次點擊。尚未證明需全架構重寫或換模型。

若有功能修復：本輪raw依賴bounded_ocr改變，舊raw V1快取失效，不能沿用舊39通過冒稱新版本；先聚焦RED->GREEN/反例，再40完整新鮮回放，之後當版prefix/full74/negative/units回歸並綁commit/hash。新功能通過後才依序41..60；只在全部60通過才進正式保留集30。原39當前引用來自performance-20261027/random39-current-01，明示前回合同功能版本，歷史first-traceable15pass24fail非absolute-first-ever。

計畫 docs/superpowers/plans/2026-10-27-development-40-60.md；持續ledger .superpowers/sdd/2026-10-27-development-40-60/progress.md。此計畫未完成，保留scratch供接續，不刪其他plan資料。沒有需要手動中止的現有測試，所有失敗原證據不可覆寫。
