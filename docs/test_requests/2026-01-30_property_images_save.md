# テスト依頼書: 物件画像保存機能

## 検証日
2026-01-30

## 対象ファイル

### API（新規）
- `rea-api/app/api/api_v1/endpoints/images.py`

### API（修正）
- `rea-api/app/api/api_v1/api.py` - ルーター登録
- `rea-api/app/crud/generic.py` - get_fullにproperty_images追加

### フロントエンド（修正）
- `rea-admin/src/services/propertyService.ts` - 画像API呼び出し追加
- `rea-admin/src/pages/Properties/PropertyEditDynamicPage.tsx` - 画像保存処理追加

---

## テスト項目

### 1. 画像アップロード（正常系）

| # | 操作 | 期待結果 |
|---|------|---------|
| 1-1 | 物件編集画面で画像タブを開く | 画像一覧が表示される（既存画像がある場合） |
| 1-2 | 画像をドラッグ&ドロップでアップロード | プレビューが表示される |
| 1-3 | 画像の種別を「外観」に変更 | 選択が即時反映される |
| 1-4 | キャプションを入力 | 入力が即時反映される |
| 1-5 | 保存ボタンをクリック | 「保存しました」表示、画像がDBに保存される |
| 1-6 | ページをリロード | アップロードした画像が表示される |

### 2. 画像メタデータ更新（正常系）

| # | 操作 | 期待結果 |
|---|------|---------|
| 2-1 | 既存画像の種別を変更 | 選択が反映される |
| 2-2 | 既存画像のキャプションを変更 | 入力が反映される |
| 2-3 | 既存画像の表示順を変更（↑↓ボタン） | 順番が変わる |
| 2-4 | 保存ボタンをクリック | メタデータがDBに反映される |

### 3. 画像削除（正常系）

| # | 操作 | 期待結果 |
|---|------|---------|
| 3-1 | 既存画像の削除ボタンをクリック | 画像が一覧から消える |
| 3-2 | 保存ボタンをクリック | 画像がDB上で論理削除される |

### 4. 異常系

| # | 操作 | 期待結果 |
|---|------|---------|
| 4-1 | 10MBを超える画像をアップロード | エラーメッセージ表示 |
| 4-2 | 非画像ファイル（.txt等）をアップロード | エラーメッセージ表示 |
| 4-3 | 未ログイン状態でAPI直接呼び出し | 401エラー |

### 5. 新規物件での画像アップロード

| # | 操作 | 期待結果 |
|---|------|---------|
| 5-1 | 新規物件作成画面で画像をアップロード | プレビュー表示 |
| 5-2 | 物件名を入力して保存 | 物件作成後、画像も保存される |
| 5-3 | 作成された物件の編集画面を開く | アップロードした画像が表示される |

---

## 攻撃ポイント

1. **境界値**: 0枚、1枚、30枚（上限）の画像
2. **不正入力**: 特殊文字を含むファイル名
3. **権限**: 他人の物件への画像アップロード試行
4. **同時実行**: 同じ物件に複数人が同時に画像保存

---

## テスト環境

```bash
# API起動
cd ~/my_programing/REA/rea-api && PYTHONPATH=~/my_programing/REA python -m uvicorn app.main:app --reload --port 8005

# フロント起動
cd ~/my_programing/REA/rea-admin && npm run dev
```

---

## 確認SQL

```sql
-- 特定物件の画像一覧
SELECT id, property_id, image_type, file_url, display_order, caption, is_public, deleted_at
FROM property_images
WHERE property_id = [物件ID]
ORDER BY display_order;

-- 画像アップロード数（直近1時間）
SELECT COUNT(*) FROM property_images
WHERE created_at > NOW() - INTERVAL '1 hour';
```

---

## 補足

- 画像ファイルは `uploads/properties/{property_id}/` に保存される
- 削除は論理削除（deleted_atを設定）
- image_typeの値は文字列（"0"=未分類, "2"=外観 等）
