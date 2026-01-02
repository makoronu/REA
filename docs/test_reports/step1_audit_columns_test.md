# テストレポート: Step 1 監査カラム追加

**作成日**: 2026-01-02
**担当**: Claude
**ステータス**: ローカル実装完了・テスト依頼

---

## 変更概要

9テーブルに監査用カラムを追加しました。

| カラム名 | 型 | 用途 |
|---------|-----|------|
| created_by | VARCHAR(100) | 作成者（現在は未設定） |
| updated_by | VARCHAR(100) | 更新者（現在は未設定） |
| deleted_at | TIMESTAMPTZ | 論理削除日時（現在は未使用） |

### 対象テーブル

1. properties
2. building_info
3. land_info
4. property_images
5. property_equipment
6. property_locations
7. property_registries
8. column_labels
9. equipment_master

---

## テスト項目

### 1. 物件一覧画面

| # | 確認項目 | 期待結果 | 結果 |
|---|---------|---------|------|
| 1-1 | 物件一覧が表示される | 正常に一覧表示 | □ |
| 1-2 | 検索が動作する | 検索結果が表示 | □ |
| 1-3 | フィルタが動作する | フィルタ結果が表示 | □ |
| 1-4 | ソートが動作する | ソート結果が表示 | □ |

### 2. 物件詳細画面

| # | 確認項目 | 期待結果 | 結果 |
|---|---------|---------|------|
| 2-1 | 物件詳細が表示される | 全タブ正常表示 | □ |
| 2-2 | 基本情報タブ | データ表示OK | □ |
| 2-3 | 建物情報タブ | データ表示OK | □ |
| 2-4 | 土地情報タブ | データ表示OK | □ |

### 3. 物件編集

| # | 確認項目 | 期待結果 | 結果 |
|---|---------|---------|------|
| 3-1 | 編集画面が開く | 正常に開く | □ |
| 3-2 | データ保存 | 保存成功 | □ |
| 3-3 | 保存後の再表示 | 変更が反映 | □ |

### 4. 物件新規作成

| # | 確認項目 | 期待結果 | 結果 |
|---|---------|---------|------|
| 4-1 | 新規作成画面が開く | 正常に開く | □ |
| 4-2 | 必須項目入力して保存 | 保存成功 | □ |
| 4-3 | 一覧に新規物件が表示 | 表示される | □ |

### 5. APIレスポンス確認

| # | 確認項目 | 期待結果 | 結果 |
|---|---------|---------|------|
| 5-1 | GET /api/v1/properties/ | 新カラム含む（null値） | □ |
| 5-2 | GET /api/v1/properties/{id}/full | 新カラム含む（null値） | □ |

---

## 確認用コマンド

### API動作確認

```bash
# 物件一覧取得
curl -s "http://localhost:8005/api/v1/properties/?limit=3" | python3 -m json.tool

# 物件詳細取得（ID=2480）
curl -s "http://localhost:8005/api/v1/properties/2480/full" | python3 -m json.tool

# 新カラム確認
curl -s "http://localhost:8005/api/v1/properties/2480" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('created_by:', d.get('created_by'))
print('updated_by:', d.get('updated_by'))
print('deleted_at:', d.get('deleted_at'))
"
```

### DB直接確認

```sql
-- 新カラム存在確認
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'properties'
  AND column_name IN ('created_by', 'updated_by', 'deleted_at');

-- データ件数確認
SELECT
  (SELECT COUNT(*) FROM properties) as properties,
  (SELECT COUNT(*) FROM building_info) as building_info,
  (SELECT COUNT(*) FROM land_info) as land_info;
```

---

## 既知の制限事項

1. **created_by / updated_by は現在未設定**
   - Step 2以降でアプリケーション側の対応が必要
   - 現時点では全てNULL

2. **deleted_at は現在未使用**
   - Step 2で論理削除対応時に使用開始

3. **geomカラムなし（ローカル環境のみ）**
   - ローカルにPostGIS未インストールのため
   - 本番環境には影響なし

---

## テスト結果記入欄

**テスト実施者**:
**テスト実施日**:
**テスト環境**: ローカル / 本番

### 総合判定

- [ ] 全項目OK → 本番デプロイ可
- [ ] 問題あり → 下記に詳細記載

### 問題詳細（あれば）

```
問題箇所:
再現手順:
エラー内容:
```

---

## 次のステップ

1. テストOKの場合 → 本番デプロイ
2. 本番デプロイ後 → Step 2（論理削除対応）へ進む
