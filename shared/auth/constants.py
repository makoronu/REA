# 認証関連定数
# ロールコードはm_rolesテーブルと同期

# 管理者以上のロール（ユーザー管理、フィールド可視性など）
ADMIN_ROLES = ['admin', 'super_admin']

# システム管理者のみ（システム設定など）
SUPER_ADMIN_ROLES = ['super_admin']

# 一般ユーザー以上（基本機能）
USER_ROLES = ['user', 'admin', 'super_admin']
