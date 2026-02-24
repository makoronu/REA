# REA変換（Converter）

## やること
共通中間形式を REA の master_options コード値に変換するレイヤーを実装する。
**このレイヤーはサイト差異が完全に消えた後に動く。全サイト共通。**

## 作成ファイル
```
mi-scraper/src/converters/
├── rea_converter.py  (〜200行) — 中間形式→REAスキーマ変換
└── field_map.py      (〜100行) — 中間フィールド名→DBカラム名対応表
```

## rea_converter.py の責務

### 1. 値の変換（正規化済み文字列 → master_optionsコード値）
```python
# 入力: 正規化済み中間形式
{"use_district": "第一種低層住居専用地域", "building_structure": "木造", ...}

# 出力: REAスキーマ準拠
{"use_district": 1, "building_structure": 1, ...}
```

### 2. 変換ロジック
- master_options から `option_value` → `option_code` の逆引きマップを構築
- `api_aliases` も逆引き対象に含める
- option_code が `rea_N` 形式なら N を数値化（REA準拠）
- option_code が数字文字列なら数値化
- マッチしない場合は None + WARNING ログ

### 3. フィールド名の変換
```python
# 中間形式 → DBカラム名
FIELD_MAP = {
    "price": "sale_price",
    "land_area": "land_area",
    "building_area": "building_area",
    "use_district": "use_district",
    "structure": "building_structure",
    "construction_date": "construction_date",
    "room_count": "room_count",
    "room_type": "room_type",
    # ...
}
```
※ フィールドマップはハードコードではなく field_map.py に定数として集約

### 4. データ型の変換
- INTEGER カラム → int()
- DECIMAL カラム → float()
- JSONB カラム → list or dict
- TIMESTAMPTZ → UTC datetime
- TEXT → str（そのまま）

## field_map.py の仕様
- 中間フィールド名 → scraped_properties のカラム名の対応表
- 企画書 §5.3 のスキーマ対応表に準拠
- 逆引き（DBカラム名 → 中間フィールド名）も提供

## 完了条件
- [ ] 正規化済み中間形式を渡すとREAスキーマのdictが返る
- [ ] master_options コード値への変換が正しい
- [ ] マッチしない値で例外が出ない（None + ログ）
- [ ] 全ファイル500行以下

## 次の工程
→ registrar.md
