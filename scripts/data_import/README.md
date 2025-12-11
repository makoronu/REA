# データインポートスクリプト

周辺施設データの取得・更新用スクリプト集。

## 使用方法

```bash
cd ~/my_programing/REA
PYTHONPATH=~/my_programing/REA python3 scripts/data_import/<スクリプト名>.py
```

## スクリプト一覧

| スクリプト | 対象 | データソース | 件数 |
|-----------|------|-------------|------|
| import_schools.py | 小中高大短大高専幼稚園認定こども園専門学校 | 国土数値情報 P29 | 約57,000件 |
| import_vocational_training.py | 職業訓練校 | 手動収集 | 8件（北海道のみ） |
| import_stations.py | 駅 | HeartRails Express API | 約10,000件 |
| import_osm_facilities.py | 商業施設・公共施設 | OpenStreetMap Overpass API | 多数 |
| import_medical.py | 病院・診療所 | 国土数値情報 P04 | 約180,000件 |

## データソース詳細

### 国土数値情報（MLIT）
- URL: https://nlftp.mlit.go.jp/ksj/
- 形式: GeoJSON / Shapefile
- 更新頻度: 年1回程度
- **学校データ (P29)**: 小中高大短大高専幼稚園認定こども園専門学校
- **医療機関データ (P04)**: 病院・診療所

### HeartRails Express API
- URL: http://express.heartrails.com/api.html
- 形式: JSON API
- 更新頻度: 随時
- **対象**: 全国の駅（約10,000駅）

### OpenStreetMap (Overpass API)
- URL: https://overpass-api.de/
- 形式: JSON API
- 更新頻度: 随時（ボランティア更新）
- **対象**: 商業施設（スーパー、コンビニ、ドラッグストア等）、公共施設（役所、郵便局等）

### 手動収集データ
- **職業訓練校**: 各都道府県の公式サイトから収集
  - 北海道: https://www.pref.hokkaido.lg.jp/kz/jzi/69081.html

## データソース管理テーブル

`m_data_sources` テーブルでデータソース情報を管理。

```sql
SELECT category_code, source_name, last_updated, record_count
FROM m_data_sources
ORDER BY category_code;
```

## 更新手順

1. スクリプトを実行
2. `m_data_sources` テーブルの `last_updated` が自動更新される
3. 必要に応じて `m_facility_categories` の `display_order` を調整

## 未対応データ

- **保育所**: 公式CSVデータなし。「ここdeサーチ」にAPIなし。各自治体オープンデータ収集が必要。
- **職業訓練校（北海道以外）**: 手動収集が必要。全国166校のうち8校のみ登録済み。
