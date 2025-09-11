# 🤖 Claude専用：REAデータベース情報

> **最適化済みチャンク** - Claude用に情報を最適化

## 📊 重要な事実
- **メインテーブル**: properties（294カラム）
- **分割必要**: 機能別8テーブルに分割推奨
- **マスターテーブル**: 10個（equipment_master等）
- **データベース名**: real_estate_db
- **接続方式**: shared/database.py 統一システム

## 🎯 properties テーブル問題
- **294カラム**: 管理困難・パフォーマンス問題
- **推奨分割**:
  - properties_core（基本情報）
  - properties_images（画像30枚分）
  - properties_pricing（価格・収益）
  - properties_location（住所・交通）
  - properties_building（建物情報）
  - properties_contract（契約情報）
  - properties_land（土地情報）  
  - properties_facilities（周辺施設）

## 🔧 DB接続の統一化（重要）
- **従来**: 各モジュールで個別接続
- **新方式**: `shared/database.py` で統一
- **利点**: エラー激減、保守性向上、コード重複排除

## 💡 よくある質問への回答
**Q: テーブル分割は必要？**
A: 絶対必要。294カラムは非現実的。

**Q: どの順序で分割する？**
A: 1)画像 2)価格 3)住所 4)建物...の順

**Q: データは失われる？**
A: いいえ。分割はデータ移行で安全に実行。

**Q: DB接続エラーが頻発するのは？**
A: shared/database.py を使えば解決。統一された接続システム。
