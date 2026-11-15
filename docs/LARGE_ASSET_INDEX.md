# 大型素材位置索引

影片、模型權重、虛擬環境與批次產生的測試輸出留在目前工作站；不提交至 Git。請依下列路徑在原工作站查找。檔案不存在時，使用來源網址/雜湊尋找或重新取得，切勿以缺少素材推測測試通過。

## 關鍵來源

| 類型 | 本機路徑 | 識別/備註 |
|---|---|---|
| 原始 CRK 影片 | `F:/CRK helper/data/video-validation/buAwy1zf2LI/buAwy1zf2LI.mp4` | SHA-256 `af0edce98d57e893d0051bb710668ba9a4ee8a5352aa363a8f5b097586cd901a` |
| 兩節點回放影格、manifest、證據 | `C:/Users/User/Documents/Codex/CRK-Helper-V2/artifacts/rift-episode-20261113-01/` | 連續原片視窗影格2514–8130；實際識別只抽取階段觀測。詳見同資料夾`RESULTS.md`及`verification-final.json` |
| 結果修復素材 | `C:/Users/User/Documents/Codex/CRK-Helper-V2/artifacts/result-repair-20261113-01/` | OCR/結果證據與來源影格 |
| YOLO26n 研究模型 | `C:/Users/User/Documents/Codex/CRK-Helper-V2/artifacts/candidate-research-pilot-20261112-01/fit/research-model/weights/` | `best.pt`、`best.onnx`；研究模型，非正式A1/生產模型 |
| OCR 執行環境 | `F:/CRK helper/.venv/` | 有限重現需要`Scripts/python.exe`及已安裝相依 |
| 研究訓練虛擬環境 | `C:/Users/User/Documents/Codex/CRK-Helper-V2/artifacts/candidate-training-20261112-01/venv/` | 本機隔離環境；不要提交 |

## 素材清單

素材樹在建立本索引時約有140,281個PNG/JPG/JPEG影格、7個影片檔路徑及若干模型檔。全部留在`artifacts/`原位置，不複製、不移動、不上傳。用下列命令在原工作站重新列舉：

```powershell
rg --files artifacts | Where-Object { $_ -match '\.(png|jpe?g|mp4|mkv|avi|mov|pt|onnx|engine|pth)$' } | Set-Content artifacts-local-index.txt
```

本 repo 的 `artifacts/` 預設被 Git 忽略，因此上述索引命令產生的逐檔清單亦留在本機。路徑反映目前工作站；Claude 在其他電腦上須以來源 SHA、資料集 manifest、case/frame ID 對應自己的素材位置。
