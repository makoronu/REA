# テスト依頼書: Seg1 ハードコーディング撲滅

**作成日:** 2026-01-03
**対象:** 公開時バリデーションのメタデータ駆動化

---

## 変更概要

`publication_validator.py` の5箇所のハードコーディングをDB読み込み型に変更。

| No | 変更前 | 変更後 |
|----|--------|--------|
| 1 | `PUBLICATION_STATUSES_REQUIRING_VALIDATION` 定数 | `master_options.requires_validation` から取得 |
| 2 | `VALID_NONE_VALUES` 定数 | `column_labels.valid_none_text` から取得 |
| 3 | `ZERO_VALID_COLUMNS` 定数 | `column_labels.zero_is_valid` から取得 |
| 4 | `CONDITIONAL_EXCLUSIONS` 定数 | `column_labels.conditional_exclusion` から取得 |
| 5 | `SPECIAL_FLAG_COLUMNS` 定数 | `column_labels.special_flag_key` から取得 |

---

## テスト対象ファイル

- `rea-api/app/services/publication_validator.py`
- `scripts/migrations/seg1_hardcoding_elimination.sql`

---

## 前提条件

1. DBマイグレーション実行済み
2. データ移行完了

---

## テストケース

### 正常系

| No | テスト内容 | 手順 | 期待結果 |
|----|-----------|------|----------|
| N1 | 公開バリデーション基本動作 | 必須項目未入力の物件を「公開」に変更 | バリデーションエラー発生、不足項目が表示される |
| N2 | 必須項目入力済みで公開 | 全必須項目入力済みの物件を「公開」に変更 | 正常に公開ステータスに変更される |
| N3 | 「なし」値の許容 | 小学校区に「なし」を入力して公開 | バリデーション通過 |
| N4 | 管理費0円許容 | 管理費=0、修繕積立金=0で公開 | バリデーション通過（zero_is_valid=true） |
| N5 | 条件付き除外（戸建） | 戸建物件で所在階・総戸数未入力で公開 | バリデーション通過（detached除外） |
| N6 | 条件付き除外（用途地域なし） | 用途地域「指定なし」で建ぺい率未入力で公開 | バリデーション通過 |
| N7 | 特殊フラグ（駅なし） | transportation: {"no_station": true} で公開 | バリデーション通過 |
| N8 | 非公開への変更 | 任意の物件を「非公開」に変更 | バリデーション不要、即座に変更される |

### 異常系

| No | テスト内容 | 手順 | 期待結果 |
|----|-----------|------|----------|
| E1 | 物件種別未設定 | property_type=nullで公開試行 | 「物件種別が未設定です」エラー |
| E2 | DB接続エラー時 | DBを停止して公開試行 | フォールバック値で動作（エラーにならない） |

### DB設定変更テスト

| No | テスト内容 | 手順 | 期待結果 |
|----|-----------|------|----------|
| D1 | requires_validation追加 | master_optionsに新ステータス追加、requires_validation=true | 新ステータスでもバリデーション発動 |
| D2 | zero_is_valid追加 | 別カラムにzero_is_valid=true設定 | そのカラムで0が許容される |
| D3 | conditional_exclusion追加 | 新ルール追加 | 新ルールが適用される |

---

## 攻撃ポイント

| 項目 | 確認内容 |
|------|----------|
| 境界値 | 空文字、null、0、空配列、空オブジェクト |
| 型不正 | 数値期待に文字列、配列期待に単一値 |
| SQLインジェクション | column_nameに`'; DROP TABLE --`等 |

---

## テスト環境

- API: http://localhost:8005
- DB: PostgreSQL (local or production)

---

## 確認用SQLクエリ

```sql
-- 新カラム確認
SELECT column_name FROM information_schema.columns
WHERE table_name = 'column_labels'
  AND column_name IN ('valid_none_text', 'zero_is_valid', 'conditional_exclusion', 'special_flag_key');

-- データ確認
SELECT column_name, zero_is_valid, conditional_exclusion, special_flag_key
FROM column_labels
WHERE zero_is_valid = TRUE OR conditional_exclusion IS NOT NULL OR special_flag_key IS NOT NULL;

-- requires_validation確認
SELECT option_value, requires_validation
FROM master_options
WHERE category_id = (SELECT id FROM master_categories WHERE category_code = 'publication_status');
```

---

## 合格基準

- 正常系N1〜N8: 全てパス
- 異常系E1〜E2: 全てパス
- DB設定変更D1〜D3: 全てパス
