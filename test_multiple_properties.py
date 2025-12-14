"""
複数物件の編集画面テスト
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def test_property(driver, prop_id, expected):
    """1物件をテスト"""
    print(f"\n[物件ID: {prop_id}]")
    driver.get(f"http://localhost:5173/properties/{prop_id}/edit")
    time.sleep(3)

    page = driver.page_source
    results = []

    for keyword, label in expected:
        if keyword and keyword in page:
            results.append(f"  ✓ {label}: 表示あり")
        elif keyword:
            results.append(f"  ✗ {label}: 表示なし (期待: {keyword})")
        else:
            results.append(f"  - {label}: データなし")

    for r in results:
        print(r)

    # スクリーンショット
    driver.save_screenshot(f"/Users/yaguchimakoto/my_programing/REA/test_screenshots/multi_prop_{prop_id}.png")
    return all("✗" not in r for r in results)

def main():
    options = Options()
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1400, 900)
    driver.set_page_load_timeout(30)

    try:
        print("=" * 60)
        print("複数物件の編集画面テスト")
        print("=" * 60)

        # テストケース: (物件ID, [(期待キーワード, ラベル), ...])
        test_cases = [
            (1, [
                ("1866", "土地面積"),
                ("所有権", "土地権利"),
                (None, "建物構造"),  # 土地のみなので建物情報なし
            ]),
            (4, [
                ("木造", "建物構造"),
                ("98", "建物面積"),
                ("210", "土地面積"),
                ("所有権", "土地権利"),
            ]),
            (5, [
                ("395", "土地面積"),
                ("所有権", "土地権利"),
            ]),
            (100, [
                ("木造", "建物構造"),
                ("142", "建物面積"),
                ("573", "土地面積"),
                ("所有権", "土地権利"),
            ]),
        ]

        success_count = 0
        for prop_id, expected in test_cases:
            if test_property(driver, prop_id, expected):
                success_count += 1

        print("\n" + "=" * 60)
        print(f"結果: {success_count}/{len(test_cases)} 物件でデータ表示OK")
        print("=" * 60)

        time.sleep(2)

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
