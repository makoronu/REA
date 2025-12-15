# REA チラシ・マイソク自動生成システム

## 概要

REAの物件データから**チラシ**と**マイソク**を自動生成し、印刷入稿可能なSVG形式で出力するモジュール。

---

## チラシ vs マイソク

| 項目 | チラシ | マイソク |
|------|--------|----------|
| **目的** | 集客・訴求 | 詳細情報提供 |
| **対象** | エンドユーザー | 不動産業者・購入検討者 |
| **デザイン** | 写真大きめ、視覚重視 | 情報網羅、業界標準フォーマット |
| **用途** | ポスティング、店頭 | 業者間共有、内見時配布 |

---

## アーキテクチャ原則

**dev-protocol-prompt.md 準拠**

| 原則 | 実装方針 |
|------|---------|
| **メタデータ駆動** | テンプレート定義・フィールドマッピングはYAML設定ファイルで管理 |
| **設定の一元管理** | 出力仕様は`config/output_settings.yaml`で管理 |
| **共通処理の集約** | フォーマット関数は`shared/format_utils.py`に集約 |
| **DRY原則** | 重複実装禁止、既存共通処理を最大活用 |

---

## 処理フロー

```
┌─────────────┐
│  REA DB     │
│ (properties,│
│  land_info, │
│  building,  │
│  images)    │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────────┐
│ field_      │────▶│ shared/          │
│ mappings.   │     │ format_utils.py  │
│ yaml        │     │ (価格、面積変換)  │
└──────┬──────┘     └──────────────────┘
       │
       ▼
┌─────────────┐     ┌──────────────────┐
│ templates.  │────▶│ generators/      │
│ yaml        │     │ (maisoku.py,     │
│             │     │  chirashi.py)    │
└──────┬──────┘     └──────────────────┘
       │
       ▼
┌─────────────┐
│ SVG出力     │
│ (イラレ     │
│  編集可能)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 印刷屋入稿  │
└─────────────┘
```

---

## ディレクトリ構造

```
rea-flyer/
├── README.md                     # このファイル
├── config/
│   ├── output_settings.yaml      # 出力仕様（塗り足し、DPI等）
│   ├── templates.yaml            # テンプレート定義
│   └── field_mappings.yaml       # DB→出力フィールドマッピング
├── templates/
│   ├── maisoku/                  # マイソクSVGテンプレート
│   │   ├── land.svg              # 土地用
│   │   ├── detached.svg          # 戸建用
│   │   ├── apartment.svg         # マンション用
│   │   └── investment.svg        # 収益物件用
│   └── chirashi/                 # チラシSVGテンプレート
│       ├── single.svg            # 1件用（A4全面）
│       ├── dual.svg              # 2件用（上下分割）
│       └── grid.svg              # 4件用（グリッド）
├── generators/
│   ├── __init__.py
│   ├── base.py                   # 基底クラス
│   ├── maisoku.py                # マイソク生成
│   └── chirashi.py               # チラシ生成
├── utils/
│   ├── __init__.py
│   └── svg_builder.py            # SVG操作ユーティリティ
└── tests/
    ├── test_maisoku.py
    └── test_chirashi.py
```

---

## 設定ファイル

### output_settings.yaml

出力仕様を一元管理。ハードコーディング禁止。

```yaml
output:
  format: svg           # 出力形式
  color_mode: cmyk      # 色空間（印刷用）
  bleed_mm: 3           # 塗り足し
  dpi: 350              # 解像度
  font_family: "Noto Sans JP"

paper_sizes:
  a4:
    width_mm: 210
    height_mm: 297
  b4:
    width_mm: 257
    height_mm: 364
```

### templates.yaml

テンプレート定義（メタデータ駆動の核心）

```yaml
maisoku:
  land:
    template: maisoku/land.svg
    property_types: [land]
    sections:
      - name: header
        fields: [property_name, price, price_per_tsubo]
      - name: location
        fields: [address, access]
      - name: land_info
        fields: [land_area, land_area_tsubo, use_district]

chirashi:
  single:
    template: chirashi/single.svg
    max_properties: 1
    layout: full_page
```

### field_mappings.yaml

DB列→出力フィールドのマッピング。column_labelsと連携。

```yaml
fields:
  price:
    source: properties.sale_price
    label_source: column_labels    # 日本語ラベル取得元
    format: price_man              # shared/format_utils.py の関数名

  land_area:
    source: land_info.land_area
    label_source: column_labels
    format: area_with_tsubo        # ㎡（坪）形式
```

---

## 共通処理（shared/format_utils.py）

フォーマット関数を集約。チラシ以外でも使用可能。

```python
def format_price_man(price: int) -> str:
    """価格を万円表示（1億以上は億円併記）

    Examples:
        >>> format_price_man(35000000)
        '3,500万円'
        >>> format_price_man(150000000)
        '1億5,000万円'
    """

def format_area_with_tsubo(sqm: float) -> str:
    """面積を㎡（坪）形式で表示

    Examples:
        >>> format_area_with_tsubo(100.5)
        '100.50㎡（30.40坪）'
    """

def format_building_age(construction_date: date) -> str:
    """築年数を表示

    Examples:
        >>> format_building_age(date(2010, 3, 1))
        '築15年（平成22年築）'
    """

def format_wareki(dt: date) -> str:
    """西暦→和暦変換"""

def format_road_access(direction: str, width: float) -> str:
    """接道状況を表示

    Examples:
        >>> format_road_access('south', 6.0)
        '南側6.0m公道'
    """
```

---

## APIエンドポイント

```
POST /api/v1/flyer/maisoku/{property_id}
  Request: なし（property_typeから自動テンプレート選択）
  Response: SVGファイル（Content-Type: image/svg+xml）

POST /api/v1/flyer/chirashi
  Request: { "property_ids": [1, 2, 3], "layout": "grid" }
  Response: SVGファイル

GET /api/v1/flyer/templates
  Response: { "maisoku": [...], "chirashi": [...] }

GET /api/v1/flyer/preview/{property_id}
  Response: PNGファイル（プレビュー用）
```

---

## 使用ライブラリ

| ライブラリ | 用途 |
|-----------|------|
| svgwrite | SVG生成 |
| cairosvg | SVG→PNG/PDF変換 |
| Pillow | 画像処理（写真リサイズ） |
| PyYAML | 設定ファイル読み込み |

---

## 開発手順

### 1. 環境構築

```bash
cd ~/my_programing/REA
pip install svgwrite cairosvg Pillow PyYAML
```

### 2. 設定ファイル作成

```bash
mkdir -p rea-flyer/config
# output_settings.yaml, templates.yaml, field_mappings.yaml を作成
```

### 3. テンプレート作成

1. Illustratorでデザイン
2. SVG形式で保存
3. プレースホルダーを挿入（例: `{{property_name}}`）
4. `templates/` に配置

### 4. 生成テスト

```bash
cd ~/my_programing/REA
PYTHONPATH=. python -m pytest rea-flyer/tests/ -v
```

---

## テンプレートSVGの規約

### プレースホルダー形式

```svg
<text id="property_name">{{property_name}}</text>
<text id="price">{{price}}</text>
<image id="main_photo" href="{{main_photo_url}}" />
```

### ID命名規則

- `field_mappings.yaml` のフィールド名と一致させる
- スネークケース統一

### 画像配置

```svg
<!-- 写真エリア -->
<rect id="photo_placeholder_1" x="10" y="10" width="180" height="120" />
```

---

## テスト方針

### 単体テスト

- `format_utils.py` の各関数
- YAML設定ファイルのバリデーション

### 結合テスト

- 実物件データでSVG生成
- 生成SVGのバリデーション（必須フィールド埋まっているか）

### 実務テスト

- 印刷屋に入稿して確認
- 色味、サイズ、塗り足しの確認

---

## 関連ドキュメント

- [ROADMAP.md](../ROADMAP.md) - フェーズ4.7
- [dev-protocol-prompt.md](../../dev-protocol-prompt.md) - 開発プロトコル
- [shared/constants.py](../../shared/constants.py) - 既存共通処理

---

## 更新履歴

| 日付 | 内容 |
|------|------|
| 2025-12-15 | 初版作成（概念設計） |
