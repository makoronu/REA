"""
全物件種別の完全自動テスト
各物件種別でフォームを入力し、全機能を使ってスクリーンショットを撮る

使い方:
    cd ~/my_programing/REA
    PYTHONPATH=~/my_programing/REA python3 tests/e2e/test_all_property_types.py
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from datetime import datetime
from pathlib import Path


class PropertyTypeTest:
    """物件種別ごとの完全テスト"""

    # 全物件種別
    PROPERTY_TYPES = [
        '一戸建て',
        'マンション',
        'アパート',
        '土地',
        '店舗',
        '事務所',
        '倉庫',
        '工場',
        'ビル（一棟）',
        '駐車場',
    ]

    # 物件種別ごとのダミーデータ
    DUMMY_DATA = {
        '一戸建て': {
            'property_name': '北見市北進町 中古一戸建て',
            'sale_price': '12000000',
            'land_area': '200.50',
            'building_area': '80.25',
            'total_floor_area': '120.50',
            'room_count': '4',
            'room_type': 'LDK',
            'building_structure': '木造',
            'construction_date': '2005-04-15',
            'building_floors_above': '2',
        },
        'マンション': {
            'property_name': '北見市中央町 サンプルマンション',
            'sale_price': '18000000',
            'total_floor_area': '75.50',
            'room_count': '3',
            'room_type': 'LDK',
            'building_structure': '鉄筋コンクリート',
            'construction_date': '2010-03-01',
            'building_floors_above': '10',
        },
        'アパート': {
            'property_name': '北見市美芳町 サンプルアパート',
            'sale_price': '35000000',
            'land_area': '300',
            'building_area': '200',
            'total_floor_area': '400',
            'total_units': '8',
            'building_structure': '木造',
            'construction_date': '2015-06-01',
            'building_floors_above': '2',
        },
        '土地': {
            'property_name': '北見市端野町 売地',
            'sale_price': '5000000',
            'land_area': '500',
            'terrain': '平坦',
        },
        '店舗': {
            'property_name': '北見市北進町 貸店舗',
            'sale_price': '25000000',
            'building_area': '150',
            'total_floor_area': '150',
            'building_structure': '鉄骨造',
            'construction_date': '2000-01-01',
        },
        '事務所': {
            'property_name': '北見市大通 オフィスビル',
            'sale_price': '45000000',
            'building_area': '300',
            'total_floor_area': '900',
            'building_structure': '鉄骨造',
            'construction_date': '1995-04-01',
            'building_floors_above': '5',
        },
        '倉庫': {
            'property_name': '北見市端野町 倉庫',
            'sale_price': '15000000',
            'land_area': '1000',
            'building_area': '500',
            'building_structure': '鉄骨造',
            'construction_date': '1990-01-01',
        },
        '工場': {
            'property_name': '北見市端野町 工場',
            'sale_price': '80000000',
            'land_area': '3000',
            'building_area': '1500',
            'building_structure': '鉄骨造',
            'construction_date': '1985-01-01',
        },
        'ビル（一棟）': {
            'property_name': '北見市大通 収益ビル',
            'sale_price': '150000000',
            'land_area': '500',
            'building_area': '400',
            'total_floor_area': '2000',
            'building_structure': '鉄筋コンクリート',
            'construction_date': '1998-01-01',
            'building_floors_above': '8',
            'total_units': '20',
        },
        '駐車場': {
            'property_name': '北見市北進町 月極駐車場',
            'sale_price': '8000000',
            'land_area': '200',
            'parking_capacity': '10',
        },
    }

    # 共通住所データ
    COMMON_ADDRESS = {
        'postal_code': '090-0061',
        'prefecture': '北海道',
        'city': '北見市',
        'address': '北進町4丁目6-9',
    }

    def __init__(self, screenshot_dir=None):
        self.driver = None
        self.screenshot_dir = Path(screenshot_dir or 'test_screenshots/property_types')
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.results = []

    def start_browser(self):
        """ブラウザ起動"""
        options = Options()
        options.add_argument("--window-size=1400,900")
        options.add_argument("--window-position=100,100")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("detach", True)

        self.driver = webdriver.Chrome(options=options)
        self._setup_helpers()
        print("[Browser] Chrome起動")

    def stop_browser(self):
        """ブラウザ終了"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            print("[Browser] Chrome終了")

    def _setup_helpers(self):
        """JavaScript ヘルパー関数を登録"""
        self.driver.execute_script("""
            window.setInput = function(name, value) {
                const el = document.querySelector(`[name="${name}"]`);
                if (!el) return false;
                if (el.tagName === 'SELECT') {
                    for (let opt of el.options) {
                        if (opt.text.includes(value) || opt.value.includes(value)) {
                            el.value = opt.value;
                            el.dispatchEvent(new Event('change', { bubbles: true }));
                            return true;
                        }
                    }
                    return false;
                }
                const proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
                const setter = Object.getOwnPropertyDescriptor(proto, 'value')?.set;
                if (setter) setter.call(el, value);
                else el.value = value;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
                return true;
            };

            window.clickButton = function(text) {
                const buttons = document.querySelectorAll('button');
                for (let btn of buttons) {
                    if (btn.textContent.includes(text)) {
                        btn.scrollIntoView({block: 'center'});
                        btn.click();
                        return true;
                    }
                }
                return false;
            };

            window.clickTab = function(text) {
                const tabs = document.querySelectorAll('[role="tab"], button');
                for (let tab of tabs) {
                    if (tab.textContent.includes(text)) {
                        tab.click();
                        return true;
                    }
                }
                return false;
            };
        """)

    def screenshot(self, name, full_page=True):
        """スクリーンショット保存（CDP フルページ対応）"""
        import base64
        filename = f"{name}.png"
        filepath = self.screenshot_dir / filename

        if full_page:
            try:
                # Chrome DevTools Protocolでフルページスクリーンショット
                metrics = self.driver.execute_cdp_cmd('Page.getLayoutMetrics', {})
                width = int(metrics['contentSize']['width'])
                height = int(metrics['contentSize']['height'])

                # デバイスメトリクスをページ全体サイズに設定
                self.driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
                    'mobile': False,
                    'width': width,
                    'height': height,
                    'deviceScaleFactor': 1,
                })

                # フルページスクリーンショット
                screenshot = self.driver.execute_cdp_cmd('Page.captureScreenshot', {
                    'format': 'png',
                    'captureBeyondViewport': True,
                })

                # base64デコードして保存
                with open(filepath, 'wb') as f:
                    f.write(base64.b64decode(screenshot['data']))

                # デバイスメトリクスをリセット
                self.driver.execute_cdp_cmd('Emulation.clearDeviceMetricsOverride', {})

                print(f"  [Screenshot CDP] {filepath} ({width}x{height})")
            except Exception as e:
                print(f"  [Screenshot CDP Error] {e}, falling back to regular")
                self.driver.save_screenshot(str(filepath))
        else:
            self.driver.save_screenshot(str(filepath))

        return str(filepath)

    def test_property_type(self, property_type):
        """1つの物件種別をテスト"""
        print("\n" + "=" * 70)
        print(f"テスト: {property_type}")
        print("=" * 70)

        safe_name = property_type.replace('（', '_').replace('）', '')

        try:
            # 新規登録ページを開く
            self.driver.get("http://localhost:5173/properties/new")
            time.sleep(3)
            self._setup_helpers()

            # 1. 物件種別選択
            print(f"\n[1] 物件種別選択: {property_type}")
            self.driver.execute_script(f"setInput('property_type', '{property_type}')")
            time.sleep(2)
            self.screenshot(f"{safe_name}_01_type")

            # 2. 基本情報入力
            print("[2] 基本情報入力")
            data = self.DUMMY_DATA.get(property_type, {})
            for key, value in data.items():
                self.driver.execute_script(f"setInput('{key}', '{value}')")
            time.sleep(1)
            self.screenshot(f"{safe_name}_02_basic")

            # 3. 所在地タブ
            print("[3] 所在地・住所入力")
            self.driver.execute_script("clickTab('所在地')")
            time.sleep(1)
            for key, value in self.COMMON_ADDRESS.items():
                self.driver.execute_script(f"setInput('{key}', '{value}')")
            time.sleep(1)

            # 座標取得
            self.driver.execute_script("clickButton('住所から座標')")
            time.sleep(3)

            # 学校候補取得
            self.driver.execute_script("clickButton('学校候補')")
            time.sleep(3)
            self.screenshot(f"{safe_name}_03_location")

            # 4. 土地情報タブ（土地がある物件種別のみ）
            if property_type not in ['マンション']:
                print("[4] 土地情報・法規制自動取得")
                self.driver.execute_script("clickTab('土地情報')")
                time.sleep(1)
                self.driver.execute_script("clickButton('位置情報から自動取得')")
                time.sleep(4)
                self.screenshot(f"{safe_name}_04_land")

            # 5. 建物情報タブ（建物がある物件種別のみ）
            if property_type not in ['土地', '駐車場']:
                print("[5] 建物情報")
                self.driver.execute_script("clickTab('建物情報')")
                time.sleep(1)
                self.screenshot(f"{safe_name}_05_building")

            # 6. 設備・周辺環境タブ
            print("[6] 設備・周辺環境")
            self.driver.execute_script("clickTab('設備')")
            time.sleep(2)

            # 設備チェック
            self.driver.execute_script("""
                document.querySelectorAll('input[type="checkbox"]').forEach((cb, i) => {
                    if (i < 5 && !cb.checked) cb.click();
                });
            """)
            time.sleep(1)
            self.screenshot(f"{safe_name}_06_equipment")

            # 最寄駅モーダル
            self.driver.execute_script("window.scrollTo(0, 500)")
            time.sleep(0.5)
            self.driver.execute_script("clickButton('最寄駅を追加')")
            time.sleep(2)
            self.screenshot(f"{safe_name}_07_station_modal")

            # モーダル閉じる
            self.driver.execute_script("""
                const modal = document.querySelector('[role="dialog"]');
                if (modal) {
                    const closeBtn = modal.querySelector('button');
                    if (closeBtn) closeBtn.click();
                }
            """)
            time.sleep(1)

            # 周辺施設モーダル
            self.driver.execute_script("clickButton('周辺施設を追加')")
            time.sleep(2)
            self.screenshot(f"{safe_name}_08_facility_modal")

            # 7. 画像情報タブ
            print("[7] 画像情報")
            self.driver.execute_script("clickTab('画像情報')")
            time.sleep(1)
            self.screenshot(f"{safe_name}_09_image")

            # 結果記録
            self.results.append({
                'property_type': property_type,
                'status': 'SUCCESS',
                'screenshots': 9,
            })
            print(f"\n✓ {property_type} テスト完了")

        except Exception as e:
            print(f"\n✗ {property_type} テスト失敗: {e}")
            self.screenshot(f"{safe_name}_error")
            self.results.append({
                'property_type': property_type,
                'status': 'FAILED',
                'error': str(e),
            })

    def run_all_tests(self):
        """全物件種別をテスト"""
        print("\n" + "=" * 70)
        print("REA 全物件種別テスト")
        print(f"テスト対象: {len(self.PROPERTY_TYPES)}種別")
        print(f"スクリーンショット保存先: {self.screenshot_dir}")
        print("=" * 70)

        self.start_browser()

        for property_type in self.PROPERTY_TYPES:
            self.test_property_type(property_type)

        self.print_summary()
        # ブラウザは開いたまま（確認用）

    def print_summary(self):
        """サマリー表示"""
        print("\n" + "=" * 70)
        print("テスト結果サマリー")
        print("=" * 70)

        success = sum(1 for r in self.results if r['status'] == 'SUCCESS')
        failed = len(self.results) - success

        print(f"成功: {success} / 失敗: {failed} / 合計: {len(self.results)}")
        print(f"スクリーンショット: {self.screenshot_dir}")

        if failed > 0:
            print("\n失敗した物件種別:")
            for r in self.results:
                if r['status'] == 'FAILED':
                    print(f"  - {r['property_type']}: {r.get('error', 'Unknown')}")

        print("\n" + "=" * 70)


def main():
    """メイン実行"""
    test = PropertyTypeTest()
    test.run_all_tests()


if __name__ == "__main__":
    main()
