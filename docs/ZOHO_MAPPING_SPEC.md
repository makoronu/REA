# ZOHO → REA マッピング仕様書

**作成日**: 2025-12-14
**目的**: ZOHOデータをREAにインポートする際の変換ルールを定義

---

## 1. 概要

### 1.1 データフロー
```
[ZOHO CRM API] → [zoho_import_staging] → [Transform] → [REA tables]
```

### 1.2 対象テーブル
- properties（物件基本情報）
- building_info（建物情報）
- land_info（土地情報）
- amenities（設備情報）

---

## 2. フィールドマッピング

### 2.1 properties テーブル

| ZOHOフィールド | REAカラム | 変換 |
|---------------|----------|------|
| id | zoho_id | そのまま |
| Name | property_name | そのまま |
| field57 | company_property_number | そのまま |
| field3 | sale_price | 数値変換 |
| field8 | property_type | **値変換必要** |
| field6 | transaction_type | **値変換必要** |
| field7 | publication_status, sales_status | **値変換必要** |
| field5 | prefecture | そのまま |
| field4 | city | そのまま |
| field14 + field16 | address | 結合（町名+住居表示） |
| field13 | - | 地番（land_info.chibanへ） |
| field18 | latitude | 数値変換 |
| field15 | longitude | 数値変換 |
| field46 | elementary_school | そのまま |
| field47 | junior_high_school | そのまま |
| field49 | catch_copy2 | そのまま |
| field50 | catch_copy | そのまま |
| field52 | catch_copy3 | そのまま |
| field51 | remarks | そのまま |
| field56.name | property_manager_name | オブジェクトから抽出 |
| field89 | contractor_phone | そのまま |
| field91 | contractor_email | そのまま |
| - | is_new_construction | **field8から判定** |
| - | is_investment | **field8から判定** |
| - | is_commercial | **field8から判定** |

### 2.2 building_info テーブル

| ZOHOフィールド | REAカラム | 変換 |
|---------------|----------|------|
| m2 | building_area | 数値変換 |
| field22 | building_structure | **値変換必要** |
| field21 | building_floors_above | 数値変換 |
| field20 | building_floors_below | 数値変換 |
| field12, field11 | construction_date | 年月→日付変換 |
| field2 | room_type | **値変換必要** |
| field48 | floor_plan_notes | そのまま |
| field45 | parking_availability | **値変換必要** |
| field44 | parking_notes | そのまま |
| field39 | direction | **値変換必要** |

### 2.3 land_info テーブル

| ZOHOフィールド | REAカラム | 変換 |
|---------------|----------|------|
| field28 | land_area | 数値変換 |
| field26 | land_category | **値変換必要** |
| field25 | use_district | **値変換必要** |
| field30 | city_planning | **値変換必要** |
| field27 | building_coverage_ratio | 数値変換 |
| field29 | floor_area_ratio | 数値変換 |
| field42 | land_rights | **値変換必要** |
| field31 | terrain | **値変換必要** |
| field43 | setback | **値変換必要** |
| field13 | chiban | そのまま |
| field37 | road_info.road_access | **値変換必要** |
| field38 | road_info.road1_type | **値変換必要** |
| field39 | road_info.road1_direction | **値変換必要** |
| field33 | road_info.road1_width | 数値変換 |
| field34 | road_info.road1_frontage | 数値変換 |

---

## 3. 値変換ルール

### 3.1 property_type（物件種別）

**選択肢（8種）**: マンション, 一戸建て, アパート, 土地, 店舗・事務所, ビル, 倉庫, その他

| ZOHO値 | → | REA値 | is_new | is_investment | is_commercial |
|--------|---|-------|--------|---------------|---------------|
| 【売戸建】中古戸建 | → | 一戸建て | - | - | - |
| 【売戸建】新築戸建 | → | 一戸建て | ✓ | - | - |
| 【売地】売地 | → | 土地 | - | - | - |
| 【売地】建付土地 | → | 土地 | - | - | - |
| 【売マン】中古マンション | → | マンション | - | - | - |
| 【売建物全部】店舗付住宅 | → | 一戸建て | - | - | ✓ |
| 【売建物全部】店舗 | → | 店舗・事務所 | - | - | ✓ |
| 【売建物全部】事務所 | → | 店舗・事務所 | - | - | ✓ |
| 【売建物全部】アパート | → | アパート | - | ✓ | - |
| 【売建物全部】ビル | → | ビル | - | ✓ | ✓ |
| 【売建物全部】倉庫 | → | 倉庫 | - | - | ✓ |
| 【売建物全部】旅館 | → | その他 | - | - | ✓ |
| 【売建物全部】その他 | → | その他 | - | - | - |
| 【売建物一部】店舗 | → | 店舗・事務所 | - | - | ✓ |
| 【賃貸居住】一戸建 | → | 一戸建て | - | ✓ | - |
| 【賃貸居住】アパート | → | アパート | - | ✓ | - |
| 【賃貸事業】一戸建 | → | 一戸建て | - | ✓ | ✓ |
| 【賃貸事業】その他 | → | その他 | - | ✓ | ✓ |
| (NULL) | → | NULL | - | - | - |

### 3.2 transaction_type（取引態様）

**ENUM値**: 1:売主, 2:代理, 3:専任媒介, 4:一般媒介, 5:専属専任, 6:買取

| ZOHO値 | 件数 | → | REA値 |
|--------|------|---|-------|
| 仲介 | 1714 | → | 4:一般媒介 |
| 専任 | 386 | → | 3:専任媒介 |
| 一般 | 138 | → | 4:一般媒介 |
| 売主 | 64 | → | 1:売主 |
| 買取 | 27 | → | 6:買取 |
| 賃貸 | 4 | → | NULL（売買物件ではないためスキップ） |

### 3.3 publication_status（公開状況）& sales_status（販売状況）

**publication_status ENUM**: 非公開, 会員公開, 公開
**sales_status ENUM**: 準備中, 販売中, 商談中, 成約済み, 販売終了, 販売準備

| ZOHO値 | 件数 | → | publication_status | sales_status |
|--------|------|---|-------------------|--------------|
| 終了非公開 | 2234 | → | 非公開 | 成約済み |
| 公開 | 93 | → | 公開 | 販売中 |
| 賃貸（貸出中） | 22 | → | 非公開 | 販売中（賃貸中） |
| 賃貸（終了非公開） | 6 | → | 非公開 | 成約済み |
| 非公開（決済予定） | 4 | → | 非公開 | 商談中 |
| 未公開 | 4 | → | 非公開 | 販売準備 |
| 非公開（契約決済予定） | 4 | → | 非公開 | 商談中 |
| 非公開（契約予定） | 3 | → | 非公開 | 商談中 |

### 3.4 current_status（現況）

**ENUM値**: 1:空家, 2:居住中, 3:賃貸中, 9:その他

| ZOHO値 | 件数 | → | REA値 | 備考 |
|--------|------|---|-------|------|
| 空家 | 1392 | → | 1:空家 | |
| 居住中 | 549 | → | 2:居住中 | |
| 賃貸中 | 54 | → | 3:賃貸中 | |
| 更地 | 185 | → | 9:その他 | **要検討：ENUM追加？** |
| 上物有 | 43 | → | 9:その他 | **要検討：ENUM追加？** |
| 未完成 | 1 | → | 9:その他 | |

### 3.5 use_district（用途地域）

**ENUM値**: 1〜12（無指定なし）

| ZOHO値 | 件数 | → | REA値 |
|--------|------|---|-------|
| 第一種低層住居専用 | 485 | → | 1:第一種低層住居専用 |
| 第二種低層住居専用 | 13 | → | 2:第二種低層住居専用 |
| 第一種中高層住居専用 | 50 | → | 3:第一種中高層住居専用 |
| 第二種中高層住居専用 | 654 | → | 4:第二種中高層住居専用 |
| 第一種住居 | 568 | → | 5:第一種住居 |
| 第二種住居 | 145 | → | 6:第二種住居 |
| 準住居 | 0 | → | 7:準住居 |
| 近隣商業 | 31 | → | 8:近隣商業 |
| 商業 | 22 | → | 9:商業 |
| 準工業 | 53 | → | 10:準工業 |
| 工業 | 65 | → | 11:工業 |
| 工業専用 | 0 | → | 12:工業専用 |
| 無指定 | 170 | → | NULL | **要検討：ENUM追加？** |

### 3.6 direction（方向）

**ENUM値**: 1:北, 2:北東, 3:東, 4:南東, 5:南, 6:南西, 7:西, 8:北西

| ZOHO値 | → | REA値 |
|--------|---|-------|
| 北 | → | 1:北 |
| 北東 | → | 2:北東 |
| 東 | → | 3:東 |
| 南東 | → | 4:南東 |
| 南 | → | 5:南 |
| 南西 | → | 6:南西 |
| 西 | → | 7:西 |
| 北西 | → | 8:北西 |

### 3.7 land_rights（土地権利）

**ENUM値**: 1:所有権, 2:借地権, 3:定期借地権, 4:地上権
**column_labels**: 1:所有権, 2:旧法地上, 3:旧法賃借, ... 99:その他

| ZOHO値 | 件数 | → | REA値 | 備考 |
|--------|------|---|-------|------|
| 所有権 | 2256 | → | 1:所有権 | |
| 旧法地上 | 1 | → | 4:地上権 | **ENUM/column_labels不一致** |

### 3.8 setback（セットバック）

**ENUM値**: 0:不要, 1:要, 2:セットバック済

| ZOHO値 | 件数 | → | REA値 |
|--------|------|---|-------|
| 不要 | 1237 | → | 0:不要 |
| 要 | 7 | → | 1:要 |
| 届出中 | 1 | → | 1:要 |

### 3.9 building_structure（建物構造）

**ENUM値**: 1:木造, 2:鉄骨造, 3:RC造, 4:SRC造, 5:軽量鉄骨, 6:ALC, 9:その他
**column_labels**: 1:木造, 2:ブロック, 3:鉄骨造, 4:RC, ... 13:CFT

| ZOHO値 | 件数 | → | REA値 | 備考 |
|--------|------|---|-------|------|
| 木造 | 1971 | → | 1:木造 | |
| 鉄骨造 | 11 | → | 2:鉄骨造 | |
| 鉄筋コンクリート造 | 4 | → | 3:RC造 | |
| 軽量鉄骨造 | 12 | → | 5:軽量鉄骨 | |
| ブロック造 | 25 | → | 9:その他 | **ENUM/column_labels不一致** |
| 木造・鉄骨造 | 2 | → | 9:その他 | 混構造 |
| 木造・鉄筋コンクリート造 | 4 | → | 9:その他 | 混構造 |
| その他 | 1 | → | 9:その他 | |

### 3.10 room_type（間取り）

**ENUM値**: 1:R, 2:K, 3:DK, 4:LDK, 5:SLDK, 6:その他

| ZOHO値 | → | REA値 |
|--------|---|-------|
| 1R, 1Ｒ | → | 1:R |
| 1K, 1Ｋ | → | 2:K |
| 1DK〜4DK, 1ＤＫ〜4ＤＫ | → | 3:DK |
| 1LDK〜10LDK, 1ＬＤＫ〜10ＬＤＫ | → | 4:LDK |
| 1SLDK〜6SLDK, 1ＳＬＤＫ〜6ＳＬＤＫ | → | 5:SLDK |
| その他 | → | 6:その他 |

### 3.11 parking_availability（駐車場）

**ENUM値**: 1:無, 2:有(無料), 3:有(有料), 4:近隣(無料), 5:近隣(有料)

| ZOHO値 | 件数 | → | REA値 |
|--------|------|---|-------|
| 無 | 67 | → | 1:無 |
| 有 | 478 | → | 2:有(無料) |
| 有(1台) | 167 | → | 2:有(無料) |
| 有(2台) | 578 | → | 2:有(無料) |
| 有(3台以上) | 631 | → | 2:有(無料) |

### 3.12 road_access（接道状況）

**column_labels**: 1:一方, 2:角地, 3:三方, 4:四方, 5:二方(除角地), 10:接道なし

| ZOHO値 | 件数 | → | REA値 |
|--------|------|---|-------|
| 一方 | 1129 | → | 1:一方 |
| 角地 | 315 | → | 2:角地 |
| 三方 | 24 | → | 3:三方 |
| 二方(除角地) | 92 | → | 5:二方(除角地) |
| 接道なし | 3 | → | 10:接道なし |

### 3.13 road_type（道路種別）

**column_labels**: 1:公道, 2:私道

| ZOHO値 | 件数 | → | REA値 |
|--------|------|---|-------|
| 公道 | 2085 | → | 1:公道 |
| 私道 | 120 | → | 2:私道 |

### 3.14 terrain（地勢）

**column_labels**: 1:平坦, 2:高台, 3:低地, 4:ひな段, 5:傾斜地, 9:その他

| ZOHO値 | 件数 | → | REA値 |
|--------|------|---|-------|
| 平坦 | 1398 | → | 1:平坦 |
| 高台 | 83 | → | 2:高台 |
| 低地 | 2 | → | 3:低地 |
| ひな段 | 21 | → | 4:ひな段 |
| 傾斜地 | 378 | → | 5:傾斜地 |
| その他 | 1 | → | 9:その他 |

### 3.15 land_category（地目）

**column_labels**: 1:宅地, 2:田, 3:畑, 4:山林, 5:雑種地, 9:その他, 10:原野, 11:田･畑

| ZOHO値 | 件数 | → | REA値 |
|--------|------|---|-------|
| 宅地 | 1707 | → | 1:宅地 |
| 田 | 9 | → | 2:田 |
| 畑 | 42 | → | 3:畑 |
| 山林 | 15 | → | 4:山林 |
| 雑種地 | 459 | → | 5:雑種地 |
| 原野 | 55 | → | 10:原野 |

### 3.16 city_planning（都市計画）

**column_labels**: 1:市街化区域, 2:市街化調整区域, 3:非線引区域, 4:都市計画区域外

| ZOHO値 | 件数 | → | REA値 |
|--------|------|---|-------|
| 市街化区域 | 1552 | → | 1:市街化区域 |
| 市街化調整区域 | 12 | → | 2:市街化調整区域 |
| 非線引区域 | 292 | → | 3:非線引区域 |
| 都市計画区域外 | 91 | → | 4:都市計画区域外 |
| 準都市計画区域 | 18 | → | **?** (選択肢にない) |

---

## 4. 未解決の問題

### 4.1 ENUM追加が必要

| フィールド | 追加すべき値 | 件数 |
|-----------|-------------|------|
| current_status | 更地 | 185 |
| current_status | 上物有 | 43 |
| use_district | 無指定 | 170 |
| city_planning | 準都市計画区域 | 18 |

### 4.2 ENUM/column_labels不一致

| フィールド | 問題 |
|-----------|------|
| building_structure | ENUMとcolumn_labelsでコード番号が異なる |
| land_rights | ENUMとcolumn_labelsで選択肢が異なる |
| setback | ENUMとcolumn_labelsでコード番号が異なる |

### 4.3 UIの選択肢更新が必要

| ファイル | フィールド | 変更内容 |
|---------|-----------|---------|
| PropertyEditPage.tsx | property_type | 8選択肢に拡張 |
| column_labels | property_type | 8選択肢に更新 |

---

## 5. 実装タスク

### 5.1 DB変更
- [ ] property_type選択肢を8種に更新（PropertyEditPage.tsx）
- [ ] property_type選択肢を8種に更新（column_labels）
- [ ] current_status ENUMに「更地」「上物有」追加検討
- [ ] use_district ENUMに「無指定」追加検討
- [ ] city_planning選択肢に「準都市計画区域」追加

### 5.2 mapper.py修正
- [ ] PROPERTY_TYPE_MAP作成
- [ ] TRANSACTION_TYPE_MAP確認・修正
- [ ] PUBLICATION_STATUS_MAP作成
- [ ] SALES_STATUS判定ロジック作成
- [ ] CURRENT_STATUS_MAP作成
- [ ] USE_DISTRICT_MAP作成
- [ ] DIRECTION_MAP作成
- [ ] LAND_RIGHTS_MAP作成
- [ ] SETBACK_MAP作成
- [ ] BUILDING_STRUCTURE_MAP確認・修正
- [ ] ROOM_TYPE_MAP確認・修正
- [ ] PARKING_AVAILABILITY_MAP確認・修正
- [ ] ROAD_ACCESS_MAP作成
- [ ] ROAD_TYPE_MAP作成
- [ ] TERRAIN_MAP作成
- [ ] LAND_CATEGORY_MAP作成
- [ ] CITY_PLANNING_MAP作成
- [ ] フラグ設定ロジック（is_new_construction, is_investment, is_commercial）

### 5.3 再インポート
- [ ] 既存propertiesデータ削除
- [ ] 既存building_infoデータ削除
- [ ] 既存land_infoデータ削除
- [ ] stagingから再インポート実行

### 5.4 検証
- [ ] 各フィールドの値分布確認
- [ ] NULL率確認
- [ ] UI表示確認（Selenium）

---

---

## 6. ZOHO全フィールド一覧（120個）

### 6.1 システムフィールド（使用しない）
| フィールド | 内容 |
|-----------|------|
| $approval, $approval_state, $approved | 承認関連 |
| $currency_symbol, Currency, Exchange_Rate | 通貨関連 |
| $editable, $locked_for_me, Locked__s | 編集権限 |
| $field_states, $in_merge, $orchestration, $process_flow | システム状態 |
| $layout_id, $review, $review_process, $state | レイアウト/レビュー |
| $zia_owner_assignment | AI割当 |
| Created_By, Created_Time, Modified_By, Modified_Time | 作成/更新情報 |
| Last_Activity_Time | 最終活動日時 |
| Owner | 所有者 |
| Record_Image, Tag | 画像/タグ |
| Email, Email_Opt_Out, Unsubscribed_Mode, Unsubscribed_Time | メール関連 |
| id | ZOHO内部ID → zoho_idへ |

### 6.2 物件基本情報
| フィールド | 内容 | 件数 | → REAカラム |
|-----------|------|------|------------|
| Name | 物件名（番号+種別+住所+価格） | 2370 | property_name |
| field57 | 自社物件番号 | 2370 | company_property_number |
| ID1 | 物件ID | 2369 | external_property_id |
| field8 | 物件種別 | 2350 | property_type（**要変換**） |
| field3 | 価格（円） | 2370 | sale_price |
| field9 | 不明（1-10の数字） | 2194 | **要調査** |

### 6.3 販売情報
| フィールド | 内容 | 件数 | → REAカラム |
|-----------|------|------|------------|
| field6 | 取引態様 | 2333 | transaction_type（**要変換**） |
| field7 | 公開状況 | 2370 | publication_status, sales_status（**要変換**） |
| field23 | 引渡時期（相談/即時） | 2202 | delivery_timing（**要変換**） |
| field94 | 媒介開始日？ | 75 | brokerage_contract_date |
| field95 | 媒介終了日 | 73 | - |
| field96 | 契約期限？ | 73 | - |

### 6.4 所在地情報
| フィールド | 内容 | 件数 | → REAカラム |
|-----------|------|------|------------|
| field5 | 都道府県 | 2370 | prefecture |
| field4 | 市区町村 | 2370 | city |
| field14 | 町名 | 2370 | （addressに結合） |
| field16 | 住居表示 | 2370 | （addressに結合） |
| field13 | 地番 | 2370 | land_info.chiban |
| field10 | バス停/目印 | 2189 | （備考へ？） |
| field62 | 住所詳細 | 263 | address_detail？ |
| field88 | 郵便番号 | 81 | postal_code |
| field90 | 建物名/部屋番号 | 10 | address_detail |
| field18 | 緯度 | 少 | latitude |
| field15 | 経度 | 少 | longitude |

### 6.5 交通情報
| フィールド | 内容 | 件数 | → REAカラム |
|-----------|------|------|------------|
| field17 | 最寄駅 | 1927 | transportation（JSONB） |
| field19 | 駅徒歩分 | 2307 | transportation（JSONB） |

### 6.6 学区情報
| フィールド | 内容 | 件数 | → REAカラム |
|-----------|------|------|------------|
| field46 | 小学校区 | 2370 | elementary_school |
| field47 | 中学校区 | 2370 | junior_high_school |

### 6.7 土地情報
| フィールド | 内容 | 件数 | → REAカラム |
|-----------|------|------|------------|
| field28 | 土地面積 | 2370 | land_info.land_area |
| field26 | 地目 | 2287 | land_info.land_category（**要変換**） |
| field25 | 用途地域 | 2256 | land_info.use_district（**要変換**） |
| field30 | 都市計画 | 1965 | land_info.city_planning（**要変換**） |
| field27 | 建蔽率 | 2370 | land_info.building_coverage_ratio |
| field29 | 容積率 | 2370 | land_info.floor_area_ratio |
| field42 | 土地権利 | 2257 | land_info.land_rights（**要変換**） |
| field31 | 地勢 | 1883 | land_info.terrain（**要変換**） |
| field43 | セットバック | 1245 | land_info.setback（**要変換**） |
| field32 | 法令制限 | 686 | land_info.legal_restrictions |

### 6.8 道路情報
| フィールド | 内容 | 件数 | → REAカラム |
|-----------|------|------|------------|
| field37 | 接道状況 | 1563 | land_info.road_info.road_access（**要変換**） |
| field38 | 道路種別1 | 2205 | land_info.road_info.road1_type（**要変換**） |
| field39 | 道路方向1 | 2249 | land_info.road_info.road1_direction（**要変換**）/ building_info.direction |
| field33 | 道路幅員1 | 2309 | land_info.road_info.road1_width |
| field34 | 接面間口1 | 2305 | land_info.road_info.road1_frontage |
| field40 | 道路種別2 | 365 | land_info.road_info.road2_type |
| field41 | 道路方向2 | 391 | land_info.road_info.road2_direction |
| field35 | 道路幅員2 | 2149 | land_info.road_info.road2_width |
| field36 | 接面間口2 | 2152 | land_info.road_info.road2_frontage |

### 6.9 建物情報
| フィールド | 内容 | 件数 | → REAカラム |
|-----------|------|------|------------|
| m2 | 建物面積 | 2287 | building_info.building_area |
| field22 | 建物構造 | 2030 | building_info.building_structure（**要変換**） |
| field21 | 地上階 | 2291 | building_info.building_floors_above |
| field20 | 地下階 | 2145 | building_info.building_floors_below |
| field12 | 築年 | 2289 | building_info.construction_date（年） |
| field11 | 築月 | 2287 | building_info.construction_date（月） |
| field2 | 間取り | 1941 | building_info.room_type（**要変換**） |
| field48 | 間取り備考 | 860 | building_info.floor_plan_notes |
| field71 | 間取り（重複？） | 138 | - |
| field24 | 現況 | 2224 | current_status（**要変換**） |

### 6.10 駐車場情報
| フィールド | 内容 | 件数 | → REAカラム |
|-----------|------|------|------------|
| field45 | 駐車場有無 | 1921 | building_info.parking_availability（**要変換**） |
| field44 | 駐車場備考 | 7 | building_info.parking_notes |

### 6.11 設備情報
| フィールド | 内容 | 件数 | → REAカラム |
|-----------|------|------|------------|
| field53 | 設備リスト | 85 | amenities.facilities（JSONB） |
| field84 | 地域？（北見/美幌/その他） | 2367 | **要調査** |

### 6.12 キャッチコピー・備考
| フィールド | 内容 | 件数 | → REAカラム |
|-----------|------|------|------------|
| field49 | キャッチコピー2 | 2370 | catch_copy2 |
| field50 | キャッチコピー1 | 2370 | catch_copy |
| field52 | キャッチコピー3 | 2370 | catch_copy3 |
| field51 | 備考 | 少 | remarks |

### 6.13 担当者情報
| フィールド | 内容 | 件数 | → REAカラム |
|-----------|------|------|------------|
| field56 | 担当者（オブジェクト） | 2370 | property_manager_name（.name） |
| field89 | 元請電話番号 | 少 | contractor_phone |
| field91 | 元請メール | 少 | contractor_email |
| field74 | 元請会社住所 | 83 | contractor_address |
| field92 | 元請会社住所詳細 | 83 | contractor_address |

### 6.14 外部連携
| フィールド | 内容 | 件数 | → REAカラム |
|-----------|------|------|------------|
| HP_URL | HP URL | 166 | property_url |
| HOMES | HOMES ID | 61 | - |
| HOMES_URL | HOMES URL | 155 | - |

### 6.15 ホームズ出力用（整形済みテキスト）
| フィールド | 内容 | 使用 |
|-----------|------|------|
| field63 | 土地面積テキスト | 不要 |
| field64 | 坪数 | 不要 |
| field65 | 建物面積テキスト | 不要 |
| field66 | 構造テキスト | 不要 |
| field67 | 校区テキスト | 不要 |
| field68 | 築年月テキスト | 不要 |
| field69 | 都市計画等テキスト | 不要 |
| field73 | 物件種別（重複） | 不要 |
| field75 | 帳票用テキスト | 不要 |

### 6.16 その他/不明
| フィールド | 内容 | 件数 | 備考 |
|-----------|------|------|------|
| field54 | オブジェクト | 19 | 要調査 |
| field55 | オブジェクト | 271 | 要調査 |
| field76 | 連絡方法（メール/SMS/LINE） | 86 | - |
| field77 | 関連物件ID？ | 264 | - |
| field78 | 価格関連？ | 230 | - |
| field82 | 数値（0/1） | 74 | - |
| field83 | 数値 | 225 | - |
| field85 | 数値（0） | 74 | - |

---

## 7. 変換が必要なフィールド一覧

### 7.1 ENUM変換（16種）
1. property_type（物件種別）→ 8選択肢
2. transaction_type（取引態様）→ 6選択肢
3. publication_status（公開状況）→ 3選択肢
4. sales_status（販売状況）→ 6選択肢
5. current_status（現況）→ 4選択肢
6. delivery_timing（引渡時期）→ 3選択肢
7. use_district（用途地域）→ 12選択肢
8. land_category（地目）→ 7選択肢
9. city_planning（都市計画）→ 4選択肢
10. terrain（地勢）→ 6選択肢
11. land_rights（土地権利）→ 4選択肢
12. setback（セットバック）→ 3選択肢
13. building_structure（建物構造）→ 7選択肢
14. room_type（間取り）→ 6選択肢
15. direction（方向）→ 8選択肢
16. parking_availability（駐車場）→ 5選択肢
17. road_access（接道状況）→ 6選択肢
18. road_type（道路種別）→ 2選択肢

### 7.2 数値変換
- field3 → sale_price（価格）
- field28 → land_area（土地面積）
- m2 → building_area（建物面積）
- field27 → building_coverage_ratio（建蔽率）
- field29 → floor_area_ratio（容積率）
- field33, field35 → road_width（道路幅員）
- field34, field36 → road_frontage（接面間口）
- field19 → 駅徒歩分
- field21, field20 → 階数

### 7.3 日付変換
- field12 + field11 → construction_date（築年月）
- field94, field95, field96 → 媒介関連日付

### 7.4 複合変換
- field14 + field16 → address（町名+住居表示）
- field17 + field19 → transportation（JSONB）
- field37〜field41 → road_info（JSONB）
- field53 → facilities（JSONB）

### 7.5 オブジェクト抽出
- field56.name → property_manager_name

### 7.6 フラグ設定
- field8 → is_new_construction, is_investment, is_commercial

---

## 8. 変更履歴

| 日付 | 内容 |
|------|------|
| 2025-12-14 | 初版作成 |
| 2025-12-14 | ZOHO全フィールド一覧追加 |
