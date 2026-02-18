# テスト依頼書: Seg C-2 - 外部URL定数集約

**日付:** 2026-02-17
**対象コミット:** (未コミット)

---

## テスト対象

| ファイル | 変更内容 |
|----------|----------|
| rea-admin/src/constants.ts | MAP_TILES, LEAFLET_ICON_URLS, EXTERNAL_API 追加 |
| rea-admin/src/components/regulations/RegulationMap.tsx | GSIタイルURL→MAP_TILES.GSI_PALE |
| rea-admin/src/pages/ZoningMap/ZoningMapPage.tsx | GSIタイルURL→MAP_TILES.GSI_PALE |
| rea-admin/src/components/form/ZoningMapField.tsx | GSIタイルURL→MAP_TILES.GSI_PALE |
| rea-admin/src/components/form/LocationField.tsx | OSMタイルURL→MAP_TILES.OSM、LeafletアイコンURL→LEAFLET_ICON_URLS |
| rea-admin/src/services/geoService.ts | zipcloud URL→EXTERNAL_API.ZIPCLOUD |

---

## 変更概要

ハードコードされた外部URL（地図タイル・Leafletアイコン・郵便番号API）を定数ファイルに集約。
ロジックの変更なし。URL値の変更なし。import追加と定数参照への置換のみ。

---

## テストケース

### 正常系 - 地図表示

| # | テスト | 手順 | 期待結果 |
|---|--------|------|----------|
| 1 | 法令制限MAP | 物件編集→法令制限タブ→MAP表示 | 地理院タイルが正常表示 |
| 2 | 用途地域MAP（全体） | /zoning-mapページを開く | 地理院タイルが正常表示 |
| 3 | 用途地域MAP（物件内） | 物件編集→所在地→法令調査→MAP表示 | 地理院タイルが正常表示 |
| 4 | 所在地MAP | 物件編集→所在地→地図表示 | OSMタイルが正常表示 |
| 5 | 地図マーカー | 所在地MAPでマーカー表示 | Leafletデフォルトマーカーアイコンが表示 |

### 正常系 - 外部API

| # | テスト | 手順 | 期待結果 |
|---|--------|------|----------|
| 6 | 郵便番号検索 | 物件編集→郵便番号入力 | 住所が自動補完される |

### 攻撃ポイント

| # | 観点 | 確認内容 |
|---|------|----------|
| 7 | レグレッション | 全地図表示が変更前と同一であること |
| 8 | TypeScript | ビルドエラーなし（tsc --noEmit通過済み） |

---

## テスト環境

- フロント: `cd ~/my_programing/REA/rea-admin && npm run dev`
