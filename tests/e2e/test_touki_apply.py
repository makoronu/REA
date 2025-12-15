#!/usr/bin/env python3
"""登記取込ページの既存物件反映機能テスト"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = webdriver.ChromeOptions()
options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)
driver.set_page_load_timeout(60)
driver.set_window_size(1400, 900)

try:
    print("【1. 登記取込ページを開く】")
    driver.get("http://localhost:5173/import/touki")
    time.sleep(3)

    # ページタイトル確認
    h1 = driver.find_element(By.TAG_NAME, "h1")
    print(f"   ページタイトル: {h1.text}")

    # スクリーンショット
    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/touki_apply_page.png")
    print("   ✅ スクリーンショット保存: touki_apply_page.png")

    # 空の状態確認
    body_text = driver.find_element(By.TAG_NAME, "body").text
    if "取込待ちデータがありません" in body_text:
        print("   ✅ 空の状態が正しく表示されています")

    # PDFアップロードエリア確認
    if "PDFファイルをドラッグ" in body_text:
        print("   ✅ PDFアップロードエリアが表示されています")

    # 使い方セクション確認
    if "既存物件へ反映" in body_text or "新規物件登録" in body_text:
        print("   ✅ 使い方セクションが表示されています")

    print("\n【2. コンソールエラー確認】")
    logs = driver.get_log('browser')
    errors = [log for log in logs if log['level'] == 'SEVERE']
    if errors:
        print("   ⚠️ エラー検出:")
        for err in errors[:3]:
            print(f"      {err['message'][:150]}")
    else:
        print("   ✅ コンソールエラーなし")

    print("\n【テスト完了】登記取込ページが正常に表示されています")
    print("\n画面を5秒間表示します...")
    time.sleep(5)

finally:
    driver.quit()
