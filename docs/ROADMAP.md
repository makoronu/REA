# REA ロードマップ

## ビジョン

**日本一の不動産情報システムを目指す**

- マルチテナント対応（他社への販売を前提）
- ホームズ/SUUMO/athome等の複数ポータル連携
- メタデータ駆動による拡張性と保守性の両立
- 住所入力だけで査定・重説に必要な情報を自動収集

---

## 現在の状態

**最終更新**: 2025-12-14
**現在フェーズ**: UI精査対応（フェーズ2.5）

---

## メタデータ駆動 実装検証 ✅ 完了（2025-12-15）

**詳細**: `docs/metadata-driven-verification.md`, `docs/metadata-driven-diagnosis-report.md`

### 実施内容

| # | 項目 | 状態 |
|---|------|------|
| 0-1 | Layer 1診断: DB→API | [x] |
| 0-2 | Layer 2診断: API→フロント | [x] |
| 0-3 | Layer 3診断: データフロー全体 | [x] |
| 0-4 | ハードコードされたカラム名の検索 | [x] |
| 0-5 | 診断結果レポート作成 | [x] |
| 0-6 | **汎用CRUD作成（GenericCRUD）** | [x] |
| 0-7 | **properties.pyを汎用CRUDに置き換え** | [x] |
| 0-8 | **models/schemas/crud/property.py最小化** | [x] |
| 0-9 | **types/property.ts動的型化** | [x] |
| 0-10 | **旧版ファイル6つ削除** | [x] |
| 0-11 | **住所上書き問題解決** | [x] |

**達成**: 「column_labelsにカラム追加 → コード変更ゼロ → 画面に反映」

### 削除したファイル
- rea-api/app/models/property.py（97行→15行に最小化）
- rea-api/app/schemas/property.py（129行→33行に最小化）
- rea-api/app/crud/property.py（204行→16行に最小化）
- rea-admin/src/pages/PropertyEditPage.tsx
- rea-admin/src/pages/PropertyEditPageAutoSave.tsx
- rea-admin/src/pages/Properties/PropertyEditPageV2.tsx
- rea-admin/src/types/propertyTables.types.ts
- rea-admin/src/components/properties/PropertyTabs.tsx
- rea-admin/src/services/propertyFullService.ts

### 新規作成
- rea-api/app/crud/generic.py（汎用CRUD、350行）

---

## UI精査対応（2024-12-14）

詳細: `docs/UI_REVIEW_20241214.md`

### 今すぐやる

| # | 項目 | 状態 |
|---|------|------|
| 1 | ダブり解消：最寄駅・バス・周辺施設を所在地タブに統一、設備タブから削除 | [x] |
| 2 | ダブり解消：物件種別を基本タブのみに統一 | [x] |
| 3 | 不要フィールド削除：物件名カナ | [x] |
| 4 | 不要フィールド削除：画像タブのシステム管理セクション、ファイルパス、URL系 | [x] |
| 5 | ボタン配置：公開を左、登録を右に | [x] |
| 6 | 保存ボタンを上部にも追加 | [x] |
| 7 | タブ順序変更：所在地を最初に | [x] |
| 8 | 最終更新日時を一番上に小さく表示 | [x] |

### 次にやる

| # | 項目 | 状態 |
|---|------|------|
| 9 | 取引態様をラジオ化、「仲介」選択時のみ元請会社入力欄表示 | [x] |
| 10 | ステータス名変更：「案件ステータス」に統一 | [x] |
| 11 | ステータス選択肢：査定中/保留/販売準備/販売中/商談中/成約済み/販売終了/取り下げ/他決 | [x] |
| 12 | 建ぺい率・容積率・用途地域：自動取得値→手入力欄に反映（編集可能） | [x] |
| 13 | 物件種別による設備表示制御（土地・駐車場は建物設備非表示） | [x] |

### 設計検討

| # | 項目 | 状態 |
|---|------|------|
| 14 | 設備タブのアコーディオン折りたたみ | [x] |
| 15 | モーダルのサイズ修正（固定高さ+内部スクロール） | [x] |
| 16 | 学校候補の件数制限（5件程度） | [x] |
| 17 | 公開時バリデーション（必須項目チェック） | [x] |

### フォーム入力方式の改善（2025-12-14追加）

**複数選択に変更（チェックボックス/タグ形式）**
| # | フィールド | 理由 | 状態 |
|---|-----------|------|------|
| 18 | 現況 | 複数状態が混在する場合あり | [x] |
| 19 | 引き渡し時期 | 複数条件を提示する場合あり | [x] |
| 20 | 用途地域 | 複数の用途地域にまたがる土地あり | [x] |
| 21 | 都市計画 | 複数区域にまたがる場合あり | [x] |
| 22 | 地目 | 複数地目の土地あり（宅地+田など） | [x] |

**ラジオボタンに変更（単一選択を明確化）**
| # | フィールド | 備考 | 状態 |
|---|-----------|------|------|
| 23 | 計測方式 | - | [x] |
| 24 | 土地権利 | - | [x] |
| 25 | セットバック | あり/なし/不明 | [x] |
| 26 | 国土法届出 | 要/不要/届出済 | [x] |
| 27 | 地勢 | 平坦/傾斜/高台など | [x] |
| 28 | 建物構造 | 「その他」選択時→テキスト欄追加 | [x] |
| 29 | 面積計測方式 | 壁芯/内法 | [x] |
| 30 | 間取りタイプ | - | [x] |
| 31 | 駐車場 | あり/なし/近隣 | [x] |
| 32 | 駐車場種別 | - | [x] |

**バグ修正**
| # | 項目 | 状態 |
|---|------|------|
| 33 | 設備・周辺環境タブの「設備」重複表示を削除 | [x] |

**検討事項**
| # | 項目 | 状態 |
|---|------|------|
| 34 | 小学校選択UIの改善案（要相談） | [ ] |

### システムの位置づけ（重要メモ）

- **査定から決済まで一貫して使うシステム**（ホームページ掲載だけではない）
- 自社管理番号形式: `会社コード-英数字`（しろくま=4690）
- 掲載確認日: 2週間ごとの確認義務あり

---

## データ表示修正（2025-12-14発見） ✅ 解決済み

### 住所データ上書き問題 ✅ 解決（2025-12-15）

**問題**: `/properties/{id}/full` APIで住所データがNULLになる

**原因**: `land_info`テーブルにも同名カラムがあり、NULLで上書きしていた

**解決方法**: GenericCRUD.get_full()で「propertiesに値がある場合は上書きしない」ロジックを実装

```python
# 既に値がある場合は上書きしない（propertiesを優先）
if key not in result or result[key] is None:
    result[key] = value
```

| # | 項目 | 状態 |
|---|------|------|
| 35 | 住所データ上書き問題の修正（/properties/{id}/full） | [x] |
| 36 | 全物件で住所データ表示確認 | [x] |

### 全項目データ表示確認

**目的**: DBにデータがある項目が全て編集画面に表示されることを確認

| # | 項目 | 状態 |
|---|------|------|
| 37 | propertiesテーブルの全カラム表示確認 | [ ] |
| 38 | building_infoテーブルの全カラム表示確認 | [ ] |
| 39 | land_infoテーブルの全カラム表示確認 | [ ] |
| 40 | amenitiesテーブルの全カラム表示確認 | [ ] |

**関連ファイル**:
- `rea-api/app/api/api_v1/endpoints/properties.py:69-133`（/fullエンドポイント）
- `rea-admin/src/pages/Properties/PropertyEditDynamicPage.tsx`
- `docs/logs/2025-12-14-edit-form-fix.md`（詳細ログ）

---

## 実装済み機能一覧

### API
| エンドポイント | メソッド | 機能 |
|---------------|---------|------|
| /api/properties | GET | 物件一覧 |
| /api/properties/{id} | GET | 物件詳細 |
| /api/properties | POST | 物件登録 |
| /api/properties/{id} | PUT | 物件更新 |
| /api/metadata/{table} | GET | テーブルメタデータ |
| /api/master/{category} | GET | マスターデータ |

### フロントエンド
| ページ | パス | 機能 |
|-------|------|------|
| 物件一覧 | /properties | 一覧表示 |
| 物件詳細 | /properties/{id} | 5タブ編集フォーム |
| 物件新規 | /properties/new | 新規登録 |

### UI機能
| 機能 | 状態 | 備考 |
|------|------|------|
| 自動保存 | ✅ | 2秒デバウンス、ヘッダーにステータス表示 |
| 5タブフォーム | ✅ | 基本/土地/建物/設備/画像 |
| 設備エディタ | ✅ | 152件マスター、カテゴリ別表示 |
| 枠線排除UI | ✅ | 下線スタイル統一 |
| スマホファーストレイアウト | ✅ | ボトムナビ対応 |

---

## フェーズ1: 基盤構築 ✅ 完了

### インフラ
- [x] GitHub Codespaces移行（2025年9月11日〜10月13日）
- [x] Docker環境構築（PostgreSQL:5433, Redis:6379）
- [x] 環境変数の整理（20+ファイルでハードコードパス除去）
- [x] Claude Code移行（2025年12月10日）

### DB最適化
- [x] モノリシック構造から分散構造へ移行
  - Before: propertiesテーブル 294カラム
  - After: 5テーブル、44コアカラム（85%削減）
- [x] column_labelsテーブル構築（143カラム定義）
- [x] マスターデータテーブル整備（9テーブル）

### メタデータ駆動実証
- [x] 設備管理機能（amenitiesテーブル）
  - 14個のbooleanカラム追加
  - バックエンド0行、フロントエンド0行の変更で完全動作
  - 日本語ラベル自動生成確認

### UI
- [x] 5タブ構成完成
  - 基本情報 / 土地情報 / 建物情報 / 設備・アメニティ / 画像
- [x] 自動保存機能（2秒デバウンス）
- [x] 保存ステータス常時表示
- [x] 枠線排除・下線スタイル統一
- [x] スマホファーストレイアウト

---

## フェーズ2: 機能拡充 🔄 進行中

### マスターデータシステム ✅ 完了（2025-12-10）
- [x] マルチテナント対応マスターテーブル設計
  - master_categories（45カテゴリ）
  - master_options（267選択肢）
  - company_master_settings（会社別カスタマイズ）
  - portal_mappings（ポータル連携用）
- [x] ホームズCSV仕様書v4.3.2からENUM抽出・登録
  - 物件種別（63件）、建物構造（12件）、用途地域（14件）等
- [x] 設備マスター完全版（152件・26カテゴリ）
- [x] 将来の拡張性確保
  - SUUMO/athome追加対応可能
  - 会社別マスター設定可能

### ENUM値拡張 ✅ 完了
- [x] property_type の選択肢追加（63種類）
- [x] 各種ステータスENUMの整備（45カテゴリ）
- [ ] バリデーション強化

### フロントエンド改善
- [x] フォームのUX改善（入力欄を日本人向けに太く）
- [x] デザインシステム（CLAUDE.md指針準拠）
- [x] 選択式UIのモーダル化（駅・バス停・周辺施設）
  - SelectableListModal共通コンポーネント作成
  - アコーディオン形式でカテゴリ別表示
  - 選択済みアイテムの横に削除ボタン配置
- [ ] エラーハンドリング強化
- [ ] 残りエディタの枠線排除（RoadInfo/FloorPlans/Transportation/Renovations）
- [ ] ImageUploader.tsxの枠線排除

### 物件種別ごとのフィールド表示制御 ✅ 完了（2025-12-12）
**目的**: 物件種別（マンション、土地、一戸建て等）に応じて表示フィールドを切り替え

**実装内容**:
- column_labelsに `visible_for TEXT[]` カラム追加
- NULL = 全種別表示 / 配列指定 = 指定種別のみ表示
- DynamicFormで物件種別に応じたフィルタリング
- 物件種別を基本情報の先頭に移動

**管理画面**: `/admin/field-visibility`（管理人専用）
- テーブル別・フィールド別に表示種別を設定
- 14種別をグループ別に表示（居住用/事業用/投資用/その他）
- チェックボックスで設定、一括保存可能

**初期設定済みフィールド**:
- 学区（小中学校）: 居住用のみ
- 利回り: 投資用のみ
- 管理費・修繕積立金: 区分所有のみ
- 所在階・専有面積等: 区分所有のみ
- building_info全般: 建物あり種別のみ
- 設備関連: 建物あり種別のみ

**物件種別の整理（2025-12-12）**:
- 15種 → 10種に整理
- 居住用: 一戸建て、マンション、アパート
- 事業用: 店舗、事務所、倉庫、工場
- 投資用: ビル（一棟）
- その他: 土地、駐車場
- `is_new_construction` チェックボックスで新築/中古を管理

### 用途タグ機能（将来実装）
**目的**: 旅館、ホテル、別荘、リゾートマンション等をタグで管理

**実装予定**:
- [ ] `property_use_tags TEXT[]` カラム追加（propertiesテーブル）
- [ ] タグマスター作成（m_property_tags）
- [ ] タグ選択UI（チップ形式）
- [ ] 検索時のタグフィルタリング
- [ ] ポータル出力時のタグ→種別変換

**タグ候補**:
- リゾート / 別荘 / 旅館 / ホテル / 民泊
- 寮 / 社宅 / シェアハウス
- 医療施設 / 介護施設
- 農地 / 山林

### 所属グループのマスター化（将来実装）
**目的**: 所属グループ（支店・部署）を動的に管理可能にする

**実装予定**:
- [ ] `m_groups` マスターテーブル作成（company_id対応）
- [ ] グループ管理画面（追加・編集・削除）
- [ ] 物件編集画面でラジオボタン選択

**優先度**: 中（マルチテナント運用時に必要）

### 自社物件番号の自動採番（将来実装）
**目的**: 既存システムからのインポート後、新規物件に自動で連番を振る

**要件**:
- ユニーク制約を追加（重複禁止）
- 自動採番ルール（例: `REA-000001`、会社別プレフィックス対応）
- 既存データインポート時は手動番号を優先
- 欠番の扱い（再利用するか、しないか）

**優先度**: 低（既存システム移行時に検討）

### 自社情報管理画面（将来実装）
**目的**: 自社の会社情報を管理する管理画面

**実装予定**:
- [ ] `companies` テーブル（マルチテナントの親テーブル）
  - company_name, address, phone, fax, email
  - license_number（宅建免許番号）
  - representative_name（代表者名）
  - logo_url, website_url
- [ ] 自社情報編集画面（/admin/company）
- [ ] 帳票・広告出力時に自社情報を自動挿入

**優先度**: 高（帳票出力に必要）

### 元請会社マスターテーブル化（将来実装）
**目的**: 元請会社情報を正規化し、オートコンプリートで選択可能にする

**背景**:
- 他社物件を扱う際、元請会社情報が必要
- 同じ会社を何度も入力するのは非効率
- 会社情報の一元管理で更新漏れ防止

**実装予定**:
- [ ] `m_contractor_companies` マスターテーブル作成
  - company_name, contact_person, phone, email, address, license_number
- [ ] propertiesテーブルに `contractor_company_id` カラム追加
- [ ] 会社選択UI（オートコンプリート + 自社DB蓄積）
- [ ] 新規会社のその場登録機能
- [ ] 入力するほどDBにデータが溜まる仕組み
- [ ] 既存データの移行

### API開発
- [x] Properties CRUD基本実装
- [ ] 検索・フィルタリング強化
- [ ] ページネーション
- [ ] マスターデータAPI追加

### 設備管理テスト
- [ ] 保存機能の動作確認
- [ ] バリデーションテスト
- [ ] 自動保存エラー時の再試行UI

---

## フェーズ3: 地理データ自動取得システム ✅ 大部分完了

物件の住所から各種地理情報を自動取得し、DBに反映。**査定・重説に必要なデータを自動収集。**

**最終更新**: 2025-12-11

---

### Phase 0: 空間DB基盤 ✅ 完了

**PostGIS導入（全地理機能の前提）**
- [x] PostgreSQLにPostGIS拡張追加
- [x] 空間インデックス設計
- [x] SRID統一（4326: WGS84）

---

### Phase 1: 基盤（必須） ✅ 大部分完了

**1. 位置情報基盤** ✅
- [x] 住所→緯度経度変換（Geocoding）
  - 国土地理院API + Nominatim（フォールバック）
- [ ] 地図表示UI（Leaflet.js + 地理院タイル）
- [ ] 地図上でのピン位置調整UI
- [ ] 地理院標高API連携（土地の高さ自動取得）

**2. 最寄駅** ✅ 完了
- [x] 駅データ取得・DB投入（10,390駅・HeartRails Express API）
- [x] 緯度経度から最寄駅検索（ST_Distance）
- [x] 複数駅（徒歩圏内）の自動取得
- [x] 駅までの距離・徒歩分数自動計算
- [ ] 駅別乗降客数データ連携（S12）

**3. 用途地域・法規制（国土数値情報 A29/A55）**
- [ ] 用途地域データ取得・PostGIS投入
- [ ] 緯度経度から用途地域自動判定（ST_Contains）
- [ ] 建ぺい率・容積率の自動取得
- [ ] 防火地域・準防火地域の自動取得
- [ ] 高度地区の自動取得

**4. 学区情報** ✅ 完了
- [x] 小学校区データ取得・DB投入（13,586学区）
- [x] 中学校区データ取得・DB投入（1,532学区）
- [x] 緯度経度から学区自動判定
- [x] 学校までの距離自動計算
- [x] 学区外でも最寄り学校を検索（フォールバック）

**5. バス停** ✅ 完了
- [x] バス停データ取得・DB投入（278,515件・国土数値情報P11）
- [x] 緯度経度から最寄りバス停検索
- [x] 事業者名・路線名の表示

**6. ハザードマップ（国土数値情報 A31/A33/A40/A41）**
- [ ] 洪水浸水想定区域データ投入
- [ ] 土砂災害警戒区域データ投入
- [ ] 津波浸水想定データ投入
- [ ] 高潮浸水想定区域データ投入
- [ ] 緯度経度からリスク判定・自動表示

**6. 道路情報（重説必須）**
- [ ] 接道状況の入力UI
- [ ] 道路種別マスター（公道/私道/位置指定道路/開発道路/農道/通路）
- [ ] セットバック必要面積の自動計算
- [ ] 道路幅員の記録

---

### Phase 2: 価値向上

**7. 周辺施設** ✅ 大部分完了

| 状態 | カテゴリ | 施設 | データソース | 件数 |
|------|---------|------|-------------|------|
| ✅ | 医療 | 病院 | 国土数値情報 P04 | 8,269件 |
| ✅ | 医療 | 診療所 | 国土数値情報 P04 | 172,864件 |
| ✅ | 行政 | 役所 | OSM | 4,812件 |
| ✅ | 行政 | 郵便局 | OSM | 24,526件 |
| ✅ | 金融 | 銀行 | OSM | 13,783件 |
| ✅ | 公園 | 公園 | OSM | 84,822件 |
| ✅ | 教育 | 幼稚園 | 国土数値情報 P29 | 9,402件 |
| ✅ | 教育 | 認定こども園 | 国土数値情報 P29 | 6,258件 |
| ✅ | 教育 | 高校 | 国土数値情報 P29 | 4,996件 |
| ✅ | 教育 | 大学 | 国土数値情報 P29 | 1,239件 |
| ✅ | 教育 | 短大 | 国土数値情報 P29 | 333件 |
| ✅ | 教育 | 高専 | 国土数値情報 P29 | 60件 |
| ✅ | 教育 | 専門学校 | 国土数値情報 P29 | 3,074件 |
| ✅ | 教育 | 職業訓練校 | 手動収集 | 8件（北海道のみ） |
| ✅ | 商業 | スーパー | OSM | 19,991件 |
| ✅ | 商業 | コンビニ | OSM | 48,229件 |
| ✅ | 商業 | ドラッグストア | OSM | 3,482件 |
| ✅ | 商業 | ホームセンター | OSM | 3,507件 |
| ✅ | 生活 | ガソリンスタンド | OSM | 16,021件 |
| ✅ | 娯楽 | 図書館 | OSM | 3,987件 |
| ❌ | 教育 | 保育所 | 未対応 | 公式CSVなし |
| ❌ | 教育 | 職業訓練校（北海道以外） | 未対応 | 手動収集が必要 |

**データソース管理**
- `m_data_sources` テーブルでデータソース情報を管理
- `scripts/data_import/` に更新スクリプト配置
- DBにカテゴリ追加すれば自動的に画面に反映（ハードコード廃止）

**8. ネガティブ要素（減点・告知項目）**

| カテゴリ | 施設 | 理由 |
|---------|------|------|
| 嫌悪施設 | 墓地・火葬場 | 告知義務の可能性 |
| 嫌悪施設 | ゴミ処理場・下水処理場 | 臭気 |
| 嫌悪施設 | 産業廃棄物処理場 | 環境懸念 |
| 嫌悪施設 | 刑務所・拘置所 | イメージ |
| 騒音 | 高速道路・幹線道路沿い | 騒音・振動 |
| 騒音 | 鉄道線路沿い | 騒音・振動 |
| 騒音 | 空港・飛行ルート | 騒音 |
| 騒音 | パチンコ店・風俗店 | 治安イメージ |
| 危険 | 危険物取扱施設 | 爆発・火災リスク |
| 危険 | 高圧電線 | 健康懸念（心理的） |

**9. 不動産情報ライブラリAPI統合** 🔜 次回着手予定

**基本方針**
- メイン機能: 座標ベース自動判定 → テキスト表示（編集可能）
- サブ機能: MAP表示は確認用として最小限
- 免責: 「参考情報です。正確な内容は役所でご確認ください」

**APIエンドポイント共通仕様**
- ベースURL: https://www.reinfolib.mlit.go.jp/ex-api/external/
- 認証: Ocp-Apim-Subscription-Key ヘッダー
- 形式: XYZタイル方式（z/x/y指定）
- 出力: GeoJSON または ベクトルタイル（pbf）

**Phase 1-A: テキスト判定のみ（MAP不要）**
- [ ] 立地適正化計画 (XKT003) → 表示例「居住誘導区域内」
- [ ] 地区計画 (XKT024) → 表示例「○○地区計画区域内」or「対象外」
- [ ] 高度利用地区 (XKT025) → 表示例「対象外」
- [ ] 都市計画道路 (XKT030) → 表示例「計画道路あり（幅員○m）」or「なし」
- [ ] 自然公園地域 (XKT020) → 表示例「対象外」
- [ ] 災害危険区域 (XKT017) → 表示例「対象外」
- [ ] 大規模盛土造成地 (XKT021) → 表示例「対象外」
- [ ] 地すべり防止地区 (XKT022) → 表示例「対象外」
- [ ] 急傾斜地崩壊危険区域 (XKT023) → 表示例「対象外」

**Phase 1-B: テキスト判定 + MAP表示**
- [ ] 防火・準防火地域 (XKT014) → 既存ZoningMapFieldに重ねて表示
- [x] 用途地域 (XKT002) → 実装済み（ローカルDB）、MAP追加
- [x] 都市計画区域/区域区分 (XKT001) → 実装済み（ローカルDB）
- [ ] 洪水浸水想定区域 (XKT026) → 表示例「浸水想定あり（0.5〜3m）」
- [ ] 土砂災害警戒区域 (XKT029) → 表示例「土砂災害警戒区域（急傾斜）」
- [ ] 津波浸水想定 (XKT028) → 表示例「津波浸水想定あり（2m）」
- [ ] 高潮浸水想定区域 (XKT027) → 表示例「対象外」
- [ ] 液状化傾向図 (XKT023) → 表示例「液状化リスク：中」

**Phase 1-C: 周辺施設（既存機能拡張）**
- [x] 小学校区 (XKT004) → 実装済み
- [x] 中学校区 (XKT005) → 実装済み
- [x] 学校 (XKT006) → 実装済み
- [ ] 保育園・幼稚園等 (XKT007) → 距離計算・リスト表示
- [ ] 医療機関 (XKT010) → 距離計算・リスト表示
- [ ] 指定緊急避難場所 (XGT001) → 距離計算・リスト表示

**Phase 2: 価格情報（将来検討）**
- [ ] 取引価格・成約価格 (XIT001)
- [ ] 地価公示・調査 (XPT002)

**DB設計: property_regulationsテーブル新規作成**
- property_id: propertiesへの外部キー
- 都市計画系: fire_prevention_district, height_district, district_plan, location_optimization, planned_road, planned_road_width
- 災害リスク系: flood_risk_level, flood_depth_min, flood_depth_max, landslide_warning_area, landslide_type, tsunami_risk_level, tsunami_depth, storm_surge_risk, liquefaction_risk
- その他制限: natural_park, disaster_risk_area, large_fill_area, landslide_prevention, steep_slope_area
- メタ情報: auto_fetched_at, manually_edited, verified_at, verified_by

**実装順序**
1. 不動産情報ライブラリAPI申請・キー取得 ← **次回最優先**
2. DB設計・マイグレーション作成
3. 不動産情報ライブラリAPI共通クライアント作成（認証、タイル座標変換）
4. Phase 1-A のAPI統合（テキスト判定のみ）
5. Phase 1-B のAPI統合（MAP表示含む）
6. Phase 1-C の周辺施設拡張
7. フロントエンド：物件詳細画面に法令制限セクション追加
8. フロントエンド：災害ハザードMAP表示コンポーネント

**実装不要（スキップ）**
- XIT002（市区町村一覧）、XCT001（鑑定評価書）、XPT001（価格ポイント）
- XKT011（福祉施設）、XKT015（駅別乗降客数）、XKT018（図書館）
- XKT019（市区町村役場）、XKT031（人口集中地区）、XKT013（将来推計人口）

**10. 交通利便性（国土数値情報 P11/N07）**
- [ ] バス停留所データ投入
- [ ] バスルートデータ投入
- [ ] 最寄りバス停の自動取得
- [ ] 高速道路ICまでの距離

**11. 地価情報（国土数値情報 L01/L02）**
- [ ] 地価公示データ投入
- [ ] 都道府県地価調査データ投入
- [ ] 周辺地価の自動表示
- [ ] 坪単価相場との比較

---

### Phase 3: 差別化（査定機能強化）

**12. 地盤・災害リスク詳細（地理院タイル）**
- [ ] 土地条件図の表示・保存
- [ ] 治水地形分類図の表示
- [ ] 活断層図の表示
- [ ] 地すべり地形分布図の表示
- [ ] 明治期の低湿地データ表示（地盤リスク）

**13. 土地履歴（地理院タイル）**
- [ ] 過去の空中写真取得・保存（1936年〜現在）
- [ ] 年代別比較表示機能
- [ ] 土地利用変遷の可視化

**14. 登記情報連携（差別化の切り札）**
- [ ] 登記情報提供サービスAPI連携検討
- [ ] 所有者情報の自動取得
- [ ] 抵当権情報の自動取得
- [ ] 地積測量図のPDF保存

**15. 地図・画像の自動保存**
- [ ] 物件周辺地図画像の自動生成・保存
- [ ] ハザードマップ画像の自動保存
- [ ] 空中写真の自動保存
- [ ] 査定資料用PDF自動生成

---

### データソース一覧

| データ | ソース | コード | コスト |
|--------|--------|--------|--------|
| 緯度経度 | 国土地理院API | - | 無料 |
| 緯度経度 | Google Geocoding API | - | 有料（月$200無料枠≒2,800件） |
| 標高 | 地理院標高API | - | 無料 |
| 用途地域 | 国土数値情報 | A29 | 無料 |
| 都市計画決定情報 | 国土数値情報 | A55 | 無料 |
| 鉄道・駅 | 国土数値情報 | N02 | 無料 |
| 駅別乗降客数 | 国土数値情報 | S12 | 無料 |
| 小学校区 | 国土数値情報 | A27 | 無料 |
| 中学校区 | 国土数値情報 | A32 | 無料 |
| 学校 | 国土数値情報 | P29 | 無料 |
| 洪水浸水想定 | 国土数値情報 | A31 | 無料 |
| 土砂災害警戒 | 国土数値情報 | A33 | 無料 |
| 津波浸水想定 | 国土数値情報 | A40 | 無料 |
| 高潮浸水想定 | 国土数値情報 | A41 | 無料 |
| 医療機関 | 国土数値情報 | P04 | 無料 |
| 公園 | 国土数値情報 | P13 | 無料 |
| 福祉施設 | 国土数値情報 | P14 | 無料 |
| 郵便局 | 国土数値情報 | P30 | 無料 |
| バス停留所 | 国土数値情報 | P11 | 無料 |
| バスルート | 国土数値情報 | N07 | 無料 |
| 地価公示 | 国土数値情報 | L01 | 無料 |
| 地価調査 | 国土数値情報 | L02 | 無料 |
| 取引価格情報 | 不動産情報ライブラリAPI | - | 無料（申請制） |
| 商業施設等 | OpenStreetMap (Overpass API) | - | 無料 |
| 商業施設等 | Google Places API | - | 有料（月$200無料枠） |
| 地図タイル | 地理院タイル | - | 無料 |
| 空中写真 | 地理院タイル | - | 無料 |
| 土地条件図 | 地理院タイル | - | 無料 |

---

### 空間DB設計

```sql
-- ========================================
-- マスターテーブル
-- ========================================

-- 駅マスター
CREATE TABLE m_stations (
    id SERIAL PRIMARY KEY,
    station_code VARCHAR(20) UNIQUE,
    station_name VARCHAR(100) NOT NULL,
    line_name VARCHAR(100),
    company_name VARCHAR(100),
    geom GEOMETRY(POINT, 4326),
    prefecture_code CHAR(2),
    passenger_count INTEGER,  -- 乗降客数
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_stations_geom ON m_stations USING GIST(geom);

-- 用途地域
CREATE TABLE m_zoning (
    id SERIAL PRIMARY KEY,
    zone_code VARCHAR(10),
    zone_name VARCHAR(50),
    building_coverage_ratio DECIMAL(5,2),
    floor_area_ratio DECIMAL(5,2),
    fire_prevention VARCHAR(20),  -- 防火地域
    height_district VARCHAR(50),  -- 高度地区
    geom GEOMETRY(MULTIPOLYGON, 4326),
    prefecture_code CHAR(2),
    city_code VARCHAR(5)
);
CREATE INDEX idx_zoning_geom ON m_zoning USING GIST(geom);

-- 学区
CREATE TABLE m_school_districts (
    id SERIAL PRIMARY KEY,
    school_name VARCHAR(100),
    school_type VARCHAR(20),  -- elementary/junior_high
    address TEXT,
    geom GEOMETRY(MULTIPOLYGON, 4326),
    school_point GEOMETRY(POINT, 4326),
    prefecture_code CHAR(2),
    city_code VARCHAR(5)
);
CREATE INDEX idx_school_districts_geom ON m_school_districts USING GIST(geom);

-- ハザードマップ
CREATE TABLE m_hazard_areas (
    id SERIAL PRIMARY KEY,
    hazard_type VARCHAR(50),  -- flood/landslide/tsunami/storm_surge
    risk_level INTEGER,
    description TEXT,
    geom GEOMETRY(MULTIPOLYGON, 4326),
    data_source VARCHAR(100),
    data_year INTEGER
);
CREATE INDEX idx_hazard_geom ON m_hazard_areas USING GIST(geom);

-- 施設カテゴリ
CREATE TABLE m_facility_categories (
    id SERIAL PRIMARY KEY,
    category_code VARCHAR(20) UNIQUE,
    category_name VARCHAR(50),
    parent_category VARCHAR(20),
    is_negative BOOLEAN DEFAULT false,
    icon VARCHAR(50),
    display_order INTEGER
);

-- 施設マスター
CREATE TABLE m_facilities (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES m_facility_categories(id),
    facility_name VARCHAR(200),
    address TEXT,
    geom GEOMETRY(POINT, 4326),
    prefecture_code CHAR(2),
    city_code VARCHAR(5),
    data_source VARCHAR(50),
    external_id VARCHAR(100),
    metadata JSONB,
    updated_at TIMESTAMP
);
CREATE INDEX idx_facilities_geom ON m_facilities USING GIST(geom);
CREATE INDEX idx_facilities_category ON m_facilities(category_id);

-- ========================================
-- 物件関連テーブル
-- ========================================

-- 物件の地理情報キャッシュ
CREATE TABLE property_geo_cache (
    property_id INTEGER PRIMARY KEY REFERENCES properties(id),
    geom GEOMETRY(POINT, 4326),
    elevation DECIMAL(8,2),
    
    -- 最寄駅（JSON配列）
    nearest_stations JSONB,
    -- [{"station_id":1,"name":"渋谷","line":"JR山手線","distance_m":450,"walk_min":6},...]
    
    -- 学区
    elementary_school_id INTEGER,
    elementary_school_name VARCHAR(100),
    elementary_school_distance_m INTEGER,
    junior_high_school_id INTEGER,
    junior_high_school_name VARCHAR(100),
    junior_high_school_distance_m INTEGER,
    
    -- 用途地域
    zoning_id INTEGER,
    zoning_name VARCHAR(50),
    building_coverage_ratio DECIMAL(5,2),
    floor_area_ratio DECIMAL(5,2),
    fire_prevention VARCHAR(20),
    
    -- ハザード情報（JSON配列）
    hazard_info JSONB,
    -- [{"type":"flood","risk_level":3,"description":"0.5m〜3m未満"},...]
    
    -- 周辺施設（JSON）
    nearby_facilities JSONB,
    
    -- ネガティブ要素（JSON配列）
    negative_factors JSONB,
    
    calculated_at TIMESTAMP DEFAULT NOW()
);

-- 物件の最寄駅（正規化版）
CREATE TABLE property_stations (
    property_id INTEGER REFERENCES properties(id),
    station_id INTEGER REFERENCES m_stations(id),
    distance_meters INTEGER,
    walk_minutes INTEGER,
    is_primary BOOLEAN DEFAULT false,
    PRIMARY KEY (property_id, station_id)
);

-- 物件の周辺施設（正規化版）
CREATE TABLE property_facilities (
    property_id INTEGER REFERENCES properties(id),
    facility_id INTEGER REFERENCES m_facilities(id),
    distance_meters INTEGER,
    walk_minutes INTEGER,
    PRIMARY KEY (property_id, facility_id)
);
```

---

### 技術スタック

| 用途 | 技術 |
|------|------|
| 空間DB | PostGIS（PostgreSQL拡張） |
| 地図表示 | Leaflet.js + 地理院タイル |
| 空間検索 | ST_Contains, ST_Distance, ST_DWithin |
| データ形式 | GeoJSON / Shapefile |
| Shapefile変換 | ogr2ogr (GDAL) |
| API通信 | Python requests / axios |

---

### 実装スケジュール（目安）

#### Week 1: 空間DB基盤
- PostGIS導入
- 駅データ投入（全国約9,000駅）
- 最寄駅検索API実装

#### Week 2: 法規制
- 用途地域データ投入
- 用途地域判定API実装
- 建ぺい率・容積率の自動取得

#### Week 3: 学区・ハザード
- 学区データ投入
- ハザードマップデータ投入
- 判定API実装

#### Week 4: UI統合
- 物件登録時の自動判定
- 地図表示UI
- 周辺施設表示

---

### 国土数値情報の注意点

1. **年度でデータ構造が変わる** - 2023年版と2024年版でカラム名が違うことがある
2. **全国一括だと巨大** - 都道府県別にダウンロードすべき
3. **座標系に注意** - JGD2000/JGD2011の混在あり、PostGISでSRID統一必要
4. **Shapefile→PostGIS変換** - ogr2ogrコマンドで投入

```bash
# Shapefile→PostGIS投入例
ogr2ogr -f "PostgreSQL" PG:"host=localhost port=5433 dbname=real_estate_db user=rea_user password=rea_password" \
  N02-23_Station.shp -nln m_stations -overwrite -lco GEOMETRY_NAME=geom -t_srs EPSG:4326
```

---

## フェーズ4: 自動計算・業務自動化

### 価格・費用の自動計算
- [ ] 坪単価自動計算（sale_price ÷ land_area × 0.3025）
- [ ] 仲介手数料自動計算（価格×3%+6万円+税）
- [ ] 表面利回り自動計算（年間収入÷価格×100）
- [ ] 月額ランニングコスト合計表示
- [ ] 固定資産税概算（評価額×1.4%）

### 日付・期限の自動管理
- [ ] 築年数自動計算（construction_dateから）
- [ ] 媒介契約更新アラート（3ヶ月前通知）
- [ ] 掲載確認日自動算出（専任:2週/一般:なし）
- [ ] 物件鮮度管理（掲載開始からの経過日数）
- [ ] 重説作成期限リマインダー

### ワークフロー自動化
- [ ] 成約時の自動掲載停止
- [ ] 価格変更時のポータル自動更新通知
- [ ] レインズ登録リマインダー
- [ ] 内見予約管理

### バリデーション自動化
- [ ] 建ぺい率/容積率の妥当性チェック（用途地域上限）
- [ ] 専有面積 ≤ 延床面積チェック
- [ ] 所在階 ≤ 地上階数チェック
- [ ] 接道義務チェック（幅員4m以上×間口2m以上）

### 画像処理
- [ ] アップロード時の自動リサイズ・最適化
- [ ] EXIF情報から撮影日取得
- [ ] 画像の自動分類（AI）

---

## フェーズ4.5: ZOHO CRM 連携 🔜 次回着手

**目的**: ZOHO CRM から物件データをインポートし、REA と同期

**詳細ドキュメント**: `docs/ZOHO_INTEGRATION_ROADMAP.md`

### Phase 1: 認証基盤
- [ ] 環境変数設定（ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET等）
- [ ] OAuth 2.0 認証フロー実装
- [ ] 接続確認UI

### Phase 2: データマッピング
- [ ] ZOHO CRM モジュール/フィールド調査
- [ ] zoho_field_mappings テーブル作成
- [ ] マッピング定義

### Phase 3: インポート機能
- [ ] ZOHO物件取得API
- [ ] データ変換処理（ZOHO → REA）
- [ ] インポートAPI（/api/v1/zoho/import）
- [ ] インポートUI（/import/zoho）
- [ ] propertiesテーブルにzoho_id, zoho_synced_at追加

### Phase 4: 同期管理
- [ ] zoho_sync_logs テーブル作成
- [ ] 同期状態表示（物件一覧）
- [ ] 差分検出機能

### 将来検討
- [ ] 双方向同期（REA → ZOHO）
- [ ] Webhook リアルタイム同期

---

## フェーズ4.7: チラシ・マイソク自動生成

**目的**: REAの物件データからチラシとマイソクを自動生成し、印刷入稿可能な形式で出力

**詳細ドキュメント**: `docs/temp_flyer_concept.md`

### チラシ vs マイソク

| 項目 | チラシ | マイソク |
|------|--------|----------|
| 目的 | 集客・訴求 | 詳細情報提供 |
| 対象 | エンドユーザー | 不動産業者・購入検討者 |
| デザイン | 写真大きめ、視覚重視 | 情報網羅、業界標準フォーマット |
| 用途 | ポスティング、店頭 | 業者間共有、内見時配布 |

### 処理フロー

```
REA DB → Python → SVG → 印刷屋（イラレ調整）→ 入稿
```

### Phase 1: 基盤構築
- [ ] データマッピング設計（properties/land_info/building_info→出力項目）
- [ ] 設定ファイル構造設計
- [ ] SVG生成基盤（svgwrite等）
- [ ] ユーティリティ関数（面積変換、築年数計算、価格フォーマット）

### Phase 2: マイソク
- [ ] 土地用テンプレート
- [ ] 戸建用テンプレート
- [ ] マンション用テンプレート
- [ ] 収益物件用テンプレート（利回り、レントロール）

### Phase 3: チラシ（1件用）
- [ ] A4全面テンプレート
- [ ] 写真配置ロジック
- [ ] キャッチコピー配置

### Phase 4: チラシ（複数件）
- [ ] 2件レイアウト（上下/左右分割）
- [ ] 4件グリッドレイアウト
- [ ] 一覧形式レイアウト

### Phase 5: UI連携
- [ ] rea-adminに生成ボタン追加
- [ ] プレビュー機能
- [ ] テンプレート選択UI

### 出力仕様

| 項目 | 仕様 |
|------|------|
| 形式 | SVG（Illustrator編集可能） |
| 色 | CMYK値指定 |
| 塗り足し | 3mm |
| 解像度 | 350dpi相当 |
| フォント | Noto Sans JP |

### 拡張アイデア（将来）
- AIキャッチコピー生成（Claude API）
- QRコード埋め込み
- PDF直接出力
- バッチ生成（新着物件の夜間自動生成）
- REINS/HOMES連携（ポータル用画像として直接アップロード）

---

## フェーズ5: マルチテナント化

### 会社管理
- [ ] companiesテーブル作成
- [ ] 会社別認証・認可
- [ ] 会社別マスター設定UI
- [ ] 会社ロゴ・カラー設定

### ポータル連携
- [ ] ホームズCSV出力機能
- [ ] SUUMO連携対応
- [ ] athome連携対応
- [ ] レインズ連携
- [ ] portal_mappingsを使ったコード変換

### データ連携
- [ ] CSV/Excelインポート
- [ ] 既存データ移行ツール
- [ ] 他社システムからのAPI連携

---

## フェーズ6: 本番準備

### テスト
- [ ] ユニットテスト
- [ ] E2Eテスト
- [ ] パフォーマンステスト
- [ ] セキュリティテスト

### デプロイ
- [ ] 本番環境構築（AWS/GCP）
- [ ] CI/CD設定（GitHub Actions）
- [ ] 監視設定（Datadog/Sentry）
- [ ] バックアップ設定

### セキュリティ
- [ ] 認証・認可の強化
- [ ] データ暗号化
- [ ] 監査ログ
- [ ] GDPR/個人情報保護対応
- [ ] WAF設定
- [ ] DDoS対策
- [ ] 脆弱性診断

---

## フェーズ7: 他社販売

### SaaS化
- [ ] サブスクリプション課金（Stripe）
- [ ] プラン別機能制限
- [ ] オンボーディングフロー
- [ ] 使用量ダッシュボード

### 営業・サポート
- [ ] デモ環境
- [ ] ドキュメント整備
- [ ] サポート体制構築
- [ ] FAQ・ヘルプセンター
- [ ] チャットサポート

---

## データ設計正規化（2025-12-15発足） 🔥 最優先

**目的**: メタデータ駆動アーキテクチャの完全実現

**背景（なぜ必要か）**:
- ENUM型に「3:RC造」のようにコード+ラベルを格納していた → 検索・フィルタが正常動作しない
- column_labels.enum_values と master_options の二重管理 → どちらが正か不明
- マスターテーブル乱立 → 統一感なし
- FK制約なし → データ整合性が担保されない

---

### Phase 1: ENUM廃止 ✅ 完了（2025-12-15）

| # | 項目 | 状態 |
|---|------|------|
| 1-1 | 全ENUM型をINTEGER型に変換（17カラム） | [x] |
| 1-2 | VARCHAR code:label形式をINTEGERに変換（land_category, terrain） | [x] |
| 1-3 | ラベルのみENUMをINTEGERに変換（publication_status, sales_status, tax_type） | [x] |
| 1-4 | フロントエンドのvalue送信をコードのみに修正（FieldFactory.tsx） | [x] |
| 1-5 | m_city_planningマスターテーブル作成 | [x] |

**変換済みカラム一覧**:
- building_info: building_structure, direction, room_type, parking_availability, parking_type, area_measurement_type, building_manager, management_type, management_association
- properties: current_status, transaction_type, delivery_timing, price_status, publication_status, sales_status, tax_type
- land_info: use_district, city_planning, land_rights, setback, land_area_measurement, land_transaction_notice, terrain, land_category
- property_images: image_type

---

### Phase 2: マスターテーブル統合 ✅ 完了（2025-12-15）

**目標**: 選択肢系データを `master_options` に統一

| # | 項目 | 状態 |
|---|------|------|
| 2-1 | 現状のマスターテーブル棚卸し | [x] |
| 2-2 | 統合対象の特定（重複・類似テーブル） | [x] |
| 2-3 | master_categoriesにカテゴリ追加 | [x] |
| 2-4 | 既存データをmaster_optionsに移行 | [x] |
| 2-5 | 旧マスターテーブル参照を切り替え | [x] |
| 2-6 | 旧マスターテーブル削除 | [x] |

**実施内容**:
- enum_valuesの内容を`master_options`に移行（source='rea'）
- `column_labels`に`master_category_code`カラム追加
- メタデータAPIを`master_options`参照に切り替え
- 旧マスターテーブル6つを削除（building_structure, current_status, floor_plan_room_types, land_rights, zoning_districts, image_types）
- `property_types`は残存（Phase 5で対応）

**維持するテーブル（地理系）**:
- m_stations（駅）
- m_facilities（施設）
- m_schools（学校）
- m_zoning（用途地域）
- m_urban_planning（都市計画）
- m_school_districts（学区）
- m_postal_codes（郵便番号）

---

### Phase 3: column_labels.enum_values 廃止 ✅ 完了（2025-12-15）

**目標**: enum_valuesをmaster_optionsから自動生成、enum_valuesカラム削除

| # | 項目 | 状態 |
|---|------|------|
| 3-1 | column_labelsに `master_category_code` カラム追加 | [x] |
| 3-2 | enum_valuesカラムを廃止 | [x] |
| 3-3 | メタデータAPI修正（master_optionsからoptions生成） | [x] |
| 3-4 | cache.py修正（master_optionsから取得） | [x] |

**Before/After**:
```
Before:
column_labels.enum_values = "1:木造,2:鉄骨造,..." ← 手動管理

After:
column_labels.master_category_code = "building_structure"
→ APIがmaster_optionsからoptionsを動的生成
```

---

### Phase 4: FK制約追加 ⏸️ 保留

**目標**: データ整合性の担保

**保留理由（2025-12-15）**:
- master_optionsにHomesコード（source='homes'）とREAコード（source='rea'）が混在
- 同一category_idで異なるsource間でoption_codeが衝突（例: homes:1=木造, homes:2=ブロック vs rea:1=木造, rea:2=鉄骨造）
- FK制約追加には以下のいずれかが必要:
  1. unique制約を(category_id, source, option_code)に変更
  2. REA専用の選択肢テーブルを作成
  3. CHECK制約で代替
- 現状: API層で入力バリデーション済み、優先度低

| # | 項目 | 状態 |
|---|------|------|
| 4-1 | building_info.building_structure → master_options(code) | [ ] 保留 |
| 4-2 | properties.current_status → master_options(code) | [ ] 保留 |
| 4-3 | land_info.use_district → m_zoning(zone_code) | [ ] 保留 |
| 4-4 | land_info.city_planning → m_city_planning(code) | [ ] 保留 |
| 4-5 | 全INTEGER選択肢カラムにFK制約追加 | [ ] 保留 |

---

### Phase 5: property_type 統一 ⏸️ 保留

**目標**: property_typeもINTEGER + master_options参照に統一

**保留理由（2025-12-15）**:
- 現在のVARCHARベース（"detached", "land"等）の設計が正常動作中
- INTEGER化は30+ファイルに影響する大規模リファクタリング
- property_typesテーブルによる参照整合性は担保済み
- 可読性の観点では現在のVARCHARの方が優れる（"detached"は"1"より明確）
- 優先度: 低（他の機能開発を優先）

| # | 項目 | 状態 |
|---|------|------|
| 5-1 | property_typesテーブルの構造確認 | [x] 確認済み |
| 5-2 | master_optionsにproperty_typeカテゴリ統合 | [ ] 保留 |
| 5-3 | properties.property_typeをINTEGERに変換 | [ ] 保留 |
| 5-4 | 既存データ移行（"detached" → 1 等） | [ ] 保留 |
| 5-5 | フロントエンド修正（property_type選択） | [ ] 保留 |

**現状（維持）**:
```
properties.property_type = "detached" ← VARCHAR、英語ID（可読性良好）
property_types.id = "detached", label = "一戸建て"
```

---

### データ設計ルール（今後の開発で必ず守る）

```markdown
## 選択肢カラムの設計ルール

1. **型は必ずINTEGER**
   - ENUM禁止（ALTER必要、マイグレーション面倒）
   - VARCHAR禁止（typo危険、検索効率悪い）

2. **マスターテーブルは2種類のみ**
   - 選択肢系 → master_options（category + code + value）
   - 地理系 → m_* テーブル（GeoJSON/PostGIS）

3. **表示ラベルはDBに保存しない**
   - DBにはコードのみ格納
   - ラベルはmaster_optionsから取得
   - 多言語対応の余地を残す

4. **FK制約は必須**
   - 孤立データ防止
   - 参照整合性担保

5. **column_labels.enum_valuesは廃止方向**
   - master_category_codeを使ってmaster_optionsを参照
   - 二重管理を排除
```

---

### マイルストーン

| フェーズ | 目標 | 効果 |
|---------|------|------|
| Phase 1 | ENUM廃止 | 検索・フィルタ正常動作 |
| Phase 2 | マスター統合 | 管理コスト削減 |
| Phase 3 | enum_values自動生成 | 二重管理解消 |
| Phase 4 | FK制約 | データ整合性担保 |
| Phase 5 | property_type統一 | 完全なメタデータ駆動 |

---

## 技術的負債・メモ

- Tailwindのレスポンシブが効かない箇所あり → インラインstyleで対応中
- 実データ未投入（マスターデータのみ）
- テストコード未整備
- エラーハンドリング未整備
- ~~ENUM型の乱用~~ → Phase 1で解決（2025-12-15）

---

## コードベース統計（2025年12月時点）

| 指標 | 数値 |
|------|------|
| 総ファイル数 | 212 |
| 総行数 | 13,371 |
| 総関数数 | 372 |
| 総クラス数 | 58 |

### マスターデータ統計

| テーブル | 件数 |
|---------|------|
| master_categories | 45 |
| master_options | 267 |
| column_labels | 143 |
| equipment_master | 152 |