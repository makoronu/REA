# ローカルテスト実行

## 実行順序

### 1. サーバー起動確認

```bash
# 既存プロセス確認
lsof -i :8005  # API
lsof -i :5173  # フロント
```

### 2. API起動

```bash
cd ~/my_programing/REA/rea-api
PYTHONPATH=~/my_programing/REA python -m uvicorn app.main:app --reload --port 8005
```

確認:
- [ ] 起動ログにエラーなし
- [ ] `http://localhost:8005/docs` でSwagger表示

### 3. フロント起動

```bash
cd ~/my_programing/REA/rea-admin
npm run dev
```

確認:
- [ ] コンパイルエラーなし
- [ ] `http://localhost:5173` で画面表示

### 4. Selenium動作確認

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from datetime import datetime

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
driver.set_page_load_timeout(10)

# テスト対象画面
driver.get("http://localhost:5173/対象画面")

# スクリーンショット
os.makedirs("test_screenshots", exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
driver.save_screenshot(f"test_screenshots/{timestamp}_画面名.png")

driver.quit()
```

## 確認事項

- [ ] 画面が正しく表示される
- [ ] レイアウト崩れなし
- [ ] API連携が動作する
- [ ] エラー表示なし

## スクリーンショット保存先

```
test_screenshots/[YYYYMMDD_HHMMSS]_[画面名].png
```

## 問題発見時

→ 即停止
→ スクリーンショット添付して報告
→ 修正後に再確認

## 次の工程

→ doc_update.md
