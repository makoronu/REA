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
| 作業中 | **全体テスト→デプロイ準備** |
| 次回 | **全体テスト後、デプロイ実施** |
| 残り | Seg4（日付・メッセージ）、HOMES入稿、ZOHO画像同期 |
| 更新 | 2026-01-04 |

### 次回やること

1. **全体テスト実施**（Seg1〜3d統合テスト）
2. **デプロイ実施**（8件まとめて）
   - Seg1〜3d + property_locations削除（8件）
   - デプロイプロンプト `.claude/prompts/3_deploy/_main.md` に従う
   - 本番: https://realestateautomation.net/

### 今日完了した作業（2026-01-04）

- **Seg3d: 設定値DB化（メタデータ駆動）**
  - DB: `system_config`テーブル新規作成
  - DB: `property_types.sort_order`カラム追加
  - shared/constants.py: DB読み込み型に変更（_LazyDict）
  - constants.ts: GEO_SEARCH_CONFIG定数追加
  - DynamicForm.tsx: 直書き3件→定数参照
  - geoService.ts: デフォルト値→定数参照
  - コミット: f60b255

- **法令制限自動取得メタデータ駆動化**
  - DB: `master_options.api_aliases`カラム追加
  - API: コード変換処理追加（全角数字→漢数字対応）
  - フロント: 自動取得→直接代入、ハードコーディング削除
  - コミット: c962685, 0d16315

---

## ロードマップ

| タスク | ファイル | 状態 |
|--------|---------|------|
| 該当なし対応 | `docs/roadmap_publication_validation_none_option.md` | ✅実装完了 |
| ハードコーディング撲滅 | `docs/roadmap_hardcoding_elimination.md` | Seg1〜3d完了（デプロイ待ち） |

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
