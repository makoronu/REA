#!/usr/bin/env python3
"""本番サイトの物件表示を確認"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

options = webdriver.ChromeOptions()
options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.set_page_load_timeout(30)

try:
    # 本番サイトにアクセス（認証不要でAPIテスト）
    print("本番サイトにアクセス...")
    driver.get("https://realestateautomation.net/")
    time.sleep(3)
    print(f"URL: {driver.current_url}")

    # APIテスト
    print("\nAPIテスト...")
    result = driver.execute_script("""
        return fetch('https://realestateautomation.net/api/v1/properties/?limit=5')
            .then(r => r.json())
            .then(data => ({
                success: true,
                count: data.length,
                properties: data.map(p => ({id: p.id, name: p.property_name?.substring(0, 30)}))
            }))
            .catch(e => ({success: false, error: e.message}));
    """)
    time.sleep(1)
    print(f"結果: {json.dumps(result, ensure_ascii=False, indent=2)}")

    # コンソールログ確認
    print("\nコンソールログ:")
    logs = driver.get_log('browser')
    for log in logs[-5:]:
        print(f"  {log['level']}: {log['message'][:100]}")

except Exception as e:
    print(f"エラー: {e}")

finally:
    driver.quit()
    print("\n完了")
