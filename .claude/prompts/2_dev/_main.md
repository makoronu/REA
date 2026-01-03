# 開発（大プロンプト）

**このファイルを読んだら、以下の順序で小工程を実行せよ。スキップ禁止。**

---

## 必須ルール（逸脱防止）

1. **各小工程の冒頭で「現在位置: X/Y.md」を出力せよ**
2. **問題発生時 → 即停止 → ユーザーに報告 → 指示を待て**
3. **開発完了後 → 必ず `3_deploy/_main.md` へ進め（本番反映必須）**

---

## 実行順序

### 0. 物件関連の場合（該当時のみ）
```
→ 0_property/_main.md  ← 物件管理機能開発時は必読
```

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

### 3. テスト依頼（中プロンプト）
```
→ 3_test/request.md  ← 他人に丸投げ用のテスト依頼書作成
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
✓ テスト依頼
✓ 完了

【成果物】
- コミット: [hash] "[message]"
- テスト依頼: docs/test_requests/[ファイル名].md

【次のステップ】
→ 3_deploy/_main.md（デプロイ必須）
━━━━━━━━━━━━━━━━━━━━
```

---

## 停止条件

- 判断に迷う → 即停止 → 質問

