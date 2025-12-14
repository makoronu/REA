"""
登記インポート → 物件登録 E2Eテスト
"""
import os
import sys
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

API_URL = "http://localhost:8005"
FRONTEND_URL = "http://localhost:5173"

# テスト用PDFファイル
PDF_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'rea-api', 'uploads', 'touki')


def test_touki_flow():
    """登記PDF → パース → 物件登録の全フロー"""
    print("\n" + "="*60)
    print("登記インポート → 物件登録 E2Eテスト")
    print("="*60)

    # 1. API経由で登記レコード一覧を取得
    print("\n[1] 登記レコード一覧を取得...")
    response = requests.get(f"{API_URL}/api/v1/touki/records/list")
    assert response.status_code == 200, f"API error: {response.text}"
    records = response.json()
    print(f"  ✓ 登記レコード数: {records['total']}")

    if records['total'] == 0:
        print("  ! 登記レコードがありません。先にPDFをアップロード・パースしてください。")
        return

    # 2. 最初の登記レコードを使って物件を作成
    first_record = records['items'][0]
    print(f"\n[2] 登記レコードID {first_record['id']} から物件を作成...")
    print(f"  - 種別: {first_record['document_type']}")
    print(f"  - 所在: {first_record['location']}")

    # 土地か建物かで分岐
    if first_record['document_type'] == 'land':
        payload = {"land_touki_record_id": first_record['id']}
    else:
        payload = {"building_touki_record_id": first_record['id']}

    response = requests.post(
        f"{API_URL}/api/v1/touki/records/create-property",
        json=payload
    )

    if response.status_code == 200:
        result = response.json()
        property_id = result['property_id']
        print(f"  ✓ 物件ID {property_id} を作成しました")
    else:
        print(f"  ✗ エラー: {response.text}")
        return

    # 3. 作成した物件を取得して確認
    print(f"\n[3] 作成した物件 (ID: {property_id}) を確認...")
    response = requests.get(f"{API_URL}/api/v1/properties/{property_id}")
    assert response.status_code == 200, f"Property not found: {response.text}"
    property_data = response.json()

    print(f"  - 物件名: {property_data.get('property_name', 'N/A')}")
    print(f"  - 物件種別: {property_data.get('property_type', 'N/A')}")
    print(f"  - 住所: {property_data.get('address', 'N/A')}")
    print(f"  - 備考: {property_data.get('remarks', 'N/A')[:50]}...")

    # 4. Seleniumでブラウザを開いて物件詳細を表示
    print(f"\n[4] ブラウザで物件詳細を表示...")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.set_page_load_timeout(30)

    try:
        # 物件詳細ページを開く
        detail_url = f"{FRONTEND_URL}/properties/{property_id}"
        print(f"  URL: {detail_url}")
        driver.get(detail_url)

        # ページ読み込み待機
        time.sleep(3)

        # スクリーンショット保存
        screenshot_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'test_screenshots')
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshot_dir, f'touki_property_{property_id}.png')
        driver.save_screenshot(screenshot_path)
        print(f"  ✓ スクリーンショット保存: {screenshot_path}")

        # 物件編集ページも開く
        edit_url = f"{FRONTEND_URL}/properties/{property_id}/edit"
        print(f"\n[5] 物件編集ページを表示...")
        print(f"  URL: {edit_url}")
        driver.get(edit_url)

        time.sleep(3)

        screenshot_path = os.path.join(screenshot_dir, f'touki_property_{property_id}_edit.png')
        driver.save_screenshot(screenshot_path)
        print(f"  ✓ スクリーンショット保存: {screenshot_path}")

        print("\n" + "="*60)
        print("✅ テスト完了")
        print("="*60)

        # 確認のため少し待機
        print("\n5秒後にブラウザを閉じます...")
        time.sleep(5)

    finally:
        driver.quit()

    # 5. 作成した物件を削除（クリーンアップ）
    print(f"\n[6] クリーンアップ: 物件ID {property_id} を削除...")
    response = requests.delete(f"{API_URL}/api/v1/properties/{property_id}")
    if response.status_code == 200:
        print(f"  ✓ 物件を削除しました")
    else:
        print(f"  ! 削除失敗: {response.text}")


def test_touki_records_list():
    """登記レコード一覧の確認"""
    print("\n" + "="*60)
    print("登記レコード一覧の確認")
    print("="*60)

    response = requests.get(f"{API_URL}/api/v1/touki/records/list")
    assert response.status_code == 200
    data = response.json()

    print(f"\n登記レコード数: {data['total']}")

    for record in data['items']:
        doc_type = "土地" if record['document_type'] == 'land' else "建物"
        print(f"\n[ID: {record['id']}] {doc_type}")
        print(f"  不動産番号: {record['real_estate_number']}")
        print(f"  所在: {record['location']}")

        if record['document_type'] == 'land':
            print(f"  地番: {record['lot_number']}")
            print(f"  地目: {record['land_category']}")
            print(f"  地積: {record['land_area_m2']}㎡")
        else:
            print(f"  家屋番号: {record['building_number']}")
            print(f"  構造: {record['structure']}")
            print(f"  床面積: {record['floor_area_m2']}㎡")

        if record['owners']:
            print(f"  所有者: {record['owners'][0]['name']}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', action='store_true', help='登記レコード一覧を表示')
    args = parser.parse_args()

    if args.list:
        test_touki_records_list()
    else:
        test_touki_flow()
