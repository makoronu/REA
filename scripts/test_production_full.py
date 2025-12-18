#!/usr/bin/env python3
"""本番環境で物件一覧を確認"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

options = webdriver.ChromeOptions()
options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.set_page_load_timeout(30)

# テスト用認証情報（環境変数から取得、またはデフォルト）
EMAIL = os.environ.get('TEST_EMAIL', 'test@example.com')
PASSWORD = os.environ.get('TEST_PASSWORD', 'password')

try:
    # ログインページにアクセス
    print("ログインページにアクセス...")
    driver.get("https://realestateautomation.net/login")
    time.sleep(2)

    # ログイン
    print(f"ログイン中... ({EMAIL})")
    email_input = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
    password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")

    email_input.send_keys(EMAIL)
    password_input.send_keys(PASSWORD)

    login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    login_button.click()

    print("ログインボタンクリック後、3秒待機...")
    time.sleep(3)
    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/prod_after_login.png")
    print(f"現在のURL: {driver.current_url}")

    # ログイン成功したか確認
    if "/login" not in driver.current_url:
        print("✅ ログイン成功")

        # 物件一覧ページに移動
        print("\n物件一覧ページに移動...")
        driver.get("https://realestateautomation.net/properties")
        time.sleep(5)
        driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/prod_properties_list.png")
        print(f"URL: {driver.current_url}")

        # テーブルの内容を確認
        body = driver.find_element(By.TAG_NAME, "body")
        print(f"\nページ内容（先頭800文字）:\n{body.text[:800]}")

        # テーブル行数を確認
        rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
        print(f"\nテーブル行数: {len(rows)}")

        # スケルトンローディングの有無
        skeletons = driver.find_elements(By.CSS_SELECTOR, ".animate-pulse")
        print(f"スケルトンローディング: {len(skeletons)}個")

        # エラーメッセージの有無
        error_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='error'], [class*='Error']")
        print(f"エラー要素: {len(error_elements)}個")

    else:
        print("❌ ログイン失敗")
        body = driver.find_element(By.TAG_NAME, "body")
        print(f"ページ内容:\n{body.text[:500]}")

    # コンソールログ
    print("\n--- ブラウザコンソールログ ---")
    logs = driver.get_log('browser')
    for log in logs[-30:]:
        print(f"{log['level']}: {log['message'][:200]}")

except Exception as e:
    print(f"エラー: {e}")
    import traceback
    traceback.print_exc()
    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/prod_full_error.png")

finally:
    print("\n完了。Enterで終了...")
    try:
        input()
    except:
        pass
    driver.quit()
