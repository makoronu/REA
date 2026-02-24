# 正規化パーサー（Normalizers）

## やること
サイトごとにバラバラな表記を統一する共通パーサー群を実装する。

## 作成ファイル
```
mi-scraper/src/normalizers/
├── price.py       (〜100行) — 金額パーサー
├── area.py        (〜80行)  — 面積パーサー
├── address.py     (〜150行) — 住所パーサー
├── date_parser.py (〜80行)  — 日付パーサー（築年月等）
├── mapping.py     (〜150行) — 表記ゆれマッピング（DB駆動）
└── __init__.py    (〜30行)  — normalize()統合関数
```

## price.py の仕様
```
入力例                → 出力（整数・円単位）
"2,980万円"           → 29800000
"2980万円"            → 29800000
"1億2,000万円"        → 120000000
"298万円"             → 2980000
"価格未定"            → None
""                    → None
```
- カンマ除去 → 「億」「万」単位変換 → 整数化
- 変換失敗時は None を返す（例外を投げない）

## area.py の仕様
```
入力例                → 出力（float・㎡単位）
"150.25㎡"            → 150.25
"150.25m²"            → 150.25
"150.25平米"          → 150.25
"45.5坪"              → 150.41（坪→㎡変換: ×3.30579）
""                    → None
```

## address.py の仕様
```
入力例                              → 出力
"北海道札幌市中央区南1条西5丁目"     → {
                                        "prefecture": "北海道",
                                        "city": "札幌市中央区",
                                        "address": "南1条西5丁目"
                                      }
```
- 都道府県パターン（47都道府県）で分割
- 市区町村パターン（市・区・町・村）で分割
- 残りを address に格納

## date_parser.py の仕様
```
入力例                → 出力（YYYY-MM-DD or YYYY-MM）
"2020年3月築"         → "2020-03"
"築5年"               → （現在年 - 5）の計算結果
"2020年3月"           → "2020-03"
"令和2年3月"           → "2020-03"
"不明"                → None
```

## mapping.py の仕様（DB駆動）
- master_options の `api_aliases` を読み込む
- サイトごとの表記 → 正式名称のマッピングを構築
- マッピングにヒットしない場合は原文をそのまま返す + ログ出力

```python
# 使用例
mapper = FieldMapper(db_session)

# "1種低層" → "第一種低層住居専用地域"（api_aliasesから解決）
normalized = mapper.normalize("use_district", "1種低層")

# ヒットしない場合
normalized = mapper.normalize("use_district", "見たことない表記")
# → "見たことない表記" をそのまま返す + WARNING ログ
```

## __init__.py の統合関数
```python
def normalize(raw_data: dict, source_site: str) -> dict:
    """生データdict → 共通中間形式dictに変換"""
    return {
        "price": parse_price(raw_data.get("価格") or raw_data.get("販売価格")),
        "land_area": parse_area(raw_data.get("土地面積") or raw_data.get("敷地面積")),
        "address": parse_address(raw_data.get("所在地") or raw_data.get("住所")),
        # ...
    }
```
※ フィールド名の揺れ（「価格」vs「販売価格」）はサイト固有。
  この統合関数はサイトごとに「どのキーが何に対応するか」の定義を受け取る。

## 完了条件
- [ ] 各パーサーが単体テストレベルで動作する
- [ ] 表記ゆれマッピングがDB（master_options.api_aliases）から読み込まれる
- [ ] 変換失敗時に None を返す（例外を投げない）
- [ ] 全ファイル500行以下

## 次の工程
→ converter.md
