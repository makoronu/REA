# テスト依頼：公開時バリデーション機能

## 概要

物件の公開ステータスを「公開」または「会員公開」に変更する際、必須項目が未入力の場合はエラーを返す機能。

---

## テスト対象

| 種別 | ファイル |
|------|---------|
| API | `rea-api/app/api/api_v1/endpoints/properties.py` |
| バリデーター | `rea-api/app/services/publication_validator.py` |
| フロントエンド | `rea-admin/src/components/form/DynamicForm.tsx` |
| エラー処理 | `rea-admin/src/pages/Properties/PropertyEditDynamicPage.tsx` |

---

## 期待動作

### 正常系
1. 必須項目がすべて入力済み → 公開成功
2. 「非公開」への変更 → バリデーションなしで成功
3. 既に「公開」の物件を更新 → バリデーションなしで成功

### 異常系
1. 必須項目が未入力で「公開」 → 400エラー + グループ別未入力項目リスト
2. エラー時フロントエンド → モーダル表示 + 未入力項目一覧

---

## テストシナリオ

### API テスト

#### シナリオ1: 基本バリデーション
```bash
# 必須項目未入力のdetached物件を公開しようとする
curl -X PUT "http://localhost:8005/api/v1/properties/{detached_id}" \
  -H "Content-Type: application/json" \
  -d '{"publication_status": "公開"}'
```
**期待結果:** HTTP 400 + `{"detail": {"message": "...", "groups": {...}}}`

#### シナリオ2: 物件種別による必須項目の違い
- `mansion` → `room_floor`, `total_units` が必須
- `detached` → `room_floor`, `total_units` は不要（条件付き除外）

#### シナリオ3: 特殊フラグ対応
```json
// road_infoが {"no_road_access": true} の場合
// → setback は必須から除外されるべき
```

#### シナリオ4: 「なし」テキストの有効性
```json
// elementary_school = "なし" は有効値として扱われるべき
// elementary_school = "" は無効（バリデーションエラー）
```

### フロントエンド テスト

#### シナリオ5: エラーモーダル表示
1. 物件編集画面を開く
2. 案件ステータスを「販売中」に変更
3. 保存ボタンをクリック
4. **期待:** エラーモーダルが表示される
5. **期待:** グループ別に未入力項目が表示される
6. **期待:** 「詳細を見る」ボタンでモーダル展開

#### シナリオ6: エラー後の操作
1. エラーモーダルを閉じる
2. 未入力項目を入力
3. 再度保存
4. **期待:** 保存成功

#### シナリオ7: ステータス連動
1. 「販売準備」の物件で「公開」ボタンが無効化されているか確認
2. 「販売中」に変更すると「公開」ボタンが有効になるか確認

---

## 境界値・異常系テスト

### 攻撃すべきポイント

| No | テスト内容 | 期待結果 |
|----|-----------|---------|
| 1 | 存在しない物件IDで公開変更 | 404エラー |
| 2 | `publication_status`に不正値（"hoge"） | 400エラーまたは無視 |
| 3 | `property_type`がnullの物件を公開 | 明確なエラーメッセージ |
| 4 | 必須項目に0を入力（management_fee等） | 0は有効値として通過 |
| 5 | 必須項目にスペースのみ入力 | バリデーションエラー |
| 6 | 同時に2つのタブから保存 | データ不整合なし |
| 7 | 保存中にページ離脱 | 警告表示またはデータ保持 |

---

## セキュリティテスト（2026-01-03追加）

### 認証テスト

| No | エンドポイント | テスト内容 | 期待結果 |
|----|--------------|-----------|---------|
| 1 | GET `/api/v1/properties/` | 認証なしでアクセス | 401エラー |
| 2 | GET `/api/v1/properties/{id}` | 認証なしでアクセス | 401エラー |
| 3 | GET `/api/v1/properties/{id}/full` | 認証なしでアクセス | 401エラー |
| 4 | POST `/api/v1/properties/` | 認証なしでアクセス | 401エラー |
| 5 | PUT `/api/v1/properties/{id}` | 認証なしでアクセス | 401エラー |
| 6 | DELETE `/api/v1/properties/{id}` | 認証なしでアクセス | 401エラー |
| 7 | GET `/api/v1/properties/contractors/contacts` | 認証なしでアクセス | 401エラー |

### 入力バリデーションテスト

| No | テスト内容 | 期待結果 |
|----|-----------|---------|
| 1 | PUT で `property_name: null` を送信 | 400エラー（nullにできません） |
| 2 | POST で `property_name: null` を送信 | 400エラー（必須） |
| 3 | PUT で `property_name: "  test  "` を送信 | 前後スペースがトリムされる |
| 4 | POST で `property_name: "  "` を送信 | 400エラー（空白のみは無効） |

### publication_statusバリデーションテスト（2026-01-03追加）

| No | テスト内容 | 期待結果 |
|----|-----------|---------|
| 1 | PUT で `publication_status: null` を送信 | 400エラー「publication_statusをnullにすることはできません」 |
| 2 | PUT で `publication_status: "invalid"` を送信 | 400エラー「publication_statusの値が不正です。有効な値: 公開, 非公開, 会員公開」 |
| 3 | PUT で `publication_status: "公開"` を送信 | 正常処理（公開バリデーション実行） |
| 4 | PUT で `publication_status: "非公開"` を送信 | 正常処理（バリデーションスキップ） |
| 5 | PUT で `publication_status: "会員公開"` を送信 | 正常処理（公開バリデーション実行） |
| 6 | PUT で `publication_status: ""` を送信 | 400エラー（空文字は不正値） |
| 7 | PUT で `publication_status: " 公開 "` を送信 | トリム後「公開」として正常処理 |

---

## 条件付き除外ルールの検証

| 条件 | 除外されるフィールド |
|------|---------------------|
| `use_district` = "指定なし" | `building_coverage_ratio`, `floor_area_ratio` |
| `property_type` = "detached" | `room_floor`, `total_units` |
| `road_info.no_road_access` = true | `setback` |
| `transportation.no_station` = true | 交通関連フィールド |

---

## テスト環境

```bash
# API起動
cd ~/my_programing/REA/rea-api
PYTHONPATH=~/my_programing/REA python -m uvicorn app.main:app --reload --port 8005

# フロント起動
cd ~/my_programing/REA/rea-admin
npm run dev
```

---

## 使用すべきテストデータ

| 物件種別 | 説明 | 用途 |
|---------|------|------|
| `mansion` | 必須42項目 | フルバリデーション確認 |
| `detached` | 条件付き除外あり | 除外ルール確認 |
| `land` | 必須項目なし | バリデーションスキップ確認 |

---

## 発見した問題の報告先

問題を発見した場合は以下のフォーマットで報告：

```markdown
## 発見した問題

### [重大度] タイトル
- **再現手順:**
- **期待結果:**
- **実際の結果:**
- **スクリーンショット:** （あれば）
```
