# HTML構造調査

## 前提
- **Seleniumヘッドレスでページを開き、driver.page_sourceからHTMLを取得せよ**
- curlやrequestsでのHTML取得は禁止（ボットガードで正しいHTMLが返らない）

## やること
1. Seleniumで検索結果ページ（一覧）を開き、page_sourceを保存・調査
   - 物件カード要素、リンク要素、ページネーション要素
2. Seleniumで物件詳細ページを開き、page_sourceを保存・調査
   - タイトル、価格、情報テーブル（dl or table）、会社情報
3. 物件種別ごとにサンプル取得（土地・戸建・マンション）
4. スクリーンショットを各ページで保存

## 完了条件
- [ ] 一覧/詳細ページの構造を把握した
- [ ] テーブル形式を特定した（dl or table）
- [ ] サンプルHTMLを保存した

## 次 → selectors.md
