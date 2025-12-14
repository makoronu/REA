"""
DBにデータがある物件で、実際に表示されるか確認
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import subprocess
import json

def get_api_data(prop_id):
    """APIからデータを取得"""
    result = subprocess.run(
        ['curl', '-s', f'http://localhost:8005/api/v1/properties/{prop_id}/full'],
        capture_output=True, text=True
    )
    return json.loads(result.stdout)

def test():
    options = Options()
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1400, 900)
    driver.set_page_load_timeout(30)

    # DBにデータがある物件をテスト
    test_ids = [7, 10, 11, 13, 14, 15]

    try:
        print("=" * 70)
        print("DBデータ vs 画面表示 比較テスト")
        print("=" * 70)

        for prop_id in test_ids:
            print(f"\n[物件ID: {prop_id}]")

            # APIデータ取得
            api_data = get_api_data(prop_id)
            db_structure = api_data.get('building_structure', '-')
            db_b_area = api_data.get('building_area', '-')
            db_l_area = api_data.get('land_area', '-')
            print(f"  API: 構造={db_structure}, 建物面積={db_b_area}, 土地面積={db_l_area}")

            # 編集画面を開く
            driver.get(f"http://localhost:5173/properties/{prop_id}/edit")
            time.sleep(3)

            # 土地情報タブ
            for btn in driver.find_elements(By.CSS_SELECTOR, "button"):
                if "土地情報" in btn.text:
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(1)
                    break

            page = driver.page_source

            # 土地面積の表示確認
            if db_l_area and db_l_area != '-':
                l_area_str = str(db_l_area).split('.')[0]  # 整数部分
                if l_area_str in page:
                    print(f"  ✓ 土地面積 {db_l_area} が表示されている")
                else:
                    print(f"  ✗ 土地面積 {db_l_area} が表示されていない！")
                    driver.save_screenshot(f"/Users/yaguchimakoto/my_programing/REA/test_screenshots/missing_land_{prop_id}.png")

            # 建物情報タブ
            for btn in driver.find_elements(By.CSS_SELECTOR, "button"):
                if "建物情報" in btn.text:
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(1)
                    break

            page = driver.page_source

            # 建物構造の表示確認
            if db_structure and db_structure != '-' and db_structure != 'None':
                structure_label = db_structure.split(':')[1] if ':' in str(db_structure) else str(db_structure)
                if structure_label in page:
                    print(f"  ✓ 建物構造 {structure_label} が表示されている")
                else:
                    print(f"  ✗ 建物構造 {structure_label} が表示されていない！")
                    driver.save_screenshot(f"/Users/yaguchimakoto/my_programing/REA/test_screenshots/missing_building_{prop_id}.png")

        print("\n" + "=" * 70)
        print("テスト完了")
        print("=" * 70)

    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    test()
