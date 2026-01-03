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
| 作業中 | **Seg1〜3c + property_locations削除 デプロイ待ち（6件全テスト済み）** |
| 次回 | **デプロイ実施** → `.claude/prompts/3_deploy/_main.md` から開始 |
| 残り | Seg3d〜4（優先度低）、HOMES入稿、ZOHO画像同期 |
| 更新 | 2026-01-04 |

### 次回やること

1. **デプロイ実施**（Seg1〜3c + property_locations削除、6件）
   - デプロイプロンプト `.claude/prompts/3_deploy/_main.md` に従う
   - 本番: https://realestateautomation.net/

2. デプロイ後、残りセグメント検討
   - Seg3d: その他設定値（30+件、優先度低）
   - Seg4: 日付・メッセージ（85+件、優先度低）

---

## ロードマップ

| タスク | ファイル | 状態 |
|--------|---------|------|
| 該当なし対応 | `docs/roadmap_publication_validation_none_option.md` | ✅実装完了 |
| ハードコーディング撲滅 | `docs/roadmap_hardcoding_elimination.md` | Seg1〜3c完了（デプロイ待ち） |

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
