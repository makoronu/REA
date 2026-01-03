# Seg3c テスト依頼書：APIパス統一

**作成日:** 2026-01-03
**実装者:** Claude
**対象:** APIパスのハードコーディング排除（40件）

---

## 変更概要

全APIパスを`constants/apiPaths.ts`に集約し、ハードコーディングを排除。

### 変更ファイル

#### 新規作成
| ファイル | 内容 |
|----------|------|
| `constants/apiPaths.ts` | APIパス定数（10カテゴリ） |

#### 修正ファイル（14ファイル）
| ファイル | 変更箇所 |
|----------|----------|
| DynamicForm.tsx | GEO API（4件） |
| FieldFactory.tsx | GEO API（3件） |
| ZoningMapField.tsx | GEO API（4件） |
| ZoningMapPage.tsx | GEO API（2件） |
| ToukiImportPage.tsx | TOUKI API（8件） |
| IntegrationsPage.tsx | INTEGRATIONS API（5件） |
| FieldVisibilityPage.tsx | ADMIN API（4件） |
| UsersPage.tsx | USERS API（4件） |
| RegulationMap.tsx | REINFOLIB API（1件） |
| RegulationTab.tsx | REINFOLIB API（1件） |
| JsonEditors.tsx | EQUIPMENT API（1件） |
| PropertyEditDynamicPage.tsx | ZOHO API（1件） |
| PropertiesPage.tsx | PORTAL API（1件） |
| metadataService.ts | METADATA API（1件） |

---

## テスト手順

### 1. 物件一覧・編集（基本動作）

- [ ] 物件一覧表示
- [ ] 物件編集画面表示
- [ ] 物件保存成功

### 2. 地理情報系（GEO API）

- [ ] 住所から座標取得（ジオコード）
- [ ] 用途地域情報取得
- [ ] 最寄駅自動取得
- [ ] バス停自動取得
- [ ] 学区自動取得
- [ ] 周辺施設自動取得

### 3. 用途地域MAP

- [ ] 用途地域MAPページ表示
- [ ] MAPクリックで用途地域情報表示
- [ ] 物件編集画面内のMAPフィールド動作

### 4. 法令制限タブ

- [ ] 法令制限情報自動取得
- [ ] レイヤー切替動作

### 5. 登記インポート

- [ ] 登記インポートページ表示
- [ ] PDFアップロード
- [ ] 登記解析
- [ ] 物件作成

### 6. ユーザー管理

- [ ] ユーザー一覧表示
- [ ] ユーザー作成（オプション）
- [ ] ユーザー有効/無効切替

### 7. 外部連携

- [ ] 連携一覧表示
- [ ] 連携状況表示
- [ ] ZOHO同期（物件編集画面から）

### 8. フィールド設定

- [ ] フィールド表示設定ページ表示
- [ ] 設定変更・保存

### 9. 設備選択

- [ ] 物件編集画面で設備選択UI表示
- [ ] 設備の選択・解除動作

### 10. HOMES CSV出力

- [ ] 物件一覧からHOMES CSV出力

---

## 期待される動作

| 機能 | 期待動作 |
|------|----------|
| 全API呼び出し | 正常動作（パス変更影響なし） |
| ブラウザコンソール | エラーなし |
| ネットワークタブ | API呼び出しURL正常 |

---

## 問題発生時の確認ポイント

1. **ブラウザコンソールでエラーがないか確認**
2. **ネットワークタブでAPIリクエストのURLを確認**
   - 全て `/api/v1/xxx` 形式であること
3. **APIレスポンスのステータスコードを確認**

---

## 備考

- この変更は内部リファクタリングであり、ユーザーから見た動作に変更はない
- APIパスを一箇所で管理することで、将来の変更が容易になる
- バックエンドのエンドポイント変更時は`apiPaths.ts`のみ修正すればよい
