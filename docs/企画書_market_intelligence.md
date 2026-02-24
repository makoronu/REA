# REA Market Intelligence 企画書

不動産市場情報収集システム

---

## 1. エグゼクティブサマリー

REA Market Intelligence は、SUUMO・HOMES・at home 等の不動産ポータルサイトから他社物件情報を自動収集し、REA と同じデータスキーマで蓄積・分析するシステムである。REA（自社物件管理）とは完全に別プロジェクト（別リポジトリ・別DB・別デプロイ）として構築し、仲介ソーシング・査定書作成・市場分析の基礎データを提供する。収集データは REA の column_labels / master_options 体系に変換して保存するため、仲介時に「自社取扱い物件」へシームレスに変換できる。

---

## 2. 課題定義

| 課題 | 現状 | 影響 |
|------|------|------|
| 他社物件情報が手動収集 | 営業担当が各ポータルを目視巡回 | 漏れ・遅延・属人化 |
| 査定時の比較データ不足 | REINS + 手持ちデータのみ | 査定精度が担当者の経験に依存 |
| 市場動向の定量把握不可 | 感覚値での相場判断 | 価格設定ミス・機会損失 |
| 成約検知ができない | 掲載消失に気づかない | 競合動向が見えない |
| 滞留物件の発見が遅い | 長期掲載を定期確認できない | 仕入れチャンスを逃す |

---

## 3. ユースケース

### UC-1: 仲介ソーシング（他社物件→自社取扱い）

他社が掲載している売物件を発見し、売主への媒介提案に活用する。収集データは REA 形式と同一スキーマのため、媒介契約締結後に REA へワンクリック変換・登録できる。

### UC-2: 査定書アプリの基礎データ

査定対象物件の周辺エリアで「現在売り出し中の類似物件」「過去に消失（＝成約推定）した物件」のデータを提供する。坪単価・㎡単価の統計値を自動算出し、査定根拠の客観性を担保する。

### UC-3: 地図上での他社物件表示（顧客向け情報提供）

買主への物件案内時に、自社取扱い物件だけでなく他社物件も含めた地図表示を提供する。REA の GeoPanel と同じ座標体系（latitude/longitude）で格納するため、地図統合が容易。

### UC-4: 掲載消失検知→成約推定

定期巡回で「前回あったが今回ない」物件を検知し、成約済みと推定する。消失日時・掲載期間・最終価格を記録し、エリアの成約速度・価格帯を分析する。

### UC-5: 価格トラッキング（値下げ推移）

物件ごとの掲載価格を巡回ごとに記録し、値下げ推移を可視化する。「3回値下げした物件」「掲載90日超で値下げなし」等の条件で滞留物件を抽出する。

### UC-6: エリアレポート（相場分析）

市区町村・町丁目単位で、掲載中物件数・平均坪単価・中央値・価格帯分布を自動集計する。査定時のエリア相場説明資料として活用する。

### UC-7: 滞留物件検知（長期掲載の仕入れチャンス）

掲載開始から90日以上経過した物件を自動抽出する。売主が困っている可能性が高く、媒介変更提案の対象となる。

### UC-8: 顧客マッチング（希望条件×市場在庫）

買主の希望条件（エリア・価格帯・面積・間取り）を登録しておき、新規掲載物件が条件に合致したら通知する。

### UC-9: 競合分析（エリア別シェア）

掲載元会社名を収集し、エリア別の掲載件数シェアを集計する。競合他社の営業エリア・得意物件種別を把握する。

### UC-10: 売上推計（消失件数×平均単価）

エリア内の月間消失（成約推定）件数 × 平均成約価格で、エリアの市場規模を推計する。新規出店・営業リソース配分の判断材料とする。

---

## 4. アーキテクチャ

### 4.1 完全分離の原則

```
REA（自社物件管理）           Market Intelligence（市場情報収集）
─────────────────            ─────────────────────────────
別リポジトリ                  別リポジトリ
別DB（rea_db）                別DB（market_intel_db）
別デプロイ                    別デプロイ
本番: port 8005               本番: port 8010（予定）

         ↓ 必要時のみ REST API で読み取り連携 ↓
```

**理由**: 他社物件データは自社データではない。混在させるとデータ整合性・法的リスク・運用負荷が跳ね上がる。

### 4.2 技術スタック

| レイヤー | 技術 | 理由 |
|---------|------|------|
| API | Python / FastAPI | REA と同じ。共通ライブラリ再利用可 |
| DB | PostgreSQL | REA と同じスキーマ体系を踏襲 |
| フロント | React（将来） | REA と同じ。Phase 3以降 |
| スクレイパー | Python / Selenium + BeautifulSoup | 既存 rea-scraper 資産活用 |
| スケジューラー | APScheduler or cron | 日次/週次巡回 |

### 4.3 ディレクトリ構成案

```
market-intelligence/
├── mi-api/                     # FastAPI（データ提供・管理API）
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   └── endpoints/
│   │   │       ├── properties.py       # 収集物件CRUD
│   │   │       ├── analytics.py        # 分析API
│   │   │       └── metadata.py         # メタデータAPI
│   │   ├── crud/
│   │   │   └── generic.py              # 汎用CRUD（REA踏襲）
│   │   └── config.py
│   └── requirements.txt
│
├── mi-scraper/                 # スクレイパー群
│   ├── src/
│   │   ├── main.py             # CLIエントリーポイント
│   │   ├── scrapers/
│   │   │   ├── base/
│   │   │   │   └── base_scraper.py     # 基底クラス
│   │   │   ├── homes/
│   │   │   │   └── homes_scraper.py    # HOMES固有パーサー
│   │   │   ├── suumo/
│   │   │   │   └── suumo_scraper.py    # SUUMO固有パーサー
│   │   │   └── athome/
│   │   │       └── athome_scraper.py   # at home固有パーサー
│   │   ├── normalizers/                # 正規化レイヤー（新規）
│   │   │   ├── price.py                # 金額パーサー
│   │   │   ├── area.py                 # 面積パーサー
│   │   │   ├── address.py              # 住所パーサー
│   │   │   └── field_mapping.py        # 表記ゆれマッピング
│   │   ├── converters/                 # REA変換レイヤー（新規）
│   │   │   └── rea_converter.py        # 中間形式→REAスキーマ変換
│   │   ├── pipeline/                   # パイプライン管理（新規）
│   │   │   ├── discovery.py            # URL発見
│   │   │   ├── fetcher.py              # HTML取得
│   │   │   ├── dedup.py                # 重複排除・名寄せ
│   │   │   └── status_tracker.py       # 消失検知・価格追跡
│   │   └── utils/
│   │       ├── rate_limiter.py         # レート制限
│   │       ├── proxy_manager.py        # プロキシローテーション
│   │       ├── block_detector.py       # ブロック検知
│   │       └── robots_checker.py       # robots.txt遵守
│   └── requirements.txt
│
├── shared/                     # REAと共有可能なライブラリ
│   ├── real_estate_utils.py    # 不動産計算（坪単価等）
│   └── formatters.py           # フォーマッター
│
├── scripts/
│   ├── create_tables.sql       # DDL
│   ├── seed_master_data.sql    # マスターデータ（REAからコピー）
│   └── migrations/
│
└── docs/
```

### 4.4 6レイヤーアーキテクチャ

```
[1. 発見]  →  [2. 取得]  →  [3. パース]  →  [4. 正規化]  →  [5. REA変換]  →  [6. 登録]

  サイト固有       共通基盤        サイト固有        半共通            全共通            全共通
  (URL構造)     (HTTP/Selenium)  (HTMLセレクタ)  (パーサー群+       (master_options    (UPSERT/
  (ページネーション)  (レート制限)                  表記ゆれマップ)     コード変換)       差分検知)
```

| レイヤー | 責務 | 共通/固有 |
|---------|------|----------|
| 発見 | 検索条件→一覧ページ→物件URLリスト | パターン共通、URL構造は固有 |
| 取得 | HTTP GET、レート制限、リトライ、robots.txt | **全部共通** |
| パース | HTML→生データdict抽出 | **全部固有**（各サイトのHTML構造が別物） |
| 正規化 | 生データ→共通中間形式（金額・面積・住所統一） | パーサー群は共通、表記ゆれマップは固有 |
| REA変換 | 共通中間形式→REAスキーマ（master_optionsコード値） | **全部共通** |
| 登録 | UPSERT、差分検知、価格履歴、消失検知 | **全部共通** |

---

## 5. データモデル

### 5.1 メタデータ駆動の踏襲

REA と同じ column_labels / master_categories / master_options 体系をそのまま採用する。

```sql
-- Market Intelligence DB にも同じメタデータテーブルを作成
-- REA の master_options をそのままコピー（source列で区別）

CREATE TABLE master_categories (
    id SERIAL PRIMARY KEY,
    category_code VARCHAR(50) UNIQUE NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    description TEXT,
    source VARCHAR(50) DEFAULT 'system',
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    icon VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE master_options (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES master_categories(id),
    option_code VARCHAR(50) NOT NULL,
    option_value VARCHAR(200) NOT NULL,
    source VARCHAR(50) DEFAULT 'rea',
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    api_aliases VARCHAR[],       -- ポータル表記ゆれ吸収用
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);
```

### 5.2 主要テーブル

#### scraped_properties（収集物件）

REA の properties テーブルと同じカラム構成 + スクレイピング固有カラム。

```sql
CREATE TABLE scraped_properties (
    id SERIAL PRIMARY KEY,

    -- スクレイピング固有
    source_site VARCHAR(50) NOT NULL,           -- 'homes', 'suumo', 'athome'
    source_url TEXT NOT NULL,                    -- 掲載URL
    listing_id VARCHAR(100),                     -- サイト内物件ID
    first_seen_at TIMESTAMPTZ NOT NULL,          -- 初回発見日時
    last_seen_at TIMESTAMPTZ NOT NULL,           -- 最終確認日時
    disappeared_at TIMESTAMPTZ,                  -- 消失検知日時
    listing_status VARCHAR(20) DEFAULT 'active', -- active/disappeared/converted
    raw_html_path TEXT,                          -- 生HTML保存パス

    -- REA互換カラム（properties相当）
    property_name VARCHAR(255),
    property_type VARCHAR(50),                   -- REA master_options準拠
    sale_price BIGINT,
    price_per_tsubo INTEGER,
    tax_type INTEGER,
    current_status VARCHAR(50),
    transaction_type VARCHAR(50),

    -- REA互換カラム（land_info相当）
    postal_code VARCHAR(10),
    prefecture VARCHAR(10),
    city VARCHAR(50),
    address TEXT,
    latitude DECIMAL(10,8),
    longitude DECIMAL(10,8),
    land_area DECIMAL(10,2),
    land_category INTEGER,                       -- REA master_options準拠
    use_district INTEGER,                        -- REA master_options準拠
    city_planning JSONB,                         -- REA master_options準拠
    building_coverage_ratio DECIMAL(5,2),
    floor_area_ratio DECIMAL(5,2),

    -- REA互換カラム（building_info相当）
    building_structure INTEGER,                  -- REA master_options準拠
    construction_date DATE,
    building_area DECIMAL(10,2),
    total_floor_area DECIMAL(10,2),
    room_count INTEGER,
    room_type INTEGER,                           -- REA master_options準拠

    -- 掲載元情報
    listing_company_name VARCHAR(200),
    listing_company_phone VARCHAR(50),

    -- 名寄せ
    dedup_key VARCHAR(255),                      -- 住所+面積+価格ハッシュ

    -- 監査
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100) DEFAULT 'scraper',
    updated_by VARCHAR(100) DEFAULT 'scraper',
    deleted_at TIMESTAMPTZ,

    UNIQUE(source_site, listing_id)
);
```

#### price_history（価格履歴）

```sql
CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    scraped_property_id INTEGER REFERENCES scraped_properties(id),
    price BIGINT NOT NULL,
    price_per_tsubo INTEGER,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    price_change BIGINT,                         -- 前回比（マイナス=値下げ）
    change_count INTEGER DEFAULT 0               -- 累計変更回数
);

CREATE INDEX idx_price_history_property ON price_history(scraped_property_id, recorded_at);
```

#### listing_status_history（掲載状態履歴）

```sql
CREATE TABLE listing_status_history (
    id SERIAL PRIMARY KEY,
    scraped_property_id INTEGER REFERENCES scraped_properties(id),
    status VARCHAR(20) NOT NULL,                 -- active/disappeared/reappeared
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    days_since_first_seen INTEGER                -- 初回発見からの日数
);
```

#### scrape_sessions（巡回セッション）

```sql
CREATE TABLE scrape_sessions (
    id SERIAL PRIMARY KEY,
    source_site VARCHAR(50) NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'running',        -- running/completed/failed/stopped
    urls_discovered INTEGER DEFAULT 0,
    properties_new INTEGER DEFAULT 0,
    properties_updated INTEGER DEFAULT 0,
    properties_disappeared INTEGER DEFAULT 0,
    errors INTEGER DEFAULT 0,
    error_details JSONB
);
```

#### scrape_sources（巡回対象定義）

```sql
CREATE TABLE scrape_sources (
    id SERIAL PRIMARY KEY,
    source_site VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,                 -- 'hokkaido', 'tokyo' 等
    property_type VARCHAR(50) NOT NULL,          -- 'land', 'detached', 'mansion'
    base_url TEXT NOT NULL,                      -- 検索結果ページURL
    schedule VARCHAR(20) DEFAULT 'daily',        -- daily/weekly
    is_active BOOLEAN DEFAULT TRUE,
    last_run_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);
```

### 5.3 REA スキーマ対応表

スクレイピングで取得 → REA の master_options コード値に変換する対応表。

#### 物件種別（property_type）

| ポータル表記 | SUUMO | HOMES | at home | REA値 |
|-------------|-------|-------|---------|-------|
| 土地 | ○ | ○ | ○ | land |
| 中古一戸建 | 中古一戸建て | 中古一戸建て | 中古一戸建て | detached |
| 中古マンション | 中古マンション | 中古マンション | 中古マンション | mansion |

#### 用途地域（use_district）→ master_options コード値

| ポータル表記例 | 正規化後 | REA option_code | REA数値 |
|--------------|---------|----------------|---------|
| 1種低層 / 第一種低層住居専用地域 / 一低専 | 第一種低層住居専用地域 | rea_1 | 1 |
| 2種低層 / 第二種低層住居専用地域 | 第二種低層住居専用地域 | rea_2 | 2 |
| 1種中高層 / 第一種中高層住居専用地域 | 第一種中高層住居専用地域 | rea_3 | 3 |
| 2種中高層 / 第二種中高層住居専用地域 | 第二種中高層住居専用地域 | rea_4 | 4 |
| 1種住居 / 第一種住居地域 | 第一種住居地域 | rea_5 | 5 |
| 2種住居 / 第二種住居地域 | 第二種住居地域 | rea_6 | 6 |
| 準住居 / 準住居地域 | 準住居地域 | rea_7 | 7 |
| 近商 / 近隣商業地域 | 近隣商業地域 | rea_8 | 8 |
| 商業 / 商業地域 | 商業地域 | rea_9 | 9 |
| 準工業 / 準工業地域 | 準工業地域 | rea_10 | 10 |
| 工業 / 工業地域 | 工業地域 | rea_11 | 11 |
| 工専 / 工業専用地域 | 工業専用地域 | rea_12 | 12 |
| 田園住居 / 田園住居地域 | 田園住居地域 | rea_21 | 21 |
| 指定なし / 無指定 | 指定なし | rea_99 | 99 |

#### 建物構造（building_structure）

| ポータル表記例 | REA option_code | REA数値 |
|--------------|----------------|---------|
| 木造 / W造 | 1 | 1 |
| 鉄骨造 / S造 / 軽量鉄骨造 | 2 | 2 |
| RC造 / 鉄筋コンクリート造 | 3 | 3 |
| SRC造 / 鉄骨鉄筋コンクリート造 | 4 | 4 |
| ブロック造 / CB造 | 5 | 5 |
| その他 | 9 | 9 |

#### 都市計画（city_planning）

| ポータル表記例 | REA option_code | REA数値 |
|--------------|----------------|---------|
| 市街化区域 | rea_1 | 1 |
| 市街化調整区域 / 調整区域 | rea_2 | 2 |
| 非線引区域 / 非線引き区域 / 区域区分非設定 | rea_3 | 3 |
| 都市計画区域外 | rea_4 | 4 |

#### 地目（land_category）

| ポータル表記例 | REA option_code | REA数値 |
|--------------|----------------|---------|
| 宅地 | rea_1 | 1 |
| 田 | rea_2 | 2 |
| 畑 | rea_3 | 3 |
| 山林 | rea_4 | 4 |
| 原野 | rea_5 | 5 |
| その他 / 雑種地 | rea_9 | 9 |

#### 間取り（room_type）

| ポータル表記例 | REA option_code | REA数値 |
|--------------|----------------|---------|
| ワンルーム / 1R | 1 | 1 |
| 1K〜 | 2 | 2 |
| 1DK〜 | 3 | 3 |
| 1LDK〜 | 4 | 4 |
| 1SLDK〜 | 5 | 5 |
| その他 | 6 | 6 |
| 不明 / 記載なし | 7 | 7 |

---

## 6. スクレイピング対象

### 6.1 対象ポータル

| ポータル | URL | 物件種別 | 優先度 |
|---------|-----|---------|--------|
| HOMES（ホームズ） | homes.co.jp | 土地・戸建・マンション | **Phase 1**（既存実装あり） |
| SUUMO（スーモ） | suumo.jp | 土地・戸建・マンション | **Phase 2** |
| at home（アットホーム） | athome.co.jp | 土地・戸建・マンション | **Phase 2** |
| 不動産ジャパン | fudousan.or.jp | 土地・戸建・マンション | Phase 3 |
| Yahoo!不動産 | realestate.yahoo.co.jp | 土地・戸建・マンション | Phase 3 |

### 6.2 物件種別

| 種別 | 取得項目 | 備考 |
|------|---------|------|
| 土地 | 価格・面積・用途地域・建ぺい率・容積率・接道・住所 | land_info中心 |
| 中古一戸建 | 上記 + 建物面積・構造・築年・間取り | building_info追加 |
| 中古マンション | 上記 + 専有面積・階数・管理形態・管理費・修繕積立金 | building_info中心 |

### 6.3 既存 rea-scraper の活用

| コンポーネント | ファイル | 行数 | 活用方針 |
|--------------|---------|------|---------|
| BaseScraper | base_scraper.py | 281 | **そのまま活用**。Selenium/requests切り替え、統計、バリデーション |
| URLQueue | scrapers_common.py | 150 | **そのまま活用**。URL管理・バッチ処理 |
| RateLimiter | scrapers_common.py | 30 | **そのまま活用**。ランダム待機 |
| HomesPropertyScraper | homes_scraper.py | 330 | **改修して活用**。パースレイヤーとして分離 |
| UniversalScraper | universal_scraper.py | 620 | **参考のみ**。パターン学習は有用だが620行は分割必要 |
| SeleniumManager | selenium_manager.py | 310 | **そのまま活用** |
| デコレータ群 | decorators.py | 449 | **そのまま活用**。@retry等 |

**改修が必要な点**:
- DB保存ロジック: homes_scraper.py内のINSERT文 → 統一保存APIに変更
- master_options連携: ハードコードのテーブルマッピング → DB駆動に変更
- 正規化レイヤー: homes固有の正規化が散在 → normalizers/に分離

---

## 7. スクレイピング設計

### 7.1 処理パイプライン

```
                    ┌─────────────────────────────────────────┐
                    │           スケジューラー（日次）           │
                    └────────────┬────────────────────────────┘
                                 │
                    ┌────────────▼────────────────────────────┐
                    │     1. 発見（URL収集）                    │
                    │     検索条件 → 一覧ページ巡回 → URLリスト  │
                    │     [サイト固有: URL構造・ページネーション]   │
                    └────────────┬────────────────────────────┘
                                 │
                    ┌────────────▼────────────────────────────┐
                    │     2. 取得（HTML取得）                   │
                    │     レート制限 → HTTP GET → 生HTML保存    │
                    │     [共通基盤: RateLimiter/robots.txt]    │
                    └────────────┬────────────────────────────┘
                                 │
                    ┌────────────▼────────────────────────────┐
                    │     3. パース（HTML→生データ）             │
                    │     CSSセレクタ → フィールド抽出           │
                    │     [サイト固有: セレクタ・テーブル構造]     │
                    └────────────┬────────────────────────────┘
                                 │
                    ┌────────────▼────────────────────────────┐
                    │     4. 正規化（表記統一）                  │
                    │     "2,980万円"→29800000                 │
                    │     "150.25㎡"→150.25                    │
                    │     "1種低層"→"第一種低層住居専用地域"     │
                    │     [共通パーサー + サイト固有マッピング]    │
                    └────────────┬────────────────────────────┘
                                 │
                    ┌────────────▼────────────────────────────┐
                    │     5. REA変換（→master_optionsコード値）  │
                    │     "第一種低層住居専用地域"→1             │
                    │     フィールド名→REAカラム名               │
                    │     [全部共通: api_aliasesマッピング]      │
                    └────────────┬────────────────────────────┘
                                 │
                    ┌────────────▼────────────────────────────┐
                    │     6. 登録（DB保存）                     │
                    │     新規→INSERT / 既存→差分UPDATE         │
                    │     消失→disappeared_at記録              │
                    │     価格変更→price_history追加            │
                    │     [全部共通]                            │
                    └──────────────────────────────────────────┘
```

### 7.2 robots.txt遵守

```python
# 起動時に取得・パース
# Disallowパスは巡回しない
# Crawl-delay指定があれば従う
# 定期的に再取得（サイト側変更対応）
```

### 7.3 レート制限

| 項目 | 設定値 |
|------|--------|
| リクエスト間隔 | 3〜8秒（ランダム） |
| 開始時刻 | ランダム化（パターン検知回避） |
| 1サイト/日 上限 | 初期: 500リクエスト |
| 連続エラー閾値 | 5回で自動停止 |

### 7.4 人間擬態

| 項目 | 対策 |
|------|------|
| User-Agent | 実在ブラウザの文字列（Chrome最新版） |
| Referer | 一覧→詳細の遷移順序を再現 |
| Accept-Language | ja,en-US;q=0.9 |
| Cookie | セッション維持 |
| アクセスパターン | 一覧→詳細→一覧→詳細の人間的遷移 |

### 7.5 ブロック検知・自動停止

| 検知対象 | 判定方法 | 対処 |
|---------|---------|------|
| HTTP 403/429/503 | ステータスコード | 即座にバックオフ→停止 |
| CAPTCHA | レスポンスHTML内の特定要素 | 即停止→通知 |
| ブロックページ | 物件HTMLとの内容差異 | 即停止→通知 |
| パース失敗連続 | 期待フィールド取得不可×5 | 停止→HTML構造変更の可能性を通知 |

### 7.6 差分更新

```
巡回ごとに以下を判定:

新規: listing_id が DB に存在しない → INSERT + first_seen_at = now()
更新: listing_id が DB に存在 + データ変更あり → UPDATE + last_seen_at = now()
価格変更: sale_price が前回と異なる → price_history に追記
消失: 前回の巡回で存在したが今回の巡回で存在しない → disappeared_at = now()
再出現: disappeared_at が設定済みだが今回存在する → disappeared_at = NULL + ログ
```

### 7.7 生HTML保存

パーサー改修時に再取得不要とするため、取得した生HTMLを一定期間保存する。

```
storage/
├── homes/
│   └── 2026-02/
│       ├── {listing_id}_20260224.html
│       └── ...
├── suumo/
└── athome/

保存期間: 90日（パーサー改修の余裕を持たせる）
```

---

## 8. REA連携設計

### 8.1 テナント / サブテナント関係

```
REA（テナント）                Market Intelligence（サブテナント）
┌─────────────────┐          ┌───────────────────────────┐
│ 自社物件          │          │ 他社物件（スクレイピング）    │
│ properties       │          │ scraped_properties         │
│ organization_id  │          │ source_site                │
│ 手動入力/登記取込  │          │ 自動収集                    │
│ 公開/非公開管理    │          │ 掲載状態追跡                │
└────────┬────────┘          └────────────┬──────────────┘
         │                                │
         │   ← 仲介変換（ワンクリック） ←    │
         │                                │
         └────────────────────────────────┘
```

### 8.2 仲介時のデータ変換フロー

```
1. Market Intelligence で他社物件を発見
2. 売主に媒介提案 → 媒介契約締結
3. 「REAに変換」ボタン
4. scraped_properties → REA properties にコピー
   - 同じ master_options コード値なのでそのまま移行
   - organization_id: 自社のIDを付与
   - sales_status: '販売準備' にセット
   - publication_status: '非公開' にセット
   - source: 'market_intelligence' タグ付与
5. REA上で自社物件として編集・公開管理
```

### 8.3 査定書アプリへのデータ提供API

```
GET /api/v1/comparable-properties
  ?latitude=43.0621
  &longitude=141.3544
  &radius_km=3
  &property_type=detached
  &min_land_area=100
  &max_land_area=300

Response:
{
  "active": [
    { "address": "...", "sale_price": 29800000, "land_area": 150.25, ... },
    ...
  ],
  "disappeared_recent": [
    { "address": "...", "last_price": 28000000, "days_on_market": 45, ... },
    ...
  ],
  "stats": {
    "avg_price_per_tsubo": 250000,
    "median_price_per_tsubo": 240000,
    "active_count": 15,
    "disappeared_30d_count": 3
  }
}
```

### 8.4 地図表示用API

```
GET /api/v1/map-properties
  ?bounds=43.0,141.3,43.1,141.4    -- 緯度経度バウンディングボックス
  &property_type=land,detached
  &status=active

Response:
{
  "properties": [
    {
      "id": 123,
      "latitude": 43.062,
      "longitude": 141.354,
      "sale_price": 29800000,
      "property_type": "detached",
      "source_site": "homes",
      "listing_status": "active"
    },
    ...
  ]
}
```

---

## 9. 法務・コンプライアンス

### 9.1 利用規約確認

| ポータル | スクレイピング言及 | 対応方針 |
|---------|-----------------|---------|
| HOMES | 利用規約で自動アクセスに制限あり | robots.txt遵守、低頻度、社内利用限定 |
| SUUMO | 利用規約で自動アクセスに制限あり | 同上 |
| at home | 利用規約で自動アクセスに制限あり | 同上 |
| 不動産ジャパン | REINS系、業者利用前提 | 会員資格確認必要 |

### 9.2 著作権法・不正競争防止法

| リスク | 対策 |
|--------|------|
| データベースの著作物性 | 物件情報の「事実」部分のみ取得。掲載文章・写真はコピーしない |
| 不正競争防止法（営業秘密） | 公開情報のみ取得。ログイン後ページは対象外 |
| 著作権法30条の4（情報解析） | 統計・分析目的での利用は適法（2018年改正） |

### 9.3 個人情報の取扱い

| 情報 | 取得可否 | 理由 |
|------|---------|------|
| 物件価格・面積・住所 | ○ | 不動産広告として公開されている事実情報 |
| 掲載会社名 | ○ | 法人情報（宅建業者） |
| 掲載会社電話番号 | △ | 取得するが社内利用限定 |
| 個人名・個人電話番号 | × | 取得しない。パーサーで除外 |

### 9.4 robots.txt遵守

- 全ポータルの robots.txt を起動時に取得・パース
- Disallow パスは巡回対象から自動除外
- Crawl-delay 指定があれば遵守（なくても最低3秒間隔）
- 24時間ごとに robots.txt を再取得

---

## 10. フェーズ計画

### Phase 1: 基盤構築（1ポータル）

| 作業 | 内容 |
|------|------|
| DB構築 | market_intel_db作成、テーブルDDL、master_dataシード |
| API基盤 | FastAPI、ヘルスチェック、メタデータAPI |
| パイプライン基盤 | 6レイヤー実装（発見→取得→パース→正規化→変換→登録） |
| HOMES対応 | 既存homes_scraper.pyを改修、正規化レイヤー分離 |
| 差分更新 | 新規/更新/消失検知の基本ロジック |
| 運用基盤 | ログ、エラー通知、ブロック検知 |

### Phase 2: スクレイパー拡張

| 作業 | 内容 |
|------|------|
| SUUMO対応 | suumo_scraper.py新規実装（パースレイヤー） |
| at home対応 | athome_scraper.py新規実装（パースレイヤー） |
| 名寄せ | 複数サイト間の同一物件検知（住所+面積+価格） |
| プロキシ | プロキシローテーション（規模拡大対応） |

### Phase 3: 分析機能

| 作業 | 内容 |
|------|------|
| 価格推移 | price_history の可視化・統計API |
| 消失検知 | 成約推定ロジック、エリア別成約速度 |
| エリアレポート | 市区町村別相場統計（平均/中央値/分布） |
| 滞留検知 | 掲載日数ベースの抽出API |

### Phase 4: REA連携

| 作業 | 内容 |
|------|------|
| 仲介変換 | scraped_properties → REA properties ワンクリック変換 |
| 査定書API | 類似物件検索・統計API |
| 地図統合 | REA GeoPanel上での他社物件表示 |
| 顧客マッチング | 希望条件×市場在庫の通知 |

---

## 11. 技術的制約・リスク

| リスク | 影響度 | 発生確率 | 対策 |
|--------|--------|---------|------|
| HTML構造変更 | 高 | 高（年数回） | パース失敗検知→即通知。生HTML保存で再パース可 |
| アクセスブロック | 高 | 中 | レート制限遵守、プロキシ、自動停止 |
| データ量増大 | 中 | 確実 | パーティショニング（月次）、古いデータのアーカイブ |
| 法的リスク | 高 | 低 | robots.txt遵守、社内利用限定、個人情報除外 |
| サイト閉鎖・統合 | 中 | 低 | 複数ソース対応で分散 |
| 名寄せ精度 | 中 | 中 | 住所正規化の精度向上、手動補正UI |

---

## 12. REA プロトコル準拠

Market Intelligence は REA と同じ開発プロトコルに従う。

| 項目 | 準拠内容 |
|------|---------|
| ENUM禁止 | 全選択肢は master_options で管理。ハードコード禁止 |
| 論理削除 | 全テーブルに deleted_at。物理削除禁止 |
| ハードコード禁止 | URL・認証情報・マジックナンバーは定数/環境変数/DB |
| 500行/ファイル上限 | 超えたら責務分割 |
| メタデータ駆動 | column_labels / master_options でUI・バリデーション制御 |
| 監査カラム | created_at / updated_at / created_by / updated_by |
| タイムゾーン | datetime は UTC 統一（TIMESTAMPTZ） |
| N+1禁止 | バッチ取得、IN句 |
| エラー握りつぶし禁止 | 最低限ログ出力、通知 |
| トランザクション | 複数テーブル更新は必ずトランザクション内 |

---

## 13. 次のステップ

### 企画書承認後の開発開始手順

1. **リポジトリ作成**: `market-intelligence` を新規作成（REAリポジトリには触れない）
2. **DB構築**: market_intel_db 作成、DDL実行、master_dataシード（REAからコピー）
3. **Phase 1開始**: HOMES パイプライン基盤構築
4. **既存コード移植**: rea-scraper から base_scraper / scrapers_common を移植・改修
5. **6レイヤー実装**: 発見→取得→パース→正規化→REA変換→登録
6. **運用テスト**: ヘッドレスモードで日次巡回テスト

### 開発時の注意

- REA コードベースへの変更は一切行わない
- 共通ライブラリ（shared/）は将来的にパッケージ化して両プロジェクトから参照する可能性あり
- Phase 4 の REA 連携時に初めて REA 側の改修が発生する（API追加のみ）
