#!/usr/bin/env python3
"""物件一覧の物件種別表示・検索・フィルター機能テスト"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = webdriver.ChromeOptions()
options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)
driver.set_page_load_timeout(60)
driver.set_window_size(1400, 900)

try:
    print("【1. 物件一覧ページを開く】")
    driver.get("http://localhost:5173/properties")
    time.sleep(3)
    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/properties_list_01_initial.png")
    print("   ✅ ページ表示完了")

    # 物件種別カラムを確認
    print("\n【2. 物件種別の表示確認】")
    try:
        # テーブルの物件種別カラムを取得
        table_body = driver.find_element(By.TAG_NAME, "tbody")
        rows = table_body.find_elements(By.TAG_NAME, "tr")

        if rows:
            # 最初の5行の物件種別を確認
            property_types_found = []
            for row in rows[:5]:
                cells = row.find_elements(By.TAG_NAME, "td")
                # 物件種別は5番目のカラム（デフォルト表示の場合）
                if len(cells) >= 5:
                    property_type = cells[4].text
                    property_types_found.append(property_type)
                    print(f"   物件種別: {property_type}")

            # 日本語が含まれているか確認
            japanese_found = any(any('\u3040' <= c <= '\u9fff' for c in pt) for pt in property_types_found if pt and pt != '-')
            if japanese_found:
                print("   ✅ 物件種別が日本語で表示されています")
            else:
                print("   ⚠️ 物件種別が英語IDのままです")
        else:
            print("   ⚠️ 物件データがありません")
    except Exception as e:
        print(f"   ⚠️ エラー: {e}")

    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/properties_list_02_property_type.png")

    # フィルター機能テスト
    print("\n【3. 物件種別フィルターのテスト】")
    try:
        # フィルターボタンをクリック
        filter_button = driver.find_element(By.XPATH, "//button[contains(text(), 'フィルター')]")
        filter_button.click()
        time.sleep(1)
        driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/properties_list_03_filter_open.png")
        print("   ✅ フィルターメニュー表示")

        # 物件種別フィルターボタンを探す
        filter_buttons = driver.find_elements(By.XPATH, "//div[contains(text(), '物件種別')]/..//button")
        if filter_buttons:
            # 最初のフィルターをクリック（例：一戸建て）
            first_filter = filter_buttons[0]
            filter_label = first_filter.text
            print(f"   フィルター選択: {filter_label}")
            first_filter.click()
            time.sleep(2)
            driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/properties_list_04_filter_applied.png")

            # フィルターチップが表示されるか確認
            body_text = driver.find_element(By.TAG_NAME, "body").text
            if "種別:" in body_text:
                print("   ✅ フィルターチップが表示されています")
            else:
                print("   ⚠️ フィルターチップが表示されていません")

            # フィルターが適用されたか確認（件数が変わる等）
            rows_after = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
            print(f"   フィルター後の行数: {len(rows_after)}")
        else:
            print("   ⚠️ 物件種別フィルターボタンが見つかりません")
    except Exception as e:
        print(f"   ⚠️ フィルターテストエラー: {e}")

    # 検索機能テスト
    print("\n【4. 検索機能のテスト】")
    try:
        # フィルターをクリア
        driver.get("http://localhost:5173/properties")
        time.sleep(2)

        # 検索ボックスに入力
        search_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='検索']")
        search_input.clear()
        search_input.send_keys("美幌")
        time.sleep(2)
        driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/properties_list_05_search.png")

        # 検索結果を確認
        rows_after_search = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
        print(f"   検索後の行数: {len(rows_after_search)}")

        if rows_after_search:
            # 検索結果に「美幌」が含まれているか確認
            body_text = driver.find_element(By.TAG_NAME, "tbody").text
            if "美幌" in body_text:
                print("   ✅ 検索結果に「美幌」が含まれています")
            else:
                print("   ⚠️ 検索結果に「美幌」が含まれていません")
    except Exception as e:
        print(f"   ⚠️ 検索テストエラー: {e}")

    # コンソールエラー確認
    print("\n【5. コンソールエラー確認】")
    logs = driver.get_log('browser')
    errors = [log for log in logs if log['level'] == 'SEVERE' and 'favicon' not in log['message']]
    if errors:
        print("   ⚠️ エラー検出:")
        for err in errors[:3]:
            print(f"      {err['message'][:150]}")
    else:
        print("   ✅ 重大なエラーなし")

    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/properties_list_06_final.png")

    print("\n【テスト完了】")
    print("\n画面を5秒間表示します...")
    time.sleep(5)

finally:
    driver.quit()
