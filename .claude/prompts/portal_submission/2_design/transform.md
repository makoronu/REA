# 変換ロジック定義

## やること

1. transform 型のマッピングについて変換ルールを定義
2. コード変換表を作成
3. `transform.json` を作成

## 変換パターン

| パターン | 説明 | 例 |
|----------|------|-----|
| code_map | コード変換 | 1 → "A01" |
| format | 書式変換 | 1000000 → "1,000,000" |
| unit | 単位変換 | 100㎡ → 30.25坪 |
| date | 日付形式 | 2026-01-12 → 2026/01/12 |
| split | 分割 | "東京都渋谷区" → ["東京都", "渋谷区"] |
| conditional | 条件分岐 | null → "未定" |

## 出力テンプレート

```json
{
  "transforms": {
    "field_name": {
      "type": "code_map|format|unit|date|split|conditional",
      "config": {}
    }
  },
  "code_maps": {
    "property_type": {
      "land": "01",
      "house": "02",
      "mansion": "03"
    },
    "prefecture": {
      "東京都": "13",
      "神奈川県": "14"
    }
  },
  "date_formats": {
    "source": "YYYY-MM-DD",
    "target": "YYYY/MM/DD"
  },
  "unit_conversions": {
    "sqm_to_tsubo": 0.3025
  }
}
```

## 完了条件

- [ ] 全変換ルール定義済み
- [ ] コード変換表作成済み
- [ ] transform.json 作成済み

## 次 → 3_implement/config.md
