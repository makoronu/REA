# 品質チェック

## チェックリスト

### コード品質
- [ ] 全ファイル500行以下（`wc -l`で確認。超過→分離必須、進めるな）
- [ ] ハードコードなし（URL・セレクタはselectors.py/config.pyに集約）
- [ ] マジックナンバーなし
- [ ] 共通基盤を改変していない
- [ ] パーサーがサイト固有ディレクトリ内に閉じている
- [ ] エラー握りつぶしなし（最低限ログ出力）

### master_options 準拠
- [ ] 全選択フィールドが master_options コード値で保存されている
- [ ] 新しい表記ゆれが api_aliases に登録されている
- [ ] ENUM を使用していない

### データ品質
- [ ] 必須フィールド（price/address）の取得率が90%以上
- [ ] master_options コード変換の成功率が95%以上
- [ ] 型不一致エラーがない

### 防御
- [ ] robots.txt に違反していない
- [ ] レート制限が設定されている（最低3秒間隔）
- [ ] ブロック検知が有効になっている
- [ ] 個人情報（掲載者個人名・個人電話番号）を取得していない

## 確認コマンド
```bash
# ファイル行数確認
wc -l mi-scraper/src/scrapers/{site_name}/*.py

# ハードコード検索
grep -rn "https://" mi-scraper/src/scrapers/{site_name}/ | grep -v "selectors\|config"
```

## 完了条件
- [ ] 全チェック項目OK

## 中断条件
- 1つでもNG → 修正してから次へ

## 次の工程
→ commit.md
