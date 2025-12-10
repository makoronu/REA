import React from 'react';
import { Link, useLocation } from 'react-router-dom';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();

  const isActive = (path: string) => {
    if (path === '/properties') {
      return location.pathname === '/' || location.pathname === '/properties';
    }
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  // メニュー項目
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
      {/* ヘッダー - 最小限 */}
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

        {/* デスクトップナビ（768px以上） */}
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
      </header>

      {/* メインコンテンツ - 下部ナビ分のpaddingを確保 */}
      <main style={{
        flex: 1,
        padding: '16px',
        paddingBottom: '80px', // ボトムナビの高さ分
        maxWidth: '1200px',
        width: '100%',
        margin: '0 auto',
        boxSizing: 'border-box',
      }}>
        {children}
      </main>

      {/* ボトムナビゲーション（モバイル） - 親指が届く位置 */}
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
        paddingBottom: 'max(8px, env(safe-area-inset-bottom))', // iPhone対応
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

      {/* レスポンシブCSS */}
      <style>{`
        /* デスクトップ（768px以上）*/
        @media (min-width: 768px) {
          .mobile-nav {
            display: none !important;
          }
          .desktop-nav {
            display: flex !important;
          }
        }

        /* モバイル（768px未満）*/
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
