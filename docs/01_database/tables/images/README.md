# 📸 画像管理 テーブル群

## 📋 概要
物件画像の管理・表示機能

## 🗂️ 含まれるテーブル
- [properties_images](properties_images.md) - 94カラム, 0レコード

## 🎯 主な用途
- 物件画像の保存・管理
- 画像ギャラリーの表示
- 画像の分類・最適化

## 🔗 関連テーブル
- properties（基本情報）
- image_types（画像種別マスター）

## 🚀 よく使うクエリ例
```sql
-- 物件の画像一覧
SELECT * FROM properties_images 
WHERE property_id = 12345 
ORDER BY image_order;

-- 特定種別の画像
SELECT * FROM properties_images 
WHERE image_type_1 = '外観';
```
