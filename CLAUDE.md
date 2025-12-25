# REA

## 工程プロンプト（必ず読め）

| 作業 | ファイル |
|------|---------|
| 開発 | `.claude/prompts/2_dev/_main.md` |
| 検証 | `.claude/prompts/1_audit/_main.md` |
| デプロイ | `.claude/prompts/3_deploy/_main.md` |
| 緊急 | `.claude/prompts/emergency.md` |

常に、プロンプトのどこの段階にいるのか、確認して、そこに立ち戻ること。
勝手にデプロイは厳禁、プロンプトに沿ってやること、ユーザーの指示を特別得た場合は、デプロイプロンプトから始めること。

---

## セッション

| 項目 | 内容 |
|------|------|
| 作業中 | なし |
| 完了 | 物件一覧フィルターUI改善・価格フィルター機能追加（本番デプロイ済み） |
| 残り | ユーザー管理v1.0拡張、HOMES入稿、ZOHO画像同期 |
| 更新 | 2025-12-25 |

---

## 起動

```bash
# API
cd ~/my_programing/REA/rea-api && PYTHONPATH=~/my_programing/REA python -m uvicorn app.main:app --reload --port 8005

# フロント
cd ~/my_programing/REA/rea-admin && npm run dev
```

本番: https://realestateautomation.net/
