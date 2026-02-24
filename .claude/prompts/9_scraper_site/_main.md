# サイト追加（大プロンプト）

**このファイルを読んだら、以下の順序で小工程を実行せよ。スキップ禁止。**

---

## 必須ルール

1. **各小工程の冒頭で「現在位置: 9_scraper_site/X/Y.md [{サイト名}]」を出力せよ**
2. **問題発生時 → 即停止 → 報告 → 指示待ち**
3. **共通基盤を改変するな**（バグ発見→報告→指示待ち）
4. **基盤（8_scraper_foundation）が構築済みであること**

## 対象サイト
作業開始時にユーザーが指定: homes / suumo / athome / 他

---

## 実行順序

### 1. 事前調査
```
→ 1_survey/robots.md
→ 1_survey/html_analysis.md
→ 1_survey/selectors.md
→ 1_survey/pagination.md
→ 1_survey/field_survey.md
```

### 2. 実装
```
→ 2_implement/discovery.md
→ 2_implement/parser.md
→ 2_implement/mapping.md
```

### 3. テスト
```
→ 3_test/unit.md
→ 3_test/batch.md
→ 3_test/diff.md
```

### 4. 完了
```
→ 4_complete/quality.md
→ 4_complete/commit.md
→ 4_complete/log.md
```

---

## 完了後

```bash
afplay /System/Library/Sounds/Glass.aiff
```

別サイト追加 → このプロンプトを再度実行
