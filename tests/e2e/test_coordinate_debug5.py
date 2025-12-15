#!/usr/bin/env python3
"""座標取得・保存のデバッグテスト (待機時間延長版)"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains

options = webdriver.ChromeOptions()
options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)
driver.set_page_load_timeout(60)
driver.set_window_size(1400, 900)

TEST_PROPERTY_ID = 2478

try:
    print(f"【1. 物件編集ページを開く (ID={TEST_PROPERTY_ID})】")
    driver.get(f"http://localhost:5173/properties/{TEST_PROPERTY_ID}/edit")
    time.sleep(5)
    print("   ✅ ページ表示完了")

    # 所在地タブに移動
    print("\n【2. 所在地タブに移動】")
    tabs = driver.find_elements(By.XPATH, "//button[contains(text(), '所在地')]")
    if tabs:
        tabs[0].click()
        time.sleep(2)
        print("   ✅ 所在地タブをクリック")

    # 位置情報セクションにスクロール
    print("\n【3. 位置情報セクションにスクロール】")
    location_section = driver.find_element(By.XPATH, "//h4[contains(text(), '位置情報')]")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", location_section)
    time.sleep(1)

    # 座標取得ボタンをクリック
    print("\n【4. 座標取得ボタンをクリック】")
    geocode_button = driver.find_element(By.XPATH, "//button[contains(text(), '住所から座標を取得')]")
    actions = ActionChains(driver)
    actions.move_to_element(geocode_button).click().perform()
    print("   ✅ クリック完了")

    # APIレスポンスを待つ
    print("   10秒待機中...")
    time.sleep(10)

    # 座標入力欄を再取得して確認
    print("\n【5. 座標値を確認】")
    lat_inputs = driver.find_elements(By.XPATH, "//input[@step='0.000001']")
    for i, inp in enumerate(lat_inputs):
        val = inp.get_attribute('value')
        print(f"   入力欄{i+1}: value='{val}'")

    # コンソールログ（LocationFieldのみ）
    print("\n【6. LocationFieldログ】")
    logs = driver.get_log('browser')
    for log in logs:
        if 'LocationField' in log['message']:
            print(f"   {log['message'][80:250]}")

    # ページのHTML確認
    print("\n【7. 位置情報セクションのHTML確認】")
    try:
        section = driver.find_element(By.XPATH, "//h4[contains(text(), '位置情報')]/ancestor::div[1]")
        # 緯度ラベルを探す
        lat_label = driver.find_elements(By.XPATH, "//label[contains(text(), '緯度')]")
        if lat_label:
            # 緯度ラベルの次のinput
            lat_input = lat_label[0].find_element(By.XPATH, "./following-sibling::input | ../following-sibling::*/input")
            print(f"   緯度input value: {lat_input.get_attribute('value')}")
    except Exception as e:
        print(f"   エラー: {e}")

    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/coord_debug5_01.png")

    print("\n【テスト完了】")
    print("\n画面を10秒間表示します...")
    time.sleep(10)

finally:
    driver.quit()
