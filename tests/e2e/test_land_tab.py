#!/usr/bin/env python3
"""土地情報タブの全フィールド確認"""

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
    try:
        tab = driver.find_element(By.XPATH, "//button[contains(text(), '土地情報')]")
        tab.click()
        time.sleep(2)
    except Exception as e:
        print(f"タブクリック失敗: {e}")

    # 土地情報タブ内の全inputフィールドを取得
    print("【土地情報タブ内のフィールド】")

    # すべてのinput, select, textareaを取得
    for tag in ['input', 'select', 'textarea']:
        elements = driver.find_elements(By.TAG_NAME, tag)
        for el in elements:
            name = el.get_attribute("name")
            if name:
                value = el.get_attribute("value") or ""
                print(f"  {tag}: name={name}, value={value[:30]}...")

    # グループ名を確認
    print("\n【表示されているグループ名】")
    groups = driver.find_elements(By.XPATH, "//h3 | //h4 | //legend | //span[contains(@class, 'group')]")
    for g in groups:
        text = g.text.strip()
        if text and len(text) < 50:
            print(f"  - {text}")

    # 特定フィールドを探す
    print("\n【特定フィールド検索】")
    fields_to_find = ['use_district', 'city_planning', 'land_category', 'building_coverage_ratio', 'floor_area_ratio']
    for f in fields_to_find:
        try:
            el = driver.find_element(By.NAME, f)
            print(f"  ✅ {f}: 見つかった (tag={el.tag_name})")
        except:
            try:
                el = driver.find_element(By.ID, f)
                print(f"  ✅ {f}: 見つかった (ID)")
            except:
                # XPathで検索
                try:
                    el = driver.find_element(By.XPATH, f"//*[contains(@name, '{f}')]")
                    print(f"  ✅ {f}: 見つかった (部分一致)")
                except:
                    print(f"  ❌ {f}: 見つからない")

    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/land_tab_debug.png")
    time.sleep(3)

finally:
    driver.quit()
