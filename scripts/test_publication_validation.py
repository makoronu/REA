"""
公開時バリデーションテスト

テスト内容:
1. ログイン
2. 物件編集画面を開く
3. 公開ステータスを「公開」に変更して保存
4. バリデーションエラーモーダルが表示されることを確認

使用方法:
PYTHONPATH=. python3 scripts/test_publication_validation.py
"""

import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# 設定
BASE_URL = "http://localhost:5173"
API_URL = "http://localhost:8005"
TEST_EMAIL = "admin@shirokuma.co.jp"
TEST_PASSWORD = "test1234"

def setup_driver():
    """ヘッドレスモードでChrome起動"""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)

def wait_and_click(driver, by, value, timeout=10):
    """要素を待機してクリック"""
    element = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )
    element.click()
    return element

def wait_for_element(driver, by, value, timeout=10):
    """要素を待機"""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )

def login(driver):
    """ログイン処理"""
    print("  ログイン中...")
    driver.get(f"{BASE_URL}/login")
    time.sleep(1)

    # メールアドレス入力
    email_input = wait_for_element(driver, By.CSS_SELECTOR, "input[type='email']")
    email_input.clear()
    email_input.send_keys(TEST_EMAIL)

    # パスワード入力
    password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
    password_input.clear()
    password_input.send_keys(TEST_PASSWORD)

    # ログインボタンクリック
    login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    login_button.click()

    # ログイン完了を待機
    time.sleep(2)

    # URLが変わったか確認
    if "/login" not in driver.current_url:
        print("  ✓ ログイン成功")
        return True
    else:
        print("  ✗ ログイン失敗")
        return False

def test_publication_validation(driver):
    """公開バリデーションテスト"""
    print("\n[テスト] 公開バリデーション")

    # 既存のdetached物件（ID 2479）で直接テスト
    PROPERTY_ID = 2479
    print(f"  物件ID {PROPERTY_ID} の編集ページに移動中...")
    driver.get(f"{BASE_URL}/properties/{PROPERTY_ID}/edit")
    time.sleep(3)

    # 1. ページが読み込まれたことを確認
    print("  ページ読み込み確認中...")
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), '物件編集')]"))
        )
        print("  ✓ 物件編集ページ表示")
    except:
        driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/edit_page_load.png")
        print("  物件編集ページへの移動を確認中...")

    # 2. 案件ステータスを「販売中」に変更
    print("  案件ステータスを「販売中」に変更中...")
    try:
        sales_status_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '販売中')]"))
        )
        sales_status_button.click()
        time.sleep(1)
        print("  ✓ 案件ステータスを「販売中」に変更")
    except Exception as e:
        print(f"  ✗ 案件ステータスの変更に失敗: {e}")
        driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/status_change_fail.png")
        return False

    # 3. 公開ステータスを「公開」に変更（販売中にすると自動で公開になるはず）
    print("  公開ステータスを「公開」に変更中...")
    try:
        pub_button = driver.find_element(By.XPATH, "//button[contains(text(), '公開') and not(contains(text(), '非'))]")
        if not pub_button.get_attribute("style") or "solid" not in pub_button.get_attribute("style"):
            pub_button.click()
            time.sleep(1)
        print("  ✓ 公開ステータスを「公開」に変更")
    except Exception as e:
        print(f"  公開ステータス変更をスキップ: {e}")

    # 4. 保存ボタンをクリック
    print("  保存ボタンをクリック中...")
    try:
        save_button = driver.find_element(By.XPATH, "//button[contains(text(), '保存')]")
        save_button.click()
        time.sleep(3)
    except Exception as e:
        print(f"  ✗ 保存ボタンのクリックに失敗: {e}")
        return False

    # 8. バリデーションエラーモーダルが表示されることを確認
    print("  バリデーションエラーモーダルを確認中...")
    try:
        # モーダルのタイトルを探す
        error_modal = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), '公開に必要な項目が未入力です')]"))
        )
        print("  ✓ バリデーションエラーモーダルが表示された")

        # グループ名が表示されているか確認
        group_elements = driver.find_elements(By.XPATH, "//div[contains(@style, 'FEF2F2')]//div[contains(@style, 'fontWeight')]")
        if group_elements:
            print(f"  ✓ {len(group_elements)}個のグループが表示された")
            for elem in group_elements[:3]:  # 最初の3つを表示
                print(f"    - {elem.text}")

        return True
    except Exception as e:
        # モーダルが表示されない場合、エラーバナーを確認
        try:
            error_banner = driver.find_element(By.XPATH, "//div[contains(text(), '項目が必要です')]")
            print(f"  ✓ エラーバナーが表示された: {error_banner.text[:50]}...")
            return True
        except:
            pass

        print(f"  ✗ バリデーションエラーの表示確認に失敗: {e}")
        # スクリーンショットを保存
        driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/validation_error_test.png")
        print("  スクリーンショットを保存: test_screenshots/validation_error_test.png")
        return False

def cleanup_test_property(driver):
    """テスト用物件を削除"""
    # TODO: 必要に応じて実装
    pass

def main():
    print("=" * 60)
    print("公開時バリデーションテスト")
    print("=" * 60)

    driver = None
    try:
        driver = setup_driver()

        # ログイン
        if not login(driver):
            print("\n✗ テスト失敗: ログインできませんでした")
            return 1

        # 公開バリデーションテスト
        if test_publication_validation(driver):
            print("\n" + "=" * 60)
            print("✓ テスト成功: 公開バリデーションが正常に動作しています")
            print("=" * 60)
            return 0
        else:
            print("\n" + "=" * 60)
            print("✗ テスト失敗: 公開バリデーションに問題があります")
            print("=" * 60)
            return 1

    except Exception as e:
        print(f"\n✗ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    sys.exit(main())
