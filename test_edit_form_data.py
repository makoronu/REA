"""
編集画面で関連テーブルデータが表示されることを確認するテスト
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_edit_form_data():
    driver = webdriver.Chrome()
    driver.set_window_size(1400, 900)
    wait = WebDriverWait(driver, 15)

    try:
        print("=" * 60)
        print("編集画面データ表示テスト")
        print("=" * 60)

        # 1. 物件編集画面を開く（property_id=100）
        print("\n[1] 物件編集画面を開く...")
        driver.get("http://localhost:5173/properties/100/edit")
        time.sleep(3)

        # ページ読み込み完了待ち
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/edit_full_01_initial.png")
        print("   ✓ 編集画面読み込み完了")

        # 2. 基本情報タブで物件種別を確認
        print("\n[2] 基本情報を確認...")
        time.sleep(2)

        # property_type が表示されているか確認
        page_source = driver.page_source

        if "一戸建て" in page_source or "detached" in page_source:
            print("   ✓ 物件種別が表示されている")
        else:
            print("   ✗ 物件種別が表示されていない")

        # 3. 土地情報タブに移動
        print("\n[3] 土地情報タブに移動...")
        tabs = driver.find_elements(By.CSS_SELECTOR, "button")
        land_tab = None
        for tab in tabs:
            if "土地情報" in tab.text:
                land_tab = tab
                break

        if land_tab:
            driver.execute_script("arguments[0].click();", land_tab)
            time.sleep(1)
            driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/edit_full_02_land_tab.png")
            print("   ✓ 土地情報タブに移動")

            # 土地面積が表示されているか
            page_source = driver.page_source
            if "573" in page_source:  # 573.35㎡
                print("   ✓ 土地面積(573.35)が表示されている")
            else:
                print("   ✗ 土地面積が表示されていない")

            # 土地権利が表示されているか
            if "所有権" in page_source:
                print("   ✓ 土地権利(所有権)が表示されている")
            else:
                print("   ✗ 土地権利が表示されていない")
        else:
            print("   ✗ 土地情報タブが見つからない")

        # 4. 建物情報タブに移動
        print("\n[4] 建物情報タブに移動...")
        building_tab = None
        tabs = driver.find_elements(By.CSS_SELECTOR, "button")
        for tab in tabs:
            if "建物情報" in tab.text:
                building_tab = tab
                break

        if building_tab:
            driver.execute_script("arguments[0].click();", building_tab)
            time.sleep(1)
            driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/edit_full_03_building_tab.png")
            print("   ✓ 建物情報タブに移動")

            page_source = driver.page_source

            # 建物構造が表示されているか
            if "木造" in page_source:
                print("   ✓ 建物構造(木造)が表示されている")
            else:
                print("   ✗ 建物構造が表示されていない")

            # 建物面積が表示されているか
            if "142" in page_source:  # 142.56㎡
                print("   ✓ 建物面積(142.56)が表示されている")
            else:
                print("   ✗ 建物面積が表示されていない")

            # 方位が表示されているか
            if "南東" in page_source:
                print("   ✓ 方位(南東)が表示されている")
            else:
                print("   ✗ 方位が表示されていない")
        else:
            print("   ✗ 建物情報タブが見つからない")

        # 5. 最終スクリーンショット
        driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/edit_full_final.png")

        print("\n" + "=" * 60)
        print("テスト完了")
        print("=" * 60)
        print("\nスクリーンショット保存先: test_screenshots/edit_full_*.png")

        time.sleep(2)

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/edit_full_error.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_edit_form_data()
