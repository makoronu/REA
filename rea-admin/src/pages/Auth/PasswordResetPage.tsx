// パスワードリセットページ
import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { authService } from '../../services/authService';

const PasswordResetPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isValidToken, setIsValidToken] = useState<boolean | null>(null);
  const [tokenMessage, setTokenMessage] = useState('');

  // トークン検証
  useEffect(() => {
    if (token) {
      authService.verifyResetToken(token)
        .then((result) => {
          setIsValidToken(result.valid);
          setTokenMessage(result.message);
        })
        .catch(() => {
          setIsValidToken(false);
          setTokenMessage('トークンの検証に失敗しました');
        });
    } else {
      setIsValidToken(false);
      setTokenMessage('トークンが指定されていません');
    }
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // バリデーション
    if (password.length < 8) {
      setError('パスワードは8文字以上で入力してください');
      return;
    }

    if (password !== confirmPassword) {
      setError('パスワードが一致しません');
      return;
    }

    setIsSubmitting(true);

    try {
      await authService.confirmPasswordReset(token!, password);
      setSuccess('パスワードを更新しました。ログインページに移動します...');
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error && 'response' in err
        ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
        : null;
      setError(errorMessage || 'パスワードの更新に失敗しました');
    } finally {
      setIsSubmitting(false);
    }
  };

  // トークン検証中
  if (isValidToken === null) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#F9FAFB',
      }}>
        <div style={{ color: '#6B7280' }}>確認中...</div>
      </div>
    );
  }

  // 無効なトークン
  if (!isValidToken) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#F9FAFB',
        padding: '16px',
      }}>
        <div style={{
          width: '100%',
          maxWidth: '400px',
          backgroundColor: 'white',
          borderRadius: '12px',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
          padding: '32px',
          textAlign: 'center',
        }}>
          <div style={{
            width: '64px',
            height: '64px',
            backgroundColor: '#FEF2F2',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 24px',
          }}>
            <svg width="32" height="32" fill="none" stroke="#DC2626" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 style={{ fontSize: '20px', fontWeight: 600, color: '#1F2937', marginBottom: '8px' }}>
            無効なリンク
          </h2>
          <p style={{ color: '#6B7280', marginBottom: '24px' }}>
            {tokenMessage}
          </p>
          <Link
            to="/login"
            style={{
              display: 'inline-block',
              padding: '12px 24px',
              backgroundColor: '#3B82F6',
              color: 'white',
              borderRadius: '8px',
              textDecoration: 'none',
              fontWeight: 500,
            }}
          >
            ログインページへ
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: '#F9FAFB',
      padding: '16px',
    }}>
      <div style={{
        width: '100%',
        maxWidth: '400px',
        backgroundColor: 'white',
        borderRadius: '12px',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        padding: '32px',
      }}>
        {/* タイトル */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <h1 style={{
            fontSize: '24px',
            fontWeight: 700,
            color: '#1F2937',
            marginBottom: '8px',
          }}>
            パスワード設定
          </h1>
          <p style={{
            fontSize: '14px',
            color: '#6B7280',
          }}>
            新しいパスワードを入力してください
          </p>
        </div>

        {/* エラーメッセージ */}
        {error && (
          <div style={{
            padding: '12px 16px',
            backgroundColor: '#FEF2F2',
            border: '1px solid #FECACA',
            borderRadius: '8px',
            marginBottom: '24px',
            color: '#DC2626',
            fontSize: '14px',
          }}>
            {error}
          </div>
        )}

        {/* 成功メッセージ */}
        {success && (
          <div style={{
            padding: '12px 16px',
            backgroundColor: '#F0FDF4',
            border: '1px solid #BBF7D0',
            borderRadius: '8px',
            marginBottom: '24px',
            color: '#16A34A',
            fontSize: '14px',
          }}>
            {success}
          </div>
        )}

        {/* フォーム */}
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: 500,
              color: '#374151',
              marginBottom: '6px',
            }}>
              新しいパスワード
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              autoComplete="new-password"
              autoFocus
              style={{
                width: '100%',
                padding: '12px 14px',
                fontSize: '16px',
                border: '1px solid #D1D5DB',
                borderRadius: '8px',
                outline: 'none',
                transition: 'border-color 150ms, box-shadow 150ms',
                boxSizing: 'border-box',
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#3B82F6';
                e.target.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#D1D5DB';
                e.target.style.boxShadow = 'none';
              }}
              placeholder="8文字以上"
            />
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: 500,
              color: '#374151',
              marginBottom: '6px',
            }}>
              パスワード確認
            </label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              autoComplete="new-password"
              style={{
                width: '100%',
                padding: '12px 14px',
                fontSize: '16px',
                border: '1px solid #D1D5DB',
                borderRadius: '8px',
                outline: 'none',
                transition: 'border-color 150ms, box-shadow 150ms',
                boxSizing: 'border-box',
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#3B82F6';
                e.target.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#D1D5DB';
                e.target.style.boxShadow = 'none';
              }}
              placeholder="もう一度入力"
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
              backgroundColor: isSubmitting ? '#93C5FD' : '#3B82F6',
              border: 'none',
              borderRadius: '8px',
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              transition: 'all 150ms',
            }}
            onMouseOver={(e) => {
              if (!isSubmitting) {
                e.currentTarget.style.backgroundColor = '#2563EB';
                e.currentTarget.style.transform = 'translateY(-1px)';
              }
            }}
            onMouseOut={(e) => {
              if (!isSubmitting) {
                e.currentTarget.style.backgroundColor = '#3B82F6';
                e.currentTarget.style.transform = 'translateY(0)';
              }
            }}
          >
            {isSubmitting ? '更新中...' : 'パスワードを設定'}
          </button>
        </form>

        {/* ログインへ戻る */}
        <div style={{ textAlign: 'center', marginTop: '24px' }}>
          <Link
            to="/login"
            style={{
              color: '#3B82F6',
              textDecoration: 'none',
              fontSize: '14px',
            }}
          >
            ログインページに戻る
          </Link>
        </div>
      </div>
    </div>
  );
};

export default PasswordResetPage;
