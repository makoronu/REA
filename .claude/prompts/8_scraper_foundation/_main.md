# スクレイパー基盤構築（大プロンプト）

**このファイルを読んだら、以下の順序で小工程を実行せよ。スキップ禁止。**

---

## 前提

- **このプロンプトは Phase 1 で1回だけ使う**
- 成果物: market-intelligence リポジトリの基盤（DB・共通パイプライン・API）
- REA コードベースへの変更は一切行わない
- 企画書: `docs/企画書_market_intelligence.md` を必ず読んでから着手

---

## 必須ルール（逸脱防止）

1. **各小工程の冒頭で「現在位置: 8_scraper_foundation/X/Y.md」を出力せよ**
2. **問題発生時 → 即停止 → ユーザーに報告 → 指示を待て**
3. **REA のコードを変更するな。完全に別プロジェクト**
4. **1ファイル500行以下。超えたら分割**
5. **master_options 準拠。ENUM禁止。ハードコード禁止**

---

## 実行順序

### 1. 準備
```
→ 1_prepare/session.md     ← セッション確認
→ 1_prepare/plan.md        ← 計画提示・承認取得
```

### 2. データベース
```
→ 2_database/ddl.md        ← テーブル作成（DDL）
→ 2_database/seed.md       ← マスターデータ投入（REAからコピー）
```

### 3. パイプライン共通基盤
```
→ 3_pipeline/fetcher.md    ← HTTP取得基盤（レート制限・robots.txt・ブロック検知）
→ 3_pipeline/normalizers.md ← 正規化パーサー（金額・面積・住所・表記ゆれ）
→ 3_pipeline/converter.md  ← REA変換（中間形式→master_optionsコード値）
→ 3_pipeline/registrar.md  ← 登録（UPSERT・差分検知・消失検知・価格履歴）
```

### 4. API
```
→ 4_api/api.md             ← FastAPI基盤（メタデータ・物件・分析エンドポイント）
```

### 5. 完了
```
→ 5_complete/quality.md    ← 品質チェック
→ 5_complete/commit.md     ← コミット
→ 5_complete/log.md        ← ログ記録
```

---

## 完了時

全工程完了後、以下を実行：

```bash
afplay /System/Library/Sounds/Glass.aiff
```

報告フォーマット：
```
━━━━━━━━━━━━━━━━━━━━
【スクレイパー基盤構築】完了
━━━━━━━━━━━━━━━━━━━━
✓ 準備
✓ データベース
✓ パイプライン共通基盤
✓ API
✓ 品質チェック

【成果物】
- リポジトリ: market-intelligence/
- DB: market_intel_db
- テーブル: N個
- 共通パイプライン: fetcher / normalizers / converter / registrar
- API: FastAPI (port 8010)

【次のステップ】
→ 9_scraper_site/_main.md（サイト追加プロンプト）でHOMESから開始
━━━━━━━━━━━━━━━━━━━━
```

---

## 停止条件

- 判断に迷う → 即停止 → 質問
