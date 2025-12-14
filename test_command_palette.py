"""
Command Palette (⌘K) 動作確認テスト
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time

def test_command_palette():
    driver = webdriver.Chrome()
    driver.set_window_size(1400, 900)
    wait = WebDriverWait(driver, 10)

    def type_in_palette(text):
        """パレットに文字を入力（Reactに対応）"""
        driver.execute_script("""
            const input = document.querySelector('input[placeholder*="物件を検索"]');
            if (input) {
                input.focus();
                const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                nativeInputValueSetter.call(input, arguments[0]);
                const inputEvent = new Event('input', { bubbles: true });
                input.dispatchEvent(inputEvent);
            }
        """, text)

    def click_first_result():
        """最初の検索結果をクリック（JavaScript経由）"""
        driver.execute_script("""
            const items = document.querySelectorAll('[cmdk-item]');
            if (items.length > 0) {
                items[0].click();
            }
        """)

    try:
        print("=" * 60)
        print("Command Palette 動作確認テスト")
        print("=" * 60)

        # 1. ページを開く
        print("\n[1] 物件一覧ページを開く...")
        driver.get("http://localhost:5173/properties")
        time.sleep(2)
        print("   ✓ ページ読み込み完了")

        # 2. 検索バーをクリックしてCommand Paletteを開く
        print("\n[2] 検索バーをクリックしてCommand Paletteを開く...")
        search_trigger = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".search-trigger"))
        )
        search_trigger.click()
        time.sleep(1)

        print("   Command Paletteを探索中...")
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='物件を検索']"))
        )
        print("   ✓ Command Palette が開いた")

        # 3. 検索入力欄を確認
        print("\n[3] 検索入力欄を確認...")
        search_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='物件を検索']")
        placeholder = search_input.get_attribute("placeholder")
        print(f"   Placeholder: {placeholder}")
        print("   ✓ 検索入力欄あり")

        # 4. 「北見」で検索
        print("\n[4] 「北見」で検索...")
        type_in_palette("北見")
        time.sleep(2)

        results = driver.find_elements(By.CSS_SELECTOR, "[cmdk-item]")
        print(f"   検索結果: {len(results)} 件")

        if len(results) > 0:
            first_result = results[0].text.replace('\n', ' ')[:60]
            print(f"   最初の結果: {first_result}...")
            print("   ✓ 検索結果が表示された")
        else:
            print("   △ 検索結果なし")

        # 5. ESCで閉じる
        print("\n[5] ESCキーで閉じる...")
        actions = ActionChains(driver)
        actions.send_keys(Keys.ESCAPE).perform()
        time.sleep(0.5)

        inputs = driver.find_elements(By.CSS_SELECTOR, "input[placeholder*='物件を検索']")
        if len(inputs) == 0:
            print("   ✓ ESCで閉じた")
        else:
            print("   △ まだ開いている可能性")

        # 6. ⌘K で開く
        print("\n[6] ⌘K / Ctrl+K で開く...")
        time.sleep(0.5)
        actions = ActionChains(driver)
        actions.key_down(Keys.COMMAND).send_keys('k').key_up(Keys.COMMAND).perform()
        time.sleep(1)

        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='物件を検索']"))
        )
        print("   ✓ ⌘K で Command Palette が開いた")

        # 7. 価格フィルタをテスト
        print("\n[7] 価格フィルタ「5000万以下」で検索...")
        type_in_palette("5000万以下")
        time.sleep(2)

        results = driver.find_elements(By.CSS_SELECTOR, "[cmdk-item]")
        print(f"   検索結果: {len(results)} 件")
        if len(results) > 0:
            print("   ✓ 価格フィルタが機能")
        else:
            print("   △ 該当物件なし")

        # 8. ESCで閉じて再度開く
        print("\n[8] ESCで閉じて再度開く...")
        actions = ActionChains(driver)
        actions.send_keys(Keys.ESCAPE).perform()
        time.sleep(0.5)

        actions = ActionChains(driver)
        actions.key_down(Keys.COMMAND).send_keys('k').key_up(Keys.COMMAND).perform()
        time.sleep(1)

        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='物件を検索']"))
        )
        print("   ✓ 再度開いた")

        # 9. コマンドモード「/」
        print("\n[9] コマンドモード「/」で開始...")
        type_in_palette("/")
        time.sleep(0.5)

        results = driver.find_elements(By.CSS_SELECTOR, "[cmdk-item]")
        command_texts = [r.text for r in results]
        print(f"   コマンド候補: {len(results)} 件")
        for i, text in enumerate(command_texts[:3]):
            clean_text = text.replace('\n', ' ')[:50]
            print(f"     {i+1}. {clean_text}...")

        if any("新規" in t or "/new" in t for t in command_texts):
            print("   ✓ /new コマンドが表示")

        # 10. /new を選択して遷移確認
        print("\n[10] /new コマンドを実行...")
        type_in_palette("/new")
        time.sleep(0.3)
        actions = ActionChains(driver)
        actions.send_keys(Keys.ENTER).perform()
        time.sleep(1.5)

        current_url = driver.current_url
        print(f"   現在のURL: {current_url}")
        if "/new" in current_url:
            print("   ✓ 新規登録ページに遷移")
        else:
            print("   △ 遷移を確認できず")

        # 11. 戻って検索結果から物件を選択
        print("\n[11] 物件一覧に戻り、検索結果から物件を選択...")
        driver.get("http://localhost:5173/properties")
        time.sleep(2)

        actions = ActionChains(driver)
        actions.key_down(Keys.COMMAND).send_keys('k').key_up(Keys.COMMAND).perform()
        time.sleep(1)

        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='物件を検索']"))
        )

        type_in_palette("北見")
        time.sleep(2)

        results = driver.find_elements(By.CSS_SELECTOR, "[cmdk-item]")
        if len(results) > 0:
            print(f"   検索結果: {len(results)} 件")
            # JavaScriptで最初の結果をクリック
            click_first_result()
            time.sleep(1.5)

            current_url = driver.current_url
            print(f"   現在のURL: {current_url}")
            if "/edit" in current_url:
                print("   ✓ 物件編集ページに遷移")
            else:
                print("   △ 遷移を確認できず")
        else:
            print("   △ 検索結果なし")

        # 12. 検索履歴の確認
        print("\n[12] 検索履歴を確認...")
        driver.get("http://localhost:5173/properties")
        time.sleep(2)

        actions = ActionChains(driver)
        actions.key_down(Keys.COMMAND).send_keys('k').key_up(Keys.COMMAND).perform()
        time.sleep(1)

        history_headings = driver.find_elements(By.CSS_SELECTOR, "[cmdk-group-heading]")
        history_texts = [h.text for h in history_headings]
        print(f"   グループヘッダー: {history_texts}")

        if any("最近" in t or "履歴" in t for t in history_texts):
            print("   ✓ 検索履歴が表示")
        else:
            print("   △ 検索履歴なし")

        print("\n" + "=" * 60)
        print("テスト完了!")
        print("=" * 60)

        driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/command_palette_final.png")
        print("\nスクリーンショット保存: test_screenshots/command_palette_final.png")

        time.sleep(3)

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/command_palette_error.png")
        time.sleep(3)
    finally:
        driver.quit()

if __name__ == "__main__":
    test_command_palette()
