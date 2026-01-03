# Seg3a テスト依頼書：権限判定ロールコード化

**作成日:** 2026-01-03
**実装者:** Claude
**対象:** 権限レベルハードコーディングのロールコードベース化

---

## 変更概要

権限判定を数値ベース（`role_level >= 80`）からロールコードベース（`role_code in ['admin', 'super_admin']`）に変更。

### 変更ファイル

| ファイル | 変更内容 |
|----------|----------|
| `shared/auth/constants.py` | 新規作成：ロール定数定義 |
| `shared/auth/middleware.py` | `require_roles()`関数追加、既存関数をロールコードベースに |
| `rea-api/.../users.py` | `require_admin()`をロールコードベースに |
| `rea-admin/src/constants/roles.ts` | 新規作成：ロール定数定義 |
| `rea-admin/.../PrivateRoute.tsx` | `minLevel`→`requiredRoles`に変更 |
| `rea-admin/.../Layout.tsx` | `isAdmin`判定をロールコードベースに |
| `rea-admin/src/App.tsx` | `minLevel`→`requiredRoles`に変更 |

---

## テスト手順

### 1. adminユーザーでログイン

```
Email: admin@shirokuma.com
Password: [管理者に確認]
```

### 2. ユーザー管理画面アクセス確認

- [ ] サイドメニューに「ユーザー」が表示される
- [ ] `/settings/users` にアクセスできる
- [ ] ユーザー一覧が表示される

### 3. フィールド可視性画面アクセス確認

- [ ] `/admin/field-visibility` にアクセスできる
- [ ] 設定画面が表示される

### 4. 一般ユーザーでログイン（権限なしユーザー）

```
Email: [一般ユーザーアカウント]
Password: [管理者に確認]
```

### 5. アクセス拒否確認

- [ ] サイドメニューに「ユーザー」が表示されない
- [ ] `/settings/users` に直接アクセスすると「アクセス権限がありません」表示
- [ ] `/admin/field-visibility` に直接アクセスすると「アクセス権限がありません」表示

### 6. super_adminユーザーでログイン

```
Email: [super_adminアカウント]
Password: [管理者に確認]
```

### 7. super_admin権限確認

- [ ] サイドメニューに「ユーザー」が表示される
- [ ] `/settings/users` にアクセスできる
- [ ] `/admin/field-visibility` にアクセスできる

---

## 期待される動作

| ロール | ユーザー管理 | フィールド可視性 |
|--------|-------------|-----------------|
| user | ❌ アクセス不可 | ❌ アクセス不可 |
| admin | ✅ アクセス可能 | ✅ アクセス可能 |
| super_admin | ✅ アクセス可能 | ✅ アクセス可能 |

---

## 問題発生時の確認ポイント

1. **ブラウザコンソールでエラーがないか確認**
2. **APIレスポンスで403が返っていないか確認**
3. **ローカルストレージの`rea_auth_user`に`role_code`が含まれているか確認**

---

## 備考

- この変更により、DB上のadmin（level=50）でもユーザー管理にアクセス可能になる
- 以前は`role_level >= 80`で判定していたため、admin（level=50）はアクセス不可だった
