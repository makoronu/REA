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
| 作業中 | なし |
| 完了 | Seg 19: reinfolib XKT001/XKT014区域区分取得バグ修正（kubun_idフィルタ追加、市街化区域が非線引になるバグ+防火地域境界誤判定修正）、Seg 18h: 法令制限チェックリストDB化（ハードコード撤廃→マスターテーブル駆動、LegalChecklistField新規作成）、Seg 18g: multi_select JSONB型不一致修正（用途地域・都市計画の表示・保存バグ修正）+road_* 404修正、Seg 18f: RegulationPanel入力補助化+FieldGroup法規制自動取得ボタン削除（GeoPanel同様パターン: 取得→結果表示→一括反映、ハザード情報表示追加）、Seg 18e: DynamicForm+FieldFactory責務分割（DynamicForm 1190→465行、FieldFactory 1241→447行、8ファイル新規抽出、全ファイル500行以下）、Seg 18d: GeoPanel学区FieldGroup重複削除（モーダル内の学区手動修正欄を削除、通常フォームに一本化）、Seg 18c: useGeoFetch関数参照安定化（clearResults/handleBulkFetch useCallback化、無限ループバグ修正）、Seg 18b: GeoPanel駅・バス停・施設の選択UI追加（チェックボックスリスト化+選択ベース反映）、Seg 18a: GeoPanelバス停・施設データ構造修正（BusStopsField/NearbyFacilitiesField期待構造に合わせ）、Seg 17c-3: RegulationPanel分離（法令制限タブ→モーダル化、RegulationTab508行削除）、Seg 17c-2: GeoPanelマップウィザード化（地図→ピン→一括取得→反映）、Seg 17c-1: Geoフィールド表示復元+LocationFieldマップ削除、Seg 17c: Geo UI分離（GeoPanel独立モーダル化）、Seg 17b: 新規物件作成バグ修正（property_name必須バリデーション+エラー日本語化）、Seg 17a: エラーメッセージUI改善（ErrorBanner共通化+alert全廃+setTimeout撤去）、Seg 16b: フロントエンド fetch→apiサービス統一(UsersPage/DynamicForm 8箇所)、Seg 16a: セキュリティ+バックエンド修正(admin認証追加/ZOHO print→logger/httpx timeout/deleted_at/naive datetime)、Seg 15b: 駅/バス/施設セクションをコンパクトカード+管理モーダルに変更(スクロール88%削減)、Seg 15a: CSS間隔圧縮(グループ間32→20/内部24→16/見出し24→12)、Seg 14b: Core API geo.pyデッドコード削除(GET11個/ヘルパー5個/スキーマ9個→931行削減)、Seg 14a: Geo API新サービス作成+サーバー設定完了、Seg 13b: ゴーストカラムDB物理削除(25カラム)、Seg 13a: ゴーストカラムコード参照削除、Seg 12: サーバーセキュリティ強化、Seg 11: deleted_at漏れ+naive datetime+SQLi防御、Seg 10b: バックエンドハードコード排除+未使用コード削除、Seg 10a: フロント ハードコード排除+ZONE_COLORS+準備中バグ修正、Seg 9: deleted_at全コードベース修正(14件)、Seg 8b: 定数整理・ハードコード排除、Seg 8a: console.log削除+zoho datetime修正、Seg 7: naive datetime統一、Seg 6: deleted_at漏れ修正、Seg 4/5: エラー表示改善・コード品質修正、Seg 3: ロジックバグ修正、Seg 2: データ整合性修正、Seg 1: セキュリティ修正、Seg C: フロント定数集約、Seg B: N+1解消(validator+geo)、Seg A: touki.pyログ+N+1解消、物件画像保存機能、最寄駅なし/バス停なしUI、システム設定画面、間取り不明、Googleジオコーディング |
| 残り | HOMES入稿、ZOHO画像同期 |
| 更新 | 2026-02-22 |

### 今日完了した作業（2026-02-22 Seg 19）

- **Seg 19: reinfolib XKT001/XKT014 区域区分取得バグ修正**（コミット: 60b5e26）
  - 問題: reinfolib XKT001が複数レイヤー（kubun_id=21:都市計画区域, 22:区域区分）を返し、find_containing_featureが常にkubun_id=21を先に返すため、全都市で「非線引区域」になる
  - 問題: XKT014も防火/準防火境界で準防火が先にヒット
  - client.py: API_DEFINITIONSにpreferred_kubun_ids追加（XKT001:[22], XKT014:[24,25]）
  - client.py: get_regulation_at_pointにkubun_idフィルタ+優先順ソート追加（+16行）
  - RegulationPanel.tsx: null値のsetValue防止（!== undefined → != null、6箇所）
  - 検証: 6都市すべて「市街化区域」が正しく取得されることを確認
  - テスト依頼書: docs/test_requests/2026-02-22_seg19_reinfolib_kubun_id_fix.md

### 次回やること

- HOMES入稿、ZOHO画像同期など残タスク
  - 各ファイル200-500行に収める

- Seg 18完了後: HOMES入稿、ZOHO画像同期など残タスク

### 今日完了した作業（2026-02-21 デプロイ: Seg 18g + 18h）

- **Seg 18g: multi_select JSONB型不一致修正 + road_* 404修正**（コミット: 9acf6b8）
  - SelectionFields.tsx: multi_select両ブロックでJSONB型正規化（field.value.map(String)）+保存時.map(Number)
  - DB: road_direction/road_type/road_status master_categories+master_options source='rea'に変更（19件）
  - 本番: デプロイ済み（GitHub Actions run #22252105922）

- **Seg 18h: 法令制限チェックリストDB化**（コミット: b5ad0b5）
  - LegalChecklistField.tsx新規（158行）: DBマスターオプションからカテゴリ別法令チェックリスト表示
  - FieldFactory.tsx: json_legal_checklistケース追加
  - apiPaths.ts: METADATA.options()関数追加
  - legalRegulations.ts削除（87行ハードコード撤廃）
  - DB: master_categories(legal_regulation)+master_options(44件5グループ)+column_labels更新
  - 本番: デプロイ済み（GitHub Actions run #22252105922）

### 今日完了した作業（2026-02-21 デプロイ: Seg 18f品質修正）

- **Seg 18f品質修正: RegulationPanel状態リセット+定数化+デッドコード削除**（コミット: 45d91ca）
  - RegulationPanel.tsx: パネル再オープン時にresults/messageをリセット（GeoPanel準拠useEffect追加）
  - FieldGroup.tsx: 引渡時期の条件分岐マジックストリング→DELIVERY_TIMING定数参照に変更
  - constants.ts: DELIVERY_TIMING定数追加
  - regulations/RegulationPanel.tsx: import先ゼロのデッドコード削除（261行）
  - 本番: デプロイ済み（GitHub Actions run #22251168320）

- **Seg 18f: RegulationPanel反映バグ修正+チェックリスト削除**（コミット: 24c07eb）
  - RegulationPanel.tsx: handleApply useCallback→通常関数に変更（GeoPanel準拠、クロージャ問題解消）
  - RegulationPanel.tsx: チェックリスト削除（入力補助ツールにデータ格納機能は不適切）
  - 本番: デプロイ済み

- **Seg 18f: RegulationPanel入力補助化+FieldGroup法規制自動取得ボタン削除**（コミット: 2d14184）
  - FieldGroup.tsx: 法規制（自動取得）グループの特別処理を全削除（handleFetchZoning/ZoningMapField/isAutoFetchGroup）、368→212行
  - RegulationPanel.tsx: GeoPanel同様の入力補助パターンに改修（325→429行）
    - 即setValue → ローカルstate保存+取得結果テーブル表示
    - 「閉じる」→「キャンセル」+「フォームに反映して閉じる」
    - ハザード情報4項目（洪水/土砂/津波/高潮）の表示追加
    - 反映対象(●)/情報表示のみ(○)の視覚区別
  - 本番: デプロイ済み（GitHub Actions run #22248668676）

### 今日完了した作業（2026-02-21 デプロイ: Seg 18e）

- **Seg 18e: DynamicForm+FieldFactory責務分割**（コミット: 81e6b26）
  - DynamicForm.tsx: 1190→465行（ステータス管理・タブ構築・ヘッダー・バリデーションモーダルを分離）
  - 本番: デプロイ済み（GitHub Actions run #22248002166）
  - FieldFactory.tsx: 1241→447行（選択系フィールド・郵便番号フィールド・共通ユーティリティを分離）
  - LocationField.tsx: 302→217行（不要コード整理）
  - 新規ファイル8つ: buildTabGroups.ts(201行), useStatusSync.ts(170行), FormHeader.tsx(275行), FieldGroup.tsx(368行), SelectionFields.tsx(316行), PostalCodeField.tsx(107行), ValidationErrorModal.tsx(149行), fieldUtils.ts(33行)
  - 全ファイル500行以下達成
  - テスト依頼書: docs/test_requests/2026-02-21_seg18_dynamic_form_split.md

### 今日完了した作業（2026-02-20 デプロイ: Seg 18d）

- **Seg 18d: GeoPanel学区FieldGroup重複削除**（コミット: c3befa1）
  - GeoPanel.tsx: 学区FieldGroupブロック削除（386-402行）、schoolDistrictColumns props削除、FieldGroup/ColumnWithLabel import削除（-21行）
  - DynamicForm.tsx: schoolDistrictColumns算出・渡し削除（-5行）
  - 理由: モーダル内SchoolResultSectionで候補選択→handleApplyで通常フォームに反映されるため、モーダル内の手動修正欄は重複
  - 本番: デプロイ済み（GitHub Actions run #22222514998）

### 今日完了した作業（2026-02-20 デプロイ: Seg 18c）

- **Seg 18c: useGeoFetch関数参照安定化**（コミット: 7334798）
  - useGeoFetch.ts: clearResults/handleBulkFetchをuseCallbackで包む
  - 原因: フック分離時に関数参照が毎レンダー更新→useEffect無限ループ→結果が即クリア
  - 結果: 「フォームに反映して閉じる」ボタンが常にdisabledになるバグ修正
  - 本番: デプロイ済み（GitHub Actions run #22221608715）

### 今日完了した作業（2026-02-20 デプロイ: Seg 18a + 18b）

- **デプロイ完了**（5コミット、フロントエンドのみ、DB変更なし）
  - Seg 18a: GeoPanelバス停・施設データ構造修正
  - Seg 18b: 駅・バス停・施設の選択UI追加
  - GeoPanel結果コンポーネント分離 + 開発プロンプトにファイル行数制限追加
  - GeoPanel 500行以下化（地図コンポーネント+fetchフック分離）
  - 本番: GitHub Actions成功（run #22220930527）、ヘルスチェックOK

### 今日完了した作業（2026-02-20 Seg 18a + 18b）

- **Seg 18a: GeoPanelバス停・施設データ構造修正**（コミット: 6d5cdf8）
  - handleApply バス停: `{name, routes}` → `{bus_stop_name, line_name}`（BusStopsField期待構造に合わせ）
  - handleApply 施設: `{name}` → `{facility_name}` + `distance_meters`追加（NearbyFacilitiesField期待構造に合わせ）

- **Seg 18b: GeoPanel駅・バス停・施設の選択UI追加**（コミット: 7ac9305）
  - StationResultSummary → StationSelectList（全駅チェックボックスリスト、デフォルト上位3件選択）
  - BusStopResultSummary → BusStopSelectList（全バス停チェックボックスリスト、デフォルト上位5件選択）
  - FacilityResultSummary → FacilitySelectList（カテゴリ別施設リスト+チェックボックス、デフォルト各カテゴリ最寄り1件選択）
  - handleApply: slice固定 → 選択状態ベースのfilterに変更
  - セクションヘッダに「N件選択中」カウンター追加
  - テスト依頼書: docs/test_requests/2026-02-20_seg18_geo_panel_data_fix_and_selection_ui.md

### 今日完了した作業（2026-02-20 デプロイ: Seg 17c-1 + 17c-2 + 17c-3）

- **デプロイ完了**（6コミット、フロントエンドのみ、DB変更なし）
  - Seg 17c-1: Geoフィールド表示復元+LocationFieldマップ削除
  - Seg 17c-2: GeoPanelマップウィザード化
  - Seg 17c-3: RegulationPanel分離（法令制限タブ→モーダル化）
  - 本番: GitHub Actions成功、ヘルスチェックOK

### 今日完了した作業（2026-02-20 Seg 17c-3）

- **Seg 17c-3: RegulationPanel分離**（コミット: 4abd666）
  - RegulationTab.tsx削除（508行）
  - RegulationPanel.tsx新規作成（325行、モーダル）
  - DynamicForm.tsx: 法令制限タブ除去、土地情報タブに自動取得ボタン追加
  - constants.ts: regulationFromLandInfo空配列化（法規制フィールドがland_infoタブに復帰）
  - fetch直接使用→api.get()に統一
  - テスト依頼書: docs/test_requests/2026-02-20_seg17c3_regulation_panel.md

### 今日完了した作業（2026-02-20 Seg 17c-2）

- **Seg 17c-2: GeoPanelマップウィザード化**（コミット: 64f2e2a）
  - GeoPanel.tsx完全リライト（1278→592行、54%削減）
  - Leaflet地図+ドラッグ可能マーカー+クリックでピン操作
  - Promise.allSettledで学区・駅・バス・施設を4API同時取得（部分失敗対応）
  - 学区候補は学区内フラグで自動選択、クリックで変更可能
  - 駅上位3件・バス上位5件を自動設定
  - 「フォームに反映して閉じる」でsetValue一括書き込み
  - constants.ts: GEO_SEARCH_CONFIG.PROPERTY_BUS_STOPS.LIMIT追加

### 今日完了した作業（2026-02-20 Seg 17c-1）

- **Seg 17c-1: Geoフィールド表示復元+LocationFieldマップ削除**（コミット: d96e56d）
  - constants.ts: TAB_GROUPS.location復元→['所在地','学区','電車・鉄道','バス','周辺施設']
  - DynamicForm.tsx: GEO_GROUPS除外フィルタ削除、タブラベル「所在地・周辺情報」に復元
  - LocationField.tsx: Leafletマップ完全削除（302→174行）、緯度経度入力+ジオコードボタンのみ
  - GeoPanel自動取得ボタン維持（17c-2で改修予定）

- **Seg 17c: Geo UI分離**（コミット: 2464f5a、デプロイ済み）
  - GeoPanel.tsx新規作成（1277行）: 学区・駅・バス・施設の4セクションを独立モーダルに
  - DynamicForm.tsx: Geoコード1150行削除（2325→1207行、48%削減）
  - constants.ts: TAB_GROUPS.location→['所在地']のみ、GEO_GROUPS定数追加
  - 所在地タブに「周辺情報を管理（学区・駅・バス・施設）」ボタン追加
  - テスト依頼書: docs/test_requests/2026-02-20_seg17c_geo_ui_separation.md
  - 本番: デプロイ済み（GitHub Actions run #22212975611）

### 今日完了した作業（2026-02-20 Seg 17b）

- **Seg 17b: 新規物件作成バグ修正**（コミット: 1cd4a79）
  - Backend: properties.py エラーメッセージ日本語化（"property_name is required" → "物件名は必須です"）
  - Frontend: useMetadataForm.ts createZodSchemaでis_required+テキスト型フィールドにmin(1)バリデーション追加
  - メタデータ駆動: is_requiredフラグ + label_jaでエラーメッセージ自動生成
  - テスト依頼書: docs/test_requests/2026-02-20_seg17b_property_name_required.md
  - 本番: デプロイ済み

### 今日完了した作業（2026-02-20 Seg 17a）

- **Seg 17a-1: ErrorBanner共通コンポーネント + 管理ページ6つ置換**（コミット: 3327e9f）
  - ErrorBanner.tsx新規作成（エラー: sticky/×閉じ/コピーボタン、成功: 自動消去）
  - UsersPage: error/success表示→ErrorBanner、setTimeout2箇所削除
  - FieldVisibilityPage: message表示→ErrorBanner、setTimeout2箇所削除
  - IntegrationsPage: error/success表示→ErrorBanner、setTimeout2箇所削除
  - SystemSettingsPage: error/success表示→ErrorBanner、setTimeout1箇所削除
  - ToukiImportPage: error/success表示→ErrorBanner
  - PropertiesPage: alert()8箇所→setBannerMessage+ErrorBanner

- **Seg 17a-2: 物件編集+フォーム系エラーUI改善**（コミット: 92c7764）
  - PropertyEditDynamicPage: alert()3箇所→ErrorBanner/successMessage
  - DynamicForm: setTimeout8箇所削除+インラインメッセージ×ボタン追加+validationError状態追加
  - FieldFactory: setTimeout4箇所削除+zoningMessage×ボタン追加
  - LocationField: エラー時auto-dismiss廃止+×ボタン追加
  - RegulationTab: メッセージ×ボタン追加
  - ImageUploader: alert()2箇所→ErrorBanner
  - useMetadataForm: alert()→onValidationErrorコールバック化
  - テスト依頼書: docs/test_requests/2026-02-20_seg17a_error_ui_improvement.md
  - 本番: デプロイ済み

### 今日完了した作業（2026-02-20）

- **Seg 16a + 16b デプロイ完了**
  - Seg 16a: セキュリティ+バックエンド修正
    - P9: admin認証追加（GET /property-types, GET /field-visibility）
    - P10: ZOHOトークンログ除去（print→logger）
    - P2: httpxタイムアウト10秒追加
    - P1: zoho_import_staging deleted_at IS NULLフィルタ追加（3クエリ）
    - P5: scrapers_common naive datetime→UTC
    - P3a: FieldVisibilityPage fetch→api統一（4箇所）
  - Seg 16b: フロントエンド fetch→apiサービス統一
    - P3b: UsersPage fetch→api統一（4箇所）
    - P3c: DynamicForm fetch→api統一（4箇所 geo系）
  - 本番: デプロイ済み

### 今日完了した作業（2026-02-19）

- **Seg 15a + 15b デプロイ完了**
  - Seg 15a: CSS間隔圧縮（グループ間32→20px、内部24→16px、見出し24→12px）
  - Seg 15b: 電車・鉄道/バス/周辺施設をコンパクトカード+管理モーダルに変更
  - 所在地・周辺情報タブのスクロール量約88%削減
  - 本番: デプロイ済み

### 今日完了した作業（2026-02-17）

- **Seg 14a: Geo API新サービス作成**
  - rea-geo/ ディレクトリ新規作成（独立FastAPIサービス）
  - 読み取り専用11エンドポイントをCore APIからコピー
  - config.py: GeoSettings（外部API URL管理）
  - main.py: CORS(GET only) + ヘルスチェック
  - server/rea-geo.service: systemdサービス定義
  - server/nginx-geo-location.conf: GET→:8007, POST→:8005 分離
  - deploy.yml: rea-geo再起動+ヘルスチェック追加（script_stop対応でワンライナー化）
  - サーバー設定: systemd enable/start + nginx locationブロック追加
  - 検証: ヘルスチェックOK、最寄駅OK、凡例14件OK、外部ポートアクセス不可OK
  - テスト依頼書: docs/test_requests/2026-02-17_seg14a_geo_api_service.md
  - 本番: デプロイ済み + サーバー設定済み

- **Seg 14b: Core API geo.pyデッドコード削除**
  - Core API geo.py: GET 11個+ヘルパー5個+スキーマ9個削除（1,290行→359行）
  - POST 3個のみ残す（set-nearest-stations, set-school-districts, set-zoning）
  - テスト依頼書: docs/test_requests/2026-02-19_seg14b_core_api_geo_cleanup.md

- **Seg 15a: CSS間隔圧縮**
  - DynamicForm.tsx: 8箇所のpadding/margin/gap値を縮小
  - FieldFactory.tsx: 4箇所のmargin/padding/gap値を縮小
  - グループ間32→20、内部24→16、見出し下24→12、フィールド間24→16
  - テスト依頼書: docs/test_requests/2026-02-19_seg15a_css_spacing.md

- **Seg 13a: ゴーストカラムコード参照削除**
  - properties.py: 元請会社APIエンドポイント(get_contractor_contacts)削除
  - metadata.py: shows_contractor参照+contractor_requiredクエリ削除
  - metadataService.ts: shows_contractor型+contractor_required型削除
  - publication_validator.py: 廃止カラム参照コメント整理
  - fill_dummy_property.py: ダミーデータからゴーストカラム削除
  - テスト依頼書: docs/test_requests/2026-02-17_seg13a_ghost_column_code_cleanup.md
  - コミット: 1ec3ca9
  - 本番: デプロイ済み
  - 次: Seg 13bでDB物理削除

- **Seg 13b: ゴーストカラムDB物理削除**
  - properties: 24カラムDROP（property_name_kana, property_name_public, external_property_id, affiliated_group, brokerage_contract_date, listing_start_date, listing_confirmation_date, internal_memo, property_url, contractor_company_name, contractor_address, contractor_contact_person, contractor_license_number, management_fee, repair_reserve_fund, repair_reserve_fund_base, parking_fee, housing_insurance, investment_property, commission_split_ratio, priority_score, property_manager_name, contractor_email, contractor_phone）
  - land_info: 1カラムDROP（fire_prevention_district）
  - column_labels: 25行DELETE
  - バックアップ: /tmp/rea_backup_seg13b_20260219_124113.sql
  - 本番: 実行済み

### 今日完了した作業（2026-02-19）

- **Seg 12: サーバーセキュリティ強化**
  - サーバー直接修正:
    - systemd: --host 0.0.0.0 → 127.0.0.1（API外部露出防止）
    - .env: 権限644→600（認証情報保護）
    - nginx: セキュリティヘッダー5種追加（X-Frame-Options, X-Content-Type-Options, HSTS, X-XSS-Protection, Referrer-Policy）
    - nginx: server_tokens off（バージョン非表示）
    - DB: VACUUM ANALYZE実行（dead tuples解消）
  - コード修正:
    - deploy.yml: .env復元後chmod 600追加（権限永続化）
    - main.py: CORS localhost削除
    - config.py: 未使用コード削除（SECRET_KEY, BACKEND_CORS_ORIGINS）
  - テスト依頼書: docs/test_requests/2026-02-19_seg12_server_security.md
  - コミット: a17714f
  - 本番: デプロイ済み

### 今日完了した作業（2026-02-17）

- **Seg 11: deleted_at漏れ+naive datetime+SQLi防御**
  - touki.py:967: UPDATE文にAND deleted_at IS NULL追加
  - real_estate_utils.py:166,392: datetime.now()→datetime.now(timezone.utc)
  - properties.py:51-55: trigger_typeホワイトリスト検証追加
  - テスト依頼書: docs/test_requests/2026-02-17_seg11_bugfix_security.md
  - コミット: f57f91b
  - 本番: デプロイ済み

- **Seg 10b: バックエンドハードコード排除+未使用コード削除**
  - properties.py: 公開ステータス文字列3箇所→モジュールレベル定数（PUB_STATUS_*）
  - constants.ts: 未使用エクスポート4件削除（ACTIVE/INACTIVE_SALES_STATUSES, WALK_SPEED, TAB_INFO）
  - constants/tables.ts: 未使用エクスポート2件削除（PROPERTY_TABLES, PropertyTable）
  - shared/utils/date_format.py: ファイル削除（import先ゼロ）
  - テスト依頼書: docs/test_requests/2026-02-17_seg10b_backend_cleanup.md
  - コミット: d443104

- **Seg 10a: フロント ハードコード排除+ZONE_COLORS重複解消+準備中バグ修正**
  - PropertiesPage.tsx: ステータス文字列8箇所→定数参照
  - PropertyEditDynamicPage.tsx: デフォルト値2箇所→定数（'準備中'→'販売準備'バグ修正）
  - CommandPalette.tsx: ステータス比較2箇所→定数
  - RegulationMap.tsx: ローカルZONE_COLORS削除→constants.tsからimport
  - テスト依頼書: docs/test_requests/2026-02-17_seg10a_frontend_hardcode.md
  - コミット: f8c5d68

- **Seg 9: deleted_at IS NULLフィルタ追加（全コードベース残存14件）**
  - properties.py: 元請会社集計にdeleted_atフィルタ追加
  - zoho.py: UPSERT前・既存物件・リトライ時チェック（3箇所）
  - integrations.py: 同期状態一覧・総件数・サマリー・ZOHO同期済み件数（4箇所）
  - geo.py: 最寄駅・学区・用途地域設定の物件取得（3箇所）
  - images.py: 画像更新後取得
  - touki.py: 登記適用時remarks取得
  - homes_exporter.py: LEFT JOIN ON句+WHERE句（削除済みデータのHOMES出力防止）
  - テスト依頼書: docs/test_requests/2026-02-17_seg9_deleted_at_full_codebase.md
  - コミット: 31ec501

- **Seg 8b: 定数整理・ハードコード排除**
  - constants.ts: PUBLICATION_STATUS拡張（+会員公開/公開前確認）、SALES_STATUS拡張（+査定中）、ZONE_COLORS追加
  - DynamicForm.tsx: ハードコード文字列8箇所を定数参照に置換
  - ZoningMapField.tsx: ローカルZONE_COLORS削除→constants.tsからimport
  - ZoningMapPage.tsx: ローカルZONE_COLORS削除→constants.tsからimport
  - テスト依頼書: docs/test_requests/2026-02-17_seg8b_constants_consolidation.md
  - コミット: c8051a5

- **Seg 8a: console.log削除・zoho naive datetime修正**
  - DynamicForm.tsx: console.log('Save button clicked') 削除
  - ZoningMapField.tsx: console.log('ZoningMap: Initializing at') 削除
  - zoho/auth.py: トークン期限管理のdatetime.now()をUTC化（3箇所）
  - zoho/mapper.py: zoho_synced_atのdatetime.now()をUTC化
  - テスト依頼書: docs/test_requests/2026-02-17_seg8a_console_log_zoho_datetime.md
  - コミット: c295511

- **Seg 7: naive datetime統一**
  - portal.py: CSVファイル名タイムスタンプをUTC化
  - touki.py: parsed_at・アップロードファイル名タイムスタンプをUTC化
  - homes_exporter.py: HOMES CSV日時フォールバックをJST明示化（3箇所）
  - テスト依頼書: docs/test_requests/2026-02-17_seg7_naive_datetime_fix.md
  - コミット: fa100c4

- **Seg 6: deleted_at漏れ修正**
  - registries.py: properties存在確認にdeleted_atフィルタ追加（2箇所）
  - touki.py: 全SELECT（list/get/parse/apply/link）にdeleted_atフィルタ追加（14箇所）
  - generic.py: 関連テーブル存在確認にdeleted_atフィルタ追加（1箇所）
  - 個別プロトコル調査で追加1件発見・修正（create_property_from_touki）
  - テスト依頼書: docs/test_requests/2026-02-17_seg6_deleted_at_fix.md
  - コミット: 6352732

- **Seg 4/5: エラー表示改善・コード品質修正**
  - E1: DynamicForm.tsx バリデーションAPIエラー時にユーザー通知追加
  - E5: ToukiImportPage.tsx 一括削除にtry/catch追加（部分失敗対応）
  - E6: useMetadataForm.ts フォームバリデーションエラーalert追加
  - E7: FieldFactory.tsx console.logデバッグ文10箇所削除
  - E15: PropertyEditDynamicPage.tsx setTimeout 3000→MESSAGE_TIMEOUT_MS定数化
  - B15: auth.py タイムゾーン判定安全化（三項演算子括弧追加）
  - テスト依頼書: docs/test_requests/2026-02-17_seg45_error_display_quality.md
  - コミット: c0cbbda

- **Seg 3: ロジックバグ修正**
  - useAutoSave.ts: flush()で保存実行するようlastArgs追跡追加（ページ遷移時のデータ消失防止）
  - CommandPalette.tsx: '成約済'→'成約済み'（ステータス文字列修正）
  - geo.py: GET /zoningのis_primary判定をDESCに統一 + 学校検索半径をschoolに修正
  - FieldVisibilityPage.tsx: テーブル切替時にpendingChangesクリア追加
  - PropertiesPage.tsx: Promise.all→Promise.allSettledで部分失敗対応（2箇所）
  - 偽陽性除外: B8(useMetadataForm defaults), B10(FieldVisibility null=全表示)
  - テスト依頼書: docs/test_requests/2026-02-17_seg3_logic_bugs.md
  - コミット: 861bc00

- **Seg 2: データ整合性修正**
  - generic.py: update()にcommitパラメータ追加（update_full()の部分コミット防止）
  - publication_validator.py: 同一ステータス保存時のバリデーションスキップ削除
  - registries.py: deleted_at IS NULLフィルタ13箇所追加（表題部/甲区/乙区）
  - zoho.py: deleted_at IS NULLフィルタ3箇所追加
  - users.py: メール送信try/except追加 + メール重複チェックにis_active追加
  - テスト依頼書: docs/test_requests/2026-02-17_seg2_data_integrity.md
  - コミット: 0802f2f

- **Seg 1: セキュリティ修正**
  - main.py: スタックトレースをAPIレスポンスから除去（ログには残す）
  - settings.py: 3エンドポイントに認証チェック追加
  - reinfolib.py: radiusパラメータに上限制約(le=5)追加
  - ToukiImportPage/IntegrationsPage/SystemSettingsPage: fetch()→apiサービス置換（認証ヘッダー付与）
  - テスト依頼書: docs/test_requests/2026-02-17_seg1_security_fixes.md
  - コミット: 0c16c38

- **Seg C-1: タイムアウト定数集約**
  - setTimeout(3000/5000)のハードコードをMESSAGE_TIMEOUT_MS/LONG_MESSAGE_TIMEOUT_MSに統一
  - 10ファイル23箇所のマジックナンバーを定数参照に変更
  - テスト依頼書: docs/test_requests/2026-02-17_segc1_timeout_constants.md
  - コミット: d640ade

- **Seg C-2: 外部URL定数集約**
  - 地図タイルURL(GSI/OSM)・LeafletアイコンCDN・zipcloud APIのハードコードを定数化
  - MAP_TILES/LEAFLET_ICON_URLS/EXTERNAL_APIをconstants.tsに集約
  - 6ファイル8箇所のURL直書きを定数参照に変更
  - テスト依頼書: docs/test_requests/2026-02-17_segc2_url_constants.md
  - コミット: ab44734

- **Seg B: N+1クエリ解消（publication_validator + geo）**
  - publication_validator: get_column_labels_batch()追加、ループ内個別クエリ→バッチ取得（約60回→1回）
  - geo: get_facility_categories()をループ外に移動（N回→1回）
  - テスト依頼書: docs/test_requests/2026-02-17_segb_n1_batch.md
  - コミット: 330481a

- **Seg A: touki.py ログ追加 + N+1クエリ解消**
  - create_property_from_touki(): ステップ別ログ追加、登記レコード取得をIN句バッチ化
  - apply_touki_to_property(): ステップ別ログ追加、登記レコード取得・論理削除をIN句バッチ化
  - 全量調査で「トランザクション未保護」と指摘したが、精査の結果コンテキストマネージャで保護済みと判明（修正不要）
  - テスト依頼書: docs/test_requests/2026-02-17_sega_touki_log_batch.md
  - コミット: 3ac20b3

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
| Geo API分離（3サービス化） | `docs/roadmap_geo_api_separation.md` | 🔧計画中 |
| UX改善（geo系ポップアップ化等） | `docs/roadmap_ux_improvements.md` | 📋未着手 |
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
