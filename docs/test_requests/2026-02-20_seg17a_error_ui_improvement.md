# テスト依頼書: Seg 17a エラーメッセージUI改善

## 概要
全ページのエラー表示を統一。alert()全廃、エラーメッセージのsetTimeout自動消去撤去。

## 変更内容

### Seg 17a-1（コミット: 3327e9f）
- ErrorBanner共通コンポーネント作成
- 管理ページ6つのエラー/成功表示をErrorBannerに統一
  - UsersPage, FieldVisibilityPage, IntegrationsPage, SystemSettingsPage, ToukiImportPage, PropertiesPage

### Seg 17a-2（コミット: 92c7764）
- PropertyEditDynamicPage: alert()3箇所→ErrorBanner
- DynamicForm: setTimeout8箇所削除 + インラインメッセージに×ボタン追加
- FieldFactory: setTimeout4箇所削除 + zoningMessage×ボタン追加
- LocationField: エラー時auto-dismiss廃止 + ×ボタン追加
- RegulationTab: メッセージに×ボタン追加
- ImageUploader: alert()2箇所→ErrorBanner
- useMetadataForm: alert()→onValidationErrorコールバック化

## テスト手順

### 1. 物件一覧ページ（/properties）
- [ ] ページが正常に表示される
- [ ] 一括削除でエラーが発生した場合、赤いバナーが画面上部に表示される（alert()ではない）
- [ ] エラーバナーは×ボタンで手動で閉じられる
- [ ] ステータス変更成功時、緑バナーが表示されて自動消去される

### 2. 物件編集ページ（/properties/{id}/edit）
- [ ] 保存成功時のフローティング表示が正常
- [ ] ZOHO同期成功時、緑バナーが表示される（alert()ではない）
- [ ] クリップボードコピー時、緑バナーが表示される（alert()ではない）
- [ ] 保存エラー時、エラーバナーが表示されて×で閉じられる

### 3. 物件新規登録（/properties/new/edit）
- [ ] フォームバリデーションエラー時、画面上部に赤バナーが表示される（alert()ではない）
- [ ] エラーバナーは×で閉じられる

### 4. Geoボタン（学校・駅・バス・施設）
- [ ] 「緯度・経度を先に入力してください」エラーが自動消去されない
- [ ] エラーメッセージに×ボタンがあり、手動で閉じられる
- [ ] 成功メッセージは自動消去される

### 5. 住所→座標取得（LocationField）
- [ ] エラー「座標の取得に失敗しました」が自動消去されない
- [ ] エラーに×ボタンがあり、手動で閉じられる
- [ ] 成功「座標を取得しました」は自動消去される

### 6. 法令制限自動取得（RegulationTab）
- [ ] 成功/エラーメッセージに×ボタンがある
- [ ] エラーは消えない、成功は自動消去される

### 7. 画像アップロード（ImageUploader）
- [ ] 最大枚数超過時、赤バナーが表示される（alert()ではない）
- [ ] 画像削除エラー時、赤バナーが表示される

### 8. 管理ページ共通
- [ ] ユーザー管理: エラー/成功がErrorBannerで表示
- [ ] フィールド表示設定: 保存成功/エラーがErrorBannerで表示
- [ ] 外部連携: 同期成功/エラーがErrorBannerで表示
- [ ] システム設定: 保存成功/エラーがErrorBannerで表示
- [ ] 登記インポート: エラー/成功がErrorBannerで表示

## 確認ポイント
- alert()が一切表示されないこと
- エラーメッセージが自動で消えないこと（手動×のみ）
- 成功メッセージは3秒後に自動消去されること
- 画面崩れがないこと
