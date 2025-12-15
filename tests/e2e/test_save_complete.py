#!/usr/bin/env python3
"""保存機能の完全テスト"""

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

try:
    print("【1. ページロード】")
    driver.get("http://localhost:5173/properties/55/edit")
    wait = WebDriverWait(driver, 15)
    wait.until(EC.presence_of_element_located((By.NAME, "catch_copy")))
    time.sleep(3)
    print("   ✅ ページロード完了")

    # 値を変更
    print("\n【2. フィールド編集】")
    catch_copy_input = driver.find_element(By.NAME, "catch_copy")
    original_value = catch_copy_input.get_attribute("value")
    print(f"   現在の値: {original_value}")

    new_value = f"テスト保存 {int(time.time()) % 10000}"
    catch_copy_input.clear()
    catch_copy_input.send_keys(new_value)
    print(f"   新しい値: {new_value}")

    # 手動保存ボタンをクリック
    print("\n【3. 手動保存テスト】")
    save_button = driver.find_element(By.XPATH, "//button[contains(text(), '保存')]")
    save_button.click()
    print("   保存ボタンをクリック")

    # 保存結果を待つ
    time.sleep(4)

    # 保存成功の確認
    try:
        saved_indicator = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[contains(text(), '保存しました')]")
        ))
        print(f"   ✅ 保存成功: {saved_indicator.text}")
    except:
        print("   保存インジケータ未検出（タイムアウト）")

    # コンソールエラー確認
    print("\n【4. コンソールエラー確認】")
    logs = driver.get_log('browser')
    errors = [log for log in logs if log['level'] == 'SEVERE' and 'TypeError' in log['message']]
    if errors:
        print("   ❌ エラー検出:")
        for err in errors[:3]:
            print(f"      {err['message'][:150]}")
    else:
        print("   ✅ 重大なエラーなし")

    # ページリロードして保存を確認
    print("\n【5. 保存確認（リロード）】")
    driver.refresh()
    time.sleep(5)

    catch_copy_after = driver.find_element(By.NAME, "catch_copy")
    saved_value = catch_copy_after.get_attribute("value")
    print(f"   リロード後の値: {saved_value}")

    if saved_value == new_value:
        print("   ✅ 保存が正しく反映されています")
    else:
        print(f"   ⚠️ 値が一致しません（期待: {new_value}）")

    # スクリーンショット
    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/save_complete.png")
    print("\n✅ スクリーンショット保存: save_complete.png")

    # 5秒表示
    print("\n画面を5秒間表示します...")
    time.sleep(5)

finally:
    driver.quit()
    print("\n【テスト完了】")
