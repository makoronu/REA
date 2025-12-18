#!/usr/bin/env python3
"""本番環境の物件表示を確認"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.set_page_load_timeout(30)

try:
    # 本番サイトにアクセス
    print("本番サイトにアクセス...")
    driver.get("https://realestateautomation.net/")
    time.sleep(3)

    # スクリーンショット
    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/prod_top.png")
    print(f"現在のURL: {driver.current_url}")
    print(f"タイトル: {driver.title}")

    # ログインページか確認
    if "/login" in driver.current_url:
        print("ログインページにリダイレクトされました")
        driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/prod_login.png")

    # 物件一覧ページに直接アクセス
    print("\n物件一覧ページにアクセス...")
    driver.get("https://realestateautomation.net/properties")
    time.sleep(3)
    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/prod_properties.png")
    print(f"現在のURL: {driver.current_url}")

    # ページのHTMLを取得
    body = driver.find_element(By.TAG_NAME, "body")
    print(f"\nページ内容（先頭500文字）:\n{body.text[:500]}")

    # コンソールエラーを確認
    logs = driver.get_log('browser')
    if logs:
        print("\n--- ブラウザコンソールログ ---")
        for log in logs:
            print(f"{log['level']}: {log['message']}")

except Exception as e:
    print(f"エラー: {e}")
    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/prod_error.png")

finally:
    input("\n確認が終わったらEnterを押してください...")
    driver.quit()
