# 表記ゆれマッピング登録

## やること
1. field_survey.mdで収集した表記ゆれをmaster_options api_aliasesに登録
2. マイグレーションスクリプト作成: `scripts/migrations/{date}_{site}_api_aliases.sql`

## ルール
- 冪等性あり（再実行で重複しない）
- normalizers/mapping.pyがapi_aliasesから読み込めること

## 完了条件
- [ ] 全表記ゆれが登録された
- [ ] マイグレーションスクリプトがある

## 次 → ../3_test/unit.md
