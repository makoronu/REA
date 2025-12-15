#!/usr/bin/env python3
"""
全項目表示確認テスト
DBの値と画面表示を突き合わせる
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# DBから取得した期待値
EXPECTED_VALUES = {
    # propertiesテーブル
    "property_name": "2480　売4238【土地】龍瀧",  # 部分一致でOK
    "property_type": "land",  # selectの値
    "sales_status": "販売準備",
    "publication_status": "非公開",
    "sale_price": "10000000",
    "postal_code": "090-0807",
    "prefecture": "北海道",
    "city": "網走郡美幌町",
    "address": "字東4四条南三丁目17番7",
    "elementary_school": "美幌小学校",
    "junior_high_school": "美幌中学校",

    # land_infoテーブル
    "land_area": "1866.38",
    "land_category": "1:宅地",
    "use_district": "4:第二種中高層住居専用",
    "city_planning": "3:非線引区域",
    "land_rights": "1:所有権",
    "chiban": "17番7",
}

def get_field_value(driver, field_name):
    """フィールドの値を取得（input, select, textarea対応）"""
    try:
        # name属性で検索
        element = driver.find_element(By.NAME, field_name)
        tag = element.tag_name.lower()

        if tag == "select":
            # selectの場合は選択されているオプションの値を取得
            from selenium.webdriver.support.ui import Select
            select = Select(element)
            selected = select.first_selected_option
            return selected.get_attribute("value") or selected.text
        else:
            return element.get_attribute("value") or ""
    except:
        try:
            # id属性で再検索
            element = driver.find_element(By.ID, field_name)
            return element.get_attribute("value") or ""
        except:
            return None


def test_all_fields():
    """全項目の表示確認"""

    print("=" * 80)
    print("全項目表示確認テスト")
    print("=" * 80)

    options = webdriver.ChromeOptions()
    options.add_argument('--window-size=1400,900')

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.set_page_load_timeout(30)

    screenshot_dir = "/Users/yaguchimakoto/my_programing/REA/test_screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)

    results = []

    try:
        # 編集画面を開く
        print("\n1. 編集画面を開く...")
        driver.get("http://localhost:5173/properties/1/edit")
        time.sleep(5)

        # 各タブを順番に確認
        tabs = [
            ("所在地・周辺情報", ["postal_code", "prefecture", "city", "address", "elementary_school", "junior_high_school"]),
            ("基本・取引情報", ["property_name", "property_type", "sale_price"]),
            ("土地情報", ["land_area", "land_category", "use_district", "city_planning", "land_rights", "chiban"]),
        ]

        for tab_name, fields in tabs:
            print(f"\n--- {tab_name}タブ ---")

            # タブをクリック
            try:
                tab = driver.find_element(By.XPATH, f"//button[contains(text(), '{tab_name}')]")
                tab.click()
                time.sleep(2)
            except Exception as e:
                print(f"   ⚠️ タブクリック失敗: {e}")

            driver.save_screenshot(f"{screenshot_dir}/allfields_{tab_name}.png")

            # フィールドを確認
            for field_name in fields:
                expected = EXPECTED_VALUES.get(field_name, "")
                actual = get_field_value(driver, field_name)

                if actual is None:
                    status = "❌ 見つからない"
                    match = False
                elif not actual:
                    status = "⚠️ 空"
                    match = False
                elif expected in actual or actual in expected:
                    status = "✅"
                    match = True
                else:
                    status = f"⚠️ 不一致"
                    match = False

                print(f"   {status} {field_name}")
                print(f"      期待: {expected}")
                print(f"      実際: {actual}")

                results.append({
                    "field": field_name,
                    "expected": expected,
                    "actual": actual,
                    "match": match,
                    "tab": tab_name
                })

        # サマリー
        print("\n" + "=" * 80)
        print("テスト結果サマリー")
        print("=" * 80)

        total = len(results)
        passed = sum(1 for r in results if r["match"])
        failed = total - passed

        print(f"総フィールド数: {total}")
        print(f"成功: {passed}")
        print(f"失敗: {failed}")

        if failed > 0:
            print("\n【失敗フィールド】")
            for r in results:
                if not r["match"]:
                    print(f"  - {r['tab']} > {r['field']}")
                    print(f"    期待: {r['expected']}")
                    print(f"    実際: {r['actual']}")

        print("\n" + "=" * 80)

        # 5秒表示
        time.sleep(5)

        return failed == 0

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        driver.save_screenshot(f"{screenshot_dir}/allfields_error.png")
        return False

    finally:
        driver.quit()


if __name__ == "__main__":
    success = test_all_fields()
    exit(0 if success else 1)
