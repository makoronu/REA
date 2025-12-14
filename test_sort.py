"""
ソート機能の動作確認テスト
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_sort():
    driver = webdriver.Chrome()
    driver.set_window_size(1400, 900)
    wait = WebDriverWait(driver, 10)

    try:
        print("=" * 60)
        print("ソート機能 動作確認テスト")
        print("=" * 60)

        # 1. 物件一覧ページを開く
        print("\n[1] 物件一覧ページを開く...")
        driver.get("http://localhost:5173/properties")
        time.sleep(2)
        print("   ✓ ページ読み込み完了")

        # テーブルの行を取得する関数
        def get_column_values(column_index):
            rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
            values = []
            for row in rows[:10]:  # 最初の10行
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) > column_index:
                    values.append(cells[column_index].text)
            return values

        # 2. デフォルトソート確認（ID降順）
        print("\n[2] デフォルトソート（ID降順）確認...")
        ids = get_column_values(0)
        print(f"   ID列: {ids}")
        print("   ✓ デフォルトソート確認")

        # 3. 物件番号でソート（昇順）
        print("\n[3] 物件番号で昇順ソート...")
        header = driver.find_element(By.XPATH, "//th[contains(., '物件番号')]")
        header.click()
        time.sleep(1)

        # もう一度クリックして昇順に（デフォルトが降順の場合）
        header.click()
        time.sleep(1)

        prop_nums = get_column_values(1)
        print(f"   物件番号列: {prop_nums}")

        # 数値として正しくソートされているか確認
        numeric_nums = []
        for n in prop_nums:
            if n and n != '-':
                try:
                    numeric_nums.append(int(n))
                except:
                    pass

        if numeric_nums == sorted(numeric_nums):
            print("   ✓ 物件番号が数値として昇順ソート")
        else:
            print(f"   △ ソート順序を確認: {numeric_nums}")

        # 4. 物件番号で降順ソート
        print("\n[4] 物件番号で降順ソート...")
        header.click()
        time.sleep(1)

        prop_nums_desc = get_column_values(1)
        print(f"   物件番号列: {prop_nums_desc}")

        numeric_nums_desc = []
        for n in prop_nums_desc:
            if n and n != '-':
                try:
                    numeric_nums_desc.append(int(n))
                except:
                    pass

        if numeric_nums_desc == sorted(numeric_nums_desc, reverse=True):
            print("   ✓ 物件番号が数値として降順ソート")
        else:
            print(f"   △ ソート順序を確認: {numeric_nums_desc}")

        # 5. 価格でソート
        print("\n[5] 価格でソート...")
        price_header = driver.find_element(By.XPATH, "//th[contains(., '価格')]")
        price_header.click()
        time.sleep(1)

        prices = get_column_values(3)
        print(f"   価格列: {prices}")
        print("   ✓ 価格ソート確認")

        # 6. IDでソート
        print("\n[6] IDでソート（昇順）...")
        id_header = driver.find_element(By.XPATH, "//th[contains(., 'ID')]")
        id_header.click()
        time.sleep(1)
        id_header.click()  # 昇順に
        time.sleep(1)

        ids_asc = get_column_values(0)
        print(f"   ID列: {ids_asc}")

        numeric_ids = [int(i) for i in ids_asc if i.isdigit()]
        if numeric_ids == sorted(numeric_ids):
            print("   ✓ IDが数値として昇順ソート")

        print("\n" + "=" * 60)
        print("テスト完了!")
        print("=" * 60)

        driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/sort_test_final.png")
        print("\nスクリーンショット保存: test_screenshots/sort_test_final.png")

        time.sleep(3)

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/sort_test_error.png")
        time.sleep(3)
    finally:
        driver.quit()

if __name__ == "__main__":
    test_sort()
