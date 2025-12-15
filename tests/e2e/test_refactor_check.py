"""
共通化リファクタリング後の動作確認テスト
Seleniumでブラウザを開いて確認
"""
import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# スクリーンショット保存先
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'test_screenshots')
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def save_screenshot(driver, name):
    """スクリーンショットを保存"""
    timestamp = datetime.now().strftime('%H%M%S')
    filename = f"refactor_{timestamp}_{name}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    driver.save_screenshot(filepath)
    print(f"📸 Screenshot saved: {filename}")
    return filepath


def main():
    print("=" * 60)
    print("共通化リファクタリング後の動作確認")
    print("=" * 60)

    # Chrome起動（ヘッドレスではない）
    options = webdriver.ChromeOptions()
    options.add_argument('--window-size=1400,900')

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.set_page_load_timeout(15)

    try:
        # 1. 物件一覧ページ
        print("\n[1] 物件一覧ページを開く...")
        driver.get("http://localhost:5173/properties")
        time.sleep(2)
        save_screenshot(driver, "01_property_list")

        # 物件があるか確認
        try:
            rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            print(f"✅ 物件一覧: {len(rows)}件表示")
        except:
            print("⚠️ 物件一覧テーブルが見つかりません")

        # 2. 物件編集ページ（存在する物件を開く）
        print("\n[2] 物件編集ページを開く...")
        driver.get("http://localhost:5173/properties/1/edit")
        time.sleep(3)
        save_screenshot(driver, "02_property_edit")

        # タブが表示されているか確認
        try:
            tabs = driver.find_elements(By.CSS_SELECTOR, "[role='tab']")
            tab_names = [t.text for t in tabs if t.text]
            print(f"✅ タブ: {tab_names}")
        except:
            print("⚠️ タブが見つかりません")

        # フォームフィールドがあるか確認
        try:
            inputs = driver.find_elements(By.CSS_SELECTOR, "input, select, textarea")
            print(f"✅ フォームフィールド: {len(inputs)}個")
        except:
            print("⚠️ フォームフィールドが見つかりません")

        # 3. 土地情報タブをクリック
        print("\n[3] 土地情報タブを確認...")
        try:
            land_tab = driver.find_element(By.XPATH, "//button[contains(text(), '土地情報')]")
            land_tab.click()
            time.sleep(1)
            save_screenshot(driver, "03_land_tab")
            print("✅ 土地情報タブ表示")
        except Exception as e:
            print(f"⚠️ 土地情報タブ: {e}")

        # 4. 建物情報タブをクリック
        print("\n[4] 建物情報タブを確認...")
        try:
            building_tab = driver.find_element(By.XPATH, "//button[contains(text(), '建物情報')]")
            building_tab.click()
            time.sleep(1)
            save_screenshot(driver, "04_building_tab")
            print("✅ 建物情報タブ表示")
        except Exception as e:
            print(f"⚠️ 建物情報タブ: {e}")

        # 5. コンソールエラー確認
        print("\n[5] コンソールエラー確認...")
        logs = driver.get_log('browser')
        errors = [log for log in logs if log['level'] == 'SEVERE']
        if errors:
            print(f"❌ コンソールエラー: {len(errors)}件")
            for e in errors[:3]:
                print(f"   - {e['message'][:100]}")
        else:
            print("✅ コンソールエラーなし")

        # 6. APIエンドポイント確認
        print("\n[6] API確認（設備マスター）...")
        driver.get("http://localhost:8005/api/v1/equipment/categories")
        time.sleep(1)
        save_screenshot(driver, "05_api_equipment")

        page_text = driver.find_element(By.TAG_NAME, "body").text
        if "土地" in page_text or "[" in page_text:
            print("✅ 設備マスターAPI正常")
        else:
            print("⚠️ 設備マスターAPI確認")

        print("\n" + "=" * 60)
        print("テスト完了")
        print("=" * 60)
        print(f"\nスクリーンショット保存先: {SCREENSHOT_DIR}")

        # 最後に物件一覧を表示して終了
        driver.get("http://localhost:5173/properties")
        time.sleep(2)

        input("\n確認が終わったらEnterキーを押してください...")

    finally:
        driver.quit()
        print("\nブラウザを閉じました")


if __name__ == "__main__":
    main()
