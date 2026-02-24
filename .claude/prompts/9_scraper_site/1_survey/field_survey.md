# フィールド・表記ゆれ調査

## やること
対象サイトの物件詳細ページで表示されるフィールドを全数調査し、
REA のカラムとの対応関係・表記ゆれを洗い出す。

## 調査方法
1. 物件種別ごとに3件以上の詳細ページを開く
2. テーブル内のラベル（th/dt）を全数書き出す
3. 各ラベルに対応する REA カラムを特定する
4. 値の表記パターンを記録する

## フィールド対応表フォーマット

### 基本情報（properties テーブル）
| サイトのラベル | 値の例 | REAカラム | 変換処理 |
|--------------|--------|----------|---------|
| 価格 / 販売価格 | 2,980万円 | sale_price | parse_price |
| 物件名 | ○○ニュータウン | property_name | そのまま |
| 取引形態 | 専任媒介 | transaction_type | そのまま |
| 現況 | 空家 | current_status | そのまま |

### 土地情報（land_info テーブル）
| サイトのラベル | 値の例 | REAカラム | 変換処理 |
|--------------|--------|----------|---------|
| 所在地 | 北海道札幌市... | address | parse_address |
| 土地面積 | 150.25㎡ | land_area | parse_area |
| 用途地域 | 1種低層 | use_district | mapping→code |
| 都市計画 | 市街化区域 | city_planning | mapping→code |
| 建ぺい率 | 60% | building_coverage_ratio | parse_percentage |
| 容積率 | 200% | floor_area_ratio | parse_percentage |
| 地目 | 宅地 | land_category | mapping→code |
| 接道 | 南 6.0m 公道 | road_info | parse_road |

### 建物情報（building_info テーブル）
| サイトのラベル | 値の例 | REAカラム | 変換処理 |
|--------------|--------|----------|---------|
| 建物面積 | 100.5㎡ | building_area | parse_area |
| 構造 | 木造 | building_structure | mapping→code |
| 築年月 | 2020年3月 | construction_date | parse_date |
| 間取り | 3LDK | room_type + room_count | parse_room |
| 階建 | 2階建 | building_floors_above | parse_int |
| 向き | 南向き | direction | mapping→code |

## 表記ゆれ収集

### master_options api_aliases に追加する表記ゆれ
| カテゴリ | サイト表記 | REA正式表記 |
|---------|----------|-----------|
| use_district | 1種低層 | 第一種低層住居専用地域 |
| use_district | 一低専 | 第一種低層住居専用地域 |
| building_structure | W造 | 木造 |
| building_structure | S造 | 鉄骨造 |
| city_planning | 調整区域 | 市街化調整区域 |
| ... | ... | ... |

### サイト固有フィールド（REAに該当カラムなし）
| サイトのラベル | 値の例 | 対応 |
|--------------|--------|------|
| ... | ... | 無視 / 将来対応 / メモ欄に保存 |

## 完了条件
- [ ] 全フィールドラベルを書き出した（土地・戸建・マンション各3件以上）
- [ ] REAカラムとの対応表を完成した
- [ ] 表記ゆれを収集した
- [ ] サイト固有フィールド（REA非対応）を洗い出した
- [ ] 変換処理（parse_price / parse_area / mapping等）を特定した

## 次の工程
→ ../2_implement/discovery.md
