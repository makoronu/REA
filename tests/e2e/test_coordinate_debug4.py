#!/usr/bin/env python3
"""座標取得・保存のデバッグテスト (コンソールログ確認版)"""

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

# テスト用物件ID
TEST_PROPERTY_ID = 2478

try:
    print(f"【1. 物件編集ページを開く (ID={TEST_PROPERTY_ID})】")
    driver.get(f"http://localhost:5173/properties/{TEST_PROPERTY_ID}/edit")
    time.sleep(5)
    print("   ✅ ページ表示完了")

    # 所在地・周辺情報タブに移動
    print("\n【2. 所在地・周辺情報タブに移動】")
    tabs = driver.find_elements(By.XPATH, "//button[contains(text(), '所在地')]")
    if tabs:
        tabs[0].click()
        time.sleep(2)
        print("   ✅ 所在地タブをクリック")

    # ページを下にスクロールして座標取得ボタンを見つける
    print("\n【3. ページをスクロールして座標取得セクションを表示】")
    location_section = driver.find_element(By.XPATH, "//h4[contains(text(), '位置情報')]")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", location_section)
    time.sleep(1)
    print("   ✅ 位置情報セクションを表示")

    # 座標取得ボタンをクリック
    print("\n【4. 座標取得ボタンをクリック】")
    geocode_button = driver.find_element(By.XPATH, "//button[contains(text(), '住所から座標を取得')]")
    print(f"   ボタン状態: disabled={geocode_button.get_attribute('disabled')}")

    # ActionChainsでクリック
    actions = ActionChains(driver)
    actions.move_to_element(geocode_button).click().perform()
    print("   ✅ ActionChainsでクリック")
    time.sleep(5)

    # コンソールログ確認（LocationFieldのデバッグログを探す）
    print("\n【5. コンソールログ確認】")
    logs = driver.get_log('browser')
    for log in logs:
        if 'LocationField' in log['message']:
            print(f"   {log['message'][:200]}")

    # その他のエラーも確認
    print("\n【6. エラーログ確認】")
    for log in logs:
        if 'SEVERE' in log['level'] and 'favicon' not in log['message']:
            print(f"   {log['level']}: {log['message'][:200]}")

    # 座標値を確認
    print("\n【7. 取得後の座標値を確認】")
    lat_inputs = driver.find_elements(By.XPATH, "//input[@step='0.000001']")
    if len(lat_inputs) >= 2:
        lat_value = lat_inputs[0].get_attribute('value')
        lng_value = lat_inputs[1].get_attribute('value')
        print(f"   緯度: '{lat_value}'")
        print(f"   経度: '{lng_value}'")
    else:
        print(f"   ⚠️ 座標入力欄が見つかりません")

    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/coord_debug4_01.png")

    print("\n【テスト完了】")
    print("\n画面を10秒間表示します...")
    time.sleep(10)

finally:
    driver.quit()
