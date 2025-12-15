#!/usr/bin/env python3
"""コンソールログを確認するデバッグテスト"""

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
driver.set_page_load_timeout(30)

try:
    driver.get("http://localhost:5173/properties/1/edit")
    time.sleep(5)

    # 土地情報タブをクリック
    try:
        tab = driver.find_element(By.XPATH, "//button[contains(text(), '土地情報')]")
        tab.click()
        time.sleep(3)
    except Exception as e:
        print(f"タブクリック失敗: {e}")

    # コンソールログを取得
    print("【ブラウザコンソールログ】")
    logs = driver.get_log('browser')
    for log in logs:
        if 'DEBUG' in log['message'] or 'multi_select' in log['message'].lower():
            print(f"  {log['message']}")

    # すべてのログを表示
    print("\n【全ログ（最新20件）】")
    for log in logs[-20:]:
        print(f"  [{log['level']}] {log['message'][:200]}")

finally:
    driver.quit()
