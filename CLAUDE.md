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
| 作業中 | 公開時バリデーション必須項目データ投入（デプロイ待ち） |
| 完了 | 公開時バリデーション「該当なし」対応（Segment A〜E）本番デプロイ完了 |
| 残り | HOMES入稿、ZOHO画像同期 |
| 更新 | 2026-01-03 |

---

## ロードマップ

| タスク | ファイル | 状態 |
|--------|---------|------|
| 該当なし対応 | `docs/roadmap_publication_validation_none_option.md` | ✅実装完了 |

---

## 改善提案（後回し）

| 提案 | 内容 |
|------|------|
| 保存ボタンUI | 保存時に2回点滅する → フルスクリーンオーバーレイで「保存しました」表示に改善 |

---

## 起動

```bash
# API
cd ~/my_programing/REA/rea-api && PYTHONPATH=~/my_programing/REA python -m uvicorn app.main:app --reload --port 8005

# フロント
cd ~/my_programing/REA/rea-admin && npm run dev
```

本番: https://realestateautomation.net/
