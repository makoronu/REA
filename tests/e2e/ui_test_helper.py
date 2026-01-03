"""
UIテスト用Seleniumヘルパー
ユーザーが見える形でブラウザを操作し、結果を確認する
"""
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


@dataclass
class TestResult:
    """テスト結果"""
    name: str
    passed: bool
    message: str
    screenshot_path: Optional[str] = None
    duration: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)


class UITestHelper:
    """
    UIテスト用ヘルパークラス

    特徴:
    - ヘッドレスモード対応（バックグラウンド実行可能）
    - スクリーンショットを自動保存
    - 詳細なログ出力
    - テスト結果を構造化して返す
    """

    BASE_URL = "http://localhost:5173"
    API_URL = "http://localhost:8005"
    SCREENSHOT_DIR = Path(__file__).parent.parent.parent / "test_screenshots"

    def __init__(self, slow_mode: bool = True, slow_delay: float = 1.0, headless: bool = True):
        """
        Args:
            slow_mode: Trueの場合、操作間に遅延を入れる
            slow_delay: slow_mode時の遅延秒数
            headless: Trueの場合、ヘッドレスモード（バックグラウンド実行）
        """
        self.driver: Optional[webdriver.Chrome] = None
        self.slow_mode = slow_mode
        self.slow_delay = slow_delay
        self.headless = headless
        self.results: List[TestResult] = []
        self.SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    def start(self) -> "UITestHelper":
        """ブラウザを起動"""
        options = Options()
        # ヘッドレスモード（バックグラウンド実行）
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1400,900")
        options.add_argument("--window-position=100,100")
        # 安定性のための設定
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(5)
        mode = "ヘッドレス" if self.headless else "GUI"
        print(f"[UITest] Chrome起動完了（{mode}モード）")
        return self

    def stop(self):
        """ブラウザを終了"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            print(f"[UITest] Chrome終了")

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def _slow(self, action: str = ""):
        """ゆっくりモードの場合、遅延を入れる"""
        if self.slow_mode:
            if action:
                print(f"[UITest] {action}")
            time.sleep(self.slow_delay)

    def screenshot(self, name: str) -> str:
        """スクリーンショットを保存"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = self.SCREENSHOT_DIR / filename
        self.driver.save_screenshot(str(filepath))
        print(f"[UITest] Screenshot: {filepath}")
        return str(filepath)

    def goto(self, path: str = "/") -> "UITestHelper":
        """ページに移動"""
        url = f"{self.BASE_URL}{path}"
        self._slow(f"移動: {url}")
        self.driver.get(url)
        time.sleep(0.5)  # ページ読み込み待機
        return self

    def wait_for(self, selector: str, timeout: int = 10) -> Any:
        """要素が表示されるまで待機"""
        self._slow(f"待機: {selector}")
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element
        except TimeoutException:
            print(f"[UITest] タイムアウト: {selector} が見つかりません")
            return None

    def wait_for_text(self, text: str, timeout: int = 10) -> bool:
        """特定のテキストが表示されるまで待機"""
        self._slow(f"テキスト待機: {text}")
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{text}')]"))
            )
            return True
        except TimeoutException:
            print(f"[UITest] タイムアウト: '{text}' が見つかりません")
            return False

    def click(self, selector: str) -> "UITestHelper":
        """要素をクリック"""
        self._slow(f"クリック: {selector}")
        element = self.wait_for(selector)
        if element:
            element.click()
        return self

    def type_text(self, selector: str, text: str) -> "UITestHelper":
        """テキストを入力"""
        self._slow(f"入力: {selector} <- '{text}'")
        element = self.wait_for(selector)
        if element:
            element.clear()
            element.send_keys(text)
        return self

    def exists(self, selector: str) -> bool:
        """要素が存在するか確認"""
        try:
            self.driver.find_element(By.CSS_SELECTOR, selector)
            return True
        except NoSuchElementException:
            return False

    def get_text(self, selector: str) -> str:
        """要素のテキストを取得"""
        element = self.wait_for(selector)
        return element.text if element else ""

    def get_value(self, selector: str) -> str:
        """入力要素の値を取得"""
        element = self.wait_for(selector)
        return element.get_attribute("value") if element else ""

    def count_elements(self, selector: str) -> int:
        """要素の数を数える"""
        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
        return len(elements)

    def assert_visible(self, selector: str, name: str = "") -> TestResult:
        """要素が表示されていることを確認"""
        test_name = name or f"visible: {selector}"
        start = time.time()

        element = self.wait_for(selector)
        passed = element is not None and element.is_displayed()
        duration = time.time() - start

        result = TestResult(
            name=test_name,
            passed=passed,
            message="OK" if passed else f"要素が見つからない: {selector}",
            screenshot_path=self.screenshot(test_name.replace(" ", "_").replace(":", "")),
            duration=duration
        )
        self.results.append(result)
        print(f"[UITest] {'✓' if passed else '✗'} {test_name}")
        return result

    def assert_text_contains(self, selector: str, expected: str, name: str = "") -> TestResult:
        """要素のテキストに期待値が含まれているか確認"""
        test_name = name or f"text contains '{expected}'"
        start = time.time()

        actual = self.get_text(selector)
        passed = expected in actual
        duration = time.time() - start

        result = TestResult(
            name=test_name,
            passed=passed,
            message="OK" if passed else f"期待: '{expected}', 実際: '{actual}'",
            screenshot_path=self.screenshot(test_name.replace(" ", "_").replace(":", "").replace("'", "")),
            duration=duration,
            details={"expected": expected, "actual": actual}
        )
        self.results.append(result)
        print(f"[UITest] {'✓' if passed else '✗'} {test_name}")
        return result

    def assert_count(self, selector: str, expected: int, name: str = "") -> TestResult:
        """要素の数を確認"""
        test_name = name or f"count {selector} == {expected}"
        start = time.time()

        actual = self.count_elements(selector)
        passed = actual == expected
        duration = time.time() - start

        result = TestResult(
            name=test_name,
            passed=passed,
            message="OK" if passed else f"期待: {expected}, 実際: {actual}",
            screenshot_path=self.screenshot(test_name.replace(" ", "_")),
            duration=duration,
            details={"expected": expected, "actual": actual}
        )
        self.results.append(result)
        print(f"[UITest] {'✓' if passed else '✗'} {test_name}")
        return result

    def get_summary(self) -> Dict[str, Any]:
        """テスト結果のサマリーを取得"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": f"{(passed/total*100):.1f}%" if total > 0 else "N/A",
            "results": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "message": r.message,
                    "duration": f"{r.duration:.2f}s"
                }
                for r in self.results
            ]
        }

    def print_summary(self):
        """テスト結果のサマリーを表示"""
        summary = self.get_summary()
        print("\n" + "="*60)
        print(f"[UITest] テスト結果サマリー")
        print(f"  合計: {summary['total']} / 成功: {summary['passed']} / 失敗: {summary['failed']}")
        print(f"  成功率: {summary['pass_rate']}")
        print("="*60)

        if summary['failed'] > 0:
            print("\n失敗したテスト:")
            for r in self.results:
                if not r.passed:
                    print(f"  ✗ {r.name}: {r.message}")

        print(f"\nスクリーンショット: {self.SCREENSHOT_DIR}")
        return summary


# テスト実行用のメイン関数
def run_basic_ui_tests():
    """基本的なUIテストを実行"""
    print("\n" + "="*60)
    print("REA UIテスト開始")
    print("="*60 + "\n")

    with UITestHelper(slow_mode=True, slow_delay=1.5) as ui:
        # トップページ
        ui.goto("/")
        ui.assert_visible("body", "ページが読み込まれる")

        # ナビゲーション確認
        ui.assert_visible("nav, header, [role='navigation']", "ナビゲーションが存在")

        # 物件一覧ページ
        ui.goto("/properties")
        ui.wait_for_text("物件", timeout=5)
        ui.assert_visible("table, [role='table'], .property-list", "物件一覧テーブル")

        # 物件登録ページ
        ui.goto("/properties/new")
        ui.assert_visible("form", "物件登録フォーム")

        # サマリー表示
        summary = ui.print_summary()

        return summary['failed'] == 0


if __name__ == "__main__":
    success = run_basic_ui_tests()
    exit(0 if success else 1)
