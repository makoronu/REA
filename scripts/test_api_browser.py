#!/usr/bin/env python3
"""ブラウザからAPIリクエストをテスト"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

options = webdriver.ChromeOptions()
options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # 本番サイトにアクセス（コンテキストを取得）
    print("本番サイトにアクセス...")
    driver.get("https://realestateautomation.net/")
    time.sleep(2)

    # JavaScript経由でAPIリクエスト
    print("\nAPIリクエストをテスト...")
    result = driver.execute_script("""
        return new Promise((resolve) => {
            fetch('https://realestateautomation.net/api/v1/properties/?limit=3')
                .then(response => {
                    return response.json().then(data => ({
                        ok: response.ok,
                        status: response.status,
                        dataLength: Array.isArray(data) ? data.length : 'not array',
                        firstItem: Array.isArray(data) && data.length > 0 ? data[0].property_name : null
                    }));
                })
                .then(result => resolve(result))
                .catch(error => resolve({error: error.message}));
        });
    """)
    print(f"APIレスポンス: {json.dumps(result, ensure_ascii=False, indent=2)}")

    # ブラウザコンソールログ
    print("\n--- ブラウザコンソールログ ---")
    logs = driver.get_log('browser')
    for log in logs[-10:]:
        print(f"{log['level']}: {log['message'][:150]}")

    # LocalStorageの確認
    print("\n--- LocalStorage ---")
    storage = driver.execute_script("return JSON.stringify(localStorage);")
    print(storage[:500] if len(storage) > 500 else storage)

except Exception as e:
    print(f"エラー: {e}")
    import traceback
    traceback.print_exc()

finally:
    driver.quit()
    print("\n完了")
