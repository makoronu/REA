#!/usr/bin/env python3
"""座標取得・保存のデバッグテスト (クリック問題修正版)"""

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
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
    time.sleep(1)

    # 「位置情報」セクションを探す
    location_section = driver.find_element(By.XPATH, "//h4[contains(text(), '位置情報')]")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", location_section)
    time.sleep(1)
    print("   ✅ 位置情報セクションを表示")

    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/coord_debug3_01.png")

    # 座標取得ボタンをクリック（ActionChains使用）
    print("\n【4. 座標取得ボタンをクリック】")
    geocode_button = driver.find_element(By.XPATH, "//button[contains(text(), '住所から座標を取得')]")
    print(f"   ボタン状態: disabled={geocode_button.get_attribute('disabled')}")

    # ActionChainsでクリック
    actions = ActionChains(driver)
    actions.move_to_element(geocode_button).click().perform()
    print("   ✅ ActionChainsでクリック")
    time.sleep(5)

    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/coord_debug3_02.png")

    # コンソールログ確認
    print("\n【5. コンソールログ確認】")
    logs = driver.get_log('browser')
    for log in logs[-10:]:
        if 'SEVERE' in log['level'] or 'error' in log['message'].lower():
            print(f"   {log['level']}: {log['message'][:200]}")

    # 座標値を確認
    print("\n【6. 取得後の座標値を確認】")
    lat_inputs = driver.find_elements(By.XPATH, "//input[@step='0.000001']")
    if len(lat_inputs) >= 2:
        lat_value = lat_inputs[0].get_attribute('value')
        lng_value = lat_inputs[1].get_attribute('value')
        print(f"   緯度: '{lat_value}'")
        print(f"   経度: '{lng_value}'")

        if lat_value and lng_value:
            print("   ✅ 座標が取得されました!")

            # 保存処理を確認
            print("\n【7. 保存ボタンをクリック】")
            save_button = driver.find_element(By.XPATH, "//button[contains(text(), '保存')]")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_button)
            time.sleep(0.5)
            save_button.click()
            print("   ✅ 保存ボタンをクリック")
            time.sleep(4)

            # ページをリロードして確認
            print("\n【8. ページをリロードして確認】")
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

            lat_inputs = driver.find_elements(By.XPATH, "//input[@step='0.000001']")
            if len(lat_inputs) >= 2:
                lat_after = lat_inputs[0].get_attribute('value')
                lng_after = lat_inputs[1].get_attribute('value')
                print(f"   緯度（リロード後）: '{lat_after}'")
                print(f"   経度（リロード後）: '{lng_after}'")

                if lat_after and lng_after:
                    print("   ✅ 座標が保存されています!")
                else:
                    print("   ⚠️ 座標が保存されていません！")
        else:
            print("   ⚠️ 座標が取得されていません（APIエラーの可能性）")

            # メッセージを確認
            body_text = driver.find_element(By.TAG_NAME, "body").text
            if "座標の取得に失敗しました" in body_text:
                print("   エラーメッセージ: 座標の取得に失敗しました")
            elif "座標を取得しました" in body_text:
                print("   成功メッセージ: 座標を取得しました（しかし値が空）")
    else:
        print(f"   ⚠️ 座標入力欄が見つかりません（{len(lat_inputs)}個）")

    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/coord_debug3_03.png")

    print("\n【テスト完了】")
    print("\n画面を5秒間表示します...")
    time.sleep(5)

finally:
    driver.quit()
