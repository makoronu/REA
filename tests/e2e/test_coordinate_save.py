#!/usr/bin/env python3
"""座標取得・保存のフルテスト"""

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
    time.sleep(5)

    # 座標値を確認
    print("\n【5. 座標値を確認】")
    lat_inputs = driver.find_elements(By.XPATH, "//input[@step='0.000001']")
    lat_value = lat_inputs[0].get_attribute('value') if len(lat_inputs) >= 1 else ''
    lng_value = lat_inputs[1].get_attribute('value') if len(lat_inputs) >= 2 else ''
    print(f"   緯度: '{lat_value}'")
    print(f"   経度: '{lng_value}'")

    if lat_value and lng_value:
        print("   ✅ 座標取得成功!")

        # 保存ボタンをクリック
        print("\n【6. 保存ボタンをクリック】")
        save_button = driver.find_element(By.XPATH, "//button[contains(text(), '保存')]")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_button)
        time.sleep(0.5)
        save_button.click()
        print("   ✅ 保存ボタンをクリック")

        # 保存完了を待つ
        time.sleep(5)
        driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/coord_save_01.png")

        # ページをリロード
        print("\n【7. ページをリロード】")
        driver.refresh()
        time.sleep(5)

        # 所在地タブに移動
        tabs = driver.find_elements(By.XPATH, "//button[contains(text(), '所在地')]")
        if tabs:
            tabs[0].click()
            time.sleep(2)

        # 位置情報セクションにスクロール
        location_section = driver.find_element(By.XPATH, "//h4[contains(text(), '位置情報')]")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", location_section)
        time.sleep(1)

        # 座標値を確認
        print("\n【8. リロード後の座標値を確認】")
        lat_inputs = driver.find_elements(By.XPATH, "//input[@step='0.000001']")
        lat_after = lat_inputs[0].get_attribute('value') if len(lat_inputs) >= 1 else ''
        lng_after = lat_inputs[1].get_attribute('value') if len(lat_inputs) >= 2 else ''
        print(f"   緯度: '{lat_after}'")
        print(f"   経度: '{lng_after}'")

        if lat_after and lng_after:
            print("   ✅ 座標が保存されています!")
        else:
            print("   ⚠️ 座標が保存されていません")

        driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/coord_save_02.png")
    else:
        print("   ⚠️ 座標取得失敗")

    # コンソールエラー確認
    print("\n【9. コンソールエラー確認】")
    logs = driver.get_log('browser')
    errors = [log for log in logs if log['level'] == 'SEVERE' and 'favicon' not in log['message'] and 'Warning' not in log['message']]
    if errors:
        print("   ⚠️ エラー検出:")
        for err in errors[:3]:
            print(f"      {err['message'][:150]}")
    else:
        print("   ✅ 重大なエラーなし")

    print("\n【テスト完了】")
    print("\n画面を5秒間表示します...")
    time.sleep(5)

finally:
    driver.quit()
