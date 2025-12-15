#!/usr/bin/env python3
"""保存ボタンと自動保存のテスト"""

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
driver.set_page_load_timeout(30)

try:
    print("【テスト開始】")
    driver.get("http://localhost:5173/properties/55/edit")

    # 画面ロード待ち
    wait = WebDriverWait(driver, 15)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
    time.sleep(3)

    # 保存ボタンを探す
    print("\n【保存ボタンを確認】")
    try:
        save_button = driver.find_element(By.XPATH, "//button[contains(text(), '保存')]")
        print(f"  ✅ 保存ボタン発見: {save_button.text}")
        print(f"     クラス: {save_button.get_attribute('class')}")
    except Exception as e:
        print(f"  ❌ 保存ボタンなし: {e}")

    # 入力フィールドを変更してみる
    print("\n【フィールド編集テスト】")
    try:
        # catch_copyを探す
        catch_copy_input = driver.find_element(By.NAME, "catch_copy")
        original_value = catch_copy_input.get_attribute("value")
        print(f"  現在のcatch_copy: {original_value}")

        # 値を変更
        new_value = f"テスト更新 {int(time.time())}"
        catch_copy_input.clear()
        catch_copy_input.send_keys(new_value)
        print(f"  新しい値: {new_value}")

        # 5秒待って自動保存を確認
        print("\n【自動保存確認（5秒待機）】")
        time.sleep(5)

        # 保存状態を確認
        try:
            saved_indicator = driver.find_element(By.XPATH, "//div[contains(text(), '保存しました')]")
            print(f"  ✅ 自動保存成功: {saved_indicator.text}")
        except:
            print("  保存インジケータ未検出（自動保存なしまたはエラー）")

        # コンソールエラーを確認
        print("\n【コンソールログ確認】")
        logs = driver.get_log('browser')
        errors = [log for log in logs if 'error' in log['message'].lower() or '500' in log['message']]
        if errors:
            print("  ⚠️ エラー検出:")
            for err in errors:
                print(f"     {err['message'][:200]}")
        else:
            print("  ✅ エラーなし")

    except Exception as e:
        print(f"  ❌ テスト失敗: {e}")

    # 保存ボタンをクリックして手動保存
    print("\n【手動保存テスト】")
    try:
        save_button = driver.find_element(By.XPATH, "//button[contains(text(), '保存')]")
        save_button.click()
        print("  保存ボタンをクリック")

        time.sleep(3)

        # 保存結果を確認
        try:
            saved_indicator = driver.find_element(By.XPATH, "//div[contains(text(), '保存しました')]")
            print(f"  ✅ 手動保存成功: {saved_indicator.text}")
        except:
            try:
                error_indicator = driver.find_element(By.XPATH, "//div[contains(text(), 'エラー') or contains(text(), '失敗')]")
                print(f"  ❌ 保存エラー: {error_indicator.text}")
            except:
                print("  結果不明（インジケータ未検出）")

    except Exception as e:
        print(f"  ❌ 手動保存失敗: {e}")

    # スクリーンショット保存
    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/save_button_test.png")
    print("\n✅ スクリーンショット保存: save_button_test.png")

    # 10秒表示
    print("\n画面を10秒間表示します...")
    time.sleep(10)

finally:
    driver.quit()
