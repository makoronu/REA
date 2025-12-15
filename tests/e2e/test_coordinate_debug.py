#!/usr/bin/env python3
"""座標取得・保存のデバッグテスト"""

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

# テスト用物件ID（座標がない物件）
TEST_PROPERTY_ID = 2478

try:
    print(f"【1. 物件編集ページを開く (ID={TEST_PROPERTY_ID})】")
    driver.get(f"http://localhost:5173/properties/{TEST_PROPERTY_ID}/edit")
    time.sleep(4)
    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/coord_debug_01_open.png")
    print("   ✅ ページ表示完了")

    # 現在の座標値を確認
    print("\n【2. 現在の座標値を確認】")
    try:
        lat_inputs = driver.find_elements(By.XPATH, "//input[@step='0.000001']")
        if lat_inputs:
            for i, inp in enumerate(lat_inputs[:2]):
                print(f"   座標入力欄 {i+1}: value='{inp.get_attribute('value')}'")
        else:
            print("   座標入力欄が見つかりません")
    except Exception as e:
        print(f"   エラー: {e}")

    # 所在地・周辺情報タブに移動
    print("\n【3. 所在地・周辺情報タブを探す】")
    try:
        tabs = driver.find_elements(By.XPATH, "//button[contains(text(), '所在地')]")
        if tabs:
            tabs[0].click()
            time.sleep(1)
            print("   ✅ 所在地タブをクリック")
        else:
            print("   所在地タブが見つからない（すでに選択されている可能性）")
    except Exception as e:
        print(f"   エラー: {e}")

    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/coord_debug_02_location_tab.png")

    # 「住所から座標を取得」ボタンを探す
    print("\n【4. 座標取得ボタンを探してクリック】")
    try:
        geocode_button = driver.find_element(By.XPATH, "//button[contains(text(), '住所から座標を取得')]")
        print(f"   ボタン状態: disabled={geocode_button.get_attribute('disabled')}")
        geocode_button.click()
        time.sleep(3)
        print("   ✅ 座標取得ボタンをクリック")
    except Exception as e:
        print(f"   エラー: {e}")

    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/coord_debug_03_after_geocode.png")

    # 座標値を確認
    print("\n【5. 取得後の座標値を確認】")
    try:
        lat_inputs = driver.find_elements(By.XPATH, "//input[@step='0.000001']")
        lat_value = None
        lng_value = None
        if len(lat_inputs) >= 2:
            lat_value = lat_inputs[0].get_attribute('value')
            lng_value = lat_inputs[1].get_attribute('value')
            print(f"   緯度: {lat_value}")
            print(f"   経度: {lng_value}")

            if lat_value and lng_value:
                print("   ✅ 座標が取得されました")
            else:
                print("   ⚠️ 座標が空です")
        else:
            print("   座標入力欄が見つかりません")
    except Exception as e:
        print(f"   エラー: {e}")

    # 保存ボタンをクリック
    print("\n【6. 保存ボタンをクリック】")
    try:
        save_button = driver.find_element(By.XPATH, "//button[contains(text(), '保存')]")
        save_button.click()
        print("   ✅ 保存ボタンをクリック")
        time.sleep(3)
    except Exception as e:
        print(f"   エラー: {e}")

    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/coord_debug_04_after_save.png")

    # ページをリロードして座標が保存されたか確認
    print("\n【7. ページをリロードして確認】")
    driver.refresh()
    time.sleep(4)

    try:
        # 所在地タブに移動
        tabs = driver.find_elements(By.XPATH, "//button[contains(text(), '所在地')]")
        if tabs:
            tabs[0].click()
            time.sleep(1)

        lat_inputs = driver.find_elements(By.XPATH, "//input[@step='0.000001']")
        if len(lat_inputs) >= 2:
            lat_value_after = lat_inputs[0].get_attribute('value')
            lng_value_after = lat_inputs[1].get_attribute('value')
            print(f"   緯度（リロード後）: {lat_value_after}")
            print(f"   経度（リロード後）: {lng_value_after}")

            if lat_value_after and lng_value_after:
                print("   ✅ 座標が保存されています")
            else:
                print("   ⚠️ 座標が保存されていません！")
    except Exception as e:
        print(f"   エラー: {e}")

    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/coord_debug_05_after_reload.png")

    # コンソールログ確認
    print("\n【8. コンソールログ確認】")
    logs = driver.get_log('browser')
    errors = [log for log in logs if log['level'] == 'SEVERE']
    if errors:
        print("   ⚠️ エラー検出:")
        for err in errors[:5]:
            print(f"      {err['message'][:200]}")
    else:
        print("   ✅ 重大なエラーなし")

    print("\n【テスト完了】")
    print("\n画面を5秒間表示します...")
    time.sleep(5)

finally:
    driver.quit()
