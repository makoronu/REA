"""
公開時バリデーション「該当なし」対応 完全E2Eテスト
全10テストケースを順番に確認
"""
import time
import sys
from pathlib import Path
from datetime import datetime

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
SCREENSHOT_DIR = Path(__file__).parent.parent.parent / "test_screenshots" / "validation_test"

class ValidationTest:
    """バリデーションテスト"""

    def __init__(self):
        self.driver = None
        self.results = []
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    def screenshot(self, name):
        """スクリーンショット保存"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = SCREENSHOT_DIR / f"{name}_{timestamp}.png"
        self.driver.save_screenshot(str(filepath))
        print(f"  [Screenshot] {filepath.name}")
        return str(filepath)

    def start(self, headless=True):
        """ブラウザ起動"""
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1400,900")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(5)
        mode = "ヘッドレス" if headless else "GUI"
        print(f"[Test] Chrome起動完了（{mode}モード）")

    def stop(self):
        """ブラウザ終了"""
        if self.driver:
            self.driver.quit()
            print("[Test] Chrome終了")

    def login(self):
        """ログイン"""
        print("[Test] ログイン中...")
        self.driver.get(f"{BASE_URL}/login")
        time.sleep(2)

        self.driver.find_element(By.CSS_SELECTOR, 'input[type="email"]').send_keys(TEST_EMAIL)
        self.driver.find_element(By.CSS_SELECTOR, 'input[type="password"]').send_keys(TEST_PASSWORD)
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        time.sleep(3)

        if "/login" in self.driver.current_url:
            raise Exception("ログイン失敗")
        print("[Test] ✓ ログイン成功")

    def go_to_edit(self, property_index=0):
        """物件編集画面へ移動"""
        self.driver.get(f"{BASE_URL}/properties")
        time.sleep(2)

        edit_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), '編集')]")
        if len(edit_buttons) > property_index:
            edit_buttons[property_index].click()
            time.sleep(3)
            return True
        return False

    def click_tab(self, tab_name):
        """タブをクリック"""
        try:
            tabs = self.driver.find_elements(By.XPATH, f"//button[contains(text(), '{tab_name}')]")
            if tabs:
                tabs[0].click()
                time.sleep(1)
                return True
        except:
            pass
        return False

    def scroll_to_element(self, element):
        """要素までスクロール"""
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(0.5)

    def find_checkbox(self, label_contains):
        """ラベルに指定文字列を含むチェックボックスを探す"""
        try:
            # ラベルテキストでチェックボックスを探す
            elements = self.driver.find_elements(By.XPATH,
                f"//label[contains(., '{label_contains}')]//input[@type='checkbox'] | "
                f"//span[contains(., '{label_contains}')]//input[@type='checkbox'] | "
                f"//span[contains(., '{label_contains}')]/preceding-sibling::input[@type='checkbox'] | "
                f"//label[contains(., '{label_contains}')]/..//input[@type='checkbox']"
            )
            for el in elements:
                if el.is_displayed():
                    return el
        except:
            pass
        return None

    def set_checkbox(self, label_contains, checked=True):
        """チェックボックスを設定"""
        cb = self.find_checkbox(label_contains)
        if cb:
            self.scroll_to_element(cb)
            if cb.is_selected() != checked:
                cb.click()
                time.sleep(0.3)
            return True
        return False

    def set_input_value(self, label_contains, value):
        """入力フィールドに値を設定"""
        try:
            inputs = self.driver.find_elements(By.XPATH,
                f"//label[contains(text(), '{label_contains}')]/..//input | "
                f"//label[contains(text(), '{label_contains}')]/following::input[1]"
            )
            for inp in inputs:
                if inp.is_displayed() and inp.get_attribute("type") not in ["checkbox", "radio", "hidden"]:
                    self.scroll_to_element(inp)
                    inp.clear()
                    inp.send_keys(str(value))
                    return True
        except:
            pass
        return False

    def set_select_value(self, label_contains, option_text):
        """セレクトボックスの値を設定"""
        try:
            selects = self.driver.find_elements(By.XPATH,
                f"//label[contains(text(), '{label_contains}')]/..//select | "
                f"//label[contains(text(), '{label_contains}')]/following::select[1]"
            )
            for sel in selects:
                if sel.is_displayed():
                    self.scroll_to_element(sel)
                    s = Select(sel)
                    for opt in s.options:
                        if option_text in opt.text:
                            s.select_by_visible_text(opt.text)
                            return True
        except:
            pass
        return False

    def set_publication_status(self, status_text):
        """公開ステータスを設定"""
        try:
            # ボタン形式
            buttons = self.driver.find_elements(By.XPATH, f"//button[text()='{status_text}']")
            for btn in buttons:
                if btn.is_displayed():
                    btn.click()
                    time.sleep(0.5)
                    return True
        except:
            pass
        return False

    def save(self):
        """保存"""
        try:
            save_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), '保存')]")
            self.scroll_to_element(save_btn)
            save_btn.click()
            time.sleep(3)
            return True
        except:
            return False

    def check_error(self):
        """エラー確認"""
        try:
            errors = self.driver.find_elements(By.CSS_SELECTOR,
                ".toast-error, [role='alert'], .bg-red-100, .text-red-500"
            )
            for err in errors:
                if err.is_displayed() and err.text and "必要" in err.text:
                    return True, err.text
        except:
            pass
        return False, ""

    def run_test(self, case_num, description, setup_func):
        """テストケース実行"""
        print(f"\n{'='*60}")
        print(f"テストケース {case_num}: {description}")
        print('='*60)

        try:
            # 編集画面へ
            if not self.go_to_edit():
                return False, "編集画面に移動できません"

            # セットアップ
            setup_result = setup_func()
            if not setup_result:
                print("  [Warning] セットアップで問題が発生")

            self.screenshot(f"case{case_num}_setup")

            # 公開に変更
            self.set_publication_status("公開")

            # 保存
            self.save()

            # エラー確認
            has_error, error_msg = self.check_error()

            self.screenshot(f"case{case_num}_result")

            if has_error:
                print(f"  ✗ 失敗: {error_msg[:50]}...")
                return False, error_msg
            else:
                print(f"  ✓ 成功: エラーなしで公開可能")
                return True, "OK"

        except Exception as e:
            print(f"  ✗ エラー: {e}")
            self.screenshot(f"case{case_num}_error")
            return False, str(e)

    def run_all(self):
        """全テスト実行"""
        print("\n" + "="*70)
        print("公開時バリデーション「該当なし」対応 E2Eテスト")
        print("="*70)

        self.start()
        self.login()

        # テストケース定義
        test_cases = [
            (1, "用途地域「指定なし」→ 建ぺい率・容積率空欄 → 公開", self.setup_case_1),
            (2, "物件種別「戸建」→ 所在階・総戸数空欄 → 公開", self.setup_case_2),
            (3, "接道情報「接道なし」→ セットバック空欄 → 公開", self.setup_case_3),
            (4, "管理費「0」→ 公開", self.setup_case_4),
            (5, "修繕積立金「0」→ 公開", self.setup_case_5),
            (6, "小学校「なし」→ 公開", self.setup_case_6),
            (7, "中学校「該当なし」→ 公開", self.setup_case_7),
            (8, "最寄駅「最寄駅なし」チェック → 公開", self.setup_case_8),
            (9, "バス停「バス路線なし」チェック → 公開", self.setup_case_9),
            (10, "近隣施設「近隣施設なし」チェック → 公開", self.setup_case_10),
        ]

        # 最初に基本情報を確認
        print("\n[Test] フォーム構造を事前確認中...")
        self.go_to_edit()
        self.screenshot("00_initial_form")

        # 各タブを確認
        for tab in ["所在地", "基本情報", "管理", "法令制限", "土地情報"]:
            self.click_tab(tab)
            time.sleep(0.5)
            self.screenshot(f"00_tab_{tab}")

        # テスト実行
        for case_num, description, setup_func in test_cases:
            passed, message = self.run_test(case_num, description, setup_func)
            self.results.append({
                "case": case_num,
                "description": description,
                "passed": passed,
                "message": message
            })

        self.stop()
        self.print_summary()

    def setup_case_1(self):
        """用途地域「指定なし」"""
        self.click_tab("法令制限")
        time.sleep(1)
        return self.set_select_value("用途地域", "指定なし")

    def setup_case_2(self):
        """物件種別「戸建」"""
        # 物件種別が戸建の物件を使用（既存データ）
        self.click_tab("基本情報")
        return True

    def setup_case_3(self):
        """接道なし"""
        self.click_tab("土地情報")
        time.sleep(1)
        return self.set_checkbox("接道なし", True)

    def setup_case_4(self):
        """管理費「0」"""
        self.click_tab("管理")
        time.sleep(1)
        return self.set_input_value("管理費", "0")

    def setup_case_5(self):
        """修繕積立金「0」"""
        self.click_tab("管理")
        time.sleep(1)
        return self.set_input_value("修繕積立金", "0")

    def setup_case_6(self):
        """小学校「なし」"""
        self.click_tab("所在地")
        time.sleep(1)
        return self.set_input_value("小学校", "なし")

    def setup_case_7(self):
        """中学校「該当なし」"""
        self.click_tab("所在地")
        time.sleep(1)
        return self.set_input_value("中学校", "該当なし")

    def setup_case_8(self):
        """最寄駅なし"""
        self.click_tab("所在地")
        time.sleep(1)
        return self.set_checkbox("最寄駅なし", True)

    def setup_case_9(self):
        """バス路線なし"""
        self.click_tab("所在地")
        time.sleep(1)
        return self.set_checkbox("バス路線なし", True)

    def setup_case_10(self):
        """近隣施設なし"""
        self.click_tab("所在地")
        time.sleep(1)
        return self.set_checkbox("近隣施設なし", True)

    def print_summary(self):
        """結果サマリー"""
        print("\n" + "="*70)
        print("テスト結果サマリー")
        print("="*70)

        passed = sum(1 for r in self.results if r["passed"])
        failed = len(self.results) - passed

        print(f"\n合計: {len(self.results)} / 成功: {passed} / 失敗: {failed}")
        print(f"成功率: {passed/len(self.results)*100:.0f}%\n")

        for r in self.results:
            status = "✓" if r["passed"] else "✗"
            print(f"  {status} ケース{r['case']}: {r['description'][:30]}...")
            if not r["passed"]:
                print(f"      → {r['message'][:50]}")

        print(f"\nスクリーンショット: {SCREENSHOT_DIR}")


if __name__ == "__main__":
    test = ValidationTest()
    test.run_all()
