"""
登記情報モーダルのデバッグテスト
モーダルが表示されない問題を調査
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_registry_modal_debug():
    """モーダル表示のデバッグ"""
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
        time.sleep(3)
        print("   URL:", driver.current_url)

        # 2. タブを探す
        print("\n2. ボタン一覧を確認...")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for b in buttons:
            text = b.text.strip()
            if text:
                print(f"   - {text}")

        # 3. 登記情報タブをクリック
        print("\n3. 登記情報タブをクリック...")
        registry_tab = None
        for b in buttons:
            if "登記情報" in b.text:
                registry_tab = b
                break

        if registry_tab:
            registry_tab.click()
            time.sleep(2)
            driver.save_screenshot("test_screenshots/debug_01_registry_tab.png")
            print("   ✅ 登記情報タブクリック完了")
        else:
            print("   ❌ 登記情報タブが見つからない")
            return

        # 4. 登記を追加ボタンを探す
        print("\n4. 登記を追加ボタンを探す...")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        add_btn = None
        for b in buttons:
            if "登記を追加" in b.text:
                add_btn = b
                print(f"   見つかった: {b.text}")
                break

        if not add_btn:
            print("   ❌ 登記を追加ボタンが見つからない")
            # ページのHTML構造を確認
            page_source = driver.page_source
            if "登記を追加" in page_source:
                print("   (HTMLには存在する)")
            else:
                print("   (HTMLにも存在しない)")
            return

        # 5. クリックしてモーダルを開く
        print("\n5. モーダルを開く...")
        add_btn.click()
        time.sleep(2)
        driver.save_screenshot("test_screenshots/debug_02_after_click.png")

        # 6. モーダルの存在を確認
        print("\n6. モーダルの存在を確認...")
        modals = driver.find_elements(By.CSS_SELECTOR, ".fixed.inset-0")
        print(f"   .fixed.inset-0 要素数: {len(modals)}")

        # role="dialog" を探す
        dialogs = driver.find_elements(By.CSS_SELECTOR, "[role='dialog']")
        print(f"   role='dialog' 要素数: {len(dialogs)}")

        # モーダル風の要素を探す
        bg_opacity = driver.find_elements(By.CSS_SELECTOR, ".bg-opacity-50")
        print(f"   .bg-opacity-50 要素数: {len(bg_opacity)}")

        # 7. エラーメッセージを確認
        print("\n7. エラーを確認...")
        errors = driver.find_elements(By.CSS_SELECTOR, ".text-red-600, .text-red-500, [class*='error']")
        for e in errors:
            if e.text.strip():
                print(f"   エラー: {e.text}")

        # 8. コンソールログを確認
        print("\n8. ブラウザコンソールログ...")
        logs = driver.get_log('browser')
        for log in logs[-10:]:  # 最後の10件
            if log['level'] in ['SEVERE', 'WARNING']:
                print(f"   [{log['level']}] {log['message'][:100]}")

        # 9. モーダル内のh2タグ（タイトル）を探す
        print("\n9. モーダルタイトルを確認...")
        h2_tags = driver.find_elements(By.TAG_NAME, "h2")
        for h2 in h2_tags:
            text = h2.text.strip()
            if text:
                print(f"   h2: {text}")

        # 10. ローディング状態を確認
        print("\n10. ローディング状態を確認...")
        spinners = driver.find_elements(By.CSS_SELECTOR, ".animate-spin")
        print(f"    スピナー数: {len(spinners)}")

        # 11. 待機してもう一度確認
        print("\n11. 3秒待機後、再確認...")
        time.sleep(3)
        driver.save_screenshot("test_screenshots/debug_03_after_wait.png")

        spinners = driver.find_elements(By.CSS_SELECTOR, ".animate-spin")
        print(f"    スピナー数: {len(spinners)}")

        # グループボタンを確認
        groups = driver.find_elements(By.CSS_SELECTOR, "button.font-medium")
        print(f"    .font-medium ボタン数: {len(groups)}")

        # inputフィールドを確認
        inputs = driver.find_elements(By.CSS_SELECTOR, "input, select, textarea")
        print(f"    input/select/textarea数: {len(inputs)}")

        print("\n✅ デバッグ完了")

        # ユーザーが確認できるよう10秒待機
        print("\n10秒待機中（画面を確認してください）...")
        time.sleep(10)

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        driver.save_screenshot("test_screenshots/debug_error.png")
        raise
    finally:
        driver.quit()

if __name__ == "__main__":
    import os
    os.makedirs("test_screenshots", exist_ok=True)
    test_registry_modal_debug()
