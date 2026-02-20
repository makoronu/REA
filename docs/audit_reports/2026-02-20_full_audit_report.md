# 全量プロトコル検査レポート

**検査日:** 2026-02-20
**対象:** REA全コードベース（rea-api, rea-admin, rea-geo, shared）
**検査者:** Claude Code
**判定:** パッチ修正可能

---

## 検査範囲

| 対象 | ファイル数 | 内容 |
|------|-----------|------|
| rea-api | 62 Python | FastAPI バックエンド |
| rea-admin | 75 TSX/TS | React フロントエンド |
| rea-geo | 5 Python | Geo API サービス |
| shared | 35 Python | 共通ライブラリ |
| **合計** | **177ファイル** | |

## 検査項目

| # | 検査項目 | 結果 |
|---|---------|------|
| 1 | deleted_at漏れ | 3件検出 |
| 2 | ハードコーディング | 問題なし（ADR-0001/0002準拠） |
| 3 | any型・型安全性 | 許容範囲（メタデータ駆動による設計判断） |
| 4 | セキュリティ | 4件検出（IDOR・認証バイパス・機密ログ・fetch残存） |
| 5 | N+1クエリ | 問題なし（Seg A/Bで解消済み） |
| 6 | エラーハンドリング | 2件検出 |
| 7 | naive datetime | 1件検出 |
| 8 | 重複コード | パターン重複あり（技術的負債） |
| 9 | メタデータ駆動 | 6項目中6項目準拠 |
| 10 | UX・画面巡回 | 全14画面正常動作確認 |

## 発見事項

### P1: deleted_at漏れ（HIGH）

**箇所:** `rea-api/app/api/api_v1/endpoints/zoho.py`
- L386-393: zoho_import_stagingのSELECTにdeleted_at IS NULLフィルタなし
- L393: 同上（件数カウント）
- L408-414: リトライ処理時の既存データ取得にフィルタなし

**影響:** 論理削除済みのインポートステージングデータが再処理される可能性
**対策:** WHERE句にAND deleted_at IS NULL追加

**プロトコル参照:** §2 Soft_Delete（物理削除禁止、deleted_atで論理削除）

---

### P2: httpxタイムアウト未設定（MEDIUM）

**箇所:** `shared/zoho/auth.py`（2箇所）
- トークン取得リクエスト
- トークンリフレッシュリクエスト

**影響:** ZOHO API障害時にリクエストが無限待機する可能性
**対策:** `timeout=10` パラメータ追加

**プロトコル参照:** §6 External_API timeout（明示的に設定、デフォルト10秒目安）

---

### P3: fetch()直接使用（MEDIUM）

**箇所:**
- `rea-admin/src/pages/Settings/UsersPage.tsx`（L49-50, L93-113, L118-134）
- `rea-admin/src/pages/Settings/FieldVisibilityPage.tsx`
- その他数ページ

**影響:** apiサービス（axios interceptor）を経由しないため、認証ヘッダーが付与されない箇所がある
**対策:** fetch() → api.get()/api.post() に置換

**プロトコル参照:** §5 Reusable_Components（同じ処理を2回書いたら共通化を検討）

**補足:** Seg 1でToukiImportPage/IntegrationsPage/SystemSettingsPageは修正済み。残存箇所あり。

---

### P4: CORS設定（LOW）

**箇所:** `rea-api/app/main.py` L26-28

**現状:**
```python
allow_origins=["https://realestateautomation.net"]
```

**影響:** ローカル開発時にCORSエラーが発生する（Seg 12で意図的にlocalhost削除）
**対策案:** 環境変数 `CORS_ORIGINS` で制御し、開発環境ではlocalhost含む設定

**判断:** Seg 12のセキュリティ強化で意図的に削除した設計判断。本番セキュリティ優先のため、現状維持も許容。ローカル開発時は `--disable-web-security` フラグまたはプロキシで回避可能。

---

### P5: naive datetime（LOW）

**箇所:** `shared/scrapers_common.py:381`
- `datetime.now()` がタイムゾーン指定なし

**影響:** サーバーのローカルタイムに依存（JSTとUTCの不一致リスク）
**対策:** `datetime.now(timezone.utc)` に変更

**プロトコル参照:** §13 Anti_Patterns（タイムゾーン未指定のdatetime）

---

### P6: エラー/ローディング状態管理の重複（INFO）

**箇所:** 全保護ページ（9+ファイル）

**パターン:**
```typescript
const [loading, setLoading] = useState(true);
const [error, setError] = useState('');
// ... 各ページで同一パターン
```

**影響:** 動作に問題なし。コードの冗長性が高い。
**対策案:** カスタムフック `usePageData()` の作成（技術的負債として記録）

**判断:** 現時点では機能に影響なし。将来のリファクタリング候補として記録。

---

### P7: console.error残存（INFO）

**箇所:** `rea-admin/src/services/api.ts`（6箇所）

**影響:** 本番環境でコンソールにエラー情報が出力される
**対策:** 本番ビルドではログレベル制御、または削除

**判断:** デバッグ用途で許容範囲。優先度低。

---

### P8: IDOR - オブジェクトレベル認可チェック欠如（HIGH）

**箇所:** `rea-api/app/api/api_v1/endpoints/properties.py`
- L175: `GET /{property_id}` — ownerチェックなし
- L190: `GET /{property_id}/full` — ownerチェックなし
- L251: `PUT /{property_id}` — 認証あり、ownerチェックなし
- L370: `GET /{property_id}/validate-publication` — ownerチェックなし
- L407: `DELETE /{property_id}` — ownerチェックなし

同様に registries, images, geo の各エンドポイントも同様。

**影響:** 認証済みユーザーが他組織の物件にproperty_id指定でアクセス可能
**対策:** リクエストユーザーのorganization_idと物件のorganization_idを照合

**判断:** 現在シングルテナント（同一組織内ユーザーのみ）のため実害は限定的。マルチテナント化時には必須の対策。

**プロトコル参照:** §8 Authorization（オブジェクトレベル認可、IDOR対策）

---

### P9: 管理画面エンドポイント認証バイパス（MEDIUM）

**箇所:** `rea-api/app/api/api_v1/endpoints/admin.py`
- L102: `GET /admin/property-types` — 認証なし
- L120: `GET /admin/field-visibility` — 認証なし
- L167: `PUT /admin/field-visibility` — 認証なし（書き込み操作）
- L201: `PUT /admin/field-visibility/bulk` — 認証なし（一括更新）

**影響:** 認証なしでフィールド表示設定の変更が可能
**対策:** `get_current_user()` + 管理者ロールチェック追加

**プロトコル参照:** §8 Authentication/Authorization

---

### P10: 機密情報のログ出力（MEDIUM）

**箇所:**
- `shared/zoho/auth.py:80` — ZOHOリフレッシュトークンをprint()出力
- `shared/zoho/auth.py:86` — APIドメインをprint()出力
- `rea-api/app/api/api_v1/endpoints/zoho.py:185` — OAuthコールバック画面でリフレッシュトークンを平文HTML表示

**影響:** トークン漏洩リスク（ログファイル・スクリーンショット共有時）
**対策:** print() → logger（マスキング付き）に変更。コールバック画面はDB保存に変更

**プロトコル参照:** §9 Sensitive_Data（パスワード、トークン等はログ出力禁止、マスキング必須）

---

## Selenium画面巡回結果

| # | ページ | URL | 結果 |
|---|--------|-----|------|
| 1 | ログイン | /login | 正常表示 |
| 2 | 物件一覧 | /properties | 正常表示・データ読み込みOK |
| 3 | 物件編集 | /properties/:id/edit | 正常表示・タブ切替OK |
| 4 | 物件新規 | /properties/new | 正常表示 |
| 5 | フィールド表示設定 | /admin/field-visibility | 正常表示 |
| 6 | 用途地域マップ | /map/zoning | 正常表示・地図描画OK |
| 7 | ZOHOインポート | /import/zoho | 正常表示 |
| 8 | 登記インポート | /import/touki | 正常表示 |
| 9 | 連携設定 | /settings/integrations | 正常表示 |
| 10 | ユーザー管理 | /settings/users | 正常表示 |
| 11 | システム設定 | /settings/system | 正常表示 |
| 12 | ヘルプ一覧 | /help | 正常表示 |
| 13 | ヘルプ詳細 | /help/:categoryId | 正常表示 |
| 14 | パスワードリセット | /reset-password | 正常表示 |

**UX所見:** 全画面でレイアウト崩れ・機能不全なし。Seg 15bのモーダル化によりスクロール量も適切。

---

## メタデータ駆動検証

| # | 検証項目 | 結果 | 備考 |
|---|---------|------|------|
| 1 | フォーム定義 | 準拠 | column_labelsテーブルで動的生成 |
| 2 | バリデーション | 準拠 | required_for_publication + validation_group |
| 3 | 選択肢管理 | 準拠 | master_optionsテーブル（ENUM不使用） |
| 4 | ラベル管理 | 準拠 | column_labels.display_nameで管理 |
| 5 | ENUM不使用 | 準拠 | 全選択肢がマスタテーブル管理 |
| 6 | ハードコード排除 | 準拠 | ADR-0001/0002の判定基準に基づく |

---

## 前回監査との比較

| 指標 | 前回（Seg 1〜15b実施前） | 今回 |
|------|------------------------|------|
| deleted_at漏れ | 30+件 | 3件 |
| ハードコード | 20+件 | 0件 |
| naive datetime | 10+件 | 1件 |
| N+1クエリ | 3件 | 0件 |
| セキュリティ | 5件 | 4件（IDOR・認証バイパス・機密ログ・fetch残存） |
| console.log | 12件 | 0件（console.error 6件は別カテゴリ） |

**改善率:** 全体で約90%の問題が解消済み

---

## 判定

### パッチ修正可能

- アーキテクチャの破綻なし
- データモデルの根本的欠陥なし
- メタデータ駆動設計は正しく機能
- 発見事項はすべて個別箇所の修正で対応可能

### 修正優先順位

1. **P9** admin認証バイパス（admin.py PUT 2箇所）— 認証必須
2. **P10** 機密情報ログ出力（zoho/auth.py print 2箇所）— トークン漏洩防止
3. **P1** deleted_at漏れ（zoho.py 3箇所）— データ整合性
4. **P2** httpxタイムアウト（auth.py 2箇所）— 外部API障害耐性
5. **P3** fetch→api置換（残存ページ）— 認証一貫性
6. **P5** naive datetime（scrapers_common.py 1箇所）— 時刻整合性
7. **P8** IDOR対策（properties.py等）— マルチテナント準備（現状シングルテナントのため任意）
8. **P4** CORS環境変数化 — 開発体験（任意）
9. **P6** 重複コード解消 — 技術的負債（任意）
10. **P7** console.error整理 — コード品質（任意）

---

## 関連ドキュメント

- `docs/adr/0001_metadata_vs_constants.md`
- `docs/adr/0002_rea_prefix_mapping.md`
- `docs/incident_reports/2026-01-04_land_info_type_change.md`
- `protocol.md` §2, §5, §6, §8, §13
