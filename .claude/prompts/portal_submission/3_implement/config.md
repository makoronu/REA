# 設定ファイル作成

## やること

1. 調査結果を元に設定ファイルを整備
2. 既存の共通処理が使えるか確認
3. 不足があれば共通処理を拡張

## 設定ファイル一覧

```
portal_configs/{portal_name}/
  ├── portal.json      # 基本情報（Phase 1で作成済み）
  ├── auth.json        # 認証設定（Phase 1で作成済み）
  ├── form.json        # フォーム定義（Phase 1で作成済み）
  ├── mapping.json     # マッピング（Phase 2で作成済み）
  └── transform.json   # 変換ルール（Phase 2で作成済み）
```

## チェックリスト

- [ ] 全JSONファイルが有効な形式か
- [ ] セレクタが全て取得できているか
- [ ] マッピング漏れがないか
- [ ] 変換ルールが網羅されているか

## 共通処理の確認

```python
# 以下の共通処理が設定ファイルで動作するか確認
- login.py          # auth.json を読み込み
- form_filler.py    # form.json + mapping.json を読み込み
- validator.py      # form.json のバリデーション使用
- transformer.py    # transform.json を読み込み
- image_handler.py  # 画像処理（リサイズ、形式変換）
- submission.py     # 登録ボタン待機処理
```

## 完了条件

- [ ] 全設定ファイル作成済み
- [ ] JSON構文エラーなし
- [ ] 共通処理で読み込み確認済み

## 次 → test.md
