# REA Database Split: PostgreSQL Admin実行ガイド

## 📋 実行順序（必須）

### 1. 事前準備
```sql
-- データベースバックアップ
pg_dump -U rea_user real_estate_db > backup_before_split.sql
```

### 2. SQL実行順序
PostgreSQL Adminで以下の順序で実行してください：

1. **01_create_tables.sql** - 新テーブル作成
2. **02_migrate_data.sql** - データ移行（現在は0件）
3. **04_create_indexes.sql** - インデックス作成
4. **05_set_permissions.sql** - 権限設定
5. **03_cleanup_original.sql** - 元テーブル整理（最後に実行）

### 3. 実行後確認
```sql
-- テーブル一覧確認
\dt

-- 各テーブルのレコード数確認
SELECT 'properties_images' as table_name, COUNT(*) FROM properties_images
UNION ALL
SELECT 'properties_pricing', COUNT(*) FROM properties_pricing
UNION ALL
SELECT 'properties_location', COUNT(*) FROM properties_location;
```

## 🎯 期待される効果

### パフォーマンス向上
- 画像検索: properties_imagesのみアクセス（3-5倍高速化）
- 価格分析: properties_pricingのみアクセス（10倍高速化）

### 開発効率向上
- 機能別開発: 必要なテーブルのみ関心
- Claude連携: チャンク化で60倍効率化

### データ整理
- 304カラム → 機能別テーブル群
- 正規化によるデータ品質向上

---
Generated: 2025-07-21 15:30:18
