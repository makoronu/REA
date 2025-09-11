# 📍 所在地・交通 テーブル群

## 📋 概要
住所・駅・交通アクセス情報

## 🗂️ 含まれるテーブル
- [properties_location](properties_location.md) - 11カラム, 0レコード
- [properties_transportation](properties_transportation.md) - 15カラム, 0レコード

## 🎯 主な用途
- 物件所在地の特定・表示
- 地域・駅での物件検索
- 地図表示・ルート案内

## 🔗 関連テーブル
- properties（基本情報）
- properties_transportation（交通情報と連携）

## 🚀 よく使うクエリ例
```sql
-- 住所での検索
SELECT * FROM properties_location 
WHERE address_name LIKE '%新宿%';

-- 緯度経度での範囲検索
SELECT * FROM properties_location 
WHERE latitude_longitude IS NOT NULL;
```
