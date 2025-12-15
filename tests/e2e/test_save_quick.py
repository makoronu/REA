#!/usr/bin/env python3
"""保存ボタンの簡易テスト"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=webdriver.ChromeOptions()
)
driver.set_page_load_timeout(60)

try:
    print("【テスト開始】編集画面を開きます...")
    driver.get("http://localhost:5173/properties/55/edit")

    # ページロード待ち
    time.sleep(8)

    # 保存ボタンを確認
    print("\n【保存ボタン確認】")
    buttons = driver.find_elements(By.TAG_NAME, "button")
    for btn in buttons:
        text = btn.text
        if text and ('保存' in text or '登録' in text):
            print(f"  ✅ ボタン発見: '{text}'")

    # スクリーンショット
    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/save_button_check.png")
    print("\n✅ スクリーンショット保存完了")

    # 5秒表示
    print("\n画面を5秒間表示します...")
    time.sleep(5)

finally:
    driver.quit()
    print("\n【テスト完了】")
