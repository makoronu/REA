"""
シンプルな編集画面テスト
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def test():
    options = Options()
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1400, 900)
    driver.set_page_load_timeout(30)

    try:
        print("編集画面を開いています...")
        driver.get("http://localhost:5173/properties/100/edit")
        time.sleep(5)  # ページ読み込み待ち

        print("スクリーンショット保存...")
        driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/edit_simple_01.png")

        # ページソースを確認
        page = driver.page_source

        # 物件種別確認
        print("\n=== データ表示確認 ===")
        checks = [
            ("一戸建て", "物件種別"),
            ("573", "土地面積"),
            ("142", "建物面積"),
            ("木造", "建物構造"),
            ("所有権", "土地権利"),
            ("南東", "方位"),
        ]

        for keyword, label in checks:
            if keyword in page:
                print(f"✓ {label}: 表示あり")
            else:
                print(f"✗ {label}: 表示なし")

        # 土地情報タブに移動
        print("\n土地情報タブに移動...")
        buttons = driver.find_elements(By.CSS_SELECTOR, "button")
        for btn in buttons:
            if "土地情報" in btn.text:
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(2)
                break

        driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/edit_simple_02_land.png")

        # 建物情報タブに移動
        print("建物情報タブに移動...")
        buttons = driver.find_elements(By.CSS_SELECTOR, "button")
        for btn in buttons:
            if "建物情報" in btn.text:
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(2)
                break

        driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/edit_simple_03_building.png")

        print("\n完了。スクリーンショットを確認してください。")
        time.sleep(3)

    except Exception as e:
        print(f"エラー: {e}")
        driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/edit_simple_error.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    test()
