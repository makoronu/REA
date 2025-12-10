import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useSaveStatusDisplay, SaveStatus } from '../../hooks/useAutoSave';

interface LayoutProps {
  children: React.ReactNode;
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
        return null; // 何も表示しない
      case 'unsaved':
        return {
          icon: '●',
          text: '変更あり',
          color: '#F59E0B', // オレンジ
        };
      case 'saving':
        return {
          icon: '↻',
          text: '保存中...',
          color: '#3B82F6', // 青
          animate: true,
        };
      case 'saved':
        return {
          icon: '✓',
          text: `保存済み ${formatTime(lastSaved)}`,
          color: '#9CA3AF', // 薄いグレー
        };
      case 'error':
        return {
          icon: '✗',
          text: '保存失敗',
          color: '#EF4444', // 赤
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

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();

  const isActive = (path: string) => {
    if (path === '/properties') {
      return location.pathname === '/' || location.pathname === '/properties';
    }
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  const menuItems = [
    { path: '/properties', label: '物件一覧', icon: '🏠' },
    { path: '/properties/new', label: '新規登録', icon: '➕' },
    { path: '/import/touki', label: '登記取込', icon: '📄' },
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
              }}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        {/* 右側: 保存ステータス（常時表示） */}
        <SaveStatusIndicator />
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
        }
      `}</style>
    </div>
  );
};

export default Layout;
