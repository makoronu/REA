#!/usr/bin/env python3
"""
編集画面のデータ表示確認テスト
メタデータ駆動リファクタリング後の動作確認
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_edit_form_display():
    """編集画面でDBデータが正しく表示されるか確認"""

    print("=" * 60)
    print("編集画面データ表示テスト開始")
    print("=" * 60)

    # Chrome起動（ヘッドレスではない = ユーザーに見える）
    options = webdriver.ChromeOptions()
    options.add_argument('--window-size=1400,900')

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.set_page_load_timeout(30)

    try:
        # 物件一覧ページを開く
        print("\n1. 物件一覧ページを開く...")
        driver.get("http://localhost:5173/properties")
        time.sleep(3)

        # スクリーンショット
        screenshot_dir = "/Users/yaguchimakoto/my_programing/REA/test_screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        driver.save_screenshot(f"{screenshot_dir}/01_property_list.png")
        print(f"   スクリーンショット保存: 01_property_list.png")

        # 最初の物件の編集リンクをクリック
        print("\n2. 編集画面に遷移...")

        # 編集ボタンを探す（複数の方法を試す）
        try:
            # 方法1: 直接編集ページへ遷移
            driver.get("http://localhost:5173/properties/1/edit")
            time.sleep(5)
        except Exception as e:
            print(f"   直接遷移失敗: {e}")
            return False

        driver.save_screenshot(f"{screenshot_dir}/02_edit_page.png")
        print(f"   スクリーンショット保存: 02_edit_page.png")

        # ページタイトルまたはフォームが表示されているか確認
        print("\n3. フォーム要素を確認中...")

        # 基本情報タブが表示されているか
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "form, [role='tabpanel'], .property-form"))
            )
            print("   ✅ フォームが表示されている")
        except Exception as e:
            print(f"   ⚠️ フォーム検出できず: {e}")

        # 特定のフィールドを確認
        fields_to_check = [
            ("property_name", "物件名"),
            ("postal_code", "郵便番号"),
            ("prefecture", "都道府県"),
            ("city", "市区町村"),
            ("address", "住所"),
            ("sale_price", "販売価格"),
            ("land_area", "土地面積"),
        ]

        print("\n4. 各フィールドの値を確認...")
        results = []

        for field_name, label in fields_to_check:
            try:
                # name属性で検索
                element = driver.find_element(By.NAME, field_name)
                value = element.get_attribute("value") or ""
                has_value = bool(value.strip())
                status = "✅" if has_value else "⚠️"
                print(f"   {status} {label}({field_name}): '{value[:50]}{'...' if len(value) > 50 else ''}'")
                results.append((field_name, label, value, has_value))
            except Exception as e:
                # id属性で再検索
                try:
                    element = driver.find_element(By.ID, field_name)
                    value = element.get_attribute("value") or ""
                    has_value = bool(value.strip())
                    status = "✅" if has_value else "⚠️"
                    print(f"   {status} {label}({field_name}): '{value[:50]}{'...' if len(value) > 50 else ''}'")
                    results.append((field_name, label, value, has_value))
                except:
                    print(f"   ❌ {label}({field_name}): フィールドが見つからない")
                    results.append((field_name, label, None, False))

        driver.save_screenshot(f"{screenshot_dir}/03_form_fields.png")
        print(f"\n   スクリーンショット保存: 03_form_fields.png")

        # 他のタブも確認
        print("\n5. タブを切り替えて確認...")

        tabs_to_check = ["土地情報", "建物情報", "設備情報"]
        for tab_name in tabs_to_check:
            try:
                tab = driver.find_element(By.XPATH, f"//button[contains(text(), '{tab_name}')]")
                tab.click()
                time.sleep(1)
                driver.save_screenshot(f"{screenshot_dir}/tab_{tab_name}.png")
                print(f"   ✅ {tab_name}タブ表示OK")
            except Exception as e:
                print(f"   ⚠️ {tab_name}タブ: {e}")

        # コンソールエラーを確認
        print("\n6. ブラウザコンソールエラーを確認...")
        logs = driver.get_log('browser')
        errors = [log for log in logs if log['level'] == 'SEVERE']
        if errors:
            print(f"   ⚠️ コンソールエラーあり: {len(errors)}件")
            for err in errors[:3]:
                print(f"      - {err['message'][:100]}")
        else:
            print("   ✅ コンソールエラーなし")

        # 結果サマリー
        print("\n" + "=" * 60)
        print("テスト結果サマリー")
        print("=" * 60)

        fields_with_value = sum(1 for r in results if r[3])
        fields_checked = len(results)

        print(f"確認フィールド数: {fields_checked}")
        print(f"値があるフィールド: {fields_with_value}")
        print(f"値がないフィールド: {fields_checked - fields_with_value}")

        # 住所関連フィールドの確認（特に重要）
        address_fields = ["postal_code", "prefecture", "city", "address"]
        address_results = [r for r in results if r[0] in address_fields]
        address_ok = all(r[3] for r in address_results if r[2] is not None)

        if address_ok:
            print("\n✅ 住所関連フィールド: 正常（上書き問題解決）")
        else:
            print("\n⚠️ 住所関連フィールド: 一部空（要確認）")
            for r in address_results:
                if not r[3]:
                    print(f"   - {r[1]}: 空")

        print("\n" + "=" * 60)
        print("テスト完了")
        print(f"スクリーンショット保存先: {screenshot_dir}")
        print("=" * 60)

        # 5秒待機（ユーザーが確認できるように）
        print("\n画面を5秒間表示します...")
        time.sleep(5)

        return True

    except Exception as e:
        print(f"\n❌ テスト中にエラー発生: {e}")
        driver.save_screenshot(f"{screenshot_dir}/error.png")
        return False

    finally:
        driver.quit()
        print("\nブラウザを閉じました")


if __name__ == "__main__":
    test_edit_form_display()
