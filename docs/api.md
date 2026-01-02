# REA API仕様

## 変更ログ

### 2026-01-02
- `PUT /api/v1/properties/{id}`: 公開時バリデーション追加
  - `publication_status`を「公開」「会員公開」に変更する際、`required_for_publication`で設定された必須項目をチェック
  - 未入力項目がある場合は400エラーを返す

## TODO
- 全APIエンドポイントの詳細仕様
