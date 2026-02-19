# テスト依頼書: Seg 14b - Core API geo.py デッドコード削除

**日付:** 2026-02-19
**対象コミット:** (未コミット)

---

## テスト対象

| ファイル | 変更内容 |
|----------|----------|
| rea-api/.../geo.py | GET 11エンドポイント+ヘルパー5個+スキーマ9個削除。POST 3個のみ残す |

---

## 変更概要

Geo API (:8007) への移行完了に伴い、Core API (:8005) のgeo.pyから読み取り専用のGETエンドポイントを全削除。nginxルーティングにより既にGETはGeo APIに転送されていたため、Core API側はデッドコードとなっていた。

- 削除: GET 11エンドポイント、ヘルパー関数5個、スキーマ9個
- 残存: POST 3エンドポイント（set-nearest-stations, set-school-districts, set-zoning）
- 1,290行 → 359行（-931行）

---

## テストケース

### 正常系（POST エンドポイント）

| # | テスト | 手順 | 期待結果 |
|---|--------|------|----------|
| 1 | 最寄駅自動設定 | POST /api/v1/geo/properties/{id}/set-nearest-stations | 最寄駅がtransportationに保存される |

### 正常系（GET エンドポイント - Geo API経由）

| # | テスト | 手順 | 期待結果 |
|---|--------|------|----------|
| 2 | 最寄駅検索 | GET /api/v1/geo/nearest-stations?lat=43.8&lng=143.9 | Geo API経由で駅リスト返却 |
| 3 | ジオコーディング | GET /api/v1/geo/geocode?address=北見市 | Geo API経由で座標返却 |
| 4 | 凡例 | GET /api/v1/geo/zoning/legend | 14件返却 |

### 攻撃ポイント

| # | 観点 | 確認内容 |
|---|------|----------|
| 5 | レグレッション | フロントエンドの全geo機能が正常動作すること |
| 6 | POST経路確認 | nginx経由でPOSTがCore APIに到達すること |
| 7 | Core API起動 | geo.pyのimportエラーなく起動すること |

---

## テスト環境

- Core API: `cd ~/my_programing/REA/rea-api && PYTHONPATH=~/my_programing/REA python -m uvicorn app.main:app --reload --port 8005`
- Geo API: `cd ~/my_programing/REA/rea-geo && PYTHONPATH=~/my_programing/REA python -m uvicorn app.main:app --reload --port 8007`
- フロント: `cd ~/my_programing/REA/rea-admin && npm run dev`
