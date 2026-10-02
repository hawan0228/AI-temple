# 核心程式碼參考

這裡收錄九個原專案的核心程式檔，展示功能切換、儀式設定、安全、隱私及搜尋規則。

| 檔案 | 用途 |
| --- | --- |
| `app/line/signature.py` | 驗證 LINE webhook 簽章 |
| `app/orchestration/transition_policy.py` | 決定功能切換與高風險情況的處理方式 |
| `app/companion/spiritual_policy.py` | 限制宗教語氣與權威措辭 |
| `app/divination/ritual_profile.py` | 設定允請與連續三次聖筊的參考流程 |
| `app/divination/safety_policy.py` | 攔截重大決策與高風險求籤問題 |
| `app/prayer/privacy_policy.py` | 設定祈願狀態、心願參照與保存期限 |
| `app/temple/distance.py` | 計算經緯度距離 |
| `app/temple/privacy_policy.py` | 設定搜尋狀態、位置參照與保存期限 |
| `app/temple/ranking.py` | 依地區、主題、神祇或距離排序宮廟 |

