# 公開時バリデーション「該当なし」対応 ロードマップ

## 概要
公開時必須項目で「入力不可能なケース」に対応するため、
「該当なし」選択肢・チェックボックスを追加する。

---

## セグメント構成

| Seg | 名称 | 依存 | テスト単位 | 状態 |
|-----|------|------|-----------|------|
| A | マスタデータ追加 | なし | API単体 | ✅完了 |
| B | 接道情報コンポーネント | なし | UI単体 | ✅完了 |
| C | 交通系コンポーネント | なし | UI単体 | ✅完了 |
| D | バリデーション修正 | A,B,C | 統合テスト | ✅完了 |
| E | マスタテーブル作成 | なし | API確認 | ✅完了 |

---

## Segment A: マスタデータ追加 ✅完了

### A-1: 用途地域に「指定なし」追加 ✅
- **ファイル**: scripts/migrations/add_none_options_20260102.sql
- **対象**: category_id = 40 (zoning_district)
- **追加値**: option_code='none', option_value='指定なし'

### A-2: 向きに「該当なし」追加 ✅
- **対象**: category_id = 18 (orientation)
- **追加値**: option_code='na', option_value='該当なし'

### A-3: 管理形態に「該当なし」追加 ✅
- **対象**: category_id = 16 (management_type)
- **追加値**: option_code='na', option_value='該当なし（戸建等）'

---

## Segment B: 接道情報コンポーネント ✅完了

### B-1: RoadInfoEditorに「接道なし」チェック追加 ✅
- **ファイル**: rea-admin/src/components/form/JsonEditors.tsx
- **データ形式**: `{ "no_road_access": true }`

---

## Segment C: 交通系コンポーネント ✅完了

### C-1: TransportationField「最寄駅なし」 ✅
- **ファイル**: rea-admin/src/components/form/TransportationField.tsx
- **データ形式**: `{ "no_station": true }`

### C-2: BusStopsField「バス路線なし」 ✅
- **ファイル**: rea-admin/src/components/form/BusStopsField.tsx
- **データ形式**: `{ "no_bus": true }`

### C-3: NearbyFacilitiesField「近隣施設なし」 ✅
- **ファイル**: rea-admin/src/components/form/NearbyFacilitiesField.tsx
- **データ形式**: `{ "no_facilities": true }`

---

## Segment D: バリデーション修正 ✅完了

### 精査結果（2026-01-03）

#### データ構造の確認
- `validate_for_publication` には**フラット辞書**が渡される
- テーブル名なしでカラム名のみで参照可能
- `property_type` の値: `detached`, `mansion`, `apartment` 等

#### 発見された問題
1. ロードマップのタプル形式 `('land_info', 'column')` は不要
2. `total_units` が全種別で必須になっているが、detachedには不要
3. 条件付き除外ロジックが未実装

---

### D-1: 条件付き除外ルールの実装

**ファイル**: rea-api/app/services/publication_validator.py

```python
# 条件付き除外ルール（カラム名のみ）
CONDITIONAL_EXCLUSIONS = {
    # 用途地域が「指定なし」の場合、建ぺい率・容積率は不要
    'building_coverage_ratio': {
        'depends_on': 'use_district',
        'exclude_when': ['none', '指定なし']
    },
    'floor_area_ratio': {
        'depends_on': 'use_district',
        'exclude_when': ['none', '指定なし']
    },
    # 戸建の場合、所在階・総戸数は不要
    'room_floor': {
        'depends_on': 'property_type',
        'exclude_when': ['detached']
    },
    'total_units': {
        'depends_on': 'property_type',
        'exclude_when': ['detached']
    },
    # 接道なしの場合、セットバックは不要
    'setback': {
        'depends_on': 'road_info',
        'exclude_when_func': 'is_no_road_access'
    },
}
```

---

### D-2: 特殊フラグ判定関数の実装

```python
# 特殊フラグの判定ヘルパー
def is_no_road_access(value) -> bool:
    """接道なしフラグの判定"""
    if isinstance(value, dict) and value.get('no_road_access') == True:
        return True
    return False

def is_no_station(value) -> bool:
    """最寄駅なしフラグの判定"""
    if isinstance(value, dict) and value.get('no_station') == True:
        return True
    return False

def is_no_bus(value) -> bool:
    """バス路線なしフラグの判定"""
    if isinstance(value, dict) and value.get('no_bus') == True:
        return True
    return False

def is_no_facilities(value) -> bool:
    """近隣施設なしフラグの判定"""
    if isinstance(value, dict) and value.get('no_facilities') == True:
        return True
    return False

# 特殊フラグカラムとその判定関数
SPECIAL_FLAG_COLUMNS = {
    'road_info': is_no_road_access,
    'transportation': is_no_station,
    'bus_stops': is_no_bus,
    'nearby_facilities': is_no_facilities,
}
```

---

### D-3: 有効値判定関数の実装

```python
# 「なし」として有効なテキスト値
VALID_NONE_VALUES = ['なし', '該当なし', 'なし（学区外）']

# 0が有効値となるカラム
ZERO_VALID_COLUMNS = ['management_fee', 'repair_reserve_fund']

def is_valid_value(value, column_name: str) -> bool:
    """
    値が有効（入力済み）かどうかを判定

    Returns:
        True: 有効な値（入力済み）
        False: 無効な値（未入力・空）
    """
    if value is None:
        return False

    # 文字列の場合
    if isinstance(value, str):
        if not value.strip():
            return False
        # 「なし」系テキストは有効
        if value.strip() in VALID_NONE_VALUES:
            return True
        return True

    # 数値の場合
    if isinstance(value, (int, float)):
        # 特定カラムは0を有効値とする
        if column_name in ZERO_VALID_COLUMNS:
            return True
        return True  # 0以外も全て有効

    # 辞書の場合（特殊フラグ対応）
    if isinstance(value, dict):
        # 特殊フラグカラムの場合
        if column_name in SPECIAL_FLAG_COLUMNS:
            check_func = SPECIAL_FLAG_COLUMNS[column_name]
            if check_func(value):
                return True  # 「なし」フラグは有効値
        # 通常のdict
        return bool(value)  # 空dictは無効

    # 配列の場合
    if isinstance(value, list):
        return len(value) > 0

    return True
```

---

### D-4: validate_for_publication の修正

```python
def should_exclude_field(column_name: str, property_data: Dict) -> bool:
    """条件付き除外の判定"""
    rule = CONDITIONAL_EXCLUSIONS.get(column_name)
    if not rule:
        return False

    depends_on = rule.get('depends_on')
    depends_value = property_data.get(depends_on)

    # 関数ベースの判定
    if 'exclude_when_func' in rule:
        func_name = rule['exclude_when_func']
        if func_name == 'is_no_road_access' and is_no_road_access(depends_value):
            return True
        return False

    # 値ベースの判定
    exclude_when = rule.get('exclude_when', [])
    if depends_value in exclude_when:
        return True

    # マスタオプションの値チェック（code or valueどちらでもマッチ）
    if isinstance(depends_value, (int, str)):
        str_value = str(depends_value)
        for exclude_val in exclude_when:
            if str_value == str(exclude_val):
                return True

    return False


def validate_for_publication(
    db: Session,
    property_data: Dict[str, Any],
    new_publication_status: Optional[str],
    current_publication_status: Optional[str] = None,
) -> Tuple[bool, List[str]]:
    """公開時バリデーション（改善版）"""

    # 既存チェック（省略）...

    # 未入力フィールドをチェック
    missing_fields = []
    for field in required_fields:
        column_name = field["column_name"]

        # 条件付き除外チェック
        if should_exclude_field(column_name, property_data):
            continue

        value = property_data.get(column_name)

        # 有効値判定（改善版）
        if not is_valid_value(value, column_name):
            missing_fields.append(field["japanese_label"])

    if missing_fields:
        return False, missing_fields

    return True, []
```

---

### D-5: 統合テストケース

| # | テストケース | 期待結果 |
|---|-------------|----------|
| 1 | 用途地域「指定なし」+ 建ぺい率・容積率未入力 | 公開可能 |
| 2 | 物件種別「detached」+ 所在階・総戸数未入力 | 公開可能 |
| 3 | 接道情報「接道なし」チェック + セットバック未入力 | 公開可能 |
| 4 | 管理費「0」入力 | 公開可能 |
| 5 | 修繕積立金「0」入力 | 公開可能 |
| 6 | 小学校「なし」入力 | 公開可能 |
| 7 | 中学校「該当なし」入力 | 公開可能 |
| 8 | 最寄駅「最寄駅なし」チェック | 公開可能 |
| 9 | バス停「バス路線なし」チェック | 公開可能 |
| 10 | 近隣施設「近隣施設なし」チェック | 公開可能 |

---

## 実行手順

### D実装手順

1. **D-1〜D-4**: publication_validator.py を修正
2. **APIサーバー再起動**
3. **D-5**: 統合テスト実行（手動 or Selenium）
4. **コミット**

---

## ファイル一覧

| セグメント | ファイル | 変更内容 | 状態 |
|-----------|---------|---------|------|
| A | scripts/migrations/add_none_options_20260102.sql | マスタデータ追加 | ✅完了 |
| B | rea-admin/src/components/form/JsonEditors.tsx | 接道なしチェック | ✅完了 |
| C | rea-admin/src/components/form/TransportationField.tsx | 最寄駅なしチェック | ✅完了 |
| C | rea-admin/src/components/form/BusStopsField.tsx | バス路線なしチェック | ✅完了 |
| C | rea-admin/src/components/form/NearbyFacilitiesField.tsx | 近隣施設なしチェック | ✅完了 |
| D | rea-api/app/services/publication_validator.py | 条件付き必須ロジック | ✅完了 |

---

## 完了条件

- [x] Segment A: マスタデータ3件追加、API確認OK
- [x] Segment B: 接道なしチェック動作OK
- [x] Segment C: 交通系3コンポーネントチェック動作OK
- [x] Segment E: マスタテーブル作成完了
- [x] Segment D: 全10テストケースPASS（2026-01-03）
- [x] 本番デプロイ完了（2026-01-03）

---

## リスク・注意点

1. **既存データとの互換性**: 新フラグ形式と既存配列形式の両方をサポート必要 → 実装済み
2. **マスタオプションのcode/value両対応**: exclude_whenで両方マッチするよう実装
3. **テスト網羅性**: 全物件種別 × 全条件の組み合わせテスト必要
