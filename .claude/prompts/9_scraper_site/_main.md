# サイト追加（大プロンプト）

**以下の順序で小工程を実行。スキップ禁止。**

## 必須ルール
1. 各小工程の冒頭で「現在位置: 9_scraper_site/X/Y.md [{サイト名}]」を出力
2. 問題発生 → 即停止 → 報告 → 指示待ち
3. 共通基盤を改変するな（バグ発見→報告）
4. 基盤（8_scraper_foundation）が構築済みであること
5. curl/WebFetchでのHTML取得は禁止（ローカルからはブロックされる）
6. フェッチモードはhtml_analysis.mdで判定

## 実行順序

### 1. 事前調査
→ 1_survey/robots.md → html_analysis.md → selectors.md → pagination.md → field_survey.md

### 2. 実装
→ 2_implement/fetcher_config.md → discovery.md → parser.md → mapping.md

### 3. テスト
→ 3_test/unit.md → batch.md → diff.md

### 4. 完了
→ 4_complete/type_check.md → quality.md → schema_update.md → commit.md → log.md

## 完了後
別サイト追加 → このプロンプトを再度実行
