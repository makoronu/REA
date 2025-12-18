#!/usr/bin/env python3
"""本番環境の物件表示をデバッグ"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

# ブラウザログを取得するための設定
options = webdriver.ChromeOptions()
options.set_capability('goog:loggingPrefs', {'browser': 'ALL', 'performance': 'ALL'})

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.set_page_load_timeout(30)

try:
    # 本番サイトにアクセス
    print("本番サイトにアクセス...")
    driver.get("https://realestateautomation.net/login")
    time.sleep(3)

    # スクリーンショット
    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/prod_debug_1.png")
    print(f"現在のURL: {driver.current_url}")

    # ブラウザコンソールログを取得
    print("\n--- ブラウザコンソールログ ---")
    logs = driver.get_log('browser')
    for log in logs:
        print(f"{log['level']}: {log['message']}")

    # ネットワークログを確認（パフォーマンスログから）
    print("\n--- ネットワークエラー ---")
    perf_logs = driver.get_log('performance')
    for log in perf_logs:
        try:
            msg = json.loads(log['message'])
            if 'Network.responseReceived' in str(msg):
                params = msg.get('message', {}).get('params', {})
                response = params.get('response', {})
                if response.get('status', 200) >= 400:
                    print(f"エラー: {response.get('url')} - {response.get('status')}")
        except:
            pass

    # LocalStorageの内容を確認
    print("\n--- LocalStorage ---")
    local_storage = driver.execute_script("return Object.keys(localStorage);")
    for key in local_storage:
        print(f"  {key}")

    # APIリクエストをテスト（ブラウザから）
    print("\n--- APIテスト（fetch） ---")
    result = driver.execute_script("""
        return fetch('https://realestateautomation.net/api/v1/properties?limit=3')
            .then(r => ({status: r.status, ok: r.ok, url: r.url, redirected: r.redirected}))
            .catch(e => ({error: e.message}));
    """)
    time.sleep(2)
    print(f"APIレスポンス: {result}")

except Exception as e:
    print(f"エラー: {e}")
    import traceback
    traceback.print_exc()
    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/prod_debug_error.png")

finally:
    input("\n確認が終わったらEnterを押してください...")
    driver.quit()
