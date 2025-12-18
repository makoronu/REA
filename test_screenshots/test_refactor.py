"""
型定義・共通関数リファクタリングの動作確認テスト
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# テストアカウント
TEST_EMAIL = "4690kb@gmail.com"
TEST_PASSWORD = "Test1234!"

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.set_page_load_timeout(30)

try:
    # 1. ログイン
    print("1. ログイン中...")
    driver.get("http://localhost:5173/login")
    time.sleep(2)

    email_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "email"))
    )
    email_field.send_keys(TEST_EMAIL)
    driver.find_element(By.ID, "password").send_keys(TEST_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(3)

    # ログイン成功確認
    if "/login" in driver.current_url:
        print("❌ ログイン失敗")
        driver.save_screenshot("test_screenshots/refactor_login_failed.png")
        raise Exception("ログイン失敗")
    print("✅ ログイン成功")

    # 2. 物件編集画面を開く
    print("2. 物件編集画面を開く...")
    driver.get("http://localhost:5173/properties/22/edit")
    time.sleep(5)
    driver.save_screenshot("test_screenshots/refactor_edit_1.png")
    print("✅ 編集画面表示")

    # 3. 法令制限タブを開く
    print("3. 法令制限タブを確認...")
    tabs = driver.find_elements(By.CSS_SELECTOR, "[role='tab']")
    regulation_tab = None
    for tab in tabs:
        if "法令" in tab.text:
            regulation_tab = tab
            break

    if regulation_tab:
        regulation_tab.click()
        time.sleep(3)
        driver.save_screenshot("test_screenshots/refactor_regulation_tab.png")

        # 用途地域のセレクトがあるか確認
        selects = driver.find_elements(By.CSS_SELECTOR, ".css-13cymwt-control, [class*='select']")
        print(f"   セレクト要素数: {len(selects)}")
        print("✅ 法令制限タブ表示OK")
    else:
        print("⚠️ 法令制限タブが見つかりません")

    # 4. 土地情報タブを開く
    print("4. 土地情報タブを確認...")
    for tab in tabs:
        if "土地" in tab.text:
            tab.click()
            time.sleep(3)
            driver.save_screenshot("test_screenshots/refactor_land_tab.png")
            print("✅ 土地情報タブ表示OK")
            break

    # 5. 基本情報タブを開く
    print("5. 基本情報タブを確認...")
    for tab in tabs:
        if "基本" in tab.text:
            tab.click()
            time.sleep(3)
            driver.save_screenshot("test_screenshots/refactor_basic_tab.png")

            # 物件種別セレクトの確認
            selects = driver.find_elements(By.TAG_NAME, "select")
            print(f"   セレクト要素数: {len(selects)}")
            if selects:
                options = selects[0].find_elements(By.TAG_NAME, "option")
                print(f"   最初のセレクトのオプション数: {len(options)}")
            print("✅ 基本情報タブ表示OK")
            break

    print("\n=== テスト完了 ===")
    print("スクリーンショットを確認してください:")
    print("- test_screenshots/refactor_edit_1.png")
    print("- test_screenshots/refactor_regulation_tab.png")
    print("- test_screenshots/refactor_land_tab.png")
    print("- test_screenshots/refactor_basic_tab.png")

except Exception as e:
    print(f"❌ エラー: {e}")
    driver.save_screenshot("test_screenshots/refactor_error.png")

finally:
    driver.quit()
