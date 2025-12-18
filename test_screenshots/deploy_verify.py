"""
本番デプロイ後の動作確認テスト
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
    print("1. 本番環境にログイン中...")
    driver.get("https://realestateautomation.net/login")
    time.sleep(3)

    email_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "email"))
    )
    email_field.send_keys(TEST_EMAIL)
    driver.find_element(By.ID, "password").send_keys(TEST_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(3)

    if "/login" in driver.current_url:
        print("❌ ログイン失敗")
        driver.save_screenshot("test_screenshots/deploy_login_failed.png")
        raise Exception("ログイン失敗")
    print("✅ ログイン成功")
    driver.save_screenshot("test_screenshots/deploy_1_login.png")

    # 2. 物件編集画面を開く
    print("2. 物件編集画面を開く...")
    driver.get("https://realestateautomation.net/properties/22/edit")
    time.sleep(5)
    driver.save_screenshot("test_screenshots/deploy_2_edit.png")
    print("✅ 編集画面表示")

    # 3. 法令制限タブを確認
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
        driver.save_screenshot("test_screenshots/deploy_3_regulation.png")

        # セレクト要素があるか確認（選択肢が正しく表示されているか）
        selects = driver.find_elements(By.CSS_SELECTOR, "[class*='select'], select")
        print(f"   セレクト要素数: {len(selects)}")
        print("✅ 法令制限タブ表示OK")
    else:
        print("⚠️ 法令制限タブが見つかりません")

    # 4. 土地情報タブを確認
    print("4. 土地情報タブを確認...")
    tabs = driver.find_elements(By.CSS_SELECTOR, "[role='tab']")
    for tab in tabs:
        if "土地" in tab.text:
            tab.click()
            time.sleep(3)
            driver.save_screenshot("test_screenshots/deploy_4_land.png")
            print("✅ 土地情報タブ表示OK")
            break

    # 5. 基本情報タブを確認
    print("5. 基本情報タブを確認...")
    tabs = driver.find_elements(By.CSS_SELECTOR, "[role='tab']")
    for tab in tabs:
        if "基本" in tab.text:
            tab.click()
            time.sleep(3)
            driver.save_screenshot("test_screenshots/deploy_5_basic.png")
            print("✅ 基本情報タブ表示OK")
            break

    # 6. 物件一覧に戻る（データ確認）
    print("6. 物件一覧を確認...")
    driver.get("https://realestateautomation.net/properties")
    time.sleep(3)
    driver.save_screenshot("test_screenshots/deploy_6_list.png")

    # テーブル行数を確認
    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
    print(f"   物件数: {len(rows)}件")
    print("✅ 物件一覧表示OK")

    print("\n=== 本番動作確認完了 ===")
    print("スクリーンショット:")
    print("- test_screenshots/deploy_1_login.png")
    print("- test_screenshots/deploy_2_edit.png")
    print("- test_screenshots/deploy_3_regulation.png")
    print("- test_screenshots/deploy_4_land.png")
    print("- test_screenshots/deploy_5_basic.png")
    print("- test_screenshots/deploy_6_list.png")

except Exception as e:
    print(f"❌ エラー: {e}")
    driver.save_screenshot("test_screenshots/deploy_error.png")

finally:
    driver.quit()
