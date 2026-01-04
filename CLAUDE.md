# REA

## 工程プロンプト（必ず読め）

| 作業 | ファイル |
|------|---------|
| 開発 | `.claude/prompts/2_dev/_main.md` |
| 全体プロトコル調査 | `.claude/prompts/1_audit/_main.md` |
| 個別プロトコル調査 | `.claude/prompts/1_audit/individual/_main.md` |
| デプロイ | `.claude/prompts/3_deploy/_main.md` |
| 緊急 | `.claude/prompts/emergency.md` |

### プロトコル調査の使い分け

| 種別 | 対象 | 用途 |
|------|------|------|
| 全体 | 全コード | 大規模変更前、定期監査（スクショ・UXチェック含む） |
| 個別 | 変更箇所のみ | 機能追加後、デプロイ前（軽量・5分以内） |

※ プロトコル準拠チェックの内容は同一。個別は全体スキャンを省略したもの。

常に、プロンプトのどこの段階にいるのか、確認して、そこに立ち戻ること。
勝手にデプロイは厳禁、プロンプトに沿ってやること、ユーザーの指示を特別得た場合は、デプロイプロンプトから始めること。

---

## セッション

| 項目 | 内容 |
|------|------|
| 作業中 | **Seg4完了 → デプロイ準備** |
| 次回 | **全体テスト後、デプロイ実施（9件）** |
| 残り | HOMES入稿、ZOHO画像同期 |
| 更新 | 2026-01-04 |

### 次回やること

1. **全体テスト実施**（Seg1〜4統合テスト）
2. **デプロイ実施**（9件まとめて）
   - Seg1〜4 + property_locations削除（9件）
   - デプロイプロンプト `.claude/prompts/3_deploy/_main.md` に従う
   - 本番: https://realestateautomation.net/

### 今日完了した作業（2026-01-04）

- **Seg4: ハードコーディング撲滅（定数ファイル作成）**
  - DB: column_labels.placeholder カラム追加（マイグレーション）
  - API: metadata.py でplaceholderをDB読み込み
  - 新規: errors.py（エラーメッセージ定数）
  - 新規: placeholders.ts（固定placeholder定数）
  - 新規: dateFormat.ts, date_format.py（日付フォーマット定数）
  - 判定根拠: ADR-0001（メタデータ駆動vs定数）
  - コミット: 761d0de

- **プロトコル整備**
  - protocol.md §19 追加（原則コンフリクト解決）
  - ADR-0001 作成（メタデータ駆動vs定数）
  - 7_protocol プロンプト作成

- **Seg3d: 設定値DB化（メタデータ駆動）**
  - コミット: f60b255

---

## ロードマップ

| タスク | ファイル | 状態 |
|--------|---------|------|
| 該当なし対応 | `docs/roadmap_publication_validation_none_option.md` | ✅実装完了 |
| ハードコーディング撲滅 | `docs/roadmap_hardcoding_elimination.md` | ✅全セグメント完了（デプロイ待ち） |

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
