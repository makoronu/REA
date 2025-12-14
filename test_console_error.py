"""
ブラウザコンソールエラーを確認するテスト
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def test():
    options = Options()
    options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1400, 900)

    try:
        print("編集画面を開いています...")
        driver.get("http://localhost:5173/properties/100/edit")
        time.sleep(5)

        # コンソールログを取得
        logs = driver.get_log('browser')
        print("\n=== ブラウザコンソールログ ===")
        for log in logs:
            print(f"[{log['level']}] {log['message']}")

        if not logs:
            print("コンソールログなし")

        # ページタイトルを確認
        print(f"\nページタイトル: {driver.title}")
        print(f"URL: {driver.current_url}")

        # body内容の長さを確認
        body = driver.find_element("tag name", "body")
        print(f"body内容の長さ: {len(body.text)} 文字")
        print(f"body内容: {body.text[:500] if body.text else '(空)'}")

    except Exception as e:
        print(f"エラー: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test()
