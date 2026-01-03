# テスト依頼書: Seg3d 設定値DB化

**作成日:** 2026-01-04
**対象:** 設定値のDB移行（メタデータ駆動化）

---

## 変更概要

設定値（学校種別コード、検索距離、制限値等）をハードコードからDB（system_config）への移行。

---

## 変更ファイル一覧

### バックエンド
| ファイル | 変更内容 |
|----------|----------|
| shared/constants.py | DB読み込み型に修正（_LazyDict使用） |

### フロントエンド
| ファイル | 変更内容 |
|----------|----------|
| src/constants.ts | GEO_SEARCH_CONFIG定数追加 |
| src/components/form/DynamicForm.tsx | 直書き3件→定数参照 |
| src/services/geoService.ts | デフォルト値→定数参照 |

### DB
| テーブル | 変更内容 |
|----------|----------|
| system_config（新規） | 設定値格納テーブル |
| property_types | sort_orderカラム追加 |

---

## テスト項目

### 1. system_config読み込み確認

**手順:**
```bash
PYTHONPATH=. python3 -c "
from shared.constants import get_school_type_codes, get_search_radius
print(get_school_type_codes())
print(get_search_radius())
"
```

**期待結果:**
- DBから設定値が読み込まれる
- school_type_codes: {'elementary': '16001', ...}
- search_radius: {'station': 5000, ...}

---

### 2. 後方互換性確認

**手順:**
```bash
PYTHONPATH=. python3 -c "
from shared.constants import SCHOOL_TYPE_CODES, DEFAULT_SEARCH_RADIUS
print(SCHOOL_TYPE_CODES['elementary'])
print(DEFAULT_SEARCH_RADIUS['station'])
"
```

**期待結果:**
- 既存の変数アクセス方式で値が取得できる
- SCHOOL_TYPE_CODES['elementary'] = '16001'
- DEFAULT_SEARCH_RADIUS['station'] = 5000

---

### 3. geo API動作確認

**手順:**
```bash
curl "http://localhost:8005/api/v1/geo/nearest-stations?lat=43.8041&lng=144.0972&radius=5000&limit=5"
```

**期待結果:**
- 正常にJSONレスポンスが返る
- stationsリストが含まれる

---

### 4. フロントエンド動作確認

**手順:**
1. 物件編集画面を開く
2. 緯度・経度を入力（例: 43.8041, 144.0972）
3. 「🔍 最寄駅を自動取得」ボタンをクリック
4. 「🚌 バス停を自動取得」ボタンをクリック
5. 「🏪 周辺施設を自動取得」ボタンをクリック

**期待結果:**
- 各ボタンで正常に候補リストが表示される
- エラーが発生しない

---

### 5. 物件種別グループ順序確認

**手順:**
```bash
PYTHONPATH=. python3 -c "
from shared.constants import get_property_type_group_order
print(get_property_type_group_order())
"
```

**期待結果:**
- DBから順序が取得される
- {'居住用': 1, '事業用': 2, '投資用': 3, ...}

---

## 攻撃ポイント

### 境界値
- system_configテーブルが空の場合 → フォールバック値使用

### 不正入力
- なし（読み取り専用）

### 権限
- なし（設定読み込みは認証不要）

---

## テスト環境

- API: http://localhost:8005
- フロント: http://localhost:5173
- DB: PostgreSQL (real_estate_db)

---

## 備考

- DB接続失敗時はフォールバック値（コード内のデフォルト）が使用される
- 設定変更はDBを直接更新（管理画面未実装）
