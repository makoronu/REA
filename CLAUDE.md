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
| 作業中 | **Seg3b-2〜4**: API/フロント/クリーンアップ |
| 完了 | Seg1〜Seg3a、Seg3b-1完了 |
| 残り | Seg3b-2〜4、HOMES入稿、ZOHO画像同期 |
| 更新 | 2026-01-07 |

### 今日完了した作業（2026-01-07）

- **Seg3b-1: 月額費用JSON化（DB準備）**
  - 新カラム: properties.monthly_costs (JSONB)
  - データマイグレーション: 2,277件
  - 旧フィールド非表示化: management_fee, repair_reserve_fund, repair_reserve_fund_base
  - 本番DB適用済み
  - テスト依頼書: docs/test_requests/2026-01-07_seg3b1_monthly_costs_db.md

- **Seg2: 21フィールド非表示化**
  - column_labels.visible_for = '{}' で非表示化
  - parking_fee.required_for_publication = NULL
  - 一覧ページから元請会社カラム削除
  - コミット: b1129dc

- **Seg3a: 坪単価・仲介手数料自動計算**
  - 坪単価: sale_price ÷ land_area(坪) で自動計算
  - 仲介手数料: 速算法+空き家特例（800万円以下は上限33万円）
  - 定数: TAX_RATE, SQM_TO_TSUBO, AKIYA_SPECIAL_*
  - コミット: f8710d6

### 土地物件バリデーション修正（2026-01-05）

- **問題**: 土地物件の公開時バリデーションが機能しない
- **原因**: column_labels.required_for_publicationに`land`が含まれていなかった
- **修正**: 27フィールドにlandを追加
  - properties: 16件
  - land_info: 11件
- **本番DB**: 適用済み
- **コミット**: f477565

### デプロイ完了（2026-01-04 18:15）

- **50コミット・141ファイル**を本番に反映
- スキーマ差異対応: 新テーブル1、新カラム18、型変換2
- ページネーション修正、ステータス連動DB駆動化、公開バリデーションUI
- バックアップ: `~/REA_backup/20260104/`
- 詳細: `docs/roadmap_deploy_20260104.md`

### 今日完了した作業（2026-01-04）

- **Seg5バグ修正: 非公開連動追加**
  - 問題: 売止め/成約/販売終了→非公開の連動がAPIに未実装
  - 修正: master_optionsにtriggers_unpublishカラム追加
  - 修正: properties.pyでDB駆動の連動処理追加
  - コミット: 6b14cf0

- **Seg5: ステータス連動ロジックAPI一元化**
  - 問題: sales_status→publication_status連動がフロント(2箇所)とAPI(1箇所)に分散
  - 修正: フロント側のpublication_status自動設定を削除
  - 修正: APIレスポンスでUI更新に変更
  - 連動ロジックはAPI（properties.py）で一元管理
  - コミット: e2ef9ad

- **公開バリデーション リアルタイムチェック機能**
  - API: GET /properties/{id}/validate-publication 追加
  - UI: 公開/会員公開選択時に即時バリデーション実行
  - UI: エラー時は保存ボタン無効化（グレーアウト）
  - UI: エラーモーダルからグループ名クリックで該当タブへ移動
  - テスト: 全項目PASS
  - コミット: bf4b4b2

- **city_planning INTEGER→JSONB変更**
  - DBカラム型変更: INTEGER→JSONB（複数選択対応）
  - column_labels: input_type を multi_select に変更
  - 理由: 境界線上の土地で複数の都市計画区域が該当するケースあり
  - コミット: 459a223

- **reinfolib API option_code数値変換**
  - 法令調査ボタンで取得した値を数値に変換
  - 'rea_3' → 3 に変換して返す
  - コミット: 3e40f93

- **land_info input_type修正 + 既存データマイグレーション**
  - column_labels: city_planning, land_category を radio に変更
  - use_district: 2370件を `["rea_*"]` → `[数値]` に変換
  - コミット: a23746d

- **land_info INTEGER対応（metadata API修正）**
  - option_code を数値変換（'rea_1' → 1）
  - DBカラム（INTEGER型）への保存エラー解消
  - コミット: 5c9bd31

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
| 該当なし対応 | `docs/roadmap_publication_validation_none_option.md` | ✅デプロイ完了 |
| ハードコーディング撲滅 | `docs/roadmap_hardcoding_elimination.md` | ✅デプロイ完了 |
| デプロイ 2026-01-04 | `docs/roadmap_deploy_20260104.md` | ✅完了 |

---

## 改善提案（後回し）

| 提案 | 内容 |
|------|------|
| 保存ボタンUI | 保存時に2回点滅する → フルスクリーンオーバーレイで「保存しました」表示に改善 |
| ステータス判定の定数集約 | `['公開','会員公開']`等のハードコードを定数ファイルに集約（ADR-0001準拠）→ `docs/audit_reports/2026-01-04_land_validation_hardcode.md` |

---

## 起動

```bash
# API
cd ~/my_programing/REA/rea-api && PYTHONPATH=~/my_programing/REA python -m uvicorn app.main:app --reload --port 8005

# フロント
cd ~/my_programing/REA/rea-admin && npm run dev
```

本番: https://realestateautomation.net/
