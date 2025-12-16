# 不動産情報ライブラリAPI クライアント

国土交通省の不動産情報ライブラリAPIと連携するクライアントモジュール。

## 概要

物件の緯度経度から法令制限・ハザード情報を自動取得し、重説作成を支援。

## 利用可能なAPI

| コード | 名称 | 用途 |
|--------|------|------|
| XKT002 | 用途地域 | 建ぺい率・容積率 |
| XKT014 | 防火・準防火地域 | 防火規制 |
| XKT026 | 洪水浸水想定区域 | 水害リスク |
| XKT027 | 高潮浸水想定区域 | 高潮リスク |
| XKT028 | 津波浸水想定 | 津波リスク |
| XKT029 | 土砂災害警戒区域 | 土砂災害リスク |
| XKT003 | 立地適正化計画 | 居住誘導区域等 |
| XKT024 | 地区計画 | 地区計画有無 |
| XKT030 | 都市計画道路 | 計画道路有無 |
| XIT001 | 価格情報 | 取引価格・成約価格 |

## 環境変数

```env
REINFOLIB_API_KEY=your_api_key_here
```

## 使用方法

### Pythonコード内で使用

```python
from app.services.reinfolib import ReinfLibClient

client = ReinfLibClient()

# 全規制情報を一括取得
regulations = client.get_all_regulations(lat=35.6812, lng=139.7671)

# 用途地域のみ取得
use_area = client.get_regulation_at_point("XKT002", lat=35.6812, lng=139.7671)

# 価格情報取得
prices = client.get_price_info(year=2023, area="01")  # 01=北海道
```

### APIエンドポイント

```
GET /api/v1/reinfolib/regulations?lat=35.6812&lng=139.7671
  → 全規制情報を取得

GET /api/v1/reinfolib/use-area?lat=35.6812&lng=139.7671
  → 用途地域を取得

GET /api/v1/reinfolib/hazard?lat=35.6812&lng=139.7671
  → ハザード情報（洪水・土砂・津波・高潮）を取得

GET /api/v1/reinfolib/tile/XKT002?lat=35.6812&lng=139.7671
  → MAP表示用GeoJSONを取得

GET /api/v1/reinfolib/price?year=2023&area=01
  → 価格情報を取得

GET /api/v1/reinfolib/apis
  → 利用可能API一覧
```

## ファイル構成

```
reinfolib/
├── __init__.py      # モジュール公開
├── client.py        # APIクライアント本体
├── tile_utils.py    # タイル座標変換ユーティリティ
└── README.md        # このファイル
```

## 設計原則

- **メタデータ駆動**: API定義は`API_DEFINITIONS`で管理、ハードコード禁止
- **設定一元管理**: APIキーは`.env`で管理
- **DRY原則**: タイル座標変換は`tile_utils.py`に集約

## 参考リンク

- [不動産情報ライブラリ](https://www.reinfolib.mlit.go.jp/)
- [APIマニュアル](https://www.reinfolib.mlit.go.jp/help/apiManual/)
