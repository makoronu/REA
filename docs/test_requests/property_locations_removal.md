# property_locations削除 テスト依頼書

**作成日:** 2026-01-03
**実装者:** Claude
**対象:** property_locationsテーブル廃止・propertiesへの住所一本化

---

## 変更概要

重複していたproperty_locationsテーブルを廃止し、propertiesテーブルで住所を一元管理。

### 変更理由
1. propertiesとproperty_locationsで住所カラムが重複（8カラム）
2. property_locationsには7件しかデータがなく、全てpropertiesと同一
3. property_locationsはcolumn_labelsに未登録（メタデータ駆動外）
4. 紛らわしさ解消のため削除

---

## 変更ファイル

| ファイル | 変更内容 |
|----------|----------|
| generic.py | property_locations読み書きロジック削除 |
| properties.py | 論理削除リストからproperty_locations削除 |
| zoho.py | ALLOWED_RELATED_TABLESからproperty_locations削除 |
| tables.py | PROPERTY_TABLESからproperty_locations削除 |
| tables.ts | PROPERTY_TABLESからproperty_locations削除 |
| arch.md | テーブル構成図更新 |
| traps.md | property_locations罠削除 |
| TABLE_REDESIGN_PROPOSAL.md | ステータス更新（廃止） |

### 新規作成

| ファイル | 内容 |
|----------|------|
| drop_property_locations.sql | テーブル削除マイグレーション |

---

## テスト手順

### 1. 物件一覧表示
- [ ] 物件一覧が正常に表示される
- [ ] フィルタ（販売状況、公開状態）が動作する

### 2. 物件編集
- [ ] 物件編集画面が正常に表示される
- [ ] 住所情報（郵便番号、都道府県、市区町村、番地）が表示される
- [ ] 住所情報を編集・保存できる
- [ ] 緯度・経度が保存される

### 3. 物件新規作成
- [ ] 新規物件を作成できる
- [ ] 住所情報を入力できる

### 4. 物件削除
- [ ] 物件を削除できる（論理削除）

### 5. ZOHO連携
- [ ] ZOHO同期ボタンが動作する

---

## 期待される動作

| 機能 | 期待動作 |
|------|----------|
| 住所表示 | propertiesテーブルから正常に取得 |
| 住所保存 | propertiesテーブルに正常に保存 |
| 既存データ | 全て正常に動作（データ損失なし） |

---

## 問題発生時の確認ポイント

1. **ブラウザコンソールでエラーがないか確認**
2. **APIレスポンスのステータスコードを確認**
3. **住所関連フィールドが空になっていないか確認**

---

## 備考

- この変更は内部リファクタリングであり、ユーザーから見た動作に変更はない
- property_locationsテーブル削除（DROP TABLE）はデプロイ時に実施
- 既存の全2,370件の物件データはpropertiesに存在し、影響なし
