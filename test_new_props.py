"""
新しい物件番号のテスト
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

    # データがない物件を含めてテスト
    test_ids = [2, 3, 8, 18]  # 物件番号 2479, 2478, 2473, 2463

    try:
        for prop_id in test_ids:
            print(f"\n=== 物件ID: {prop_id} ===")
            driver.get(f"http://localhost:5173/properties/{prop_id}/edit")
            time.sleep(3)

            # 土地情報タブに移動
            buttons = driver.find_elements(By.CSS_SELECTOR, "button")
            for btn in buttons:
                if "土地情報" in btn.text:
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(1)
                    break

            driver.save_screenshot(f"/Users/yaguchimakoto/my_programing/REA/test_screenshots/new_prop_{prop_id}_land.png")

            # 建物情報タブに移動
            buttons = driver.find_elements(By.CSS_SELECTOR, "button")
            for btn in buttons:
                if "建物情報" in btn.text:
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(1)
                    break

            driver.save_screenshot(f"/Users/yaguchimakoto/my_programing/REA/test_screenshots/new_prop_{prop_id}_building.png")

            page = driver.page_source
            print(f"  土地面積表示: {'あり' if any(x in page for x in ['165', '253', '273']) else 'なし'}")
            print(f"  建物構造表示: {'あり' if '木造' in page else 'なし'}")

        print("\n完了")

    except Exception as e:
        print(f"エラー: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test()
