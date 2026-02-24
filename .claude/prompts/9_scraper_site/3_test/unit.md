# 単体テスト

## やること
1件の物件詳細ページをパースして、全フィールドが正しく抽出・変換されるか確認する。

## テスト手順

### Step 1: 生HTML取得
```bash
# 1件の物件詳細ページを取得して保存
python -m mi_scraper fetch-one --site {site_name} --url "https://..." --save-html
```

### Step 2: パーサー単体テスト
```python
# 保存したHTMLでパーサーを実行
from mi_scraper.scrapers.{site_name}.parser import parse_detail_page

with open("storage/{site_name}/sample.html") as f:
    html = f.read()

raw_data = parse_detail_page(html, "https://sample-url")
print("=== 生データ ===")
for k, v in raw_data.items():
    print(f"  {k}: {v}")
```

### Step 3: 正規化テスト
```python
from mi_scraper.normalizers import normalize

normalized = normalize(raw_data, "{site_name}")
print("=== 正規化後 ===")
for k, v in normalized.items():
    print(f"  {k}: {v}")
```

### Step 4: REA変換テスト
```python
from mi_scraper.converters.rea_converter import convert_to_rea

rea_data = convert_to_rea(normalized)
print("=== REA形式 ===")
for k, v in rea_data.items():
    print(f"  {k}: {v} ({type(v).__name__})")
```

## 確認チェックリスト

### 必須フィールド（全物件種別共通）
- [ ] property_name: 文字列が取得できている
- [ ] sale_price: 整数（円単位）に変換されている
- [ ] prefecture: 都道府県が分離されている
- [ ] city: 市区町村が分離されている
- [ ] address: 残りの住所が取得できている

### 土地の場合
- [ ] land_area: float（㎡）に変換されている
- [ ] use_district: INTEGER（master_optionsコード値）に変換されている
- [ ] city_planning: JSONB（配列）に変換されている
- [ ] building_coverage_ratio: float に変換されている
- [ ] floor_area_ratio: float に変換されている

### 戸建・マンションの場合
- [ ] building_area: float（㎡）に変換されている
- [ ] building_structure: INTEGER（master_optionsコード値）に変換されている
- [ ] construction_date: 日付形式に変換されている
- [ ] room_count: INTEGER
- [ ] room_type: INTEGER（master_optionsコード値）

### メタデータ
- [ ] listing_id: サイト内物件IDが取得できている
- [ ] source_url: 元URLが保持されている
- [ ] source_site: サイト名が正しい

## 完了条件
- [ ] 物件種別ごとに1件以上テスト完了（土地・戸建・マンション）
- [ ] 全必須フィールドが正しく変換されている
- [ ] master_optionsコード値が正しい
- [ ] 型が正しい（INTEGER/DECIMAL/TEXT/JSONB）

## 次の工程
→ batch.md
