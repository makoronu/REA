# パーサー実装（Parser）

## やること
物件詳細ページのHTMLから生データdictを抽出するパーサーを実装する。
**ここがサイト追加の核。全工程で最も固有性が高い。**

## 実装ファイル
```
mi-scraper/src/scrapers/{site_name}/parser.py    (〜300行)
mi-scraper/src/scrapers/{site_name}/selectors.py  (〜80行、1_surveyで確定済み)
mi-scraper/src/scrapers/{site_name}/field_mapping.py (〜100行)
```

## parser.py の責務

### parse_detail_page() 関数
```python
def parse_detail_page(html: str, url: str) -> dict | None:
    """
    物件詳細ページのHTMLを解析し、生データdictを返す。

    Returns: {
        "タイトル": "○○ニュータウン分譲地",
        "価格": "2,980万円",
        "所在地": "北海道札幌市中央区...",
        "土地面積": "150.25㎡",
        "用途地域": "1種低層",
        ...
        "_listing_id": "12345",
        "_source_url": "https://...",
    }

    パース失敗時は None を返す。
    """
```

### 実装パターン
1. BeautifulSoup でHTMLをパース
2. selectors.py のセレクタで各要素を取得
3. テーブルデータを抽出（dl/dt/dd or table/tr/th/td）
4. field_mapping.py で生データキーを中間フィールド名に変換
5. 各フィールドの値をそのまま返す（**正規化はしない**）

### テーブル抽出の2パターン
```python
# パターンA: dl/dt/dd形式
for dl in soup.select("dl.property-detail"):
    for dt, dd in zip(dl.select("dt"), dl.select("dd")):
        data[dt.text.strip()] = dd.text.strip()

# パターンB: table/tr/th/td形式
for tr in soup.select("table.property-info tr"):
    th = tr.select_one("th")
    td = tr.select_one("td")
    if th and td:
        data[th.text.strip()] = td.text.strip()
```

## field_mapping.py の責務
```python
# サイトのラベル → 中間フィールド名
FIELD_MAP = {
    "価格": "price",
    "販売価格": "price",           # 同じフィールドの別ラベル
    "所在地": "address",
    "住所": "address",             # 同じフィールドの別ラベル
    "土地面積": "land_area",
    "敷地面積": "land_area",       # 同じフィールドの別ラベル
    "建物面積": "building_area",
    "用途地域": "use_district",
    "都市計画": "city_planning",
    "建ぺい率": "building_coverage_ratio",
    "容積率": "floor_area_ratio",
    "構造": "building_structure",
    "築年月": "construction_date",
    "間取り": "room_layout",       # room_count + room_type に分解
    "階建": "floors_above",
    "地目": "land_category",
    "接道状況": "road_info",
    "向き": "direction",
    # ...（field_survey.md の調査結果から作成）
}
```

## 注意点
- **パーサーは正規化しない**。「2,980万円」はそのまま返す
- 正規化は共通 normalizers が担当（責務分離）
- 要素が見つからない場合は None（例外を投げない）
- 想定外のHTML構造の場合はログ出力 + None 返却

## 完了条件
- [ ] サンプルHTMLから全フィールドが抽出できる（土地・戸建・マンション各1件）
- [ ] テーブル形式に対応している
- [ ] listing_id が正しく抽出できる
- [ ] 要素不在時に例外が出ない
- [ ] parser.py 300行以下
- [ ] field_mapping.py が field_survey.md の結果と一致

## 次の工程
→ mapping.md
