#!/usr/bin/env python3
"""デバッグ用テスト - ページの状態を詳細に確認"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)
driver.set_page_load_timeout(60)

try:
    print("【1. ページロード開始】")
    driver.get("http://localhost:5173/properties/55/edit")
    print(f"   現在のURL: {driver.current_url}")

    time.sleep(10)

    print("\n【2. ページソース確認（先頭500文字）】")
    source = driver.page_source[:500]
    print(f"   {source}")

    print("\n【3. body要素の内容】")
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        body_text = body.text[:300] if body.text else "(空)"
        print(f"   {body_text}")
    except Exception as e:
        print(f"   エラー: {e}")

    print("\n【4. div#root の内容】")
    try:
        root = driver.find_element(By.ID, "root")
        root_html = root.get_attribute("innerHTML")[:500] if root else "(なし)"
        print(f"   {root_html}")
    except Exception as e:
        print(f"   エラー: {e}")

    print("\n【5. コンソールログ】")
    logs = driver.get_log('browser')
    if logs:
        for log in logs[:10]:
            level = log['level']
            msg = log['message'][:200]
            print(f"   [{level}] {msg}")
    else:
        print("   (ログなし)")

    # スクリーンショット
    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/debug.png")
    print("\n✅ スクリーンショット保存: debug.png")

    time.sleep(3)

finally:
    driver.quit()
