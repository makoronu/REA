# rea-flyer

REA チラシ・マイソク自動生成モジュール

## 概要

REAの物件データからチラシとマイソクを自動生成し、印刷入稿可能なSVG形式で出力する。

## ディレクトリ構造

```
rea-flyer/
├── README.md                 # このファイル
├── config/
│   ├── output_settings.yaml  # 出力仕様
│   ├── templates.yaml        # テンプレート定義
│   └── field_mappings.yaml   # フィールドマッピング
├── templates/
│   ├── maisoku/              # マイソクSVGテンプレート
│   └── chirashi/             # チラシSVGテンプレート
├── generators/
│   ├── __init__.py
│   ├── base.py               # 基底クラス
│   ├── maisoku.py            # マイソク生成
│   └── chirashi.py           # チラシ生成
├── utils/
│   ├── __init__.py
│   └── svg_builder.py        # SVG操作
└── tests/
    ├── test_maisoku.py
    └── test_chirashi.py
```

## 依存ライブラリ

```bash
pip install svgwrite cairosvg Pillow PyYAML
```

## 使用方法

### Python直接呼び出し

```python
import sys
sys.path.insert(0, 'rea-flyer')
from generators import MaisokuGenerator

generator = MaisokuGenerator()
svg_content = generator.generate(property_data)  # dict形式の物件データ
```

### API経由

```bash
# マイソク生成（SVG）
curl -X POST "http://localhost:8005/api/v1/flyer/maisoku/{property_id}?format=svg"

# マイソク生成（PNG）
curl -X POST "http://localhost:8005/api/v1/flyer/maisoku/{property_id}?format=png"

# プレビュー（PNG）
curl "http://localhost:8005/api/v1/flyer/maisoku/{property_id}/preview"

# テンプレート一覧
curl "http://localhost:8005/api/v1/flyer/templates"
```

## 実装状況

| 機能 | 状態 | 備考 |
|------|------|------|
| マイソク（土地） | ✅ | templates/maisoku/land.svg |
| マイソク（戸建） | 🔲 | 動的生成で対応可 |
| マイソク（マンション） | 🔲 | 動的生成で対応可 |
| マイソク（収益） | 🔲 | 動的生成で対応可 |
| チラシ（1件） | 🔲 | 未実装 |
| チラシ（複数件） | 🔲 | 未実装 |
| PNG変換 | ✅ | cairosvg使用 |
| PDF変換 | 🔲 | 未実装 |

## 設計ドキュメント

- 詳細設計: `docs/flyer/README.md`
- ロードマップ: `docs/ROADMAP.md` フェーズ4.7

## 開発プロトコル

`dev-protocol-prompt.md` を必ず参照すること。

- メタデータ駆動: テンプレート定義はYAMLで管理
- 設定一元管理: 出力仕様はconfig/で管理
- 共通処理集約: フォーマット関数はshared/format_utils.pyに配置
