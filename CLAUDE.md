# REA

## 工程プロンプト（必ず読め）

| 作業 | ファイル |
|------|---------|
| 開発 | `.claude/prompts/2_dev/_main.md` |
| 全体プロトコル調査 | `.claude/prompts/1_audit/_main.md` |
| 個別プロトコル調査 | `.claude/prompts/1_audit/individual/_main.md` |
| デプロイ | `.claude/prompts/3_deploy/_main.md` |
| ポータル入稿 | `.claude/prompts/portal_submission/_main.md` |
| マニュアル作成 | `.claude/prompts/manual_creation/_main.md` |
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
| 作業中 | Seg A: touki.py ログ追加 + N+1解消 |
| 完了 | 物件画像保存機能、最寄駅なし/バス停なしUI、システム設定画面、間取り不明、Googleジオコーディング |
| 残り | HOMES入稿、ZOHO画像同期 |
| 更新 | 2026-01-30 |

### 今日完了した作業（2026-01-30）

- **物件画像保存機能を追加**
  - 問題: 物件画像が保存されない（API/GenericCRUD未対応）
  - 修正: images.py新規作成（アップロード/更新/削除API）
  - 修正: generic.pyのget_fullでproperty_images返却
  - 修正: フロントエンドで画像保存処理追加
  - テスト依頼書: docs/test_requests/2026-01-30_property_images_save.md
  - コミット: 16fb56a
  - 本番: デプロイ済み

### 今日完了した作業（2026-01-19）

- **最寄駅なし・バス停なしチェックボックス追加**
  - 問題: DynamicForm.tsx内のStationAutoFetchButton/BusStopAutoFetchButtonに「なし」オプションがなかった
  - 修正: 両コンポーネントに「最寄駅なし」「バス停なし」チェックボックス追加
  - 離島・山間部等で駅/バス停がない場合にバリデーションスキップ可能
  - コミット: 0d88455
  - 本番: デプロイ済み

- **システム設定管理画面追加**
  - system_settingsテーブル作成（API Key等の機密設定保存用）
  - settings.py: CRUD API追加
  - SystemSettingsPage.tsx: 管理UI追加（/settings/system）
  - Google Maps APIキーをDB管理可能に
  - コミット: ab92b2e, 2ad0f11
  - 本番: デプロイ済み

- **SegA: 間取り「不明」追加 + 都市計画api_aliases設定**
  - 間取りタイプに「不明」オプション追加（バリデーション通過用）
  - 都市計画api_aliasesを設定（reinfolib APIマッピング修正）
  - マイグレーション: scripts/migrations/2026-01-19_sega_room_type_and_city_planning.sql
  - 本番DB: 適用済み

- **SegB: Googleジオコーディング追加**
  - geocode_google()関数追加（geo.py）
  - 優先順位: Google → GSI → Nominatim
  - 環境変数: GOOGLE_MAPS_API_KEY
  - config.py: GOOGLE_GEOCODE_URL追加
  - テスト依頼書: docs/test_requests/2026-01-19_sega_segb_options_and_geocode.md
  - コミット: ab2c1b3

### 今日完了した作業（2026-01-16）

- **Seg3b-2: 旧月額費用カラムバリデーション整理**
  - column_labels: management_fee等のrequired_for_publicationをNULLに
  - publication_validator.py: フォールバック定数から旧カラム参照を削除
  - 本番DB: 適用済み
  - テスト依頼書: docs/test_requests/2026-01-16_seg3b2_validation_cleanup.md
  - コミット: e764a6b

- **Seg3b-3: 月額費用key_value型UIエディタ追加**
  - KeyValueEditorコンポーネント追加（JsonEditors.tsx）
  - FieldFactoryにkey_valueケース追加
  - 動的に項目名・金額の追加・編集・削除が可能
  - テスト依頼書: docs/test_requests/2026-01-16_seg3b3_key_value_ui.md
  - コミット: 2168403

- **空き家特例 仲介手数料修正**
  - 問題: 800万円以下で `min(計算結果, 33万円)` としていた
  - 修正: 800万円以下は一律33万円（固定）を返すように変更
  - ファイル: `shared/real_estate_utils.py:calculate_brokerage_fee()`
  - テスト依頼書: docs/test_requests/2026-01-16_akiya_special_fix.md
  - コミット: 971edc7

### 今日完了した作業（2026-01-14）

- **用途区分フィールドのvisible_for設定**
  - 土地/駐車場/その他で「居住用/事業用/投資用」を非表示に
  - required_for_publicationと整合性確保
  - 本番DB: 適用済み
  - コミット: ce551a6

- **公開前確認自動バリデーション（Seg1 v2）**
  - 公開前確認ステータスの物件を開くと自動でバリデーションエラー表示
  - バリデーションエラー時は「公開前確認」に自動戻し
  - 修正内容: fetch → api.get()、useRef位置修正
  - テスト依頼書: docs/test_requests/2026-01-14_pre_check_validation_seg1_v2.md
  - コミット: 0c6cb82

- **複数バグ修正**
  - Seg1: 防火地域重複解消（fire_prevention_districtを非表示）
  - Seg2: フィールド表示設定の空配列バリデーション削除
  - Seg3: 設定項目（居住用/事業用/投資用）「いずれか1つ必須」バリデーション追加
    - validation_groupカラム追加
    - 同グループで1つでもtrueがないとエラー
  - 本番DB: 適用済み
  - テスト依頼書: docs/test_requests/2026-01-14_multiple_fixes.md
  - コミット: b5e9f13

### 今日完了した作業（2026-01-13）

- **防火地域バリデーション修正**
  - 問題: 「指定なし」選択時にバリデーションエラーが発生
  - 原因: fire_prevention_district（未使用）がバリデーション対象、fire_prevention_area（実使用）が対象外
  - 修正: fire_prevention_districtを無効化、fire_prevention_areaをバリデーション対象に変更
  - 追加修正: fire_prevention_areaのvisible_forをNULL（全ユーザー表示）に変更
  - 本番DB: 適用済み
  - テスト依頼書: docs/test_requests/2026-01-13_fire_prevention_validation_fix.md
  - コミット: 0bbd518

### 今日完了した作業（2026-01-11）

- **min_selections: multi_select最小選択数バリデーション**
  - 新カラム: column_labels.min_selections (INTEGER)
  - get_min_selections関数追加
  - is_valid_value関数にmin_selectionsチェック追加
  - DBマイグレーション: add_min_selections.sql
  - テスト依頼書: docs/test_requests/2026-01-11_min_selections_validation.md
  - コミット: c11242a

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
