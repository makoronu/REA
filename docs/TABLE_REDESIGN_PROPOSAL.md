# テーブル再設計提案書

**作成日**: 2025-12-15
**ステータス**: Phase 1 完了 / Phase 2-4 未実装

---

## 現状の問題

### 1. 重複カラム（8件）
| カラム名 | 存在テーブル | 問題 |
|---------|-------------|------|
| postal_code | properties, land_info | 同じ住所を2箇所で管理 |
| prefecture | properties, land_info | 同上 |
| city | properties, land_info | 同上 |
| address | properties, land_info | 同上 |
| address_detail | properties, land_info | 同上 |
| latitude | properties, land_info | 同上 |
| longitude | properties, land_info | 同上 |
| transportation | properties, amenities | 交通情報が分散 |

### 2. 機能重複
| 情報 | properties | amenities | 問題 |
|------|-----------|-----------|------|
| 小学校 | elementary_school, elementary_school_minutes | elementary_school_name, elementary_school_distance | 別名で同じ情報 |
| 中学校 | junior_high_school, junior_high_school_minutes | junior_high_school_name, junior_high_school_distance | 別名で同じ情報 |

### 3. propertiesテーブルの肥大化
- **現在**: 70カラム
- 住所、業者、周辺施設など異なる責務が混在

### 4. amenitiesテーブルの役割曖昧
- 設備情報
- 周辺施設距離
- 学校情報（重複）
- エネルギー性能
- リフォーム履歴
→ 複数の概念が1テーブルに混在

---

## 再設計案

### テーブル構成（Before → After）

```
【Before】5テーブル + 重複多数
├── properties (70カラム) ← 肥大化
├── building_info (30カラム)
├── land_info (32カラム) ← 住所重複
├── amenities (29カラム) ← 役割曖昧
└── property_images (11カラム)

【After】6テーブル + 責務明確
├── properties (約45カラム) ← スリム化
├── property_locations (10カラム) ← 新規：住所統合
├── building_info (36カラム) ← エネルギー性能追加
├── land_info (24カラム) ← 住所削除
├── property_equipment (既存) ← 設備
├── property_images (11カラム)
└── amenities → 廃止（他テーブルに分散）
```

---

## 各テーブル詳細設計

### 1. properties（スリム化：70→約45カラム）

#### 残留するカラム

**コア情報（19）**
```sql
id, company_property_number, external_property_id,
property_name, property_name_kana, property_name_public,
property_type, affiliated_group, priority_score, property_url,
is_new_construction, is_residential, is_commercial, is_investment, investment_property,
property_manager_name, internal_memo,
created_at, updated_at
```

**価格・費用（13）**
```sql
sale_price, price_per_tsubo, yield_rate, current_yield,
management_fee, repair_reserve_fund, repair_reserve_fund_base,
parking_fee, housing_insurance, brokerage_fee, commission_split_ratio,
price_status, tax_type
```

**ステータス・取引（10）**
```sql
current_status, publication_status, sales_status,
delivery_date, move_in_consultation, delivery_timing, transaction_type,
brokerage_contract_date, listing_start_date, listing_confirmation_date
```

**ZOHO連携（3）**
```sql
zoho_id, zoho_synced_at, zoho_sync_status
```

**広告文（4）**
```sql
catch_copy, catch_copy2, catch_copy3, remarks
```

#### 削除するカラム（25）
```sql
-- → property_locations に移動
postal_code, prefecture, city, address, address_detail,
latitude, longitude, geom

-- → 動的計算（m_schools利用）
elementary_school, elementary_school_minutes,
junior_high_school, junior_high_school_minutes

-- → property_nearby（JSONB統合）
transportation, bus_stops, nearby_facilities

-- → property_contractors に移動
contractor_company_name, contractor_contact_person, contractor_phone,
contractor_email, contractor_address, contractor_license_number
```

---

### 2. property_locations（新規：住所統合）

```sql
CREATE TABLE property_locations (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,

    -- 住所
    postal_code VARCHAR(10),
    prefecture VARCHAR(10),
    city VARCHAR(50),
    address VARCHAR(200),
    address_detail VARCHAR(200),

    -- 座標
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),
    geom GEOMETRY(Point, 4326),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(property_id)  -- 1物件1住所
);

-- 空間インデックス
CREATE INDEX idx_property_locations_geom ON property_locations USING GIST(geom);
```

**メリット**:
- 住所は1箇所で管理
- land_infoから住所カラム削除可能
- GeoQueryが簡単

---

### 3. land_info（住所削除：32→24カラム）

#### 削除するカラム
```sql
postal_code, prefecture, city, address, address_detail,
latitude, longitude, address_code
```

#### 残留するカラム（土地固有情報のみ）
```sql
id, property_id,
land_area, building_coverage_ratio, floor_area_ratio,
land_rent, land_ownership_ratio,
private_road_area, private_road_ratio,
setback_amount, legal_restrictions, road_info,
land_law_permission, chiban,
-- 選択肢系（INTEGER + master_options参照）
use_district, city_planning, land_rights, setback,
land_area_measurement, land_transaction_notice, land_category, terrain,
created_at, updated_at
```

---

### 4. building_info（エネルギー性能追加：30→36カラム）

#### 追加するカラム（amenitiesから移動）
```sql
-- エネルギー性能
energy_consumption_min INTEGER,
energy_consumption_max INTEGER,
insulation_performance_min INTEGER,
insulation_performance_max INTEGER,
utility_cost_min INTEGER,
utility_cost_max INTEGER
```

---

### 5. property_contractors（新規：業者情報分離）

```sql
CREATE TABLE property_contractors (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,

    company_name VARCHAR(100),
    contact_person VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    address VARCHAR(200),
    license_number VARCHAR(50),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(property_id)  -- 1物件1業者（必要なら複数対応可）
);
```

---

### 6. property_nearby（周辺情報JSONB統合）

**選択肢A**: propertiesにJSONBカラムとして残す
```sql
-- properties テーブル内
nearby_info JSONB  -- transportation, bus_stops, nearby_facilities を統合
```

**選択肢B**: 別テーブル化
```sql
CREATE TABLE property_nearby (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,

    transportation JSONB,      -- 駅情報
    bus_stops JSONB,           -- バス停情報
    nearby_facilities JSONB,   -- 周辺施設

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(property_id)
);
```

**推奨**: 選択肢A（JSONBのままpropertiesに残す）
- 既存コードへの影響が少ない
- 周辺情報は動的計算（m_facilities, m_stations）との併用

---

### 7. amenities → 廃止

| 現amenitiesカラム | 移行先 |
|------------------|--------|
| facilities | property_equipment（既存） |
| transportation, other_transportation | properties.nearby_info (JSONB) |
| elementary_school_*, junior_high_school_* | 削除（m_schoolsから動的計算） |
| *_distance（周辺施設距離） | 削除（m_facilitiesから動的計算） |
| energy_*, insulation_*, utility_* | building_info |
| renovations | building_info.renovations (JSONB) |
| property_features, notes | properties.remarks に統合 or 削除 |

---

## 移行計画

### Phase 1: property_locations作成 ✅ 完了（2025-12-15）
1. ✅ テーブル作成（property_locations）
2. ✅ propertiesから2370件データコピー
3. ✅ API修正（GenericCRUD: get_full, update_full, delete）
4. ⏸️ propertiesから住所カラム削除 → 移行期間中は両方に保存
5. ✅ land_infoから住所カラム削除（8カラム）
6. ✅ ON DELETE CASCADE違反修正

### Phase 1.5: dev-protocol-prompt.md遵守 ✅ 完了（2025-12-15）

#### NOT NULL制約追加
| テーブル | カラム | 対応 |
|---------|--------|------|
| building_info | property_id | ✅ NOT NULL追加 |
| land_info | property_id | ✅ NOT NULL追加 |
| property_images | property_id | ✅ NOT NULL追加 |
| property_registries | property_id | ✅ NOT NULL追加 |
| properties | property_type | ✅ NOT NULL + DEFAULT 'other' |
| 全テーブル | created_at, updated_at | ✅ NOT NULL + DEFAULT NOW() |

#### データクリーンアップ
- building_info孤児レコード14件削除（property_id IS NULL）
- properties.property_type NULL 31件 → 'other' に更新
- property_types に 'other' 追加

#### JSONB型分析
| カラム | 充填率 | 判断 |
|--------|--------|------|
| land_info.road_info | 96.2% | 現状維持（構造固定、接道情報は1レコード1セット） |
| properties.transportation | 0.0% | 将来使用時に正規化検討 |
| properties.bus_stops | 0.0% | 将来使用時に正規化検討 |
| properties.nearby_facilities | 0% | 未使用（動的計算に移行予定） |
| building_info.floor_plans | 0% | 未使用 |

### Phase 2: land_info住所削除
1. property_locationsにデータ統合済み確認
2. land_infoから住所カラム削除
3. column_labels更新

### Phase 3: property_contractors分離
1. テーブル作成
2. propertiesからデータコピー
3. API/フロント修正
4. propertiesから業者カラム削除

### Phase 4: amenities廃止
1. facilitiesをproperty_equipmentに移行
2. エネルギー性能をbuilding_infoに移行
3. renovationsをbuilding_infoに移行
4. 学校・施設距離カラムは動的計算に移行
5. amenitiesテーブル削除

### Phase 5: 動的計算の実装
1. 学校情報: property_locations.geom → m_schools で最寄り計算
2. 施設距離: property_locations.geom → m_facilities で距離計算
3. キャッシュ戦略検討

---

## 影響範囲

### 修正が必要なファイル（推定）

**バックエンド**
- rea-api/app/api/api_v1/endpoints/properties.py
- rea-api/app/api/api_v1/endpoints/generic.py
- rea-api/app/schemas/property.py
- shared/database.py

**フロントエンド**
- rea-admin/src/components/form/DynamicForm.tsx
- rea-admin/src/services/propertyService.ts
- rea-admin/src/types/property.ts

**メタデータ**
- column_labels テーブル（大幅更新）

---

## 判断が必要な点

1. **property_contractors**: 1物件1業者 or 複数業者対応？
2. **nearby_info**: properties内JSONB or 別テーブル？
3. **renovations**: building_info or 別テーブル？
4. **移行順序**: どのPhaseから着手？
5. **既存データ**: 2000件以上の物件データの移行方法

---

## リスク

| リスク | 対策 |
|--------|------|
| 既存APIの破壊 | 移行期間中は両方のカラムを維持 |
| フロントエンド影響 | DynamicFormのメタデータ駆動を活用 |
| データ不整合 | 移行スクリプトでバリデーション |
| パフォーマンス | 動的計算にはキャッシュ導入 |

---

## 次のアクション

- [ ] この設計のレビュー・承認
- [ ] 判断が必要な点の決定
- [ ] Phase 1 から段階的に実装
