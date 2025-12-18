# REA

## 工程プロンプト（必ず読め）

| 作業 | ファイル |
|------|---------|
| 開発 | `.claude/prompts/2_dev/_main.md` |
| 検証 | `.claude/prompts/1_audit/_main.md` |
| デプロイ | `.claude/prompts/3_deploy/_main.md` |
| 緊急 | `.claude/prompts/emergency.md` |

---

## セッション

| 項目 | 内容 |
|------|------|
| 作業中 | フィールド表示設定の保存機能修正 |
| 完了 | プロンプトアーキテクチャ構築、visible_for復元（NOT NULL制約削除・NULLに復元） |
| 残り | ユーザー管理v1.0拡張、HOMES入稿、ZOHO画像同期 |
| 更新 | 2025-12-19 |
| 備考 | 12/16コミットでvisible_forにNOT NULL制約追加時、NULLが空配列に変換されフィールド非表示になった。修正済み。 |

---

## 起動

```bash
# API
cd ~/my_programing/REA/rea-api && PYTHONPATH=~/my_programing/REA python -m uvicorn app.main:app --reload --port 8005

# フロント
cd ~/my_programing/REA/rea-admin && npm run dev
```

本番: https://realestateautomation.net/
