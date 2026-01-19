# テスト依頼書: 間取り不明・都市計画マッピング・Googleジオコーディング

## 概要
- 日付: 2026-01-19
- 作業者: Claude
- セグメント: SegA（DB）+ SegB（API）

## 変更ファイル

### SegA（DB変更）
| ファイル | 変更内容 |
|---------|---------|
| scripts/migrations/2026-01-19_sega_room_type_and_city_planning.sql | マイグレーションSQL |

### SegB（API変更）
| ファイル | 変更内容 |
|---------|---------|
| rea-api/app/core/config.py | GOOGLE_MAPS_API_KEY, GOOGLE_GEOCODE_URL追加 |
| rea-api/app/api/api_v1/endpoints/geo.py | geocode_google()追加、優先順位変更 |

---

## テスト項目

### 1. 間取り「不明」追加（SegA）

#### 前提条件
- マイグレーションSQL実行済み

#### テスト手順
1. 物件編集画面を開く
2. 建物情報タブの「間取りタイプ」を確認
3. プルダウンに「不明」が表示されることを確認
4. 「不明」を選択して保存
5. 再度開いて「不明」が保持されていることを確認

#### 期待結果
- [x] 「不明」が選択肢に表示される
- [x] 「不明」を選択して保存できる
- [x] 保存後も「不明」が保持される

---

### 2. 都市計画api_aliases（SegA）

#### 前提条件
- マイグレーションSQL実行済み

#### テスト手順
1. 物件編集画面を開く
2. 土地情報タブで「法令調査」ボタンをクリック
3. 都市計画の自動取得が正しく動作することを確認

#### 期待結果
- [x] reinfolib APIからの「市街化区域」が正しくマッピングされる
- [x] 「市街化調整区域」が正しくマッピングされる
- [x] 「非線引区域」が正しくマッピングされる（該当地域の場合）

---

### 3. Googleジオコーディング（SegB）

#### 前提条件
- 環境変数 `GOOGLE_MAPS_API_KEY` が設定済み
- APIサーバー再起動済み

#### テスト手順
1. 物件編集画面を開く
2. 住所を入力（例: 「北海道札幌市中央区北1条西2丁目」）
3. 「住所から座標を取得」ボタンをクリック
4. 緯度・経度が正しく取得されることを確認
5. 曖昧な住所でも精度が向上していることを確認

#### 期待結果
- [x] Googleジオコーディングで座標取得成功
- [x] レスポンスのsourceが「google」
- [x] 従来より精度が向上（特に北海道など地方住所）

#### 異常系テスト
| ケース | 期待動作 |
|-------|---------|
| APIキー未設定 | GSI → Nominatimにフォールバック |
| 無効なAPIキー | GSI → Nominatimにフォールバック |
| 存在しない住所 | 404エラー返却 |

---

## 環境設定

### 環境変数（.env）
```
GOOGLE_MAPS_API_KEY=your_api_key_here
```

### 確認コマンド
```bash
# APIサーバー起動
cd ~/my_programing/REA/rea-api && PYTHONPATH=~/my_programing/REA python -m uvicorn app.main:app --reload --port 8005

# ジオコーディングテスト
curl "http://localhost:8005/api/v1/geo/geocode?address=東京都渋谷区渋谷1-1-1"
```

---

## 攻撃ポイント

| ポイント | 内容 |
|---------|------|
| 境界値 | 住所が3文字未満の場合（min_length=3） |
| 不正入力 | SQL injection風の住所入力 |
| API制限 | Google APIの月間無料枠超過時の動作 |

---

## ロールバック手順

### SegA（DB）
```sql
-- 間取りを元に戻す
UPDATE column_labels
SET options = '1:R,2:K,3:DK,4:LDK,5:SLDK,6:その他'
WHERE column_name = 'room_type' AND table_name = 'building_info';

-- api_aliasesをクリア
UPDATE master_options
SET api_aliases = '{}'
WHERE category_id = (SELECT id FROM master_categories WHERE category_code = 'city_planning');
```

### SegB（API）
- git revertでコード変更を元に戻す
- 環境変数GOOGLE_MAPS_API_KEYを削除
