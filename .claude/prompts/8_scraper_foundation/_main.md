# スクレイパー基盤構築（大プロンプト）

**このファイルを読んだら、以下の順序で小工程を実行せよ。スキップ禁止。**

---

## 必須ルール

1. **各小工程の冒頭で「現在位置: 8_scraper_foundation/X/Y.md」を出力せよ**
2. **問題発生時 → 即停止 → 報告 → 指示待ち**
3. **REAのコードを変更するな。完全に別プロジェクト**
4. **企画書 `docs/企画書_market_intelligence.md` を必ず先に読め**

---

## 実行順序

### 1. 準備
```
→ 1_prepare/session.md
→ 1_prepare/plan.md
→ 1_prepare/repo_init.md  ← git init/.gitignore/requirements.txt
→ 1_prepare/backup.md
```

### 2. データベース
```
→ 2_database/schema.md    ← 対象テーブル・カラム型確認
→ 2_database/ddl.md
→ 2_database/seed.md
```

### 3. パイプライン共通基盤
```
→ 3_pipeline/fetcher.md
→ 3_pipeline/normalizers.md
→ 3_pipeline/converter.md
→ 3_pipeline/registrar.md
→ 3_pipeline/cli.md       ← CLIエントリーポイント（main.py）
→ 3_pipeline/scheduler.md ← 日次/週次スケジューラー
```

### 4. API
```
→ 4_api/api.md
```

### 5. 完了
```
→ 5_complete/type_check.md  ← Python構文チェック
→ 5_complete/quality.md
→ 5_complete/schema_update.md ← column_labels登録・型定義確認
→ 5_complete/commit.md
→ 5_complete/log.md
```

---

## 完了後

```bash
afplay /System/Library/Sounds/Glass.aiff
```

次 → `9_scraper_site/_main.md`（HOMESから開始）
