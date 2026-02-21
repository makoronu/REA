# テスト依頼書: Seg 18 DynamicForm + FieldFactory 責務分割

## 日時
2026-02-21

## 変更概要
DynamicForm.tsx（1190行）とFieldFactory.tsx（1241行）を500行以下に責務分割。
機能追加なし、純粋なリファクタリング。動作は変更前と同一であること。

## 変更ファイル
- `rea-admin/src/components/form/DynamicForm.tsx` (1190→465行)
- `rea-admin/src/components/form/FieldFactory.tsx` (1241→447行)
- `rea-admin/src/components/form/LocationField.tsx` (302→217行)
- **新規** `rea-admin/src/components/form/buildTabGroups.ts` (201行)
- **新規** `rea-admin/src/components/form/useStatusSync.ts` (170行)
- **新規** `rea-admin/src/components/form/FormHeader.tsx` (275行)
- **新規** `rea-admin/src/components/form/FieldGroup.tsx` (368行)
- **新規** `rea-admin/src/components/form/SelectionFields.tsx` (316行)
- **新規** `rea-admin/src/components/form/PostalCodeField.tsx` (107行)
- **新規** `rea-admin/src/components/form/ValidationErrorModal.tsx` (149行)
- **新規** `rea-admin/src/components/form/fieldUtils.ts` (33行)

## テスト環境
- URL: https://realestateautomation.net/
- テストユーザー: 管理者アカウント

## テスト項目

### 1. 物件編集（正常系）
- [ ] 既存物件を開いてタブ切替（全タブ）
- [ ] 各タブのフィールドが正しく表示される
- [ ] ステータスバー（案件・公開）が表示・操作できる
- [ ] 保存ボタンで保存できる
- [ ] 前へ/次へボタンで移動できる

### 2. 所在地・周辺情報タブ
- [ ] 郵便番号入力で住所自動入力される
- [ ] 座標取得ボタンが動作する
- [ ] 周辺情報自動取得ボタンが表示される
- [ ] GeoPanelモーダルが開く

### 3. 土地情報タブ
- [ ] 法令制限自動取得ボタンが表示される
- [ ] RegulationPanelモーダルが開く
- [ ] 法規制グループの位置情報から自動取得ボタンが動作する

### 4. 基本情報タブ
- [ ] ラジオボタン、セレクトボックス、チェックボックスが正しく表示・操作できる
- [ ] 物件種別による表示/非表示切替が正しく動作する

### 5. 新規物件作成
- [ ] 物件種別選択画面が表示される
- [ ] 種別を選ぶとフォームが表示される

### 6. 公開バリデーション
- [ ] 公開ステータス変更時にバリデーションが実行される
- [ ] エラー時にバリデーションエラーモーダルが表示される
- [ ] モーダルのグループ名クリックで該当タブに移動する

### 7. 設備タブ
- [ ] アコーディオン折りたたみが動作する

### 8. 回帰テスト
- [ ] 変更前と同一の動作であること（新機能なし）

## 攻撃ポイント
- タブ切替の高速連打
- 保存中のタブ切替
- 公開→非公開→公開の連続変更
