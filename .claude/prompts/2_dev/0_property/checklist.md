# 変更前チェックリスト

## カラム追加時
- [ ] ALTER TABLEでデータテーブルに追加
- [ ] column_labelsにINSERT
- [ ] visible_for設定（NULL=全表示）

## バリデーション追加時
- [ ] column_labelsの該当カラム更新
- [ ] サービス層にロジック追加
- [ ] APIで呼び出し

## 確認必須ファイル
- generic.py（CRUD処理）
- properties.py（物件API）
- admin.py（管理API）

## 次 → ../1_prepare/session.md
