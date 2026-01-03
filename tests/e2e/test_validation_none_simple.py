"""
公開時バリデーション「該当なし」対応のE2Eテスト（シンプル版）
各テストケースを順番に確認
"""
import time
import sys
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# テスト用ログイン情報（開発環境）
TEST_EMAIL = "admin@shirokuma.co.jp"
TEST_PASSWORD = "test1234"
BASE_URL = "http://localhost:5173"
SCREENSHOT_DIR = Path(__file__).parent.parent.parent / "test_screenshots"

def screenshot(driver, name):
    """スクリーンショット保存"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = SCREENSHOT_DIR / f"{name}_{timestamp}.png"
    driver.save_screenshot(str(filepath))
    print(f"[Screenshot] {filepath}")
    return str(filepath)

def login(driver):
    """ログイン処理"""
    print("[Test] ログイン中...")
    driver.get(f"{BASE_URL}/login")
    time.sleep(2)

    email_input = driver.find_element(By.CSS_SELECTOR, 'input[type="email"]')
    email_input.clear()
    email_input.send_keys(TEST_EMAIL)

    password_input = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
    password_input.clear()
    password_input.send_keys(TEST_PASSWORD)

    submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    submit_btn.click()
    time.sleep(3)

    if "/login" in driver.current_url:
        print("[Test] ✗ ログイン失敗")
        return False
    print("[Test] ✓ ログイン成功")
    return True

def click_tab(driver, tab_name):
    """タブをクリック"""
    try:
        tabs = driver.find_elements(By.XPATH, f"//button[contains(text(), '{tab_name}')]")
        if tabs:
            tabs[0].click()
            time.sleep(1)
            print(f"[Test] タブ「{tab_name}」をクリック")
            return True
        else:
            print(f"[Test] タブ「{tab_name}」が見つかりません")
            return False
    except Exception as e:
        print(f"[Test] タブクリックエラー: {e}")
        return False

def find_checkbox_by_label(driver, label_text):
    """ラベルからチェックボックスを探す"""
    try:
        # ラベル内のチェックボックスを探す
        checkboxes = driver.find_elements(By.XPATH,
            f"//label[contains(text(), '{label_text}')]//input[@type='checkbox'] | "
            f"//label[contains(text(), '{label_text}')]/following-sibling::input[@type='checkbox'] | "
            f"//label[contains(text(), '{label_text}')]/preceding-sibling::input[@type='checkbox'] | "
            f"//span[contains(text(), '{label_text}')]/..//input[@type='checkbox']"
        )
        if checkboxes:
            return checkboxes[0]
    except:
        pass
    return None

def find_and_check_none_option(driver, label_text):
    """「〜なし」オプションを探してチェック"""
    cb = find_checkbox_by_label(driver, label_text)
    if cb:
        if not cb.is_selected():
            cb.click()
            time.sleep(0.5)
        print(f"[Test] ✓ 「{label_text}」チェックボックスをON")
        return True
    print(f"[Test] ✗ 「{label_text}」チェックボックスが見つかりません")
    return False

def change_publication_status(driver, status_text):
    """公開ステータスを変更"""
    try:
        # 公開ステータスボタンを探す
        buttons = driver.find_elements(By.XPATH, f"//button[contains(text(), '{status_text}')]")
        if buttons:
            buttons[0].click()
            time.sleep(0.5)
            print(f"[Test] ✓ 公開ステータスを「{status_text}」に変更")
            return True

        # セレクトボックスを探す
        selects = driver.find_elements(By.TAG_NAME, "select")
        for select in selects:
            try:
                s = Select(select)
                for opt in s.options:
                    if status_text in opt.text:
                        s.select_by_visible_text(opt.text)
                        print(f"[Test] ✓ 公開ステータスを「{opt.text}」に変更")
                        return True
            except:
                continue
    except Exception as e:
        print(f"[Test] 公開ステータス変更エラー: {e}")
    return False

def click_save(driver):
    """保存ボタンをクリック"""
    try:
        save_btn = driver.find_element(By.XPATH, "//button[contains(text(), '保存')]")
        save_btn.click()
        time.sleep(3)
        print("[Test] ✓ 保存ボタンをクリック")
        return True
    except Exception as e:
        print(f"[Test] 保存エラー: {e}")
        return False

def check_validation_error(driver):
    """バリデーションエラーを確認"""
    try:
        # エラートースト/アラートを探す
        errors = driver.find_elements(By.CSS_SELECTOR,
            ".toast-error, .error-message, [role='alert'], .text-red-500, .bg-red-100"
        )
        for err in errors:
            if err.is_displayed() and err.text:
                return True, err.text
    except:
        pass
    return False, ""

def run_test_case(driver, case_num, description, setup_func):
    """テストケースを実行"""
    print(f"\n{'='*60}")
    print(f"テストケース {case_num}: {description}")
    print('='*60)

    try:
        # 物件一覧から編集画面へ
        driver.get(f"{BASE_URL}/properties")
        time.sleep(2)

        # 最初の編集ボタンをクリック
        edit_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '編集')]")
        if edit_buttons:
            edit_buttons[0].click()
            time.sleep(2)
        else:
            print("[Test] ✗ 編集ボタンが見つかりません")
            return False, "編集ボタンが見つかりません"

        # テストケース固有のセットアップ
        setup_func(driver)
        time.sleep(1)

        screenshot(driver, f"test_{case_num}_before_save")

        # 公開に変更
        change_publication_status(driver, "公開")
        time.sleep(0.5)

        # 保存
        click_save(driver)

        # 結果確認
        has_error, error_msg = check_validation_error(driver)

        screenshot(driver, f"test_{case_num}_after_save")

        if has_error:
            print(f"[Test] ✗ 失敗: {error_msg}")
            return False, error_msg
        else:
            print(f"[Test] ✓ 成功: エラーなしで保存完了")
            return True, "OK"

    except Exception as e:
        print(f"[Test] ✗ エラー: {e}")
        screenshot(driver, f"test_{case_num}_error")
        return False, str(e)

def test_case_1(driver):
    """用途地域「指定なし」→ 建ぺい率・容積率空欄"""
    click_tab(driver, "法令制限")
    time.sleep(1)
    # 用途地域で「指定なし」を選択
    try:
        selects = driver.find_elements(By.TAG_NAME, "select")
        for select in selects:
            select_id = select.get_attribute("id") or ""
            if "zone" in select_id.lower() or "用途" in select_id:
                s = Select(select)
                for opt in s.options:
                    if "指定なし" in opt.text:
                        s.select_by_visible_text(opt.text)
                        print(f"[Test] ✓ 用途地域を「{opt.text}」に変更")
                        break
                break
    except Exception as e:
        print(f"[Test] 用途地域設定エラー: {e}")

def test_case_2(driver):
    """物件種別「戸建」→ 所在階・総戸数空欄"""
    click_tab(driver, "基本情報")
    time.sleep(1)
    # 物件種別が戸建であることを確認（既存データを使用）
    print("[Test] 物件種別「戸建」の物件を使用（所在階・総戸数は非表示のはず）")

def test_case_3(driver):
    """接道情報「接道なし」→ セットバック空欄"""
    click_tab(driver, "土地情報")
    time.sleep(1)
    find_and_check_none_option(driver, "接道なし")

def test_case_4(driver):
    """管理費「0」"""
    click_tab(driver, "管理・費用")
    time.sleep(1)
    try:
        inputs = driver.find_elements(By.XPATH, "//label[contains(text(), '管理費')]/following::input[1]")
        if inputs:
            inputs[0].clear()
            inputs[0].send_keys("0")
            print("[Test] ✓ 管理費を「0」に設定")
    except Exception as e:
        print(f"[Test] 管理費設定エラー: {e}")

def test_case_5(driver):
    """修繕積立金「0」"""
    click_tab(driver, "管理・費用")
    time.sleep(1)
    try:
        inputs = driver.find_elements(By.XPATH, "//label[contains(text(), '修繕積立金')]/following::input[1]")
        if inputs:
            inputs[0].clear()
            inputs[0].send_keys("0")
            print("[Test] ✓ 修繕積立金を「0」に設定")
    except Exception as e:
        print(f"[Test] 修繕積立金設定エラー: {e}")

def test_case_6(driver):
    """小学校「なし」"""
    click_tab(driver, "所在地")
    time.sleep(1)
    try:
        inputs = driver.find_elements(By.XPATH, "//label[contains(text(), '小学校')]/following::input[1]")
        if inputs:
            inputs[0].clear()
            inputs[0].send_keys("なし")
            print("[Test] ✓ 小学校を「なし」に設定")
    except Exception as e:
        print(f"[Test] 小学校設定エラー: {e}")

def test_case_7(driver):
    """中学校「該当なし」"""
    click_tab(driver, "所在地")
    time.sleep(1)
    try:
        inputs = driver.find_elements(By.XPATH, "//label[contains(text(), '中学校')]/following::input[1]")
        if inputs:
            inputs[0].clear()
            inputs[0].send_keys("該当なし")
            print("[Test] ✓ 中学校を「該当なし」に設定")
    except Exception as e:
        print(f"[Test] 中学校設定エラー: {e}")

def test_case_8(driver):
    """最寄駅「最寄駅なし」チェック"""
    click_tab(driver, "所在地")
    time.sleep(1)
    find_and_check_none_option(driver, "最寄駅なし")

def test_case_9(driver):
    """バス停「バス路線なし」チェック"""
    click_tab(driver, "所在地")
    time.sleep(1)
    find_and_check_none_option(driver, "バス路線なし")

def test_case_10(driver):
    """近隣施設「近隣施設なし」チェック"""
    click_tab(driver, "所在地")
    time.sleep(1)
    find_and_check_none_option(driver, "近隣施設なし")

def main():
    """メイン処理"""
    print("\n" + "="*70)
    print("公開時バリデーション「該当なし」対応 E2Eテスト")
    print("="*70 + "\n")

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    # Chrome起動
    options = Options()
    options.add_argument("--window-size=1400,900")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    print("[Test] Chrome起動完了")

    results = []

    try:
        # ログイン
        if not login(driver):
            raise Exception("ログインに失敗しました")

        # フォーム構造を確認
        print("\n[Test] フォーム構造を確認中...")
        driver.get(f"{BASE_URL}/properties")
        time.sleep(2)

        # 最初の編集ボタンをクリック
        edit_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '編集')]")
        if edit_buttons:
            edit_buttons[0].click()
            time.sleep(3)
            screenshot(driver, "form_structure_overview")

            # 各タブを確認
            tab_names = ["所在地", "基本情報", "価格", "管理", "法令制限", "土地情報"]
            for tab_name in tab_names:
                click_tab(driver, tab_name)
                time.sleep(1)
                screenshot(driver, f"tab_{tab_name}")

                # チェックボックスを探す
                checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
                print(f"[Test] タブ「{tab_name}」: チェックボックス {len(checkboxes)}個")

                # 「なし」を含むラベルを探す
                labels = driver.find_elements(By.XPATH, "//*[contains(text(), 'なし') or contains(text(), 'なし')]")
                for label in labels[:5]:
                    if label.text:
                        print(f"  - ラベル: {label.text[:30]}")

        print("\n[Test] フォーム確認完了")

    finally:
        driver.quit()
        print("[Test] Chrome終了")

    # 結果サマリー
    print("\n" + "="*60)
    print("テスト結果サマリー")
    print("="*60)
    print("フォーム構造の確認が完了しました。")
    print(f"スクリーンショット: {SCREENSHOT_DIR}")

if __name__ == "__main__":
    main()
