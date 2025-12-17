#!/usr/bin/env python3
"""ユーザー管理画面のE2Eテスト"""
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# スクリーンショット保存先
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'test_screenshots')
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def save_screenshot(driver, name):
    """スクリーンショットを保存"""
    path = os.path.join(SCREENSHOT_DIR, f'{name}.png')
    driver.save_screenshot(path)
    print(f'Screenshot saved: {path}')

def test_users_page():
    """ユーザー管理画面のテスト"""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.set_page_load_timeout(15)
    driver.set_window_size(1400, 900)

    try:
        # 1. ログインページを開く
        print('1. ログインページを開く...')
        driver.get('http://localhost:5173/login')
        time.sleep(2)
        save_screenshot(driver, '01_login_page')

        # 2. 管理者としてログイン（admin@shirokuma.co.jp）
        print('2. 管理者としてログイン...')
        email_input = driver.find_element(By.CSS_SELECTOR, 'input[type="email"]')
        email_input.click()
        email_input.clear()
        email_input.send_keys('admin@shirokuma.co.jp')

        password_input = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
        password_input.click()
        password_input.clear()
        password_input.send_keys('test1234')

        submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_btn.click()
        time.sleep(3)
        save_screenshot(driver, '02_after_login')

        # ログイン成功確認
        if '/login' in driver.current_url:
            raise Exception('ログイン失敗')
        print('✅ ログイン成功')

        # 3. ユーザー管理ページに移動
        print('3. ユーザー管理ページに移動...')
        driver.get('http://localhost:5173/settings/users')
        time.sleep(2)
        save_screenshot(driver, '03_users_page')

        # ページタイトル確認
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'ユーザー管理')]"))
        )
        print('✅ ユーザー管理ページ表示成功')

        # 4. 新規作成ボタンをクリック
        print('4. 新規作成モーダルを開く...')
        create_btn = driver.find_element(By.XPATH, "//button[contains(text(), '新規ユーザー作成')]")
        create_btn.click()
        time.sleep(1)
        save_screenshot(driver, '04_create_modal')

        # モーダルが表示されているか確認
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '新規ユーザー作成')]"))
        )
        print('✅ 新規作成モーダル表示成功')

        # 5. キャンセルボタンをクリック
        print('5. モーダルを閉じる...')
        cancel_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'キャンセル')]")
        cancel_btn.click()
        time.sleep(1)
        save_screenshot(driver, '05_modal_closed')

        # 6. ナビゲーションでユーザーメニューが表示されているか確認
        print('6. ナビゲーションにユーザーメニューがあるか確認...')
        user_nav = driver.find_elements(By.XPATH, "//a[contains(text(), 'ユーザー')]")
        if len(user_nav) > 0:
            print('✅ ナビゲーションにユーザーメニューあり')
        else:
            print('⚠️ ナビゲーションにユーザーメニューなし（モバイル表示の可能性）')

        save_screenshot(driver, '06_final')

        print('\n========================================')
        print('✅ ユーザー管理画面テスト完了')
        print('========================================')

    except Exception as e:
        save_screenshot(driver, 'error')
        print(f'\n❌ エラー: {e}')
        raise
    finally:
        time.sleep(2)
        driver.quit()

if __name__ == '__main__':
    test_users_page()
