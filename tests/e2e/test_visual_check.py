#!/usr/bin/env python3
"""実際の画面を確認"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=webdriver.ChromeOptions()
)
driver.set_page_load_timeout(30)

try:
    driver.get("http://localhost:5173/properties/1/edit")
    time.sleep(5)

    # 土地情報タブをクリック
    tab = driver.find_element(By.XPATH, "//button[contains(text(), '土地情報')]")
    tab.click()
    time.sleep(2)

    # checkboxを探す（multi_selectはcheckbox実装）
    print("【checkbox要素を検索】")
    checkboxes = driver.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"]')
    print(f"  見つかったcheckbox: {len(checkboxes)}個")

    # 法規制（自動取得）グループを探す
    print("\n【「法規制（自動取得）」グループを検索】")
    try:
        group = driver.find_element(By.XPATH, "//h3[contains(text(), '法規制')]")
        print(f"  ✅ グループ発見: {group.text}")

        # そのグループ内のcheckboxを探す
        parent = group.find_element(By.XPATH, "./ancestor::div[contains(@style, 'padding')]")
        inner_checkboxes = parent.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"]')
        print(f"  グループ内checkbox: {len(inner_checkboxes)}個")
    except Exception as e:
        print(f"  ⚠️ グループが見つからない: {e}")

    # ページ全体のHTML構造を確認
    print("\n【土地詳細グループを検索】")
    try:
        group2 = driver.find_element(By.XPATH, "//h3[contains(text(), '土地詳細')]")
        print(f"  ✅ グループ発見: {group2.text}")
    except Exception as e:
        print(f"  ⚠️ グループが見つからない: {e}")

    # スクリーンショット
    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/land_tab_visual.png")
    print("\n✅ スクリーンショット保存: land_tab_visual.png")

    # 10秒表示
    print("\n画面を10秒間表示します...")
    time.sleep(10)

finally:
    driver.quit()
