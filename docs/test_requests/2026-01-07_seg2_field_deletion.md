# テスト依頼: Seg2 フィールド削除

**作成日**: 2026-01-07
**依頼者**: Claude
**対象コミット**: b1129dc, ba52d26

---

## 概要

物件編集画面から21フィールドを非表示化。メタデータ駆動（column_labels.visible_for = []）による制御。

---

## テスト対象

### 変更箇所

| 種別 | 対象 | 内容 |
|------|------|------|
| DB | column_labels | 21フィールドのvisible_for = [] |
| DB | column_labels | parking_fee.required_for_publication = NULL |
| フロント | PropertiesPage.tsx | 元請会社カラム削除 |

### 非表示化フィールド（21件）

| グループ | フィールド |
|----------|------------|
| 基本情報 | property_name_kana, property_name_public, external_property_id, affiliated_group, investment_property |
| 契約条件 | commission_split_ratio, brokerage_contract_date |
| 引渡・掲載 | listing_start_date, listing_confirmation_date |
| 元請会社 | contractor_company_name, contractor_contact_person, contractor_phone, contractor_email, contractor_address, contractor_license_number |
| 費用情報 | parking_fee, housing_insurance |
| 管理情報 | property_manager_name, internal_memo, priority_score, property_url |

---

## テストケース

### 正常系

| # | テスト項目 | 手順 | 期待結果 |
|---|-----------|------|----------|
| 1 | 物件編集画面表示 | 任意の物件を編集画面で開く | 21フィールドが表示されないこと |
| 2 | 基本情報タブ確認 | 基本情報タブを開く | 物件名カナ、公開用物件名、外部物件ID、所属グループ、投資用物件が表示されないこと |
| 3 | 契約条件タブ確認 | 契約条件タブを開く | 分配率、媒介契約日が表示されないこと |
| 4 | 引渡・掲載タブ確認 | 引渡・掲載タブを開く | 掲載開始日、掲載確認日が表示されないこと |
| 5 | 元請会社タブ確認 | 元請会社タブを確認 | タブ自体が表示されない、または空であること |
| 6 | 費用情報タブ確認 | 費用情報タブを開く | 駐車場使用料、住宅保険が表示されないこと |
| 7 | 管理情報タブ確認 | 管理情報タブを開く | 社内担当者、社内メモ、優先度スコア、物件URLが表示されないこと（building_info側のフィールドは残る） |
| 8 | 一覧ページ確認 | 物件一覧ページを開く | 「元請会社」カラムが表示されないこと |
| 9 | 公開バリデーション（マンション） | マンション物件を公開に変更 | parking_feeが必須エラーにならないこと |
| 10 | 公開バリデーション（アパート） | アパート物件を公開に変更 | parking_feeが必須エラーにならないこと |
| 11 | 既存データ保持 | 非表示フィールドにデータがある物件を確認 | データが削除されていないこと（APIレスポンスで確認） |

### 異常系

| # | テスト項目 | 手順 | 期待結果 |
|---|-----------|------|----------|
| 1 | 保存動作確認 | 物件を編集して保存 | エラーなく保存できること |
| 2 | 新規作成確認 | 新規物件を作成 | 非表示フィールドなしで作成できること |

---

## 攻撃ポイント

| # | 観点 | 確認内容 |
|---|------|----------|
| 1 | データ消失 | 非表示化したフィールドの既存データが消えていないか |
| 2 | 表示漏れ | 21フィールドのうち表示されているものがないか |
| 3 | 物件種別依存 | マンション/アパート/一戸建て/土地で挙動が異なっていないか |
| 4 | 公開バリデーション | parking_fee以外の必須フィールドに影響がないか |
| 5 | 一覧ページ | カラム設定で元請会社が選択肢に残っていないか |

---

## テスト環境

| 項目 | 値 |
|------|-----|
| 本番URL | https://realestateautomation.net/ |
| バックアップ | /tmp/backup_seg2_20260107_081244.sql |

---

## ロールバック手順

```bash
# column_labelsを元に戻す
ssh rea-conoha "sudo -u postgres psql real_estate_db -c \"
UPDATE column_labels SET visible_for = NULL WHERE column_name IN (
  'property_name_kana', 'property_name_public', 'external_property_id',
  'affiliated_group', 'investment_property', 'commission_split_ratio',
  'brokerage_contract_date', 'listing_start_date', 'listing_confirmation_date',
  'contractor_company_name', 'contractor_contact_person', 'contractor_phone',
  'contractor_email', 'contractor_address', 'contractor_license_number',
  'parking_fee', 'housing_insurance', 'property_manager_name',
  'internal_memo', 'priority_score', 'property_url'
);
UPDATE column_labels SET required_for_publication = '{apartment,mansion}' WHERE column_name = 'parking_fee';
\""
```
