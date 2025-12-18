#!/usr/bin/env python3
"""本番環境でログイン後のテスト"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import os

options = webdriver.ChromeOptions()
options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.set_page_load_timeout(30)

try:
    # 本番サイトにアクセス
    print("本番サイトにアクセス...")
    driver.get("https://realestateautomation.net/")
    time.sleep(3)
    print(f"現在のURL: {driver.current_url}")
    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/prod_test_1.png")

    # ログインページにいるか確認
    if "/login" in driver.current_url:
        print("\n=== ログインページです ===")
        print("ログインしてください。ブラウザを開いたままにしています...")
        print("ログイン後、物件一覧ページ(/properties)に移動してからEnterを押してください。")
        input("\n>>> Enterを押して続行...")

    # 現在のページの状態を確認
    print(f"\n現在のURL: {driver.current_url}")
    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/prod_test_2.png")

    # 物件一覧ページに移動
    if "/properties" not in driver.current_url:
        print("\n物件一覧ページに移動...")
        driver.get("https://realestateautomation.net/properties")
        time.sleep(5)
        print(f"現在のURL: {driver.current_url}")

    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/prod_test_properties.png")

    # ページの状態を詳細に確認
    print("\n=== ページ状態 ===")

    # テーブル行数
    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
    print(f"テーブル行数: {len(rows)}")

    # スケルトンローディング
    skeletons = driver.find_elements(By.CSS_SELECTOR, ".animate-pulse")
    print(f"スケルトン数: {len(skeletons)}")

    # 「該当する物件がありません」メッセージ
    no_data = driver.find_elements(By.XPATH, "//*[contains(text(), '該当する物件がありません')]")
    print(f"「該当なし」メッセージ: {'あり' if no_data else 'なし'}")

    # エラーメッセージ
    errors = driver.find_elements(By.XPATH, "//*[contains(text(), '失敗')]")
    print(f"エラーメッセージ: {'あり' if errors else 'なし'}")

    # ページコンテンツ
    body = driver.find_element(By.TAG_NAME, "body")
    print(f"\nページ内容（先頭1000文字）:\n{body.text[:1000]}")

    # コンソールログ
    print("\n=== ブラウザコンソールログ ===")
    logs = driver.get_log('browser')
    for log in logs:
        print(f"{log['level']}: {log['message'][:200]}")

    # APIレスポンスをテスト
    print("\n=== APIテスト ===")
    api_result = driver.execute_script("""
        const token = localStorage.getItem('rea_auth_token');
        return fetch('https://realestateautomation.net/api/v1/properties/?limit=3', {
            headers: token ? {'Authorization': 'Bearer ' + token} : {}
        })
        .then(r => r.json().then(data => ({
            status: r.status,
            ok: r.ok,
            count: Array.isArray(data) ? data.length : 'not array',
            first: Array.isArray(data) && data.length > 0 ? data[0].property_name : null
        })))
        .catch(e => ({error: e.message}));
    """)
    time.sleep(1)
    print(f"APIレスポンス: {json.dumps(api_result, ensure_ascii=False, indent=2)}")

    print("\n終了するにはEnterを押してください...")
    input()

except Exception as e:
    print(f"エラー: {e}")
    import traceback
    traceback.print_exc()
    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/prod_test_error.png")

finally:
    driver.quit()
