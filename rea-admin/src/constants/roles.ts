// 認証関連定数
// ロールコードはm_rolesテーブルと同期

// 管理者以上のロール（ユーザー管理、フィールド可視性など）
export const ADMIN_ROLES = ['admin', 'super_admin'] as const;

// システム管理者のみ（システム設定など）
export const SUPER_ADMIN_ROLES = ['super_admin'] as const;

// 一般ユーザー以上（基本機能）
export const USER_ROLES = ['user', 'admin', 'super_admin'] as const;

// 型定義
export type RoleCode = 'user' | 'admin' | 'super_admin';

// ヘルパー関数
export const isAdmin = (roleCode: string | undefined): boolean => {
  return ADMIN_ROLES.includes(roleCode as typeof ADMIN_ROLES[number]);
};

export const isSuperAdmin = (roleCode: string | undefined): boolean => {
  return SUPER_ADMIN_ROLES.includes(roleCode as typeof SUPER_ADMIN_ROLES[number]);
};
