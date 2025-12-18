# デプロイ（大プロンプト）

**本番反映時に実行。手動デプロイ禁止。deploy.shを使え。**

---

## 実行順序

### 1. 準備（中プロンプト）
```
→ 1_prepare/path.md
→ 1_prepare/backup.md
→ 1_prepare/env.md
→ 1_prepare/config.md
```

### 2. 確認（中プロンプト）
```
→ 2_check/debug.md
→ 2_check/apikey.md
→ 2_check/migration.md
→ 2_check/seed.md
```

### 3. 実行（中プロンプト）
```
→ 3_execute/build.md
→ 3_execute/deploy.md
```

### 4. 検証（中プロンプト）
```
→ 4_verify/verify.md      ← 問題あれば即停止
→ 4_verify/data_check.md
→ 4_verify/cleanup.md
→ 4_verify/log.md
```

---

## 完了時

```bash
afplay /System/Library/Sounds/Glass.aiff
```

報告フォーマット：
```
━━━━━━━━━━━━━━━━━━━━
【デプロイ】完了
━━━━━━━━━━━━━━━━━━━━
✓ 準備
✓ 確認
✓ 実行
✓ 検証

【本番URL】
https://realestateautomation.net/

【確認事項】
本番で動作確認してください
━━━━━━━━━━━━━━━━━━━━
```

---

## 停止条件

- 検証中に問題発見 → 即停止 → 報告
- ロールバック必要 → emergency.md参照
