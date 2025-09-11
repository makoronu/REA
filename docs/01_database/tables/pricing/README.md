# 💰 価格・収益 テーブル群

## 📋 概要
価格・賃料・利回り等の収益情報

## 🗂️ 含まれるテーブル
- [properties_pricing](properties_pricing.md) - 16カラム, 0レコード

## 🎯 主な用途
- 物件価格・賃料の管理
- 投資収益計算・利回り算出
- 価格帯での物件検索・絞り込み

## 🔗 関連テーブル
- properties（基本情報）
- properties_building（建物情報から利回り計算）

## 🚀 よく使うクエリ例
```sql
-- 価格帯での検索
SELECT p.*, pp.price FROM properties p
JOIN properties_pricing pp ON p.id = pp.property_id
WHERE pp.price BETWEEN 100000 AND 200000;

-- 利回り順での並び替え
SELECT * FROM properties_pricing 
ORDER BY yield DESC LIMIT 10;
```
