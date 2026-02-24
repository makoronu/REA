# 表記ゆれマッピング登録

## やること
field_survey.md で収集した表記ゆれを master_options の api_aliases に登録する。

## 対象カテゴリ

### use_district（用途地域）
```sql
-- サイトで「1種低層」と表示される場合
UPDATE master_options
SET api_aliases = array_append(
    COALESCE(api_aliases, '{}'),
    '{site_name}:1種低層'
)
WHERE category_id = (SELECT id FROM master_categories WHERE category_code = 'use_district')
AND option_value = '第一種低層住居専用地域'
AND NOT ('{site_name}:1種低層' = ANY(COALESCE(api_aliases, '{}')));
```

### building_structure（建物構造）
### city_planning（都市計画）
### land_category（地目）
### room_type（間取り）
### direction（向き）

## 登録ルール
- api_aliases のフォーマット: `{site_name}:{サイト表記}` （サイトが区別できる形式）
- 既に登録済みの場合はスキップ（冪等性）
- 全サイト共通の表記ゆれ（「W造」→「木造」等）はサイト名なしで登録
- 新しい表記ゆれを発見したらここに追加（運用時にも更新）

## マイグレーションスクリプト
```
scripts/migrations/{date}_{site_name}_api_aliases.sql
```

## 確認方法
```sql
-- 登録された api_aliases を確認
SELECT mc.category_code, mo.option_value, mo.api_aliases
FROM master_options mo
JOIN master_categories mc ON mc.id = mo.category_id
WHERE mo.api_aliases IS NOT NULL AND mo.api_aliases != '{}'
ORDER BY mc.category_code, mo.display_order;
```

## 完了条件
- [ ] field_survey.md で収集した全表記ゆれが登録された
- [ ] マイグレーションスクリプトが作成された
- [ ] 冪等性がある（再実行で重複しない）
- [ ] normalizers/mapping.py が api_aliases からマッピングを読み込める

## 次の工程
→ ../3_test/unit.md
