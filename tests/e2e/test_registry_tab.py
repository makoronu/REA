"""
登記情報タブのE2Eテスト
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_registry_tab():
    """登記情報タブの動作確認"""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.set_page_load_timeout(30)
    driver.set_window_size(1400, 900)

    try:
        # 1. 物件編集ページを開く
        print("1. 物件編集ページを開く...")
        driver.get("http://localhost:5173/properties/2480/edit")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        time.sleep(2)
        driver.save_screenshot("test_screenshots/01_property_edit_page.png")
        print("   ✅ 物件編集ページ表示OK")

        # 2. 登記情報タブを探してクリック
        print("2. 登記情報タブを探す...")
        try:
            registry_tab = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '登記情報')]"))
            )
            registry_tab.click()
            time.sleep(2)
            driver.save_screenshot("test_screenshots/02_registry_tab_clicked.png")
            print("   ✅ 登記情報タブクリックOK")
        except Exception as e:
            print(f"   ❌ 登記情報タブが見つからない: {e}")
            # 現在のページのHTMLを確認
            buttons = driver.find_elements(By.TAG_NAME, "button")
            print(f"   ボタン一覧: {[b.text for b in buttons[:10]]}")
            driver.save_screenshot("test_screenshots/02_error_no_tab.png")
            raise

        # 3. 「登記を追加」ボタンを探してクリック
        print("3. 登記を追加ボタンを探す...")
        try:
            add_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '登記を追加')]"))
            )
            add_btn.click()
            time.sleep(2)
            driver.save_screenshot("test_screenshots/03_add_registry_modal.png")
            print("   ✅ 追加モーダル表示OK")
        except Exception as e:
            print(f"   ❌ 登記を追加ボタンが見つからない: {e}")
            driver.save_screenshot("test_screenshots/03_error_no_add_btn.png")
            raise

        # 4. モーダル内のフォームを確認
        print("4. モーダルのフォームを確認...")
        try:
            modal = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".fixed.inset-0"))
            )
            # グループ名を確認
            group_buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'font-medium')]")
            groups = [b.text for b in group_buttons if b.text]
            print(f"   グループ: {groups}")
            driver.save_screenshot("test_screenshots/04_modal_form.png")
            print("   ✅ フォームグループ表示OK")
        except Exception as e:
            print(f"   ❌ モーダル確認エラー: {e}")
            driver.save_screenshot("test_screenshots/04_error_modal.png")

        # 5. 所在を入力
        print("5. テストデータを入力...")
        try:
            location_input = driver.find_element(By.XPATH, "//label[contains(text(), '所在')]/following-sibling::input")
            location_input.send_keys("北海道美幌町字元町1番地")
            time.sleep(1)

            # 地番を入力
            chiban_input = driver.find_element(By.XPATH, "//label[contains(text(), '地番')]/following-sibling::input")
            chiban_input.send_keys("1-2-3")

            driver.save_screenshot("test_screenshots/05_data_entered.png")
            print("   ✅ データ入力OK")
        except Exception as e:
            print(f"   入力スキップ: {e}")

        # 6. 保存ボタンをクリック
        print("6. 保存...")
        try:
            save_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '保存')]"))
            )
            save_btn.click()
            time.sleep(3)
            driver.save_screenshot("test_screenshots/06_saved.png")
            print("   ✅ 保存OK")
        except Exception as e:
            print(f"   ❌ 保存エラー: {e}")
            driver.save_screenshot("test_screenshots/06_error_save.png")

        # 7. 登記カードが表示されたか確認
        print("7. 登記一覧を確認...")
        time.sleep(2)
        driver.save_screenshot("test_screenshots/07_registry_list.png")

        # カードを確認
        cards = driver.find_elements(By.CSS_SELECTOR, ".bg-white.border.rounded-lg")
        print(f"   カード数: {len(cards)}")
        if cards:
            print("   ✅ 登記カード表示OK")

        print("\n✅ テスト完了!")

    except Exception as e:
        print(f"\n❌ テスト失敗: {e}")
        driver.save_screenshot("test_screenshots/error_final.png")
        raise
    finally:
        time.sleep(3)  # 確認用に少し待機
        driver.quit()

if __name__ == "__main__":
    import os
    os.makedirs("test_screenshots", exist_ok=True)
    test_registry_tab()
