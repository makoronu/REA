#!/usr/bin/env python3
"""保存機能の簡易テスト - 保存ボタンのクリックのみ"""

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

try:
    print("【1. ページロード】")
    driver.get("http://localhost:5173/properties/55/edit")
    time.sleep(8)
    print("   ✅ ページロード完了")

    # 保存ボタンをクリック
    print("\n【2. 手動保存テスト】")
    save_button = driver.find_element(By.XPATH, "//button[contains(text(), '保存')]")
    print(f"   保存ボタン発見: {save_button.text}")
    save_button.click()
    print("   保存ボタンをクリック")

    # 保存結果を待つ
    time.sleep(4)

    # コンソールエラー確認
    print("\n【3. コンソール確認】")
    logs = driver.get_log('browser')
    errors = [log for log in logs if log['level'] == 'SEVERE' and ('500' in log['message'] or 'TypeError' in log['message'] or 'Error' in log['message'])]
    if errors:
        print("   ⚠️ エラー検出:")
        for err in errors[:5]:
            print(f"      {err['message'][:200]}")
    else:
        print("   ✅ 重大なエラーなし")

    # 保存成功の確認（テキストベース）
    print("\n【4. 保存結果確認】")
    page_text = driver.find_element(By.TAG_NAME, "body").text
    if "保存しました" in page_text:
        print("   ✅ 保存成功メッセージを確認")
    elif "エラー" in page_text or "失敗" in page_text:
        print("   ❌ エラーメッセージを検出")
    else:
        print("   (保存結果メッセージは表示時間が短いため検出できない場合があります)")

    # スクリーンショット
    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/save_simple.png")
    print("\n✅ スクリーンショット保存: save_simple.png")

    print("\n画面を5秒間表示します...")
    time.sleep(5)

finally:
    driver.quit()
    print("\n【テスト完了】")
