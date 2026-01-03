# ハードコーディング監査レポート（完全版）

**調査日:** 2026-01-03
**対象:** rea-api, rea-admin, shared
**調査者:** Claude（徹底調査）

---

## 総括

| カテゴリ | 件数 | 重要度 |
|----------|------|--------|
| ステータス値 | 15+ | 高 |
| 物件種別 | 10+ | 高 |
| テーブル名 | 30+ | 中 |
| グループ名 | 10+ | 高 |
| 条件付き除外ルール | 5 | 高 |
| 特殊フラグ | 4 | 高 |
| UI色/スタイル | 5+ | 低 |
| 有効値リスト | 3 | 高 |
| ユーザー権限・ロール | 3 | 高 |
| ローカルストレージキー | 8 | 中 |
| ページサイズ・制限値 | 10+ | 中 |
| エラーメッセージ | 60+ | 中 |
| 日付フォーマット | 5+ | 低 |
| APIエンドポイントパス | 50+ | 中 |
| 選択肢オプション | 15+ | 高 |
| 検索距離・制限 | 10+ | 中 |
| 学校種別コード | 10 | 中 |
| フォームplaceholder | 20+ | 低 |

---

## 1. ステータス値のハードコーディング

### 1.1 公開ステータス（publication_status）

| ファイル | 行 | ハードコード値 |
|----------|-----|----------------|
| `rea-api/app/services/publication_validator.py` | 24 | `["公開", "会員公開"]` |
| `rea-api/app/api/api_v1/endpoints/properties.py` | 206 | `["公開", "非公開", "会員公開"]` |
| `rea-admin/src/constants.ts` | 27-28 | `PUBLIC: '公開'`, `PRIVATE: '非公開'` |
| `rea-admin/src/components/form/DynamicForm.tsx` | 1378 | `'非公開'` |
| `rea-admin/src/components/form/DynamicForm.tsx` | 1389 | `'非公開'` |
| `rea-admin/src/components/form/DynamicForm.tsx` | 1394 | `'公開'` |
| `rea-admin/src/pages/Properties/PropertiesPage.tsx` | 101 | `'公開'` |
| `rea-admin/src/pages/Properties/PropertiesPage.tsx` | 682 | `'非公開'` |
| `rea-admin/src/pages/Properties/PropertyEditDynamicPage.tsx` | 242 | `'非公開'` |

### 1.2 販売ステータス（sales_status）

| ファイル | 行 | ハードコード値 |
|----------|-----|----------------|
| `rea-admin/src/constants.ts` | 8-13 | `'販売中'`, `'成約済み'`, `'取下げ'`, `'販売終了'`, `'商談中'`, `'販売準備'` |
| `rea-admin/src/components/form/DynamicForm.tsx` | 1381 | `['販売中', '商談中']` |
| `rea-admin/src/components/form/DynamicForm.tsx` | 1388 | `['販売中', '商談中']` |
| `rea-admin/src/pages/Properties/PropertiesPage.tsx` | 100 | `'販売中'` |
| `rea-admin/src/pages/Properties/PropertiesPage.tsx` | 1220 | `'販売中'`, `'成約済み'` |
| `rea-admin/src/components/CommandPalette.tsx` | 352 | `'販売中'` |

**問題点:**
- ステータス値がマスタテーブルではなくコードに直接記述
- 変更時に複数ファイルを修正必要

---

## 2. 物件種別のハードコーディング

| ファイル | 行 | ハードコード値 |
|----------|-----|----------------|
| `rea-api/app/services/publication_validator.py` | 91, 95 | `["detached"]` |
| `rea-api/app/services/portal/homes_exporter.py` | 120-122 | `'detached'`, `'apartment'`, `'mansion'` |
| `rea-api/app/services/portal/homes_exporter.py` | 191 | `'detached'`（デフォルト値） |
| `rea-admin/src/pages/Import/ToukiImportPage.tsx` | 25, 335 | `'land'`, `'building'`, `'unit'` |

**問題点:**
- 物件種別がm_property_typesマスタから取得されていない
- 条件付き除外ルールに物件種別がハードコード

---

## 3. テーブル名のハードコーディング

| ファイル | 行 | ハードコード値 |
|----------|-----|----------------|
| `rea-api/app/crud/generic.py` | 49-52 | `"properties"`, `"building_info"`, `"land_info"`, `"property_images"` |
| `rea-api/app/crud/generic.py` | 195, 365, 414 | 関連テーブル名 |
| `rea-api/app/api/api_v1/endpoints/metadata.py` | 21-22 | 許可テーブルリスト |
| `rea-api/app/api/api_v1/endpoints/properties.py` | 271 | 削除対象テーブル |
| `rea-api/app/api/api_v1/endpoints/zoho.py` | 71 | `ALLOWED_RELATED_TABLES` |
| `rea-api/app/api/api_v1/endpoints/admin.py` | 132 | テーブル名リスト |
| `rea-admin/src/constants.ts` | 131 | `'land_info'` |
| `rea-admin/src/services/metadataService.ts` | 88 | `'land_info'` |
| `rea-admin/src/pages/admin/FieldVisibilityPage.tsx` | 34 | `'land_info': '土地情報'` |
| `rea-admin/src/components/form/DynamicForm.tsx` | 1248-1249, 1347, 1990 | `'land_info'` |

**問題点:**
- テーブル構造の変更時に複数ファイル修正必要

---

## 4. グループ名のハードコーディング

| ファイル | 行 | ハードコード値 |
|----------|-----|----------------|
| `rea-admin/src/constants.ts` | 88-104 | `TAB_GROUPS` 全体 |
| `rea-api/app/api/api_v1/endpoints/metadata.py` | 324 | `"基本情報"` |
| `rea-api/app/services/publication_validator.py` | 254, 304-305 | `"基本情報"`, `"所在地"` |
| `rea-admin/src/components/form/DynamicForm.tsx` | 1225, 1257, 1280, 1288 | `'所在地'`, `'基本情報'` |

**TAB_GROUPS の詳細（constants.ts）:**
```typescript
location: ['所在地', '学区', '電車・鉄道', 'バス', '周辺施設']
basicInfo: ['物件種別', '基本情報', 'キャッチコピー']
priceDeal: ['価格情報', '契約条件', '元請会社', '引渡・掲載']
management: ['月額費用', '費用情報', '管理情報', '備考', 'ZOHO連携']
excluded: ['ステータス', 'システム']
regulationFromLandInfo: ['法規制（自動取得）', 'ハザード情報（自動取得）']
```

**問題点:**
- グループ名がDBのcolumn_labelsと一致していないと表示崩れ
- 新規グループ追加時にコード修正必要

---

## 5. 条件付き除外ルールのハードコーディング

**ファイル:** `rea-api/app/services/publication_validator.py`

| 対象カラム | 依存カラム | 除外条件 |
|------------|------------|----------|
| `building_coverage_ratio` | `use_district` | `["none", "指定なし"]` |
| `floor_area_ratio` | `use_district` | `["none", "指定なし"]` |
| `room_floor` | `property_type` | `["detached"]` |
| `total_units` | `property_type` | `["detached"]` |
| `setback` | `road_info` | `is_no_road_access()` 関数 |

**問題点:**
- 条件付き除外ルールがコードに直接記述
- DBマスタで管理されていない
- ビジネスロジックの変更にデプロイが必要

---

## 6. 特殊フラグのハードコーディング

**ファイル:** `rea-api/app/services/publication_validator.py`

| カラム | フラグ名 | 判定ロジック |
|--------|----------|--------------|
| `road_info` | `no_road_access` | `{"no_road_access": true}` |
| `transportation` | `no_station` | `{"no_station": true}` |
| `bus_stops` | `no_bus` | `{"no_bus": true}` |
| `nearby_facilities` | `no_facilities` | `{"no_facilities": true}` |

**問題点:**
- フラグ名がハードコード
- 新しい「なし」フラグ追加時にコード修正必要

---

## 7. 有効値リストのハードコーディング

| ファイル | 行 | 定数名 | 値 |
|----------|-----|--------|-----|
| `publication_validator.py` | 27 | `VALID_NONE_VALUES` | `["なし", "該当なし", "なし（学区外）"]` |
| `publication_validator.py` | 30 | `ZERO_VALID_COLUMNS` | `["management_fee", "repair_reserve_fund"]` |

**問題点:**
- 「なし」として有効な値がハードコード
- 0が有効なカラムがハードコード

---

## 8. UI色/スタイルのハードコーディング

**ファイル:** `rea-admin/src/pages/Properties/PropertiesPage.tsx`

| 行 | ハードコード |
|-----|-------------|
| 1220 | `'販売中' ? 'bg-green-50 text-green-700'` |
| 1220 | `'成約済み' ? 'bg-blue-50 text-blue-700'` |
| 1228 | `'公開' ? 'bg-green-50 text-green-700'` |
| 1296 | `'販売中' ? 'bg-green-50 text-green-700'` |
| 1300 | `'公開' ? 'bg-green-50 text-green-700'` |

**問題点:**
- ステータス値と色のマッピングがコードに直接記述

---

## 9. その他のハードコーディング

### 9.1 登記種別
**ファイル:** `rea-admin/src/components/registry/RegistryEditModal.tsx`
```tsx
<option value="土地">土地</option>
<option value="建物">建物</option>
```

### 9.2 検索半径
**ファイル:** `shared/constants.py`
```python
DEFAULT_SEARCH_RADIUS = {
    'station': 5000,
    'bus_stop': 2000,
    'facility': 1000,
    'school': 3000,
}
```

### 9.3 HOMES物件種別マッピング
**ファイル:** `rea-api/app/services/portal/homes_exporter.py`
- property_typeからHOMESコードへのマッピングがハードコード

---

## 10. ユーザー権限・ロール

**ファイル:** `scripts/init_auth_data.py`
```python
roles = [
    ('super_admin', 'システム管理者', 100),
    ('admin', '会社管理者', 50),
    ('user', '一般ユーザー', 10),
]
```

**ファイル:** `rea-api/app/api/api_v1/endpoints/users.py`
```python
if user.get('role_level', 0) < 50:  # 50未満は管理者権限なし
    raise HTTPException(status_code=403, detail="管理者権限が必要です")
```

**問題点:**
- ロールコード・権限レベルがハードコード
- 権限レベル閾値（50）がマジックナンバー

---

## 11. ローカルストレージキー

**ファイル:** `rea-admin/src/`

| ファイル | キー | 用途 |
|----------|------|------|
| `services/api.ts` | `rea_auth_token` | 認証トークン |
| `services/api.ts` | `rea_auth_user` | ユーザー情報 |
| `services/authService.ts` | `rea_auth_token` | 認証トークン |
| `services/authService.ts` | `rea_auth_user` | ユーザー情報 |
| `components/CommandPalette.tsx` | `rea_search_history` | 検索履歴 |
| `pages/Properties/PropertiesPage.tsx` | `rea_property_views` | ビュー設定 |
| `pages/Properties/PropertiesPage.tsx` | `rea_page_size` | ページサイズ |
| `pages/Properties/PropertiesPage.tsx` | `rea_visible_columns` | 表示カラム |
| `pages/Properties/PropertiesPage.tsx` | `rea_scroll_position` | スクロール位置 |

**問題点:**
- キーが複数ファイルで重複定義
- 一元管理されていない

---

## 12. ページサイズ・制限値

**ファイル:** `rea-admin/src/constants.ts`
```typescript
PAGE_CONFIG: {
  DEFAULT_PAGE_SIZE: 20,
}
PAGE_SIZE_OPTIONS = [20, 50, 100]
```

**ファイル:** `rea-admin/src/services/geoService.ts`
```typescript
limit: number = 10  // 最寄駅
limit: number = 3   // 学校
```

**ファイル:** `rea-api/app/api/api_v1/endpoints/properties.py`
```python
limit: int = Query(100, ge=1, le=1000)
```

**ファイル:** `shared/constants.py`
```python
DEFAULT_MAX_ITEMS = {
    'station': 10,
    'bus_stop': 5,
    'facility': 50,
    'school': 5,
}
```

**問題点:**
- 制限値がバラバラに定義
- フロントとバックエンドで別々に管理

---

## 13. エラーメッセージ

**ファイル:** `rea-api/app/api/api_v1/endpoints/` 全体

| HTTPコード | メッセージ例 | 件数 |
|------------|--------------|------|
| 400 | `property_nameをnullにすることはできません` | 10+ |
| 401 | `認証が必要です` | 5+ |
| 403 | `管理者権限が必要です` | 2 |
| 404 | `物件が見つかりません` | 15+ |
| 404 | `Property not found` | 5 |
| 500 | `データベースエラー` | 10+ |
| 500 | `予期せぬエラー` | 5+ |

**ファイル:** `rea-api/app/core/exceptions.py`
```python
detail = "内部エラーが発生しました"
detail = "リソースが見つかりません"
detail = "入力値が不正です"
detail = "設定が不正です"
detail = "外部サービスへの接続に失敗しました"
detail = "データベース操作に失敗しました"
detail = "既に存在します"
```

**問題点:**
- 日本語・英語が混在
- メッセージがコードに直接記述
- エラーコード体系がない

---

## 14. 日付フォーマット

**ファイル:** `rea-api/app/services/portal/homes_exporter.py`
```python
dt.strftime('%Y/%m/%d %H:%M:%S')  # datetime形式
dt.strftime('%Y/%m/%d')          # date形式
dt.strftime('%Y/%m')             # yyyymm形式
```

**問題点:**
- フォーマットがハードコード
- 統一的な定義がない

---

## 15. 選択肢オプション

### 15.1 防火地域
**ファイル:** `rea-admin/src/components/form/RegulationTab.tsx`
```typescript
const FIRE_PREVENTION_OPTIONS = [
  { value: '1', label: '防火地域' },
  { value: '2', label: '準防火地域' },
  { value: '3', label: '指定なし' },
];
```

### 15.2 画像種別
**ファイル:** `rea-admin/src/components/form/ImageUploader.tsx`
```typescript
const IMAGE_TYPES = [
  { value: '0', label: '未分類', icon: '📁' },
  { value: '2', label: '外観', icon: '🏠' },
  { value: '1', label: '間取', icon: '📐' },
];
```

### 15.3 施設カテゴリ
**ファイル:** `rea-admin/src/components/form/NearbyFacilitiesField.tsx`
```typescript
const FACILITY_CATEGORIES = [
  { value: 'convenience', label: 'コンビニ' },
  { value: 'supermarket', label: 'スーパー' },
  { value: 'hospital', label: '病院・クリニック' },
  { value: 'bank', label: '銀行・ATM' },
  { value: 'post_office', label: '郵便局' },
  { value: 'park', label: '公園' },
];
```

### 15.4 部屋タイプ
**ファイル:** `rea-admin/src/components/form/JsonEditors.tsx`
```typescript
const ROOM_TYPES = [
  { value: '30', label: 'DK' },
  { value: '35', label: 'SDK' },
  { value: '50', label: 'LDK' },
  { value: '55', label: 'SLDK' },
];
```

**問題点:**
- マスタテーブルから取得していない
- UIコンポーネントにハードコード

---

## 16. 検索距離・制限

**ファイル:** `shared/constants.py`
```python
DEFAULT_SEARCH_RADIUS = {
    'station': 5000,      # 駅: 5km
    'bus_stop': 2000,     # バス停: 2km
    'facility': 1000,     # 施設: 1km
    'school': 3000,       # 学校: 3km
}
```

**ファイル:** `rea-admin/src/components/form/DynamicForm.tsx`
- 最寄駅検索: `radius=5000&limit=15`
- バス停検索: `limit=15`
- 周辺施設: `limit_per_category=5`

**問題点:**
- 検索条件がハードコード
- 設定変更にデプロイ必要

---

## 17. 学校種別コード

**ファイル:** `shared/constants.py`
```python
SCHOOL_TYPE_CODES = {
    'elementary': '16001',      # 小学校
    'junior_high': '16002',     # 中学校
    'high_school': '16003',     # 高等学校
    'university': '16004',      # 大学
    'junior_college': '16005',  # 短期大学
    'technical_college': '16006',  # 高等専門学校
    'special_needs': '16007',   # 特別支援学校
    'kindergarten': '16008',    # 幼稚園
    'certified_childcare': '16009',  # 認定こども園
    'vocational': '16010',      # 専修学校
}
```

**問題点:**
- 国土数値情報P29コードがハードコード
- 外部仕様変更時に修正必要

---

## 18. フォームplaceholder・title

**ファイル:** `rea-admin/src/` 各所

| ファイル | placeholder/title |
|----------|-------------------|
| `pages/Auth/PasswordResetPage.tsx` | `8文字以上`, `もう一度入力` |
| `pages/Auth/LoginPage.tsx` | `mail@example.com`, `********` |
| `pages/Settings/UsersPage.tsx` | `山田 太郎`, `user@example.com` |
| `components/CommandPalette.tsx` | `物件を検索... (例: 北見 1000万以下 戸建)` |
| `components/NearestStationsEditor.tsx` | `駅名`, `路線名`, `徒歩(分)` |
| `pages/Import/ToukiImportPage.tsx` | `例: 2480` |
| `components/form/NearbyFacilitiesField.tsx` | `施設名`, `距離(m)`, `徒歩(分)` |
| `components/form/RegulationTab.tsx` | `選択してください`, `例: 60`, `例: 200` |

**問題点:**
- 多言語対応困難
- UI変更にコード修正必要

---

## 19. 物件種別グループ順序

**ファイル:** `shared/constants.py`
```python
PROPERTY_TYPE_GROUP_ORDER = {
    '居住用': 1,
    '事業用': 2,
    '投資用': 3,
}
```

---

## 20. 表示順序フォールバック

**ファイル:** `shared/constants.py`
```python
DEFAULT_DISPLAY_ORDER_FALLBACK = 999
```

---

## 21. 徒歩速度

**ファイル:** `shared/constants.py`
```python
WALK_SPEED_METERS_PER_MIN = 80  # 不動産公正取引協議会基準
```

**備考:** これは法令基準なのでハードコードでOK

---

## 推奨対応

### 優先度: 高（ビジネスロジックに影響）

1. **ステータス値のマスタ化**
   - `m_publication_statuses` テーブル作成
   - `m_sales_statuses` テーブル作成
   - API経由でフロントに配信

2. **条件付き除外ルールのDB化**
   - `publication_exclusion_rules` テーブル作成
   - `depends_on`, `exclude_when`, `exclude_when_func` をDB管理

3. **グループ名の一元管理**
   - `TAB_GROUPS` をAPIから取得
   - または `m_tab_groups` テーブル作成

4. **選択肢オプションのマスタ化**
   - 防火地域、画像種別、施設カテゴリ、部屋タイプ
   - `master_options` テーブルに統合

5. **権限レベル閾値のDB化**
   - マジックナンバー（50）を設定テーブルへ

### 優先度: 中（保守性に影響）

6. **物件種別の条件参照**
   - `m_property_types` から動的に取得

7. **特殊フラグ定義のDB化**
   - `m_special_flags` テーブル作成

8. **ローカルストレージキーの一元管理**
   - `storageKeys.ts` に集約

9. **エラーメッセージの統一**
   - 日本語/英語混在の解消
   - エラーコード体系の導入

10. **ページサイズ・制限値の一元管理**
    - フロント/バックエンドで統一

### 優先度: 低（UI/UXに影響）

11. **UI色のマスタ化**
    - ステータスごとの色設定をDBで管理

12. **placeholder/titleの外部化**
    - i18n対応の基盤として

13. **日付フォーマットの一元管理**
    - utils/dateFormat.ts に集約

---

## 影響範囲

| 変更対象 | 影響ファイル数 |
|----------|----------------|
| publication_status | 10+ |
| sales_status | 8+ |
| property_type条件 | 5+ |
| グループ名 | 6+ |
| テーブル名 | 15+ |
| エラーメッセージ | 20+ |
| 選択肢オプション | 5+ |
| ローカルストレージキー | 4 |
| ページサイズ/制限値 | 6+ |

---

## 調査結果サマリ

| 分類 | 件数 | 緊急度 |
|------|------|--------|
| ハードコード箇所 | 200+ | - |
| 重複定義 | 20+ | 中 |
| マジックナンバー | 30+ | 高 |
| 日英混在 | 10+ | 低 |

---

## 次のアクション

1. **調査完了** - 本レポートで全件洗い出し済み
2. **設計検討** - どこまでDB化するか決定
3. **実装計画** - 優先度に基づき段階的に対応
4. **開発開始には別途ユーザー承認が必要**
