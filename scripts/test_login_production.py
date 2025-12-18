#!/usr/bin/env python3
"""本番環境にログインして物件表示を確認"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

options = webdriver.ChromeOptions()
options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.set_page_load_timeout(30)

try:
    # ログインページにアクセス
    print("ログインページにアクセス...")
    driver.get("https://realestateautomation.net/login")
    time.sleep(3)
    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/prod_login_page.png")
    print(f"URL: {driver.current_url}")

    # ページの内容を確認
    body = driver.find_element(By.TAG_NAME, "body")
    print(f"\nページ内容:\n{body.text[:500]}")

    # メールフィールドを探す
    email_fields = driver.find_elements(By.CSS_SELECTOR, "input[type='email'], input[name='email'], input#email")
    print(f"\nメールフィールド数: {len(email_fields)}")

    for i, field in enumerate(email_fields):
        print(f"  フィールド{i}: id={field.get_attribute('id')}, name={field.get_attribute('name')}, type={field.get_attribute('type')}")

    # パスワードフィールドを探す
    password_fields = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
    print(f"\nパスワードフィールド数: {len(password_fields)}")

    # ブラウザコンソールログを確認
    print("\n--- ブラウザコンソールログ ---")
    logs = driver.get_log('browser')
    for log in logs[-20:]:  # 最後の20件
        print(f"{log['level']}: {log['message']}")

except Exception as e:
    print(f"エラー: {e}")
    import traceback
    traceback.print_exc()
    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/prod_error.png")

finally:
    input("\n確認が終わったらEnterを押してください...")
    driver.quit()
