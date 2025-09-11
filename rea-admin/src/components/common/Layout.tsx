import React from 'react';
import { Link, useLocation } from 'react-router-dom';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* ヘッダー */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">REA 不動産管理システム</h1>
            </div>
            <nav className="flex space-x-8">
              <Link
                to="/properties"
                className={`text-sm font-medium ${
                  isActive('/properties')
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-500 hover:text-gray-700'
                } pb-1`}
              >
                物件管理
              </Link>
              <Link
                to="/import/touki"
                className={`text-sm font-medium ${
                  isActive('/import/touki')
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-500 hover:text-gray-700'
                } pb-1`}
              >
                登記簿取込
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* サイドバーとメインコンテンツ */}
      <div className="flex">
        {/* サイドバー */}
        <aside className="w-64 bg-white shadow-md min-h-screen">
          <nav className="mt-8">
            <div className="px-4">
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                メニュー
              </h3>
              <ul className="space-y-2">
                <li>
                  <Link
                    to="/properties"
                    className={`block px-4 py-2 rounded-md text-sm font-medium ${
                      isActive('/properties')
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    物件一覧
                  </Link>
                </li>
                <li>
                  <Link
                    to="/properties/new"
                    className={`block px-4 py-2 rounded-md text-sm font-medium ${
                      location.pathname === '/properties/new'
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    新規物件登録
                  </Link>
                </li>
              </ul>
            </div>

            <div className="px-4 mt-8">
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                インポート
              </h3>
              <ul className="space-y-2">
                <li>
                  <Link
                    to="/import/touki"
                    className={`block px-4 py-2 rounded-md text-sm font-medium ${
                      isActive('/import/touki')
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    登記簿PDF取込
                  </Link>
                </li>
              </ul>
            </div>
          </nav>
        </aside>

        {/* メインコンテンツ */}
        <main className="flex-1 p-8">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;