# テスト依頼書: min_selections バリデーション

## 作成日
2026-01-11

## 概要
multi_selectフィールド（複数選択チェックボックス）で「最低N個選択必須」のバリデーションを追加。

## 変更ファイル

| ファイル | 変更内容 |
|---------|---------|
| `scripts/migrations/add_min_selections.sql` | column_labels.min_selections カラム追加 |
| `rea-api/app/services/publication_validator.py` | get_min_selections関数追加、is_valid_value修正 |

## DB変更

```sql
ALTER TABLE column_labels ADD COLUMN min_selections INTEGER DEFAULT NULL;

-- input_type='multi_select' かつ required_for_publication 設定済みフィールドに min_selections=1 を設定
UPDATE column_labels SET min_selections = 1
WHERE input_type = 'multi_select' AND required_for_publication IS NOT NULL;
```

## テスト項目

### 1. DBマイグレーション確認

- [ ] min_selectionsカラムが追加されていること
- [ ] multi_selectフィールドにmin_selections=1が設定されていること

```sql
-- 確認クエリ
SELECT column_name, input_type, min_selections, required_for_publication
FROM column_labels
WHERE min_selections IS NOT NULL;
```

### 2. 公開バリデーション動作確認

#### 正常系

| No | 条件 | 期待結果 |
|----|------|---------|
| 1 | multi_selectフィールドで1つ以上選択 | バリデーションPASS |
| 2 | 非multi_selectフィールド | 従来通り動作 |
| 3 | min_selections未設定フィールド | 従来通り1以上でPASS |

#### 異常系

| No | 条件 | 期待結果 |
|----|------|---------|
| 1 | multi_selectフィールドで0個選択 | バリデーションエラー（「未入力」表示） |
| 2 | multi_selectフィールドがnull | バリデーションエラー |

### 3. 後方互換性確認

- [ ] min_selections=NULLのフィールドは従来通り動作すること
- [ ] 既存の公開バリデーションが壊れていないこと

## 攻撃ポイント

| ポイント | 確認内容 |
|---------|---------|
| 境界値 | min_selections=0, 1, 2 での動作 |
| 型エラー | min_selectionsに文字列が入った場合（DB制約で弾かれる） |
| 権限 | 公開バリデーションは全ユーザーで動作 |

## テスト環境

- API: http://localhost:8005
- フロント: http://localhost:5173
- 物件編集ページで「公開」または「会員公開」を選択して保存

## 備考

- 対象フィールド例: `use_district`（用途地域）、`city_planning`（都市計画区域）
- DBマイグレーション実行後にテスト可能
