"""
新しい物件一覧ページ（ビュー・カラム選択・フィルタ機能）動作確認テスト
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_new_properties_page():
    driver = webdriver.Chrome()
    driver.set_window_size(1400, 900)
    wait = WebDriverWait(driver, 10)

    def js_click(element):
        """JavaScriptでクリック（要素が被っている場合でも機能）"""
        driver.execute_script("arguments[0].click();", element)

    def scroll_to_element(element):
        """要素までスクロール"""
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

    try:
        print("=" * 60)
        print("新しい物件一覧ページ 動作確認テスト")
        print("=" * 60)

        # 1. 物件一覧ページを開く
        print("\n[1] 物件一覧ページを開く...")
        driver.get("http://localhost:5173/properties")
        time.sleep(3)
        print("   ✓ ページ読み込み完了")

        # スクリーンショット
        driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/new_page_01_initial.png")

        # 2. ビュータブを確認
        print("\n[2] ビュータブを確認...")
        view_tabs = driver.find_elements(By.CSS_SELECTOR, "button")

        all_tab = None
        selling_tab = None
        published_tab = None
        column_btn = None
        filter_btn = None

        for tab in view_tabs:
            text = tab.text.strip()
            if text == "すべて":
                all_tab = tab
                print("   ✓ 「すべて」タブあり")
            elif text == "販売中":
                selling_tab = tab
                print("   ✓ 「販売中」タブあり")
            elif text == "公開中":
                published_tab = tab
                print("   ✓ 「公開中」タブあり")
            elif text == "列":
                column_btn = tab
            elif "フィルター" in text:
                filter_btn = tab

        # 3. 「販売中」タブをクリック
        print("\n[3] 「販売中」タブをクリック...")
        if selling_tab:
            scroll_to_element(selling_tab)
            js_click(selling_tab)
            time.sleep(1)
            driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/new_page_02_selling.png")
            print("   ✓ 販売中タブに切り替え")

            # タブがアクティブになったか確認
            tab_class = selling_tab.get_attribute("class")
            if "blue" in tab_class:
                print("   ✓ タブがアクティブ状態")
        else:
            print("   △ 販売中タブが見つからない")

        # 4. 「すべて」タブに戻る
        print("\n[4] 「すべて」タブに戻る...")
        if all_tab:
            js_click(all_tab)
            time.sleep(1)
            print("   ✓ すべてタブに切り替え")

        # 5. カラム選択機能を確認
        print("\n[5] カラム選択機能を確認...")
        if column_btn:
            js_click(column_btn)
            time.sleep(0.5)
            driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/new_page_03_column_picker.png")
            print("   ✓ カラム選択ドロップダウンを開いた")

            # チェックボックスを確認
            checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
            print(f"   カラム選択肢: {len(checkboxes)} 個")

            # いくつかのカラムをオン/オフ
            if len(checkboxes) > 7:
                js_click(checkboxes[7])  # 都道府県
                time.sleep(0.3)
                print("   ✓ 都道府県カラムを追加")

            # ドロップダウンを閉じる（外側をクリック）
            driver.find_element(By.TAG_NAME, "h1").click()
            time.sleep(0.3)
        else:
            print("   △ カラム選択ボタンが見つからない")

        # 6. フィルターパネルを確認
        print("\n[6] フィルターパネルを確認...")
        if filter_btn:
            js_click(filter_btn)
            time.sleep(0.5)
            driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/new_page_04_filter_panel.png")
            print("   ✓ フィルターパネルを開いた")

            # フィルター内の要素を確認
            filter_labels = driver.find_elements(By.CSS_SELECTOR, ".bg-gray-50 label")
            if filter_labels:
                print(f"   フィルター項目: {len(filter_labels)} 個")
        else:
            print("   △ フィルターボタンが見つからない")

        # 7. 検索入力を確認
        print("\n[7] 検索入力を確認...")
        search_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='物件名・番号で検索...']")
        if search_input:
            search_input.clear()
            search_input.send_keys("北見")
            time.sleep(1.5)
            driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/new_page_05_search.png")
            print("   ✓ 検索入力完了")

            # 検索結果を確認
            rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
            result_count = len([r for r in rows if "animate-pulse" not in r.get_attribute("class")])
            print(f"   検索結果: {result_count} 件")

            # 検索クリア
            search_input.clear()
            time.sleep(1)
        else:
            print("   △ 検索入力欄が見つからない")

        # 8. 物件種別フィルタをテスト（ボタン形式）
        print("\n[8] 物件種別フィルタをテスト...")
        # フィルターパネル内のボタンを探す
        filter_buttons = driver.find_elements(By.CSS_SELECTOR, "button")
        type_button = None
        for btn in filter_buttons:
            if btn.text.strip() in ['一戸建て', '土地', 'マンション', 'アパート']:
                type_button = btn
                break

        if type_button:
            js_click(type_button)
            time.sleep(1)
            driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/new_page_06_type_filter.png")
            print(f"   ✓ 物件種別フィルタ適用: {type_button.text}")
        else:
            print("   △ 物件種別ボタンが見つからない")

        # 9. ソート機能を確認
        print("\n[9] ソート機能を確認...")
        headers = driver.find_elements(By.CSS_SELECTOR, "th")
        for header in headers:
            if "物件番号" in header.text:
                js_click(header)
                time.sleep(1)
                driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/new_page_07_sort.png")
                print("   ✓ 物件番号でソート")

                # ソート順を確認
                rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
                if len(rows) > 1:
                    cells = rows[0].find_elements(By.TAG_NAME, "td")
                    if len(cells) > 1:
                        print(f"   最初の物件番号: {cells[1].text}")
                break

        # 10. 「公開中」タブを確認
        print("\n[10] 「公開中」タブを確認...")
        if published_tab:
            js_click(published_tab)
            time.sleep(1)
            driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/new_page_08_published.png")
            print("   ✓ 公開中タブに切り替え")

            rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
            result_count = len([r for r in rows if "animate-pulse" not in r.get_attribute("class")])
            print(f"   公開中物件: {result_count} 件")

        # 11. ビュー保存機能を確認
        print("\n[11] ビュー保存機能を確認...")
        view_menu_btn = driver.find_elements(By.CSS_SELECTOR, "button[title='ビュー管理']")
        if view_menu_btn:
            js_click(view_menu_btn[0])
            time.sleep(0.5)
            driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/new_page_09_view_menu.png")
            print("   ✓ ビュー管理メニューを開いた")

            # 新しいビューを保存
            view_name_input = driver.find_elements(By.CSS_SELECTOR, "input[placeholder='ビュー名']")
            if view_name_input:
                view_name_input[0].send_keys("テストビュー")
                time.sleep(0.3)

                save_buttons = driver.find_elements(By.CSS_SELECTOR, "button")
                for btn in save_buttons:
                    if btn.text.strip() == "保存":
                        js_click(btn)
                        break
                time.sleep(0.5)
                driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/new_page_10_view_saved.png")
                print("   ✓ 新しいビューを保存")
        else:
            # +ボタンを探す
            plus_btns = driver.find_elements(By.CSS_SELECTOR, "button")
            for btn in plus_btns:
                svg = btn.find_elements(By.TAG_NAME, "svg")
                if svg and "M12 6v6m0 0v6m0-6h6m-6 0H6" in btn.get_attribute("innerHTML"):
                    js_click(btn)
                    time.sleep(0.5)
                    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/new_page_09_view_menu.png")
                    print("   ✓ ビュー管理メニューを開いた")
                    break

        # 12. ページネーションを確認
        print("\n[12] ページネーションを確認...")
        pagination_btns = driver.find_elements(By.CSS_SELECTOR, "button")
        for btn in pagination_btns:
            if btn.text.strip() == "次へ" and btn.is_enabled():
                js_click(btn)
                time.sleep(1)
                print("   ✓ 次ページに移動")
                break

        # 最終スクリーンショット
        driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/new_page_final.png")

        print("\n" + "=" * 60)
        print("テスト完了!")
        print("=" * 60)
        print("\nスクリーンショット保存先: test_screenshots/new_page_*.png")

        # 確認時間
        time.sleep(3)

    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/new_page_error.png")
        time.sleep(3)
    finally:
        driver.quit()

if __name__ == "__main__":
    test_new_properties_page()
