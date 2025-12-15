#!/usr/bin/env python3
"""登記取込ページの完全フローテスト
1. PDFアップロード
2. 解析
3. 登記レコード表示
4. 既存物件へ反映モーダル確認
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# テスト用PDF
TEST_PDF = "/Users/yaguchimakoto/my_programing/REA/rea-api/uploads/touki/網走郡美幌町字青葉一丁目６－６不動産登記（土地全部事項）2025120101673995.PDF"

options = webdriver.ChromeOptions()
options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)
driver.set_page_load_timeout(60)
driver.set_window_size(1400, 900)

try:
    print("【1. 登記取込ページを開く】")
    driver.get("http://localhost:5173/import/touki")
    time.sleep(3)
    print("   ✅ ページ表示完了")

    # ファイル選択
    print("\n【2. PDFをアップロード】")
    file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
    file_input.send_keys(TEST_PDF)
    time.sleep(3)
    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/touki_uploaded.png")
    print("   ✅ PDFアップロード完了")

    # 未解析のPDFがあるか確認
    print("\n【3. 解析ボタンをクリック】")
    try:
        parse_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), '解析')]"))
        )
        parse_button.click()
        time.sleep(4)
        print("   ✅ 解析完了")
    except Exception as e:
        print(f"   ⚠️ 解析ボタンが見つからない（既に解析済みかも）: {e}")

    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/touki_parsed.png")

    # 登記レコードがあるか確認
    print("\n【4. 登記レコード確認】")
    time.sleep(2)
    body_text = driver.find_element(By.TAG_NAME, "body").text

    # チェックボックスを探す
    checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
    if checkboxes:
        print(f"   登記レコード: {len(checkboxes)}件")

        # 最初のチェックボックスをクリック
        print("\n【5. 登記レコードを選択】")
        checkboxes[0].click()
        time.sleep(1)
        driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/touki_selected.png")
        print("   ✅ レコードを選択しました")

        # アクションバーを確認
        print("\n【6. アクションバー確認】")
        action_bar = driver.find_element(By.XPATH, "//div[contains(@class, 'bg-blue-50')]")
        if action_bar:
            print("   ✅ アクションバーが表示されています")

            # 「既存物件へ反映」ボタン確認
            apply_button = driver.find_element(By.XPATH, "//button[contains(text(), '既存物件へ反映')]")
            print("   ✅ 「既存物件へ反映」ボタンが表示されています")

            # クリックしてモーダル表示
            print("\n【7. 既存物件へ反映モーダルを開く】")
            apply_button.click()
            time.sleep(1)
            driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/touki_apply_modal.png")

            # モーダルの確認
            modal = driver.find_element(By.XPATH, "//div[contains(@class, 'fixed')]//h3")
            print(f"   モーダルタイトル: {modal.text}")
            print("   ✅ モーダルが表示されています")

            # 物件ID入力欄
            property_id_input = driver.find_element(By.CSS_SELECTOR, "input[type='number']")
            print("   ✅ 物件ID入力欄があります")

            # キャンセルボタンをクリック
            cancel_button = driver.find_element(By.XPATH, "//button[contains(text(), 'キャンセル')]")
            cancel_button.click()
            time.sleep(0.5)
            print("   ✅ モーダルを閉じました")

    else:
        print("   登記レコードがありません（PDF解析に失敗したか、既に登録済み）")

    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/touki_final.png")

    # コンソールエラー確認
    print("\n【8. コンソールエラー確認】")
    logs = driver.get_log('browser')
    errors = [log for log in logs if log['level'] == 'SEVERE' and 'favicon' not in log['message']]
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
