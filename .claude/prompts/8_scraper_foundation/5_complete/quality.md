# 品質チェック

## チェックリスト
- [ ] 全ファイル500行以下（`wc -l`で確認。超過→分離必須、進めるな）
- [ ] ハードコードなし（URL・認証情報・マジックナンバー）
- [ ] ENUM なし（master_options で管理）
- [ ] 論理削除（deleted_at）全テーブルに存在
- [ ] 監査カラム（created_at/updated_at）全テーブルに存在
- [ ] 全 SELECT に deleted_at IS NULL
- [ ] SQLi 防止（パラメータバインディング）
- [ ] エラー握りつぶしなし（最低限ログ出力）
- [ ] トランザクション保護（複数テーブル更新時）
- [ ] datetime は UTC 統一

## 確認コマンド
```bash
# 500行超えファイル検索
find market-intelligence/ -name "*.py" -exec sh -c 'lines=$(wc -l < "$1"); [ "$lines" -gt 500 ] && echo "$lines $1"' _ {} \;

# ハードコード検索
grep -rn "localhost\|:8005\|:8010" market-intelligence/mi-api/ market-intelligence/mi-scraper/
grep -rn "password\|secret\|api_key" market-intelligence/ --include="*.py" | grep -v ".env"

# ENUM検索
grep -rn "class.*Enum" market-intelligence/ --include="*.py"
```

## 完了条件
- [ ] 全チェック項目OK

## 中断条件
- 1つでもNG → 修正してから次へ

## 次の工程
→ commit.md
