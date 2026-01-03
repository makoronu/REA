import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useSaveStatusDisplay, SaveStatus } from '../../hooks/useAutoSave';
import { useAuth } from '../../contexts/AuthContext';
import { isAdmin as checkIsAdmin } from '../../constants/roles';

interface LayoutProps {
  children: React.ReactNode;
  onOpenCommandPalette?: () => void;
}

// 保存ステータス表示コンポーネント
const SaveStatusIndicator: React.FC = () => {
  const { status, lastSaved } = useSaveStatusDisplay();

  const formatTime = (date: Date | null) => {
    if (!date) return '';
    return date.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' });
  };

  const getStatusDisplay = (status: SaveStatus) => {
    switch (status) {
      case 'idle':
        return null;
      case 'unsaved':
        return {
          icon: '●',
          text: '変更あり',
          color: '#F59E0B',
        };
      case 'saving':
        return {
          icon: '↻',
          text: '保存中...',
          color: '#3B82F6',
          animate: true,
        };
      case 'saved':
        return {
          icon: '✓',
          text: `保存済み ${formatTime(lastSaved)}`,
          color: '#9CA3AF',
        };
      case 'error':
        return {
          icon: '✗',
          text: '保存失敗',
          color: '#EF4444',
        };
    }
  };

  const display = getStatusDisplay(status);
  if (!display) return null;

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
        fontSize: '13px',
        color: display.color,
        padding: '4px 12px',
        borderRadius: '6px',
        backgroundColor: status === 'error' ? 'rgba(239, 68, 68, 0.1)' : 'transparent',
        cursor: status === 'error' ? 'pointer' : 'default',
        transition: 'all 150ms',
      }}
      title={status === 'error' ? 'クリックして再試行' : undefined}
    >
      <span
        style={{
          animation: display.animate ? 'spin 1s linear infinite' : undefined,
          display: 'inline-block',
        }}
      >
        {display.icon}
      </span>
      <span style={{ fontWeight: 500 }}>{display.text}</span>
    </div>
  );
};

const Layout: React.FC<LayoutProps> = ({ children, onOpenCommandPalette }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const isActive = (path: string) => {
    if (path === '/properties') {
      return location.pathname === '/' || location.pathname === '/properties';
    }
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  const isAdmin = checkIsAdmin(user?.role_code);

  const menuItems = [
    { path: '/properties', label: '物件一覧', icon: '🏠' },
    { path: '/properties/new', label: '新規登録', icon: '➕' },
    { path: '/import/touki', label: '登記取込', icon: '📄' },
    { path: '/settings/integrations', label: '外部連携', icon: '🔄' },
    ...(isAdmin ? [{ path: '/settings/users', label: 'ユーザー', icon: '👤' }] : []),
    { path: '/admin/field-visibility', label: '管理', icon: '⚙️' },
  ];

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: 'var(--color-bg)',
      display: 'flex',
      flexDirection: 'column',
    }}>
      {/* ヘッダー */}
      <header style={{
        backgroundColor: 'var(--color-bg-white)',
        borderBottom: '1px solid var(--color-border)',
        padding: '12px 16px',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '16px',
      }}>
        <Link to="/properties" style={{ textDecoration: 'none' }}>
          <h1 style={{
            fontSize: '18px',
            fontWeight: 700,
            color: 'var(--color-text-primary)',
            margin: 0,
          }}>
            REA
          </h1>
        </Link>

        {/* 検索バー（クリックでコマンドパレットを開く） */}
        <button
          onClick={onOpenCommandPalette}
          className="search-trigger"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 16px',
            backgroundColor: '#F3F4F6',
            border: '1px solid #E5E7EB',
            borderRadius: '10px',
            cursor: 'pointer',
            transition: 'all 200ms',
            minWidth: '240px',
            maxWidth: '400px',
            flex: 1,
          }}
        >
          <svg style={{ width: '16px', height: '16px', color: '#9CA3AF' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <span style={{ color: '#9CA3AF', fontSize: '14px', flex: 1, textAlign: 'left' }}>
            検索...
          </span>
          <kbd style={{
            padding: '2px 6px',
            fontSize: '11px',
            color: '#6B7280',
            backgroundColor: 'white',
            border: '1px solid #D1D5DB',
            borderRadius: '4px',
            fontFamily: 'system-ui',
          }}>
            ⌘K
          </kbd>
        </button>

        {/* 中央: デスクトップナビ */}
        <nav style={{
          display: 'flex',
          gap: '24px',
        }} className="desktop-nav">
          {menuItems.map(item => (
            <Link
              key={item.path}
              to={item.path}
              style={{
                fontSize: '14px',
                fontWeight: 500,
                color: isActive(item.path) ? 'var(--color-accent)' : 'var(--color-text-secondary)',
                textDecoration: 'none',
                padding: '8px 0',
                borderBottom: isActive(item.path) ? '2px solid var(--color-accent)' : '2px solid transparent',
                transition: 'color 150ms, border-color 150ms',
                whiteSpace: 'nowrap',
              }}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        {/* 右側: 保存ステータス + ユーザー情報 */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <SaveStatusIndicator />

          {/* テナント名 + ユーザーメニュー */}
          {user && (
            <div style={{ position: 'relative' }}>
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '6px 12px',
                  backgroundColor: '#F3F4F6',
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '13px',
                }}
              >
                <span style={{ fontWeight: 600, color: '#1F2937' }}>
                  {user.organization_name}
                </span>
                <span style={{ color: '#6B7280' }}>|</span>
                <span style={{ color: '#374151' }}>{user.name}</span>
                <svg
                  style={{ width: '16px', height: '16px', color: '#6B7280' }}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {/* ドロップダウンメニュー */}
              {showUserMenu && (
                <>
                  <div
                    style={{
                      position: 'fixed',
                      top: 0,
                      left: 0,
                      right: 0,
                      bottom: 0,
                      zIndex: 999,
                    }}
                    onClick={() => setShowUserMenu(false)}
                  />
                  <div
                    style={{
                      position: 'absolute',
                      top: '100%',
                      right: 0,
                      marginTop: '4px',
                      backgroundColor: 'white',
                      border: '1px solid #E5E7EB',
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                      minWidth: '200px',
                      zIndex: 1000,
                      overflow: 'hidden',
                    }}
                  >
                    <div style={{ padding: '12px 16px', borderBottom: '1px solid #E5E7EB' }}>
                      <div style={{ fontSize: '12px', color: '#6B7280' }}>ログイン中</div>
                      <div style={{ fontWeight: 600, color: '#1F2937' }}>{user.email}</div>
                      <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
                        {user.role_name}
                      </div>
                    </div>
                    <button
                      onClick={handleLogout}
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        backgroundColor: 'transparent',
                        border: 'none',
                        cursor: 'pointer',
                        textAlign: 'left',
                        fontSize: '14px',
                        color: '#DC2626',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                      }}
                      onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#FEF2F2'}
                      onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                    >
                      <svg style={{ width: '16px', height: '16px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                      </svg>
                      ログアウト
                    </button>
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      </header>

      {/* メインコンテンツ */}
      <main style={{
        flex: 1,
        padding: '16px',
        paddingBottom: '80px',
        maxWidth: '1200px',
        width: '100%',
        margin: '0 auto',
        boxSizing: 'border-box',
      }}>
        {children}
      </main>

      {/* ボトムナビゲーション（モバイル） */}
      <nav className="mobile-nav" style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        backgroundColor: 'var(--color-bg-white)',
        borderTop: '1px solid var(--color-border)',
        display: 'flex',
        justifyContent: 'space-around',
        padding: '8px 0',
        paddingBottom: 'max(8px, env(safe-area-inset-bottom))',
        zIndex: 100,
      }}>
        {menuItems.map(item => (
          <Link
            key={item.path}
            to={item.path}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '4px',
              padding: '8px 16px',
              borderRadius: '8px',
              textDecoration: 'none',
              color: isActive(item.path) ? 'var(--color-accent)' : 'var(--color-text-secondary)',
              backgroundColor: isActive(item.path) ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
              transition: 'all 150ms',
              minWidth: '72px',
            }}
          >
            <span style={{ fontSize: '24px' }}>{item.icon}</span>
            <span style={{
              fontSize: '11px',
              fontWeight: isActive(item.path) ? 600 : 500,
            }}>
              {item.label}
            </span>
          </Link>
        ))}
      </nav>

      {/* レスポンシブCSS + アニメーション */}
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        .search-trigger:hover {
          background-color: #E5E7EB !important;
          border-color: #D1D5DB !important;
        }

        .search-trigger:focus {
          outline: none;
          box-shadow: 0 0 0 2px #3B82F6;
        }

        @media (min-width: 768px) {
          .mobile-nav {
            display: none !important;
          }
          .desktop-nav {
            display: flex !important;
          }
        }

        @media (max-width: 767px) {
          .mobile-nav {
            display: flex !important;
          }
          .desktop-nav {
            display: none !important;
          }
          .search-trigger {
            min-width: 44px !important;
            max-width: 44px !important;
            padding: 8px !important;
          }
          .search-trigger span,
          .search-trigger kbd {
            display: none !important;
          }
        }
      `}</style>
    </div>
  );
};

export default Layout;
