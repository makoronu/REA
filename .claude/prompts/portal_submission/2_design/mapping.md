# マッピング設計

## やること

1. 自社DB項目とポータル項目を対応付け
2. 各項目のマッピング種別を決定
   - direct: そのままコピー
   - transform: 変換ロジック適用
   - static: 固定値
   - computed: 計算で導出
   - ignore: 入力しない

3. `mapping.json` を作成

## マッピング種別

| 種別 | 説明 | 例 |
|------|------|-----|
| direct | そのままコピー | 物件名 → 物件名 |
| transform | 値変換 | 自社コード1 → ポータルコードA01 |
| static | 固定値 | 会社コード = "12345" |
| computed | 計算 | 坪単価 = 価格 / 面積 |
| concat | 結合 | 住所 = 都道府県 + 市区町村 + 町名 |
| ignore | 入力不要 | - |

## 出力テンプレート

```json
{
  "portal_name": "",
  "mappings": [
    {
      "portal_field": "",
      "portal_selector": "",
      "type": "direct|transform|static|computed|concat|ignore",
      "source": {
        "table": "properties|land_info|building_info",
        "column": ""
      },
      "transform_rule": null,
      "static_value": null,
      "compute_formula": null,
      "concat_sources": [],
      "required": true
    }
  ]
}
```

## 完了条件

- [ ] 全項目マッピング済み
- [ ] mapping.json 作成済み
- [ ] ユーザー承認済み

## 次 → transform.md
