# バッチテスト

## やること
1. **全物件種別で**URL収集（各1ページ分）→ バッチ処理（各3件）→ DB保存
2. DB確認: 件数・主要フィールド・NULL率・セッション統計

## 確認項目
- [ ] **各種別（tochi/kodate/mansion）で**最低1件DB保存されている
- [ ] sale_price / addressが全件取得できている
- [ ] listing_idがユニーク
- [ ] scrape_sessionsに記録されている
- [ ] レート制限が効いている

## 異常時
- 0件保存 → unit.mdに戻る
- 特定種別だけ0件 → 物件種別コードを再確認（html_analysis.md Step 4）
- NULL率高い → selectors.mdに戻る

## 完了条件
- [ ] 全物件種別で正常にDB保存された

## 次 → diff.md
