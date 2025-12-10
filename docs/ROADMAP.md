# REA ロードマップ

## ビジョン

**日本一の不動産情報システムを目指す**

- マルチテナント対応（他社への販売を前提）
- ホームズ/SUUMO/athome等の複数ポータル連携
- メタデータ駆動による拡張性と保守性の両立
- 住所入力だけで査定・重説に必要な情報を自動収集

---

## 現在の状態

**最終更新**: 2025-12-10
**現在フェーズ**: フェーズ2（機能拡充）

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
- [ ] エラーハンドリング強化
- [ ] 残りエディタの枠線排除（RoadInfo/FloorPlans/Transportation/Renovations）
- [ ] ImageUploader.tsxの枠線排除

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

## フェーズ3: 地理データ自動取得システム 🆕

物件の住所から各種地理情報を自動取得し、DBに反映。**査定・重説に必要なデータを自動収集。**

---

### Phase 0: 空間DB基盤 ⚠️ 最初に実施

**PostGIS導入（全地理機能の前提）**
- [ ] PostgreSQLにPostGIS拡張追加
- [ ] 空間インデックス設計
- [ ] 緯度経度カラムをGEOMETRY型に変更
- [ ] SRID統一（4326: WGS84）

```sql
-- PostGIS有効化
CREATE EXTENSION IF NOT EXISTS postgis;

-- 物件テーブルに空間カラム追加
ALTER TABLE properties ADD COLUMN geom GEOMETRY(POINT, 4326);
CREATE INDEX idx_properties_geom ON properties USING GIST(geom);
```

---

### Phase 1: 基盤（必須）

**1. 位置情報基盤**
- [ ] 住所→緯度経度変換（Geocoding）
  - 優先: 国土地理院API（無料）
  - 代替: Google Geocoding API（月$200無料枠）
- [ ] 地図表示UI（Leaflet.js + 地理院タイル）
- [ ] 地図上でのピン位置調整UI
- [ ] 地理院標高API連携（土地の高さ自動取得）

**2. 最寄駅（国土数値情報 N02）**
- [ ] 鉄道・駅データ取得・DB投入（全国約9,000駅）
- [ ] 緯度経度から最寄駅検索（ST_Distance）
- [ ] 複数駅（徒歩圏内）の自動取得
- [ ] 駅までの距離・徒歩分数自動計算
- [ ] 駅別乗降客数データ連携（S12）

**3. 用途地域・法規制（国土数値情報 A29/A55）**
- [ ] 用途地域データ取得・PostGIS投入
- [ ] 緯度経度から用途地域自動判定（ST_Contains）
- [ ] 建ぺい率・容積率の自動取得
- [ ] 防火地域・準防火地域の自動取得
- [ ] 高度地区の自動取得

**4. 学区情報（国土数値情報 A27/A32）**
- [ ] 小学校区データ取得・DB投入
- [ ] 中学校区データ取得・DB投入
- [ ] 緯度経度から学区自動判定
- [ ] 学校までの距離自動計算

**5. ハザードマップ（国土数値情報 A31/A33/A40/A41）**
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

**7. 周辺施設（国土数値情報 + OpenStreetMap）**

| 優先度 | カテゴリ | 施設 | データソース |
|--------|---------|------|-------------|
| 🔴必須 | 医療 | 総合病院・救急病院 | P04 |
| 🔴必須 | 医療 | 内科・小児科・歯科 | P04 |
| 🔴必須 | 行政 | 市区町村役所・出張所 | OSM |
| 🔴必須 | 行政 | 警察署・交番 | OSM |
| 🔴必須 | 行政 | 消防署 | OSM |
| 🔴必須 | 行政 | 郵便局 | P30 |
| 🔴必須 | 金融 | 銀行・信用金庫・ATM | OSM |
| 🔴必須 | 公園 | 都市公園・児童公園 | P13 |
| 🔴必須 | 教育 | 保育園・幼稚園 | P29 |
| 🔴必須 | 教育 | 高校 | P29 |
| 🟡強化 | 教育 | 大学・専門学校 | P29 |
| 🟡強化 | 教育 | 学習塾・予備校 | OSM |
| 🟡強化 | 商業 | スーパーマーケット | OSM |
| 🟡強化 | 商業 | コンビニ | OSM |
| 🟡強化 | 商業 | ドラッグストア | OSM |
| 🟡強化 | 商業 | ホームセンター | OSM |
| 🟡強化 | 商業 | ショッピングモール | OSM |
| 🟡強化 | 商業 | 100円ショップ | OSM |
| 🟡強化 | 飲食 | ファミレス・ファストフード | OSM |
| 🟡強化 | 飲食 | カフェ | OSM |
| 🟡強化 | 娯楽 | 図書館 | OSM |
| 🟡強化 | 娯楽 | スポーツジム | OSM |
| 🟡強化 | 生活 | クリーニング店 | OSM |
| 🟡強化 | 生活 | ガソリンスタンド | OSM |
| 🟡強化 | 生活 | コインランドリー | OSM |
| 🟡強化 | 生活 | 美容院・理髪店 | OSM |
| 🟡強化 | 娯楽 | 映画館 | OSM |
| 🟡強化 | 交通 | タクシー乗り場 | OSM |
| 🟡強化 | 交通 | レンタカー・カーシェア | OSM |
| 🟢投資 | 雇用 | 大企業オフィス・工場 | OSM |
| 🟢投資 | 雇用 | 工業団地 | OSM |
| 🟢投資 | 観光 | ホテル・旅館 | OSM |
| 🟢投資 | 観光 | 観光スポット | OSM |

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

**9. 不動産情報ライブラリAPI（国交省）**
- [ ] API利用申請・キー取得
- [ ] 不動産取引価格情報の取得
- [ ] 地価公示・地価調査データ連携
- [ ] 周辺成約事例の自動表示

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

## 技術的負債・メモ

- Tailwindのレスポンシブが効かない箇所あり → インラインstyleで対応中
- 実データ未投入（マスターデータのみ）
- テストコード未整備
- エラーハンドリング未整備

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