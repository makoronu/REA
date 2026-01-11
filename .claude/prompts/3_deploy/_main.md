# デプロイ（大プロンプト）

**GitHub Actionsで実行。手動デプロイ禁止。**

---

## 実行順序

```
→ 1_prepare.md    ← git push前の確認
→ 2_execute.md    ← GitHub Actionsで実行
→ 3_verify.md     ← 本番確認
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
✓ 準備（マイグレーション実行済み）
✓ GitHub Actions実行
✓ 本番確認

【本番URL】
https://realestateautomation.net/
━━━━━━━━━━━━━━━━━━━━
```

---

## 停止条件

- GitHub Actions失敗 → 即停止 → 報告
