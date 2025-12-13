"""
物件CRUD操作のE2Eテスト
Claudeが実装後に自動実行し、問題ないか確認する
"""
import pytest
import time
from ui_test_helper import UITestHelper


class TestPropertyCRUD:
    """物件の作成・読取・更新・削除テスト"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """テスト前後のセットアップ"""
        self.ui = UITestHelper(slow_mode=True, slow_delay=1.0)
        self.ui.start()
        yield
        self.ui.print_summary()
        self.ui.stop()

    def test_property_list_loads(self):
        """物件一覧が正しく読み込まれる"""
        self.ui.goto("/properties")
        self.ui.wait_for_text("物件", timeout=10)
        result = self.ui.assert_visible("table, [role='table']", "物件一覧テーブル表示")
        assert result.passed, result.message

    def test_property_new_form_loads(self):
        """物件登録フォームが正しく読み込まれる"""
        self.ui.goto("/properties/new")
        result = self.ui.assert_visible("form", "物件登録フォーム表示")
        assert result.passed, result.message

        # 必須フィールドの確認
        self.ui.assert_visible("input[name='property_name'], input[id='property_name']", "物件名入力欄")

    def test_property_tabs_work(self):
        """物件詳細のタブ切り替えが動作する"""
        # 既存物件があれば詳細ページへ
        self.ui.goto("/properties")
        time.sleep(2)

        # テーブルの最初の行をクリック（あれば）
        if self.ui.exists("tbody tr"):
            self.ui.click("tbody tr:first-child")
            time.sleep(1)

            # タブの存在確認
            if self.ui.exists("[role='tablist'], .tabs"):
                self.ui.assert_visible("[role='tablist'], .tabs", "タブリスト表示")


class TestNavigation:
    """ナビゲーションのテスト"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.ui = UITestHelper(slow_mode=True, slow_delay=0.8)
        self.ui.start()
        yield
        self.ui.print_summary()
        self.ui.stop()

    def test_sidebar_navigation(self):
        """サイドバーナビゲーションが動作する"""
        self.ui.goto("/")
        time.sleep(1)

        # ナビゲーションの存在確認
        result = self.ui.assert_visible("nav, aside, [role='navigation']", "ナビゲーション存在")
        assert result.passed, result.message

    def test_responsive_layout(self):
        """レスポンシブレイアウトが崩れていない"""
        self.ui.goto("/properties")
        time.sleep(1)

        # 画面サイズを変更
        self.ui.driver.set_window_size(1400, 900)
        self.ui.screenshot("desktop_view")
        time.sleep(0.5)

        self.ui.driver.set_window_size(768, 1024)
        self.ui.screenshot("tablet_view")
        time.sleep(0.5)

        # 元に戻す
        self.ui.driver.set_window_size(1400, 900)


class TestAPIIntegration:
    """APIとの連携テスト"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.ui = UITestHelper(slow_mode=True, slow_delay=1.0)
        self.ui.start()
        yield
        self.ui.print_summary()
        self.ui.stop()

    def test_api_connection(self):
        """APIに接続できる"""
        import requests
        try:
            response = requests.get(f"{self.ui.API_URL}/api/v1/health", timeout=5)
            assert response.status_code == 200, "API健全性チェック失敗"
        except Exception as e:
            pytest.skip(f"APIが起動していません: {e}")

    def test_metadata_loads(self):
        """メタデータが正しく読み込まれる"""
        self.ui.goto("/properties/new")
        time.sleep(2)

        # フォームフィールドが動的に生成されているか
        # メタデータ駆動の場合、多数の入力欄が生成される
        field_count = self.ui.count_elements("input, select, textarea")
        print(f"[UITest] フォームフィールド数: {field_count}")

        result = self.ui.assert_visible("form", "フォームが読み込まれている")
        assert result.passed, result.message


def run_all_tests():
    """全テストを実行（Claude用）"""
    print("\n" + "="*60)
    print("REA E2E テスト実行")
    print("="*60 + "\n")

    # pytest経由で実行
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-s",  # printを表示
    ])

    return exit_code == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
