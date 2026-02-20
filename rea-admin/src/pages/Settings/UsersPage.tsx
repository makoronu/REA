import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { API_PATHS } from '../../constants/apiPaths';
import { MESSAGE_TIMEOUT_MS, LONG_MESSAGE_TIMEOUT_MS } from '../../constants';

interface User {
  id: number;
  email: string;
  name: string;
  role_id: number;
  role_name: string;
  is_active: boolean;
  last_login_at: string | null;
  created_at: string;
}

interface Role {
  id: number;
  code: string;
  name: string;
  level: number;
}

export const UsersPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // 新規作成モーダル
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newUser, setNewUser] = useState({ email: '', name: '', role_id: 0 });
  const [isCreating, setIsCreating] = useState(false);

  const fetchData = async () => {
    try {
      setIsLoading(true);
      const [usersRes, rolesRes] = await Promise.all([
        api.get(API_PATHS.USERS.LIST),
        api.get(API_PATHS.USERS.ROLES),
      ]);

      setUsers(usersRes.data.users);
      setRoles(rolesRes.data);

      const rolesData = rolesRes.data;

      if (rolesData.length > 0 && newUser.role_id === 0) {
        // デフォルトは一般ユーザー（最もレベルの低いロール）
        const defaultRole = rolesData[rolesData.length - 1];
        setNewUser(prev => ({ ...prev, role_id: defaultRole.id }));
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'データの取得に失敗しました';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUser.email || !newUser.name || !newUser.role_id) {
      setError('全ての項目を入力してください');
      return;
    }

    setIsCreating(true);
    setError(null);

    try {
      await api.post(API_PATHS.USERS.LIST, newUser);

      setSuccessMessage('ユーザーを作成しました。パスワード設定メールを送信しました。');
      setShowCreateModal(false);
      setNewUser({ email: '', name: '', role_id: roles[0]?.id || 0 });
      fetchData();
      setTimeout(() => setSuccessMessage(null), LONG_MESSAGE_TIMEOUT_MS);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'ユーザー作成に失敗しました';
      setError(message);
    } finally {
      setIsCreating(false);
    }
  };

  const handleToggleActive = async (userId: number, currentActive: boolean) => {
    try {
      await api.put(API_PATHS.USERS.detail(userId), { is_active: !currentActive });

      fetchData();
      setSuccessMessage(currentActive ? 'ユーザーを無効化しました' : 'ユーザーを有効化しました');
      setTimeout(() => setSuccessMessage(null), MESSAGE_TIMEOUT_MS);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : '更新に失敗しました';
      setError(message);
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (isLoading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: '#6B7280' }}>
        読み込み中...
      </div>
    );
  }

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      {/* ヘッダー */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#1F2937', margin: 0 }}>
          ユーザー管理
        </h1>
        <button
          onClick={() => setShowCreateModal(true)}
          style={{
            padding: '10px 20px',
            backgroundColor: '#3B82F6',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          <span>+</span> 新規ユーザー作成
        </button>
      </div>

      {/* メッセージ */}
      {error && (
        <div style={{
          padding: '12px 16px',
          backgroundColor: '#FEF2F2',
          border: '1px solid #FECACA',
          borderRadius: '8px',
          marginBottom: '16px',
          color: '#DC2626'
        }}>
          {error}
          <button onClick={() => setError(null)} style={{ float: 'right', background: 'none', border: 'none', cursor: 'pointer' }}>×</button>
        </div>
      )}

      {successMessage && (
        <div style={{
          padding: '12px 16px',
          backgroundColor: '#F0FDF4',
          border: '1px solid #BBF7D0',
          borderRadius: '8px',
          marginBottom: '16px',
          color: '#16A34A'
        }}>
          {successMessage}
        </div>
      )}

      {/* ユーザーテーブル */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
        overflow: 'hidden'
      }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#F9FAFB' }}>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontWeight: 600, color: '#374151', borderBottom: '1px solid #E5E7EB' }}>名前</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontWeight: 600, color: '#374151', borderBottom: '1px solid #E5E7EB' }}>メールアドレス</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontWeight: 600, color: '#374151', borderBottom: '1px solid #E5E7EB' }}>権限</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontWeight: 600, color: '#374151', borderBottom: '1px solid #E5E7EB' }}>最終ログイン</th>
              <th style={{ padding: '12px 16px', textAlign: 'center', fontWeight: 600, color: '#374151', borderBottom: '1px solid #E5E7EB' }}>状態</th>
              <th style={{ padding: '12px 16px', textAlign: 'center', fontWeight: 600, color: '#374151', borderBottom: '1px solid #E5E7EB' }}>操作</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id} style={{ borderBottom: '1px solid #E5E7EB' }}>
                <td style={{ padding: '12px 16px', color: '#1F2937' }}>{user.name}</td>
                <td style={{ padding: '12px 16px', color: '#6B7280' }}>{user.email}</td>
                <td style={{ padding: '12px 16px', color: '#6B7280' }}>{user.role_name}</td>
                <td style={{ padding: '12px 16px', color: '#6B7280', fontSize: '13px' }}>{formatDate(user.last_login_at)}</td>
                <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                  <span style={{
                    padding: '4px 12px',
                    borderRadius: '9999px',
                    fontSize: '12px',
                    fontWeight: 500,
                    backgroundColor: user.is_active ? '#D1FAE5' : '#FEE2E2',
                    color: user.is_active ? '#065F46' : '#991B1B'
                  }}>
                    {user.is_active ? '有効' : '無効'}
                  </span>
                </td>
                <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                  <button
                    onClick={() => handleToggleActive(user.id, user.is_active)}
                    style={{
                      padding: '6px 12px',
                      backgroundColor: user.is_active ? '#FEF2F2' : '#F0FDF4',
                      color: user.is_active ? '#DC2626' : '#16A34A',
                      border: 'none',
                      borderRadius: '6px',
                      fontSize: '13px',
                      cursor: 'pointer'
                    }}
                  >
                    {user.is_active ? '無効化' : '有効化'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {users.length === 0 && (
          <div style={{ padding: '40px', textAlign: 'center', color: '#6B7280' }}>
            ユーザーがいません
          </div>
        )}
      </div>

      {/* 新規作成モーダル */}
      {showCreateModal && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            padding: '24px',
            width: '100%',
            maxWidth: '480px',
            margin: '16px'
          }}>
            <h2 style={{ fontSize: '20px', fontWeight: 600, marginBottom: '20px', color: '#1F2937' }}>
              新規ユーザー作成
            </h2>

            <form onSubmit={handleCreateUser}>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '6px', fontWeight: 500, color: '#374151' }}>
                  名前 <span style={{ color: '#DC2626' }}>*</span>
                </label>
                <input
                  type="text"
                  value={newUser.name}
                  onChange={e => setNewUser({ ...newUser, name: e.target.value })}
                  required
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    border: '1px solid #D1D5DB',
                    borderRadius: '8px',
                    fontSize: '14px',
                    boxSizing: 'border-box'
                  }}
                  placeholder="山田 太郎"
                />
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '6px', fontWeight: 500, color: '#374151' }}>
                  メールアドレス <span style={{ color: '#DC2626' }}>*</span>
                </label>
                <input
                  type="email"
                  value={newUser.email}
                  onChange={e => setNewUser({ ...newUser, email: e.target.value })}
                  required
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    border: '1px solid #D1D5DB',
                    borderRadius: '8px',
                    fontSize: '14px',
                    boxSizing: 'border-box'
                  }}
                  placeholder="user@example.com"
                />
              </div>

              <div style={{ marginBottom: '24px' }}>
                <label style={{ display: 'block', marginBottom: '6px', fontWeight: 500, color: '#374151' }}>
                  権限 <span style={{ color: '#DC2626' }}>*</span>
                </label>
                <select
                  value={newUser.role_id}
                  onChange={e => setNewUser({ ...newUser, role_id: Number(e.target.value) })}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    border: '1px solid #D1D5DB',
                    borderRadius: '8px',
                    fontSize: '14px',
                    boxSizing: 'border-box'
                  }}
                >
                  {roles.map(role => (
                    <option key={role.id} value={role.id}>{role.name}</option>
                  ))}
                </select>
              </div>

              <p style={{ fontSize: '13px', color: '#6B7280', marginBottom: '20px' }}>
                ユーザー作成後、パスワード設定用のメールが送信されます。
              </p>

              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  style={{
                    padding: '10px 20px',
                    backgroundColor: '#F3F4F6',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer'
                  }}
                >
                  キャンセル
                </button>
                <button
                  type="submit"
                  disabled={isCreating}
                  style={{
                    padding: '10px 20px',
                    backgroundColor: isCreating ? '#93C5FD' : '#3B82F6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    fontWeight: 600,
                    cursor: isCreating ? 'not-allowed' : 'pointer'
                  }}
                >
                  {isCreating ? '作成中...' : '作成'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default UsersPage;
