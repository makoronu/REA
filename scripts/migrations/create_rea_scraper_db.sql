-- rea_scraper データベース作成（Seg H3: scr.realestateautomation.net用）
--
-- 手順:
--   1. DB作成（postgresユーザーで実行）
--      sudo -u postgres psql -f create_rea_scraper_db.sql
--
--   2. スキーマコピー（既存REAのテーブル構造をコピー）
--      sudo -u postgres pg_dump -d real_estate_db --schema-only \
--        | sudo -u postgres psql -d rea_scraper
--
--   3. マスターデータコピー（master_categories, master_options, column_labels）
--      sudo -u postgres pg_dump -d real_estate_db \
--        -t master_categories -t master_options -t column_labels --data-only \
--        | sudo -u postgres psql -d rea_scraper
--
--   4. 追加テーブル作成（このファイルの後半をrea_scraperで実行）
--      sudo -u postgres psql -d rea_scraper

-- ==============================
-- Step 1: データベース作成
-- ==============================
CREATE DATABASE rea_scraper
    OWNER rea_user
    ENCODING 'UTF8'
    TEMPLATE template0;

-- rea_scraperに切り替え
\c rea_scraper

-- ==============================
-- Step 4: スクレイピング固有テーブル
-- ==============================

-- 価格変遷履歴
CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id),
    price BIGINT NOT NULL,
    price_per_tsubo BIGINT,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by VARCHAR(50) NOT NULL DEFAULT 'scraper'
);

CREATE INDEX idx_price_history_property ON price_history(property_id);
CREATE INDEX idx_price_history_recorded ON price_history(recorded_at);

-- 掲載ステータス変遷履歴
CREATE TABLE listing_status_history (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id),
    old_status VARCHAR(20),
    new_status VARCHAR(20) NOT NULL,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by VARCHAR(50) NOT NULL DEFAULT 'scraper'
);

CREATE INDEX idx_listing_status_property ON listing_status_history(property_id);
CREATE INDEX idx_listing_status_changed ON listing_status_history(changed_at);
