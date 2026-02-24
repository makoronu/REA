# 単体テスト

## やること
1. 1件の詳細ページHTMLでパース→正規化→REA変換を通す
2. 物件種別ごとに1件以上テスト（土地・戸建・マンション）

## 確認項目
- 必須: property_name / sale_price / prefecture / city / address
- 土地: land_area / use_district / building_coverage_ratio / floor_area_ratio
- 建物: building_area / building_structure / construction_date / room_type
- メタ: listing_id / source_url / source_site

## 完了条件
- [ ] 全必須フィールドが正しく変換されている
- [ ] master_optionsコード値・型が正しい

## 次 → batch.md
