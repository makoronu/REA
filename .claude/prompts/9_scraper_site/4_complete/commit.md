# コミット

## やること
1. git status で変更確認
2. git add（対象ファイルを指定）
3. コミットメッセージ作成
4. git commit

## コミットメッセージ形式
```
feat: {site_name} スクレイパー追加（パーサー/セレクタ/表記ゆれマッピング）
```

## コミット対象
```
mi-scraper/src/scrapers/{site_name}/   ← サイト固有ファイル一式
scripts/migrations/{date}_{site_name}_api_aliases.sql  ← 表記ゆれ登録SQL
```

## 完了条件
- [ ] コミットした

## 次の工程
→ log.md
