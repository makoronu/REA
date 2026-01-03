# Seg3b テスト依頼書：テーブル名・ストレージキー統一

**作成日:** 2026-01-03
**実装者:** Claude
**対象:** テーブル名・ストレージキーのハードコーディング排除

---

## 変更概要

テーブル名とストレージキーを定数ファイルに集約し、重複定義を排除。

### 変更ファイル

#### バックエンド
| ファイル | 変更内容 |
|----------|----------|
| `shared/config/tables.py` | 新規作成：テーブル名定数 |
| `shared/config/__init__.py` | パッケージエクスポート |
| `rea-api/app/crud/generic.py` | ALLOWED_TABLES → CRUD_ALLOWED_TABLES参照 |
| `rea-api/.../metadata.py` | ALLOWED_TABLES → ALL_ALLOWED_TABLES参照 |

#### フロントエンド
| ファイル | 変更内容 |
|----------|----------|
| `constants/storage.ts` | 新規作成：ストレージキー定数 |
| `constants/tables.ts` | 新規作成：テーブル名定数 |
| `services/api.ts` | TOKEN_KEY → STORAGE_KEYS.AUTH_TOKEN |
| `services/authService.ts` | TOKEN_KEY/USER_KEY → STORAGE_KEYS.* |
| `services/metadataService.ts` | テーブル名リスト → PROPERTY_FORM_TABLES |
| `pages/Settings/UsersPage.tsx` | 直接文字列 → STORAGE_KEYS.AUTH_TOKEN |
| `pages/Properties/PropertiesPage.tsx` | *_KEY → STORAGE_KEYS.* |
| `components/CommandPalette.tsx` | HISTORY_KEY → STORAGE_KEYS.SEARCH_HISTORY |

---

## テスト手順

### 1. ログイン確認

- [ ] ログイン成功
- [ ] ログアウト成功
- [ ] 再ログイン成功

### 2. 物件一覧確認（ストレージキー動作）

- [ ] 物件一覧表示
- [ ] ページサイズ変更 → 画面更新後も維持
- [ ] カラム表示切替 → 画面更新後も維持
- [ ] ビュー切替（テーブル/カード）→ 画面更新後も維持

### 3. コマンドパレット確認

- [ ] ⌘K でコマンドパレット表示
- [ ] 検索実行
- [ ] 検索履歴表示

### 4. 物件編集確認（メタデータAPI）

- [ ] 物件編集画面表示
- [ ] 各タブ（基本情報、建物情報、土地情報等）表示
- [ ] 保存成功

### 5. ユーザー管理確認

- [ ] ユーザー一覧表示
- [ ] ユーザー作成（オプション）

---

## 期待される動作

| 機能 | 期待動作 |
|------|----------|
| ログイン/ログアウト | 正常動作（ストレージキー変更影響なし）|
| 物件一覧 | UI状態がブラウザ更新後も保持 |
| 物件編集 | メタデータAPIから正しくテーブル情報取得 |
| コマンドパレット | 検索履歴正常動作 |

---

## 問題発生時の確認ポイント

1. **ブラウザコンソールでエラーがないか確認**
2. **ローカルストレージのキー名が正しいか確認**
   - `rea_auth_token`, `rea_auth_user`, `rea_property_views`等
3. **APIレスポンスでエラーがないか確認**

---

## 備考

- この変更は内部リファクタリングであり、ユーザーから見た動作に変更はない
- 定数を一箇所で管理することで、将来の変更が容易になる
