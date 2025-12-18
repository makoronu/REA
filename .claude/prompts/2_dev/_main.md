# 開発（大プロンプト）

**このファイルを読んだら、以下の順序で小工程を実行せよ。スキップ禁止。**

---

## 実行順序

### 1. 準備（中プロンプト）
```
→ 1_prepare/session.md
→ 1_prepare/plan.md      ← 計画提示・承認取得
→ 1_prepare/backup.md
→ 1_prepare/schema.md
→ 1_prepare/existing.md
```

### 2. 実装（中プロンプト）
```
→ 2_implement/implement.md
→ 2_implement/type_check.md
→ 2_implement/quality.md
```

### 3. テスト（中プロンプト）
```
→ 3_test/selenium.md     ← 問題あれば即停止
→ 3_test/doc_update.md
```

### 4. 完了（中プロンプト）
```
→ 4_complete/commit.md
→ 4_complete/schema_update.md
→ 4_complete/log.md
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
【開発】完了
━━━━━━━━━━━━━━━━━━━━
✓ 準備
✓ 実装
✓ テスト
✓ 完了

【成果物】
- コミット: [hash] "[message]"

【確認事項】
次の作業に進んでよいですか？
━━━━━━━━━━━━━━━━━━━━
```

---

## 停止条件

- テスト中に問題発見 → 即停止 → 報告
- 判断に迷う → 即停止 → 質問
