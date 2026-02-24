# REA変換（Converter）

## やること
1. rea_converter.py: 正規化済み中間形式→master_optionsコード値に変換
2. field_map.py: 中間フィールド名→DBカラム名の対応表

## 変換内容
- option_value→option_code逆引き（api_aliasesも対象）
- rea_N形式→数値化
- フィールド名変換（price→sale_price等）
- データ型変換（INTEGER/DECIMAL/JSONB/TEXT）

## ルール
- マッチしない値はNone + WARNINGログ（例外投げない）
- 企画書 §5.3 のスキーマ対応表に準拠

## 完了条件
- [ ] 中間形式を渡すとREAスキーマのdictが返る
- [ ] master_optionsコード値への変換が正しい
- [ ] 全ファイル500行以下

## 次 → registrar.md
