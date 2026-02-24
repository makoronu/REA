# バッチテスト

## やること
1. URL収集（3ページ分）→ バッチ処理（10件）→ DB保存
2. DB確認: 件数・主要フィールド・NULL率・セッション統計

## 確認項目
- [ ] 10件全てDB保存されている
- [ ] sale_price / addressが全件取得できている
- [ ] listing_idがユニーク
- [ ] scrape_sessionsに記録されている
- [ ] レート制限が効いている

## 異常時
- 0件保存 → unit.mdに戻る
- NULL率高い → selectors.mdに戻る

## 完了条件
- [ ] 10件が正常にDB保存された

## 次 → diff.md
