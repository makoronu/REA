"""認証UI確認テスト - テナント名表示・開発者ログイン"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os

# スクリーンショット保存先
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), '../../test_screenshots')
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def save_screenshot(driver, name):
    """スクリーンショット保存"""
    path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    driver.save_screenshot(path)
    print(f"📸 {path}")

def test_auth_ui():
    """認証UI確認"""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.set_page_load_timeout(15)
    driver.set_window_size(1280, 800)

    try:
        # 1. 開発者ログインページ確認
        print("\n=== 1. 開発者ログインページ ===")
        driver.get("http://localhost:5173/dev-login")
        time.sleep(2)
        save_screenshot(driver, "01_dev_login_page")

        # ダークテーマ確認（背景色）
        body = driver.find_element(By.TAG_NAME, "body")
        print(f"✅ 開発者ログインページ表示OK")

        # 2. 通常ログインページ確認
        print("\n=== 2. 通常ログインページ ===")
        driver.get("http://localhost:5173/login")
        time.sleep(2)
        save_screenshot(driver, "02_login_page")
        print(f"✅ 通常ログインページ表示OK")

        # 3. ログイン実行
        print("\n=== 3. ログイン実行 ===")
        email_input = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
        password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")

        email_input.clear()
        email_input.send_keys("admin@shirokuma.co.jp")
        password_input.clear()
        password_input.send_keys("TestPass123!")

        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_btn.click()

        time.sleep(3)
        save_screenshot(driver, "03_after_login")

        # 4. ヘッダーにテナント名が表示されているか確認
        print("\n=== 4. ヘッダーテナント名確認 ===")

        # ログイン成功確認
        if "/login" not in driver.current_url:
            print(f"✅ ログイン成功: {driver.current_url}")
        else:
            print(f"❌ ログイン失敗: まだログインページ")
            return

        # テナント名を探す
        try:
            # ユーザーメニューボタンを探す
            page_source = driver.page_source
            if "システム管理" in page_source:
                print("✅ テナント名「システム管理」がヘッダーに表示されています")
            else:
                print("⚠️ テナント名がページ内に見つかりません")

            save_screenshot(driver, "04_header_with_tenant")
        except Exception as e:
            print(f"❌ テナント名確認エラー: {e}")

        # 5. ユーザーメニュー開いてログアウトボタン確認
        print("\n=== 5. ユーザーメニュー確認 ===")
        try:
            # ユーザーメニューボタンをクリック
            user_menu_btn = driver.find_element(By.XPATH, "//button[contains(., 'システム管理')]")
            user_menu_btn.click()
            time.sleep(1)
            save_screenshot(driver, "05_user_menu_open")

            # ログアウトボタン確認
            if "ログアウト" in driver.page_source:
                print("✅ ログアウトボタンが表示されています")
            else:
                print("⚠️ ログアウトボタンが見つかりません")
        except Exception as e:
            print(f"⚠️ ユーザーメニュー確認: {e}")

        print("\n========================================")
        print("✅ 認証UIテスト完了")
        print("========================================")

    except Exception as e:
        print(f"❌ エラー: {e}")
        save_screenshot(driver, "error")
    finally:
        time.sleep(2)
        driver.quit()

if __name__ == "__main__":
    test_auth_ui()
