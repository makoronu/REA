# デプロイ計画 2026-01-04

**作成日:** 2026-01-04
**状態:** デプロイ完了

---

## 概要

| 項目 | 内容 |
|------|------|
| 対象コミット | 49件（ページネーション修正含む） |
| 本番URL | https://realestateautomation.net/ |
| 本番サーバー | rea-conoha |
| 本番パス | /opt/REA |
| 本番DB | real_estate_db (PostgreSQL) |
| ローカルDB | real_estate_db (PostgreSQL) |

---

## スキーマ差異

### 新規テーブル

| テーブル | カラム |
|----------|--------|
| system_config | id, config_key, config_value, description, created_at, updated_at |

### 新規カラム追加

| テーブル | カラム | 型 |
|----------|--------|-----|
| **column_labels** | valid_none_text | ARRAY |
| | zero_is_valid | boolean |
| | conditional_exclusion | jsonb |
| | special_flag_key | varchar |
| | api_endpoint | varchar |
| | api_field_path | varchar |
| | placeholder | varchar |
| **master_categories** | icon | varchar |
| **master_options** | requires_validation | boolean |
| | is_default | boolean |
| | allows_publication | boolean |
| | linked_status | varchar |
| | ui_color | varchar |
| | shows_contractor | boolean |
| | api_aliases | jsonb |
| | triggers_unpublish | boolean |
| | triggers_pre_check | boolean |
| **property_types** | sort_order | integer |

### 型変更（要マッピング）

| テーブル | カラム | 本番 | ローカル | 変換 |
|----------|--------|------|---------|------|
| land_info | use_district | integer | jsonb | `to_jsonb(ARRAY[use_district])` |
| land_info | city_planning | integer | jsonb | `to_jsonb(ARRAY[city_planning])` |

---

## セグメント計画

### Seg 1: 準備・ローカル検証（本番影響なし）

```bash
# 1-1. バックアップディレクトリ作成
mkdir -p ~/REA_backup/20260104

# 1-2. 本番DBダンプ
ssh rea-conoha "sudo -u postgres pg_dump real_estate_db" > ~/REA_backup/20260104/prod_db.sql

# 1-3. 本番コードバックアップ
ssh rea-conoha "cd /opt && tar czf REA_code_backup.tar.gz REA"
scp rea-conoha:/opt/REA_code_backup.tar.gz ~/REA_backup/20260104/

# 1-4. ローカルDBバックアップ
pg_dump real_estate_db > ~/REA_backup/20260104/local_db.sql

# 1-5. 検証用DB作成
dropdb rea_verify 2>/dev/null || true
createdb rea_verify

# 1-6. 本番ダンプをリストア
psql rea_verify < ~/REA_backup/20260104/prod_db.sql

# 1-7. マイグレーション実行
psql rea_verify < scripts/migrations/deploy_20260104.sql

# 1-8. 動作確認
# DATABASE_URL=postgresql://localhost/rea_verify で API起動
# http://localhost:5173/properties でページネーション確認
```

**確認ポイント:**
- [x] バックアップファイル存在確認（prod_db.sql: 145MB, local_db.sql: 145MB, REA_code_backup.tar.gz: 630MB）
- [x] 検証DBデータ件数 = 2370
- [x] マイグレーション成功
- [x] クエリ動作確認（get_list, get_count）
- [x] 型変換確認（use_district, city_planning → jsonb配列）

**ロールバック:** 不要（本番に影響なし）

---

### Seg 2: 本番デプロイ（本番影響あり・承認必要）

```bash
# 2-1. マイグレーションSQL転送
scp scripts/migrations/deploy_20260104.sql rea-conoha:/tmp/

# 2-2. 本番DBマイグレーション
ssh rea-conoha "sudo -u postgres psql real_estate_db < /tmp/deploy_20260104.sql"

# 2-3. git push
git push origin main

# 2-4. 本番コード更新
ssh rea-conoha "cd /opt/REA && git pull origin main"

# 2-5. フロントビルド
ssh rea-conoha "cd /opt/REA/rea-admin && npm install && npm run build"

# 2-6. API再起動
ssh rea-conoha "sudo systemctl restart rea-api"

# 2-7. ヘルスチェック
sleep 3
curl -s https://realestateautomation.net/api/v1/health

# 2-8. 本番検証
# https://realestateautomation.net/properties
# - ページネーション確認
# - ステータス連動確認
```

**確認ポイント:**
- [ ] マイグレーション成功
- [ ] ヘルスチェック 200
- [ ] ページネーション動作
- [ ] ステータス連動動作

**ロールバック:**
```bash
# DB復元
ssh rea-conoha "sudo -u postgres psql -c 'DROP DATABASE real_estate_db; CREATE DATABASE real_estate_db;'"
cat ~/REA_backup/20260104/prod_db.sql | ssh rea-conoha "sudo -u postgres psql real_estate_db"

# コード復元
ssh rea-conoha "rm -rf /opt/REA"
scp ~/REA_backup/20260104/REA_code_backup.tar.gz rea-conoha:/opt/
ssh rea-conoha "cd /opt && tar xzf REA_code_backup.tar.gz"

# 再起動
ssh rea-conoha "cd /opt/REA/rea-admin && npm install && npm run build"
ssh rea-conoha "sudo systemctl restart rea-api"
```

---

## マイグレーションSQL

ファイル: `scripts/migrations/deploy_20260104.sql`

```sql
-- =====================================================
-- デプロイ 2026-01-04 マイグレーション
-- =====================================================

-- 1. system_config テーブル作成
CREATE TABLE IF NOT EXISTS system_config (
  id SERIAL PRIMARY KEY,
  config_key VARCHAR(255) NOT NULL UNIQUE,
  config_value JSONB,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. column_labels 新カラム追加
ALTER TABLE column_labels ADD COLUMN IF NOT EXISTS valid_none_text TEXT[];
ALTER TABLE column_labels ADD COLUMN IF NOT EXISTS zero_is_valid BOOLEAN DEFAULT FALSE;
ALTER TABLE column_labels ADD COLUMN IF NOT EXISTS conditional_exclusion JSONB;
ALTER TABLE column_labels ADD COLUMN IF NOT EXISTS special_flag_key VARCHAR(255);
ALTER TABLE column_labels ADD COLUMN IF NOT EXISTS api_endpoint VARCHAR(255);
ALTER TABLE column_labels ADD COLUMN IF NOT EXISTS api_field_path VARCHAR(255);
ALTER TABLE column_labels ADD COLUMN IF NOT EXISTS placeholder VARCHAR(255);

-- 3. master_categories 新カラム追加
ALTER TABLE master_categories ADD COLUMN IF NOT EXISTS icon VARCHAR(255);

-- 4. master_options 新カラム追加
ALTER TABLE master_options ADD COLUMN IF NOT EXISTS requires_validation BOOLEAN DEFAULT FALSE;
ALTER TABLE master_options ADD COLUMN IF NOT EXISTS is_default BOOLEAN DEFAULT FALSE;
ALTER TABLE master_options ADD COLUMN IF NOT EXISTS allows_publication BOOLEAN DEFAULT FALSE;
ALTER TABLE master_options ADD COLUMN IF NOT EXISTS linked_status VARCHAR(255);
ALTER TABLE master_options ADD COLUMN IF NOT EXISTS ui_color VARCHAR(50);
ALTER TABLE master_options ADD COLUMN IF NOT EXISTS shows_contractor BOOLEAN DEFAULT FALSE;
ALTER TABLE master_options ADD COLUMN IF NOT EXISTS api_aliases JSONB;
ALTER TABLE master_options ADD COLUMN IF NOT EXISTS triggers_unpublish BOOLEAN DEFAULT FALSE;
ALTER TABLE master_options ADD COLUMN IF NOT EXISTS triggers_pre_check BOOLEAN DEFAULT FALSE;

-- 5. property_types 新カラム追加
ALTER TABLE property_types ADD COLUMN IF NOT EXISTS sort_order INTEGER;

-- 6. land_info 型変更 (integer → jsonb)
-- use_district
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns
             WHERE table_name = 'land_info' AND column_name = 'use_district'
             AND data_type = 'integer') THEN
    ALTER TABLE land_info ADD COLUMN use_district_new JSONB;
    UPDATE land_info SET use_district_new = to_jsonb(ARRAY[use_district]) WHERE use_district IS NOT NULL;
    ALTER TABLE land_info DROP COLUMN use_district;
    ALTER TABLE land_info RENAME COLUMN use_district_new TO use_district;
  END IF;
END $$;

-- city_planning
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns
             WHERE table_name = 'land_info' AND column_name = 'city_planning'
             AND data_type = 'integer') THEN
    ALTER TABLE land_info ADD COLUMN city_planning_new JSONB;
    UPDATE land_info SET city_planning_new = to_jsonb(ARRAY[city_planning]) WHERE city_planning IS NOT NULL;
    ALTER TABLE land_info DROP COLUMN city_planning;
    ALTER TABLE land_info RENAME COLUMN city_planning_new TO city_planning;
  END IF;
END $$;

-- 確認
SELECT 'Migration completed' AS status;
```

---

## 進捗

| Seg | 状態 | 完了日時 |
|-----|------|---------|
| 1 | **完了** | 2026-01-04 18:10 |
| 2 | **完了** | 2026-01-04 18:15 |

---

## 更新履歴

| 日時 | 内容 |
|------|------|
| 2026-01-04 | 計画作成・承認 |
| 2026-01-04 18:10 | Seg 1完了（バックアップ・検証DB・マイグレーション・整合性確認） |
| 2026-01-04 18:15 | Seg 2完了（本番デプロイ・50コミット反映・141ファイル更新） |
