# テスト依頼書: Seg 14a - Geo API新サービス作成

**日付:** 2026-02-17
**対象コミット:** (未コミット)

---

## テスト対象

| ファイル | 変更内容 |
|----------|----------|
| rea-geo/ (新規) | Geo API独立サービス（読み取り専用11エンドポイント） |
| deploy.yml | rea-geo再起動ステップ追加 |
| server/rea-geo.service | systemdサービス定義 |
| server/nginx-geo-location.conf | nginx locationブロック（GET→:8007, POST→:8005） |

---

## 変更概要

Core APIのgeo.pyから読み取り専用11エンドポイントを独立したGeo APIサービス（:8007）として分離。並行稼働方式で、既存のCore API側のgeo.pyはそのまま残す。nginx設定でGETリクエストをGeo APIに、POSTリクエスト（書き込み）をCore APIにルーティング。

---

## テストケース

### 正常系（Geo APIサービス :8007）

| # | テスト | 手順 | 期待結果 |
|---|--------|------|----------|
| 1 | ヘルスチェック | curl http://localhost:8007/health | {"status":"healthy","service":"geo"} |
| 2 | 最寄駅検索 | curl http://localhost:8007/api/v1/geo/nearest-stations?lat=43.8&lng=143.9 | 駅リスト返却 |
| 3 | ジオコーディング | curl http://localhost:8007/api/v1/geo/geocode?address=北見市北進町 | 緯度経度返却 |
| 4 | 学区判定 | curl http://localhost:8007/api/v1/geo/school-districts?lat=43.8&lng=143.9 | 学校候補返却 |
| 5 | バス停検索 | curl http://localhost:8007/api/v1/geo/nearest-bus-stops?lat=43.8&lng=143.9 | バス停リスト返却 |
| 6 | 施設検索 | curl http://localhost:8007/api/v1/geo/nearest-facilities-by-category?lat=43.8&lng=143.9 | カテゴリ別施設返却 |
| 7 | 用途地域 | curl http://localhost:8007/api/v1/geo/zoning?lat=43.8&lng=143.9 | 用途地域返却 |
| 8 | 都市計画 | curl http://localhost:8007/api/v1/geo/urban-planning?lat=43.8&lng=143.9 | 都市計画区域返却 |
| 9 | 凡例 | curl http://localhost:8007/api/v1/geo/zoning/legend | 14件の凡例返却 |

### nginx経由（本番URL）

| # | テスト | 手順 | 期待結果 |
|---|--------|------|----------|
| 10 | GET経由 | https://realestateautomation.net/api/v1/geo/geocode?address=北見市 | Geo API(:8007)経由で応答 |
| 11 | POST経由 | POST https://realestateautomation.net/api/v1/geo/properties/1/set-nearest-stations | Core API(:8005)経由で応答 |

### 攻撃ポイント

| # | 観点 | 確認内容 |
|---|------|----------|
| 12 | レグレッション | フロントエンドの全geo機能が正常動作すること |
| 13 | Core API | Core API側のgeo.pyも引き続き動作すること（並行稼働） |
| 14 | 直接アクセス | 外部からhttp://サーバーIP:8007/ にアクセス不可 |

---

## デプロイ手順

```bash
# 1. git push + GitHub Actions
# 2. サーバーでsystemdサービス設定
sudo cp /opt/REA/rea-geo/server/rea-geo.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rea-geo
sudo systemctl start rea-geo

# 3. nginx設定更新（locationブロック追加）
# rea-geo/server/nginx-geo-location.conf の内容を
# /etc/nginx/sites-enabled/rea に追加
sudo nginx -t && sudo systemctl reload nginx

# 4. 確認
curl http://localhost:8007/health
```

---

## テスト環境

- Geo API: `cd ~/my_programing/REA/rea-geo && PYTHONPATH=~/my_programing/REA python -m uvicorn app.main:app --reload --port 8007`
- Core API: `cd ~/my_programing/REA/rea-api && PYTHONPATH=~/my_programing/REA python -m uvicorn app.main:app --reload --port 8005`
- フロント: `cd ~/my_programing/REA/rea-admin && npm run dev`
