"""
物件フォームに全フィールドダミーデータを入力するスクリプト
デバッグ・テスト用

使い方:
    cd ~/my_programing/REA
    PYTHONPATH=~/my_programing/REA python3 tests/e2e/fill_dummy_property.py

注意:
    - フロントエンド(localhost:5173)が起動している必要がある
    - API(localhost:8005)が起動している必要がある
    - ReactのStateを更新するため、nativeInputValueSetterを使用
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# ダミーデータ定義（北見市北進町の中古一戸建て）
DUMMY_DATA = {
    # === 基本情報・取引情報 ===
    "property_type": "一戸建て",
    "is_new_construction": False,  # 中古
    "property_name": "北見市北進町 中古一戸建て",
    "company_property_number": "REA-2024-001",

    # 価格
    "sale_price": "12000000",
    "price_status": 2,  # 確定（INTEGER: rea_2→2）
    "tax_type": 1,  # 税込（INTEGER: rea_1→1）

    # 取引
    "current_status": "販売中",
    "delivery_timing": "即入居可",
    "transaction_type": "売主",
    "brokerage_fee": "396000",

    # === 住所・立地 ===
    "postal_code": "090-0061",
    "prefecture": "北海道",
    "city": "北見市",
    "address": "北進町4丁目6-9",
    "address_detail": "サンプルハウス",

    # 学区
    "elementary_school": "北進小学校",
    "elementary_school_minutes": "8",
    "junior_high_school": "北光中学校",
    "junior_high_school_minutes": "12",

    # 用途地域
    "use_district": "第一種低層住居専用地域",
    "city_planning": "市街化区域",
    "building_coverage_ratio": "50",
    "floor_area_ratio": "100",

    # === 土地情報 ===
    "land_area": "200.50",
    "land_area_measurement": "公簿",
    "land_category": "宅地",
    "land_rights": "所有権",
    "land_rent": "0",
    "land_ownership_ratio": "100%",
    "private_road_area": "0",
    "private_road_ratio": "0%",
    "setback": "なし",
    "setback_amount": "0",
    "land_transaction_notice": "不要",
    "legal_restrictions": "特になし",
    "terrain": "平坦",

    # === 建物情報 ===
    "building_structure": "木造",
    "construction_date": "2005-04-15",
    "building_floors_above": "2",
    "building_floors_below": "0",
    "total_units": "1",
    "total_site_area": "200.50",
    "building_area": "80.25",
    "total_floor_area": "120.50",
    "area_measurement_type": "壁芯",

    # 間取り
    "room_count": "4",
    "room_type": "LDK",
    "floor_plan_notes": "1F: LDK16帖・和室6帖 / 2F: 洋室8帖×2・洋室6帖",

    # 駐車場
    "parking_availability": "あり",
    "parking_type": "敷地内",
    "parking_capacity": "2",
    "parking_distance": "0",
    "parking_notes": "普通車2台駐車可能",

    # その他
    "property_features": "閑静な住宅街に位置する4LDKの中古一戸建て。南向きで日当たり良好。",
    "notes": "・2020年に外壁塗装済み\n・給湯器2022年交換\n・ペット飼育可",
    "other_transportation": "バス「北進4丁目」停留所 徒歩3分",

    # 省エネ
    "energy_consumption_min": "80",
    "energy_consumption_max": "120",
    "insulation_performance_min": "3",
    "insulation_performance_max": "5",
    "utility_cost_min": "15000",
    "utility_cost_max": "25000",
}


def fill_property_form(driver, data=None):
    """物件フォームにデータを入力（React対応版）"""
    if data is None:
        data = DUMMY_DATA

    print("=" * 60)
    print("物件フォーム ダミーデータ入力開始")
    print("=" * 60)

    # ページ読み込み待機
    time.sleep(3)

    # 物件種別を先に選択（他のフィールドが表示される）
    print("\n[1] 物件種別を選択")
    driver.execute_script("""
        const select = document.querySelector('select[name="property_type"]');
        if (select) {
            for (let opt of select.options) {
                if (opt.text.includes(arguments[0])) {
                    select.value = opt.value;
                    select.dispatchEvent(new Event('change', { bubbles: true }));
                    console.log('物件種別: ' + opt.text);
                    break;
                }
            }
        }
    """, data.get("property_type", "一戸建て"))
    time.sleep(2)

    # 全フィールドに入力（React対応）
    print("\n[2] 全フィールドに入力中...")

    js_code = """
    // React対応の入力関数
    function setReactInput(name, value) {
        const el = document.querySelector(`[name="${name}"]`);
        if (!el) return false;

        if (el.tagName === 'SELECT') {
            // セレクトボックス
            for (let opt of el.options) {
                if (opt.text.includes(value) || opt.value.includes(value)) {
                    el.value = opt.value;
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                    return true;
                }
            }
            return false;
        } else if (el.type === 'checkbox') {
            // チェックボックス
            el.checked = !!value;
            el.dispatchEvent(new Event('change', { bubbles: true }));
            return true;
        } else if (el.type === 'radio') {
            // ラジオボタン（同名の中から選択）
            const radios = document.querySelectorAll(`[name="${name}"]`);
            for (let radio of radios) {
                const label = radio.closest('label')?.textContent?.trim() || '';
                if (label.includes(value)) {
                    radio.checked = true;
                    radio.dispatchEvent(new Event('change', { bubbles: true }));
                    return true;
                }
            }
            return false;
        } else {
            // テキスト・数値・日付（React State対応）
            const proto = el.tagName === 'TEXTAREA'
                ? window.HTMLTextAreaElement.prototype
                : window.HTMLInputElement.prototype;
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(proto, 'value')?.set;

            if (nativeInputValueSetter) {
                nativeInputValueSetter.call(el, value);
            } else {
                el.value = value;
            }
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
            return true;
        }
    }

    const data = arguments[0];
    const results = {};

    for (const [name, value] of Object.entries(data)) {
        if (name === 'property_type') continue;  // 既に設定済み
        results[name] = setReactInput(name, String(value));
    }

    return results;
    """

    results = driver.execute_script(js_code, data)

    # 結果表示
    success = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)
    print(f"  成功: {success}件 / 失敗: {failed}件")

    if failed > 0:
        print("\n  [失敗したフィールド]")
        for name, ok in results.items():
            if not ok:
                print(f"    - {name}")

    time.sleep(1)

    # スクロールして確認
    print("\n[3] 画面スクロールして確認")
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(0.5)

    # スクリーンショット
    print("\n[4] スクリーンショット保存")
    driver.save_screenshot("/Users/yaguchimakoto/my_programing/REA/test_screenshots/dummy_property_full.png")

    # 入力値確認
    print("\n[5] 入力値確認")
    check_fields = ['property_name', 'sale_price', 'city', 'address', 'land_area',
                    'building_area', 'room_count', 'construction_date']

    values = driver.execute_script("""
        const fields = arguments[0];
        const result = {};
        fields.forEach(name => {
            const el = document.querySelector(`[name="${name}"]`);
            if (el) result[name] = el.value;
        });
        return result;
    """, check_fields)

    for k, v in values.items():
        print(f"  {k}: {v}")

    print("\n" + "=" * 60)
    print("入力完了！ブラウザで確認してください。")
    print("=" * 60)

    return results


def main():
    """メイン実行"""
    options = Options()
    options.add_argument("--window-size=1400,900")
    options.add_argument("--window-position=100,100")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(options=options)

    print("物件新規登録ページを開きます...")
    driver.get("http://localhost:5173/properties/new")

    fill_property_form(driver, DUMMY_DATA)

    return driver


if __name__ == "__main__":
    main()
