# サイト追加（大プロンプト）

**このファイルを読んだら、以下の順序で小工程を実行せよ。スキップ禁止。**

---

## 前提

- **このプロンプトはポータルサイトを追加するたびに使い回す**
- 基盤（DB・共通パイプライン・API）は `8_scraper_foundation` で構築済みであること
- 作るのは**サイト固有部分のみ**（パーサー・セレクタ・表記ゆれマッピング）
- 共通部分（fetcher/normalizers/converter/registrar）は触らない

---

## 必須ルール（逸脱防止）

1. **各小工程の冒頭で「現在位置: 9_scraper_site/X/Y.md [サイト名]」を出力せよ**
2. **問題発生時 → 即停止 → ユーザーに報告 → 指示を待て**
3. **1ファイル500行以下。超えたら分割**
4. **共通基盤を改変するな**（バグ発見時はユーザーに報告して指示を待て）
5. **パーサーはサイト固有ディレクトリ内に閉じろ**

---

## 対象サイト指定

作業開始時にユーザーが指定する：
```
対象: [homes / suumo / athome / fudousan_japan / yahoo_realestate]
```

---

## 実行順序

### 1. 事前調査
```
→ 1_survey/robots.md       ← robots.txt確認
→ 1_survey/html_analysis.md ← HTML構造調査
→ 1_survey/selectors.md    ← CSSセレクタ特定
→ 1_survey/pagination.md   ← ページネーション方式特定
→ 1_survey/field_survey.md ← フィールド・表記ゆれ調査
```

### 2. 実装
```
→ 2_implement/discovery.md ← URL発見（一覧→詳細URLリスト）
→ 2_implement/parser.md    ← パーサー実装（HTML→生データdict）
→ 2_implement/mapping.md   ← 表記ゆれマッピング登録（master_options api_aliases）
```

### 3. テスト
```
→ 3_test/unit.md           ← 単体テスト（1件パース→全フィールド確認）
→ 3_test/batch.md          ← バッチテスト（10件→正規化→変換→DB保存）
→ 3_test/diff.md           ← 差分テスト（2回実行→更新/消失確認）
```

### 4. 完了
```
→ 4_complete/quality.md    ← 品質チェック
→ 4_complete/commit.md     ← コミット
→ 4_complete/log.md        ← ログ記録
```

---

## 作成ファイル（サイトごと）

```
mi-scraper/src/scrapers/{site_name}/
├── __init__.py
├── {site_name}_scraper.py    (〜300行) — 一覧巡回＋詳細取得の統括
├── parser.py                 (〜300行) — HTML→生データdict変換
├── selectors.py              (〜80行)  — CSSセレクタ定義
├── config.py                 (〜50行)  — サイト固有設定
└── field_mapping.py          (〜100行) — 生データキー→中間フィールド名対応
```

計: 5ファイル、約830行（全ファイル500行以下）

---

## 完了時

全工程完了後、以下を実行：

```bash
afplay /System/Library/Sounds/Glass.aiff
```

報告フォーマット：
```
━━━━━━━━━━━━━━━━━━━━
【サイト追加】{サイト名} 完了
━━━━━━━━━━━━━━━━━━━━
✓ 事前調査（robots.txt / HTML構造 / セレクタ / ページネーション / フィールド）
✓ 実装（発見 / パーサー / マッピング）
✓ テスト（単体 / バッチ / 差分）
✓ 品質チェック

【成果物】
- パーサー: mi-scraper/src/scrapers/{site_name}/
- ファイル数: N
- 合計行数: N
- 取得可能フィールド: N個
- テスト結果: 単体OK / バッチN件OK / 差分OK

【次のステップ】
→ 別サイトを追加する場合: このプロンプトを再度実行
→ 分析機能に進む場合: Phase 3開発
━━━━━━━━━━━━━━━━━━━━
```

---

## 停止条件

- 判断に迷う → 即停止 → 質問
- robots.txt で Disallow されているページにアクセスしようとしている → 即停止
- CAPTCHA が表示された → 即停止 → 報告
