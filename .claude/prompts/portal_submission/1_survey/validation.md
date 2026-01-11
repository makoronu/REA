# バリデーション調査

## やること

1. 各項目のバリデーションルールを特定
   - 最大/最小文字数
   - 数値範囲
   - 正規表現パターン
   - 日付形式
   - ファイル形式・サイズ

2. エラー表示方式を確認
   - inline（項目横）
   - alert
   - toast
   - モーダル

3. 仕様書との差異を記録
4. `form.json` にバリデーション追加

## 調査方法

```
1. 空送信 → 必須エラー確認
2. 極端な値入力 → 範囲エラー確認
3. 不正形式入力 → 形式エラー確認
4. DevTools → HTML5バリデーション属性確認
```

## 出力（form.json に追記）

```json
{
  "fields": [
    {
      "validation": {
        "maxLength": null,
        "minLength": null,
        "min": null,
        "max": null,
        "pattern": null,
        "format": "date|datetime|email|url|phone|postal",
        "file_types": [],
        "max_file_size_mb": null
      }
    }
  ],
  "error_display": {
    "type": "inline|alert|toast|modal",
    "selector": ""
  }
}
```

## 仕様書との差異記録

差異があれば `diff_report.md` に記録：

```markdown
| 項目 | 仕様書 | 実画面 | 備考 |
|------|--------|--------|------|
| 物件名 | 50文字 | 100文字 | 画面優先 |
```

## 完了条件

- [ ] 全項目バリデーション特定済み
- [ ] 差異記録済み
- [ ] form.json 更新済み

## 次 → 2_design/mapping.md
