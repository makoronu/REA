#!/usr/bin/env python3
"""座標取得・保存のより詳細なデバッグテスト"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = webdriver.ChromeOptions()
options.set_capability('goog:loggingPrefs', {'browser': 'ALL', 'performance': 'ALL'})

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)
driver.set_page_load_timeout(60)
driver.set_window_size(1400, 900)

# テスト用物件ID
TEST_PROPERTY_ID = 2478

try:
    print(f"【1. 物件編集ページを開く (ID={TEST_PROPERTY_ID})】")
    driver.get(f"http://localhost:5173/properties/{TEST_PROPERTY_ID}/edit")
    time.sleep(5)
    print("   ✅ ページ表示完了")

    # DevToolsでコンソールを確認
    print("\n【2. 初期状態のコンソールログ】")
    logs = driver.get_log('browser')
    for log in logs[-10:]:
        print(f"   {log['level']}: {log['message'][:150]}")

    # 所在地・周辺情報タブに移動
    print("\n【3. 所在地・周辺情報タブに移動】")
    try:
        tabs = driver.find_elements(By.XPATH, "//button[contains(text(), '所在地')]")
        if tabs:
            tabs[0].click()
            time.sleep(2)
            print("   ✅ 所在地タブをクリック")
    except Exception as e:
        print(f"   エラー: {e}")

    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/coord_debug2_01.png")

    # 住所フィールドの値を確認
    print("\n【4. 住所フィールドの値を確認】")
    try:
        # 都道府県
        pref_inputs = driver.find_elements(By.XPATH, "//input[@placeholder='例: 北海道' or contains(@value, '北海道')]")
        for inp in pref_inputs[:2]:
            print(f"   都道府県入力欄: value='{inp.get_attribute('value')}'")

        # 市区町村
        city_inputs = driver.find_elements(By.XPATH, "//input[@placeholder='例: 北見市' or contains(@value, '北見市')]")
        for inp in city_inputs[:2]:
            print(f"   市区町村入力欄: value='{inp.get_attribute('value')}'")
    except Exception as e:
        print(f"   エラー: {e}")

    # 「住所から座標を取得」ボタンを探す
    print("\n【5. 座標取得ボタンの状態を確認】")
    try:
        geocode_button = driver.find_element(By.XPATH, "//button[contains(text(), '住所から座標を取得')]")
        print(f"   ボタンテキスト: {geocode_button.text}")
        print(f"   disabled: {geocode_button.get_attribute('disabled')}")
        print(f"   class: {geocode_button.get_attribute('class')}")

        # ボタンの親要素の住所フィールドを確認
        location_section = geocode_button.find_element(By.XPATH, "./ancestor::div[contains(@style, 'backgroundColor')]")
        print(f"   セクションHTML長: {len(location_section.get_attribute('innerHTML'))}")
    except Exception as e:
        print(f"   エラー: {e}")

    # 座標取得ボタンをクリック
    print("\n【6. 座標取得ボタンをクリック】")
    try:
        geocode_button = driver.find_element(By.XPATH, "//button[contains(text(), '住所から座標を取得')]")
        driver.execute_script("arguments[0].scrollIntoView(true);", geocode_button)
        time.sleep(0.5)
        geocode_button.click()
        print("   ✅ クリック完了")

        # 5秒待ってメッセージを確認
        time.sleep(5)
    except Exception as e:
        print(f"   エラー: {e}")

    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/coord_debug2_02.png")

    # ステータスメッセージを確認
    print("\n【7. 座標取得後のメッセージを確認】")
    try:
        # 成功/エラーメッセージを探す
        messages = driver.find_elements(By.XPATH, "//span[contains(text(), '座標') or contains(text(), '取得')]")
        for msg in messages:
            print(f"   メッセージ: {msg.text}")
    except Exception as e:
        print(f"   エラー: {e}")

    # コンソールログ確認
    print("\n【8. 座標取得後のコンソールログ】")
    logs = driver.get_log('browser')
    for log in logs[-15:]:
        print(f"   {log['level']}: {log['message'][:200]}")

    # 座標値を確認
    print("\n【9. 取得後の座標値を確認】")
    try:
        lat_inputs = driver.find_elements(By.XPATH, "//input[@step='0.000001']")
        if len(lat_inputs) >= 2:
            print(f"   緯度: '{lat_inputs[0].get_attribute('value')}'")
            print(f"   経度: '{lat_inputs[1].get_attribute('value')}'")
        else:
            print(f"   座標入力欄数: {len(lat_inputs)}")
    except Exception as e:
        print(f"   エラー: {e}")

    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/coord_debug2_03.png")

    print("\n【テスト完了】")
    print("\n画面を10秒間表示します...")
    time.sleep(10)

finally:
    driver.quit()
