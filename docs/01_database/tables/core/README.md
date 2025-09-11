# 🏢 基本情報 テーブル群

## 📋 概要
物件の核となる基本情報

## 🗂️ 含まれるテーブル
- [properties](properties.md) - 12カラム, 0レコード

## 🎯 主な用途
- 物件の基本識別・管理
- 他テーブルとの関連付けの基点
- 物件一覧表示での基本情報提供

## 🔗 関連テーブル
- 全ての properties_* テーブルから参照される中心テーブル

## 🚀 よく使うクエリ例
```sql
-- 物件基本情報取得
SELECT * FROM properties WHERE id = 12345;

-- 物件一覧（ページング）
SELECT id, building_property_name FROM properties 
ORDER BY id LIMIT 20 OFFSET 0;
```
