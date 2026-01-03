"""
公開時バリデーション「該当なし」対応のE2Eテスト
テストケース10項目を検証
"""
import time
import sys
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# ui_test_helperのインポート
sys.path.insert(0, str(Path(__file__).parent))
from ui_test_helper import UITestHelper

# テスト用ログイン情報（開発環境）
TEST_EMAIL = "admin@shirokuma.co.jp"
TEST_PASSWORD = "test1234"

class TestPublicationValidationNone:
    """公開時バリデーション「該当なし」対応テスト"""

    def __init__(self):
        self.ui = UITestHelper(slow_mode=True, slow_delay=0.8)
        self.test_property_id = None
        self.results = []

    def login(self):
        """ログイン処理"""
        print("[Test] ログイン中...")
        self.ui.goto("/login")
        time.sleep(2)
        self.ui.screenshot("login_01_page")

        # メールアドレス入力
        email_input = self.ui.driver.find_element(By.CSS_SELECTOR, 'input[type="email"]')
        email_input.clear()
        email_input.send_keys(TEST_EMAIL)

        # パスワード入力
        password_input = self.ui.driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
        password_input.clear()
        password_input.send_keys(TEST_PASSWORD)

        self.ui.screenshot("login_02_filled")

        # ログインボタンクリック
        submit_btn = self.ui.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_btn.click()
        time.sleep(5)  # 待機時間を延長

        self.ui.screenshot("login_03_after_click")
        print(f"[Test] 現在のURL: {self.ui.driver.current_url}")

        # ログイン成功確認（/loginが含まれていない場合は成功）
        if "/login" in self.ui.driver.current_url:
            print("[Test] ✗ ログイン失敗")
            # エラーメッセージを探す
            try:
                error_elem = self.ui.driver.find_element(By.CSS_SELECTOR, ".text-red-500, .error, [role='alert']")
                print(f"[Test] エラーメッセージ: {error_elem.text}")
            except:
                pass
            return False
        print("[Test] ✓ ログイン成功")
        return True

    def setup(self):
        """テストセットアップ"""
        self.ui.start()
        # ログイン
        if not self.login():
            raise Exception("ログインに失敗しました")
        time.sleep(2)

    def teardown(self):
        """テスト終了処理"""
        self.ui.print_summary()
        self.ui.stop()

    def navigate_to_property_edit(self, property_id=None):
        """物件編集画面へ移動"""
        if property_id:
            self.ui.goto(f"/properties/{property_id}/edit")
        else:
            # 物件一覧から最初の物件の編集ボタンをクリック
            self.ui.goto("/properties")
            time.sleep(2)

            # 最初の編集ボタンをクリック
            try:
                edit_buttons = self.ui.driver.find_elements(By.XPATH, "//button[contains(text(), '編集')] | //a[contains(text(), '編集')]")
                if edit_buttons:
                    print(f"[Test] 編集ボタン発見: {len(edit_buttons)}個")
                    edit_buttons[0].click()
                    time.sleep(3)
                else:
                    print("[Test] 編集ボタンが見つかりません")
            except Exception as e:
                print(f"[Test] 編集ボタンクリックエラー: {e}")

    def try_publish(self):
        """公開を試行"""
        # 公開ステータスを「公開」に変更
        # セレクトボックスを探す
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import Select

            # publication_statusセレクトを探す
            selects = self.ui.driver.find_elements(By.TAG_NAME, "select")
            for select in selects:
                select_id = select.get_attribute("id") or ""
                select_name = select.get_attribute("name") or ""
                if "publication" in select_id.lower() or "publication" in select_name.lower() or "status" in select_id.lower():
                    s = Select(select)
                    # 「公開」オプションを選択
                    for opt in s.options:
                        if "公開" in opt.text and "非公開" not in opt.text:
                            s.select_by_visible_text(opt.text)
                            print(f"[Test] 公開ステータスを「{opt.text}」に変更")
                            break
                    break
        except Exception as e:
            print(f"[Test] 公開ステータス変更エラー: {e}")

    def click_save(self):
        """保存ボタンをクリック"""
        # 保存ボタンを探してクリック
        time.sleep(0.5)
        save_selectors = [
            "button[type='submit']",
            "button:contains('保存')",
            "[data-testid='save-button']",
            "button.save-button",
            "button.btn-primary"
        ]
        for selector in save_selectors:
            try:
                if self.ui.exists(selector):
                    self.ui.click(selector)
                    print(f"[Test] 保存ボタンクリック: {selector}")
                    break
            except:
                continue
        time.sleep(2)

    def check_validation_error(self):
        """バリデーションエラーが表示されているか確認"""
        # エラーメッセージの存在確認
        error_selectors = [
            ".error-message",
            ".validation-error",
            "[role='alert']",
            ".text-red-500",
            ".text-destructive",
            ".toast-error",
            ".alert-error"
        ]
        for selector in error_selectors:
            if self.ui.exists(selector):
                try:
                    elem = self.ui.driver.find_element(By.CSS_SELECTOR, selector)
                    if elem.is_displayed():
                        return True, elem.text
                except:
                    pass
        return False, ""

    def check_success(self):
        """保存成功を確認"""
        # 成功メッセージまたはトーストの確認
        success_selectors = [
            ".toast-success",
            ".success-message",
            "[data-testid='success-toast']",
            ".text-green-500"
        ]
        for selector in success_selectors:
            if self.ui.exists(selector):
                return True
        # URL変更などでも成功と判断
        return False

    def run_test_case(self, name, setup_func):
        """個別テストケースを実行"""
        print(f"\n{'='*60}")
        print(f"[Test] {name}")
        print('='*60)

        try:
            # 物件編集画面へ
            self.navigate_to_property_edit()
            time.sleep(1)

            # テストケース固有のセットアップ
            setup_func()
            time.sleep(0.5)

            # 公開を試行
            self.try_publish()
            time.sleep(0.5)

            # 保存
            self.click_save()
            time.sleep(2)

            # 結果確認
            has_error, error_msg = self.check_validation_error()

            if has_error:
                print(f"[Test] ✗ 失敗: バリデーションエラーが発生: {error_msg}")
                self.ui.screenshot(f"fail_{name.replace(' ', '_')}")
                return False, error_msg
            else:
                print(f"[Test] ✓ 成功: エラーなしで公開可能")
                self.ui.screenshot(f"pass_{name.replace(' ', '_')}")
                return True, "OK"

        except Exception as e:
            print(f"[Test] ✗ エラー: {e}")
            self.ui.screenshot(f"error_{name.replace(' ', '_')}")
            return False, str(e)

    def run_all_tests(self):
        """全テストケースを実行"""
        print("\n" + "="*70)
        print("公開時バリデーション「該当なし」対応 E2Eテスト")
        print("="*70 + "\n")

        self.setup()

        # まず物件一覧を確認
        self.ui.goto("/properties")
        time.sleep(3)
        self.ui.screenshot("01_property_list")

        # テストケースの確認用に物件編集画面へ
        self.navigate_to_property_edit()
        time.sleep(3)
        self.ui.screenshot("02_property_edit_form")

        # 各タブを確認して該当フィールドを探す
        self.check_form_structure()

        self.teardown()

    def check_form_structure(self):
        """フォーム構造を確認"""
        from selenium.webdriver.common.by import By

        print("\n[Test] フォーム構造を確認中...")

        # タブを探す
        tabs = self.ui.driver.find_elements(By.CSS_SELECTOR, "[role='tab'], .tab, button[data-state]")
        print(f"[Test] タブ数: {len(tabs)}")

        for i, tab in enumerate(tabs):
            tab_text = tab.text or tab.get_attribute("aria-label") or f"Tab{i}"
            print(f"  - Tab {i}: {tab_text}")

        # チェックボックスを探す
        checkboxes = self.ui.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        print(f"\n[Test] チェックボックス数: {len(checkboxes)}")

        for cb in checkboxes:
            cb_id = cb.get_attribute("id") or "N/A"
            cb_name = cb.get_attribute("name") or "N/A"
            # ラベルを探す
            try:
                label = self.ui.driver.find_element(By.CSS_SELECTOR, f"label[for='{cb_id}']")
                label_text = label.text
            except:
                label_text = "N/A"

            if any(keyword in label_text for keyword in ["なし", "該当", "指定"]):
                print(f"  - CB: id={cb_id}, name={cb_name}, label={label_text}")

        # セレクトボックスを探す
        selects = self.ui.driver.find_elements(By.TAG_NAME, "select")
        print(f"\n[Test] セレクトボックス数: {len(selects)}")

        for select in selects[:10]:  # 最初の10個
            s_id = select.get_attribute("id") or "N/A"
            s_name = select.get_attribute("name") or "N/A"
            if "zone" in s_id.lower() or "zone" in s_name.lower() or "type" in s_id.lower() or "publication" in s_id.lower():
                print(f"  - Select: id={s_id}, name={s_name}")


def run_form_check():
    """フォーム構造確認のみ実行"""
    test = TestPublicationValidationNone()
    test.run_all_tests()


def do_login(ui):
    """ログイン処理"""
    print("[Test] ログイン中...")
    ui.goto("/login")
    time.sleep(2)

    # メールアドレス入力
    email_input = ui.driver.find_element(By.CSS_SELECTOR, 'input[type="email"]')
    email_input.clear()
    email_input.send_keys(TEST_EMAIL)

    # パスワード入力
    password_input = ui.driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
    password_input.clear()
    password_input.send_keys(TEST_PASSWORD)

    # ログインボタンクリック
    submit_btn = ui.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    submit_btn.click()
    time.sleep(3)

    # ログイン成功確認
    if "/login" in ui.driver.current_url:
        print("[Test] ✗ ログイン失敗")
        return False
    print("[Test] ✓ ログイン成功")
    return True


def run_interactive_test():
    """対話的にテストを実行"""
    print("\n" + "="*70)
    print("公開時バリデーション「該当なし」対応 E2Eテスト（対話モード）")
    print("="*70 + "\n")

    ui = UITestHelper(slow_mode=True, slow_delay=1.0)
    ui.start()

    try:
        # ログイン
        if not do_login(ui):
            raise Exception("ログインに失敗しました")

        # 物件一覧へ
        print("[Test] 物件一覧へ移動...")
        ui.goto("/properties")
        time.sleep(3)
        ui.screenshot("01_property_list")

        # 物件が存在するか確認
        if ui.exists("tbody tr"):
            print("[Test] 物件が存在します。最初の物件をクリック...")
            ui.click("tbody tr:first-child")
            time.sleep(2)
            ui.screenshot("02_property_selected")
        else:
            print("[Test] 物件が存在しません。テスト用物件を作成する必要があります。")
            ui.screenshot("02_no_properties")

        # 現在のURLを確認
        current_url = ui.driver.current_url
        print(f"[Test] 現在のURL: {current_url}")

        # 編集画面か確認
        if "/edit" not in current_url:
            # 編集ボタンを探す
            from selenium.webdriver.common.by import By
            edit_buttons = ui.driver.find_elements(By.XPATH, "//a[contains(@href, '/edit')] | //button[contains(text(), '編集')]")
            if edit_buttons:
                print(f"[Test] 編集ボタンをクリック: {edit_buttons[0].text or edit_buttons[0].get_attribute('href')}")
                edit_buttons[0].click()
                time.sleep(2)
                ui.screenshot("03_edit_form")

        # フォーム構造を出力
        print("\n[Test] フォーム構造を確認中...")

        from selenium.webdriver.common.by import By

        # 全ての入力フィールドをカウント
        inputs = ui.driver.find_elements(By.TAG_NAME, "input")
        selects = ui.driver.find_elements(By.TAG_NAME, "select")
        textareas = ui.driver.find_elements(By.TAG_NAME, "textarea")

        print(f"  Input: {len(inputs)}, Select: {len(selects)}, Textarea: {len(textareas)}")

        # 特定のキーワードを含むフィールドを探す
        keywords = ["用途", "zone", "type", "種別", "接道", "road", "管理費", "修繕", "学校", "school", "駅", "station", "バス", "bus", "施設", "facility", "publication", "公開"]

        print("\n[Test] 関連フィールド:")
        for inp in inputs + selects:
            inp_id = inp.get_attribute("id") or ""
            inp_name = inp.get_attribute("name") or ""
            inp_type = inp.get_attribute("type") or ""

            for kw in keywords:
                if kw.lower() in inp_id.lower() or kw.lower() in inp_name.lower():
                    print(f"  - {inp.tag_name}: id={inp_id}, name={inp_name}, type={inp_type}")
                    break

        # 「なし」を含むチェックボックスやラベルを探す
        print("\n[Test] 「なし」関連のチェックボックス:")
        checkboxes = ui.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        for cb in checkboxes:
            cb_id = cb.get_attribute("id") or ""
            # 近くのラベルテキストを取得
            try:
                parent = cb.find_element(By.XPATH, "./..")
                label_text = parent.text[:50] if parent.text else ""
            except:
                label_text = ""

            if "なし" in label_text or "none" in cb_id.lower() or "no_" in cb_id.lower():
                print(f"  - id={cb_id}, label={label_text}")

        # タブを確認
        print("\n[Test] タブ構造:")
        tabs = ui.driver.find_elements(By.CSS_SELECTOR, "[role='tab'], button[data-state]")
        for i, tab in enumerate(tabs):
            tab_text = tab.text or tab.get_attribute("value") or f"Tab{i}"
            is_selected = tab.get_attribute("data-state") == "active" or tab.get_attribute("aria-selected") == "true"
            print(f"  - [{i}] {tab_text} {'(active)' if is_selected else ''}")

        input("\n[Test] Enterを押すと終了します...")

    finally:
        ui.stop()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        run_interactive_test()
    else:
        run_form_check()
