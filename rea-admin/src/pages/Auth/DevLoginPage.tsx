// 開発者ログインページ
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const DevLoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login, isLoading: authLoading } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      await login({ email, password });
      navigate('/', { replace: true });
    } catch (err: unknown) {
      const errorMessage = err instanceof Error && 'response' in err
        ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
        : null;
      setError(errorMessage || 'ログインに失敗しました');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (authLoading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#111827',
      }}>
        <div style={{ color: '#9CA3AF' }}>読み込み中...</div>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: '#111827',
      padding: '16px',
    }}>
      <div style={{
        width: '100%',
        maxWidth: '400px',
        backgroundColor: '#1F2937',
        borderRadius: '12px',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.3)',
        padding: '32px',
        border: '1px solid #374151',
      }}>
        {/* ロゴ・タイトル */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '48px',
            height: '48px',
            backgroundColor: '#10B981',
            borderRadius: '12px',
            marginBottom: '16px',
          }}>
            <svg style={{ width: '24px', height: '24px', color: 'white' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
            </svg>
          </div>
          <h1 style={{
            fontSize: '24px',
            fontWeight: 700,
            color: '#F9FAFB',
            marginBottom: '8px',
          }}>
            開発者ログイン
          </h1>
          <p style={{
            fontSize: '14px',
            color: '#9CA3AF',
          }}>
            REA Development Console
          </p>
        </div>

        {/* エラーメッセージ */}
        {error && (
          <div style={{
            padding: '12px 16px',
            backgroundColor: 'rgba(220, 38, 38, 0.2)',
            border: '1px solid #DC2626',
            borderRadius: '8px',
            marginBottom: '24px',
            color: '#FCA5A5',
            fontSize: '14px',
          }}>
            {error}
          </div>
        )}

        {/* ログインフォーム */}
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: 500,
              color: '#D1D5DB',
              marginBottom: '6px',
            }}>
              メールアドレス
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
              autoFocus
              style={{
                width: '100%',
                padding: '12px 14px',
                fontSize: '16px',
                backgroundColor: '#374151',
                border: '1px solid #4B5563',
                borderRadius: '8px',
                color: '#F9FAFB',
                outline: 'none',
                transition: 'border-color 150ms, box-shadow 150ms',
                boxSizing: 'border-box',
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#10B981';
                e.target.style.boxShadow = '0 0 0 3px rgba(16, 185, 129, 0.2)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#4B5563';
                e.target.style.boxShadow = 'none';
              }}
              placeholder="developer@example.com"
            />
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: 500,
              color: '#D1D5DB',
              marginBottom: '6px',
            }}>
              パスワード
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
              style={{
                width: '100%',
                padding: '12px 14px',
                fontSize: '16px',
                backgroundColor: '#374151',
                border: '1px solid #4B5563',
                borderRadius: '8px',
                color: '#F9FAFB',
                outline: 'none',
                transition: 'border-color 150ms, box-shadow 150ms',
                boxSizing: 'border-box',
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#10B981';
                e.target.style.boxShadow = '0 0 0 3px rgba(16, 185, 129, 0.2)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#4B5563';
                e.target.style.boxShadow = 'none';
              }}
              placeholder="********"
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            style={{
              width: '100%',
              padding: '14px',
              fontSize: '16px',
              fontWeight: 600,
              color: 'white',
              backgroundColor: isSubmitting ? '#065F46' : '#10B981',
              border: 'none',
              borderRadius: '8px',
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              transition: 'all 150ms',
            }}
            onMouseOver={(e) => {
              if (!isSubmitting) {
                e.currentTarget.style.backgroundColor = '#059669';
              }
            }}
            onMouseOut={(e) => {
              if (!isSubmitting) {
                e.currentTarget.style.backgroundColor = '#10B981';
              }
            }}
          >
            {isSubmitting ? 'ログイン中...' : 'ログイン'}
          </button>
        </form>

        {/* フッター */}
        <div style={{
          marginTop: '24px',
          paddingTop: '24px',
          borderTop: '1px solid #374151',
          textAlign: 'center',
        }}>
          <p style={{ fontSize: '12px', color: '#6B7280' }}>
            このページは開発者専用です
          </p>
        </div>
      </div>
    </div>
  );
};

export default DevLoginPage;
