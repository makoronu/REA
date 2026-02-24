# マスターデータ投入（シード）

## やること
1. REA の master_categories / master_options をコピーして投入
2. スクレイピング固有のカテゴリ・オプションがあれば追加
3. column_labels の基本定義を投入

## コピー対象（REA master_options）

### 必須カテゴリ
| category_code | 用途 |
|---------------|------|
| property_type | 物件種別（detached/mansion/land等） |
| use_district | 用途地域（13種 + 指定なし） |
| building_structure | 建物構造（木造/鉄骨造/RC造等） |
| land_category | 地目（宅地/田/畑等） |
| city_planning | 都市計画（市街化/調整/非線引等） |
| room_type | 間取りタイプ（R/K/DK/LDK等） |
| road_direction | 接道方向（8方位） |
| road_type | 接道種別（公道/私道） |
| fire_prevention | 防火地域 |

### スクレイピング固有（新規追加）
| category_code | 用途 |
|---------------|------|
| listing_status | 掲載状態（active/disappeared/converted） |
| source_site | 収集元サイト（homes/suumo/athome等） |

## api_aliases の重要性
REA の master_options には `api_aliases` カラムがある。
ポータルサイトの表記ゆれをここに登録することで、正規化→REA変換がDB駆動になる。

例:
```sql
-- use_district（用途地域）
UPDATE master_options SET api_aliases = ARRAY['1種低層', '一低専', '1低層']
WHERE category_id = (SELECT id FROM master_categories WHERE category_code = 'use_district')
AND option_value = '第一種低層住居専用地域';
```

## 確認コマンド
```sql
SELECT mc.category_code, COUNT(mo.id)
FROM master_categories mc
JOIN master_options mo ON mo.category_id = mc.id
WHERE mo.deleted_at IS NULL
GROUP BY mc.category_code
ORDER BY mc.category_code;
```

## 完了条件
- [ ] master_categories が投入された
- [ ] master_options が投入された（REAと同じコード値）
- [ ] api_aliases が主要カテゴリに設定された
- [ ] `scripts/seed_master_data.sql` にスクリプトがある

## 次の工程
→ ../3_pipeline/fetcher.md
