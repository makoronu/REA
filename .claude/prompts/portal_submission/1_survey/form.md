# フォーム項目・セレクタ取得

## やること

1. ログイン後、物件登録画面へ遷移
2. 全入力項目を洗い出し
3. 各項目について取得：
   - ラベル（表示名）
   - セレクタ（優先: id > name > data属性 > xpath）
   - 入力タイプ（text, select, radio, checkbox, datepicker, file）
   - 必須/任意
   - 選択肢（select/radio の場合）

4. 動的要素を確認
   - 条件分岐で表示/非表示
   - JSで後から生成

5. スクリーンショット保存
6. `form.json` を作成

## セレクタ取得ルール

```
1. id属性あり → #id
2. name属性あり → [name="xxx"]
3. data属性あり → [data-field="xxx"]
4. 上記なし → xpath（最終手段）
```

## 出力テンプレート

```json
{
  "form_url": "",
  "fields": [
    {
      "label": "",
      "db_hint": "",
      "selector": "",
      "type": "text|select|radio|checkbox|datepicker|file|textarea",
      "required": true,
      "options": [],
      "depends_on": null,
      "dynamic": false,
      "notes": ""
    }
  ],
  "screenshots": []
}
```

## 完了条件

- [ ] 全項目洗い出し済み
- [ ] セレクタ全取得済み
- [ ] form.json 作成済み

## 次 → validation.md
