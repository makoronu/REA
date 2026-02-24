# パーサー実装

## やること
1. parser.py: HTML→生データdict変換（**正規化はしない**）
2. selectors.py: CSSセレクタ定義（1_surveyで確定済み）
3. field_mapping.py: サイトラベル→中間フィールド名の対応表

## ルール
- 正規化は共通normalizers担当（責務分離）
- 要素不在時はNone（例外投げない）
- parser.py 300行以下

## 完了条件
- [ ] 種別ごとにサンプルHTMLから全フィールド抽出できる
- [ ] listing_idが正しく抽出できる

## 次 → mapping.md
