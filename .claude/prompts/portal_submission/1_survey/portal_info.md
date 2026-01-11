# ポータル基本情報

## やること

1. ユーザーから以下を聞き取り
   - ポータル名（HOMES, REINS, SUUMO等）
   - URL
   - 対象物件種別（売買/賃貸、土地/戸建/マンション等）
   - 入稿方式（画面入力/CSV/API）
   - 仕様書の有無

2. `portal_configs/{portal_name}/portal.json` を作成

## 出力テンプレート

```json
{
  "portal_name": "",
  "url": "",
  "property_types": [],
  "transaction_types": [],
  "submission_method": "form|csv|api",
  "spec_document": "path or null",
  "notes": ""
}
```

## 完了条件

- [ ] portal.json 作成済み
- [ ] ユーザー承認済み

## 次 → auth.md
