# 📸 properties_images テーブル詳細仕様

## 📋 基本情報
- **テーブル名**: `properties_images`
- **機能グループ**: 画像管理
- **レコード数**: 0件
- **テーブルサイズ**: 0.03MB
- **カラム数**: 94

## 🎯 テーブルの役割
物件の画像情報を管理。外観・間取り・室内写真等の画像ファイルと関連情報を格納。

## 📊 カラム詳細仕様

| No | カラム名 | データ型 | NULL | デフォルト | 説明 | 備考 |
|----|----------|----------|------|------------|------|------|
| 1 | `id` | INTEGER | ❌ | nextval('properties_... | レコード識別ID | プライマリーキー |
| 2 | `property_id` | INTEGER | ❌ | - | レコード識別ID | 外部キー |
| 3 | `local_file_name_1` | VARCHAR | ✅ | - | 名称 |  |
| 4 | `image_type_1` | TEXT | ✅ | - | 種別・タイプ |  |
| 5 | `image_comment_1` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 6 | `local_file_name_2` | VARCHAR | ✅ | - | 名称 |  |
| 7 | `image_type_2` | TEXT | ✅ | - | 種別・タイプ |  |
| 8 | `image_comment_2` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 9 | `local_file_name_3` | VARCHAR | ✅ | - | 名称 |  |
| 10 | `image_type_3` | TEXT | ✅ | - | 種別・タイプ |  |
| 11 | `image_comment_3` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 12 | `local_file_name_4` | VARCHAR | ✅ | - | 名称 |  |
| 13 | `image_type_4` | TEXT | ✅ | - | 種別・タイプ |  |
| 14 | `image_comment_4` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 15 | `local_file_name_5` | VARCHAR | ✅ | - | 名称 |  |
| 16 | `image_type_5` | TEXT | ✅ | - | 種別・タイプ |  |
| 17 | `image_comment_5` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 18 | `local_file_name_6` | VARCHAR | ✅ | - | 名称 |  |
| 19 | `image_type_6` | TEXT | ✅ | - | 種別・タイプ |  |
| 20 | `image_comment_6` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 21 | `local_file_name_7` | VARCHAR | ✅ | - | 名称 |  |
| 22 | `image_type_7` | TEXT | ✅ | - | 種別・タイプ |  |
| 23 | `image_comment_7` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 24 | `local_file_name_8` | VARCHAR | ✅ | - | 名称 |  |
| 25 | `image_type_8` | TEXT | ✅ | - | 種別・タイプ |  |
| 26 | `image_comment_8` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 27 | `local_file_name_9` | VARCHAR | ✅ | - | 名称 |  |
| 28 | `image_type_9` | TEXT | ✅ | - | 種別・タイプ |  |
| 29 | `image_comment_9` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 30 | `local_file_name_10` | VARCHAR | ✅ | - | 名称 |  |
| 31 | `image_type_10` | TEXT | ✅ | - | 種別・タイプ |  |
| 32 | `image_comment_10` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 33 | `local_file_name_11` | VARCHAR | ✅ | - | 名称 |  |
| 34 | `image_type_11` | TEXT | ✅ | - | 種別・タイプ |  |
| 35 | `image_comment_11` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 36 | `local_file_name_12` | VARCHAR | ✅ | - | 名称 |  |
| 37 | `image_type_12` | TEXT | ✅ | - | 種別・タイプ |  |
| 38 | `image_comment_12` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 39 | `local_file_name_13` | VARCHAR | ✅ | - | 名称 |  |
| 40 | `image_type_13` | TEXT | ✅ | - | 種別・タイプ |  |
| 41 | `image_comment_13` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 42 | `local_file_name_14` | VARCHAR | ✅ | - | 名称 |  |
| 43 | `image_type_14` | TEXT | ✅ | - | 種別・タイプ |  |
| 44 | `image_comment_14` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 45 | `local_file_name_15` | VARCHAR | ✅ | - | 名称 |  |
| 46 | `image_type_15` | TEXT | ✅ | - | 種別・タイプ |  |
| 47 | `image_comment_15` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 48 | `local_file_name_16` | VARCHAR | ✅ | - | 名称 |  |
| 49 | `image_type_16` | TEXT | ✅ | - | 種別・タイプ |  |
| 50 | `image_comment_16` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 51 | `local_file_name_17` | VARCHAR | ✅ | - | 名称 |  |
| 52 | `image_type_17` | TEXT | ✅ | - | 種別・タイプ |  |
| 53 | `image_comment_17` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 54 | `local_file_name_18` | VARCHAR | ✅ | - | 名称 |  |
| 55 | `image_type_18` | TEXT | ✅ | - | 種別・タイプ |  |
| 56 | `image_comment_18` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 57 | `local_file_name_19` | VARCHAR | ✅ | - | 名称 |  |
| 58 | `image_type_19` | TEXT | ✅ | - | 種別・タイプ |  |
| 59 | `image_comment_19` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 60 | `local_file_name_20` | VARCHAR | ✅ | - | 名称 |  |
| 61 | `image_type_20` | TEXT | ✅ | - | 種別・タイプ |  |
| 62 | `image_comment_20` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 63 | `local_file_name_21` | VARCHAR | ✅ | - | 名称 |  |
| 64 | `image_type_21` | TEXT | ✅ | - | 種別・タイプ |  |
| 65 | `image_comment_21` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 66 | `local_file_name_22` | VARCHAR | ✅ | - | 名称 |  |
| 67 | `image_type_22` | TEXT | ✅ | - | 種別・タイプ |  |
| 68 | `image_comment_22` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 69 | `local_file_name_23` | VARCHAR | ✅ | - | 名称 |  |
| 70 | `image_type_23` | TEXT | ✅ | - | 種別・タイプ |  |
| 71 | `image_comment_23` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 72 | `local_file_name_24` | VARCHAR | ✅ | - | 名称 |  |
| 73 | `image_type_24` | TEXT | ✅ | - | 種別・タイプ |  |
| 74 | `image_comment_24` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 75 | `local_file_name_25` | VARCHAR | ✅ | - | 名称 |  |
| 76 | `image_type_25` | TEXT | ✅ | - | 種別・タイプ |  |
| 77 | `image_comment_25` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 78 | `local_file_name_26` | VARCHAR | ✅ | - | 名称 |  |
| 79 | `image_type_26` | TEXT | ✅ | - | 種別・タイプ |  |
| 80 | `image_comment_26` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 81 | `local_file_name_27` | VARCHAR | ✅ | - | 名称 |  |
| 82 | `image_type_27` | TEXT | ✅ | - | 種別・タイプ |  |
| 83 | `image_comment_27` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 84 | `local_file_name_28` | VARCHAR | ✅ | - | 名称 |  |
| 85 | `image_type_28` | TEXT | ✅ | - | 種別・タイプ |  |
| 86 | `image_comment_28` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 87 | `local_file_name_29` | VARCHAR | ✅ | - | 名称 |  |
| 88 | `image_type_29` | TEXT | ✅ | - | 種別・タイプ |  |
| 89 | `image_comment_29` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 90 | `local_file_name_30` | VARCHAR | ✅ | - | 名称 |  |
| 91 | `image_type_30` | TEXT | ✅ | - | 種別・タイプ |  |
| 92 | `image_comment_30` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 93 | `created_at` | TIMESTAMP | ✅ | CURRENT_TIMESTAMP | 作成日時 | 自動設定 |
| 94 | `updated_at` | TIMESTAMP | ✅ | CURRENT_TIMESTAMP | 日付 | 自動更新 |

## 🔗 制約・インデックス情報

### 外部キー制約
- **properties_images_property_id_fkey**: `property_id` → `properties_original_backup.id`

### インデックス
- **idx_properties_images_created_at** (INDEX): `created_at`
- **idx_properties_images_property_id** (INDEX): `property_id`

## 💾 使用例

### 物件画像一覧
```sql
SELECT * FROM properties_images WHERE property_id = 12345;
```

### 画像種別絞り込み
```sql
SELECT * FROM properties_images WHERE image_type_1 = '外観';
```

## 📈 パフォーマンス情報
- **レコード数**: 0件
- **テーブルサイズ**: 0.03MB
- **平均レコードサイズ**: 32768bytes
- **状況**: 小規模データのため高速アクセス可能

## 🔌 API連携情報
### 関連APIエンドポイント
- `GET /api/v1/properties/{id}/images` - 画像一覧取得
- `POST /api/v1/properties/{id}/images` - 画像アップロード

### API使用例
```bash
# properties_images データ取得
curl http://localhost:8005/api/v1/images/
```
