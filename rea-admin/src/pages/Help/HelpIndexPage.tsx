/**
 * ヘルプセンター トップページ
 * Notion風カードレイアウトでカテゴリを表示
 */

import { Link } from 'react-router-dom';
import { HELP_CATEGORIES } from '../../constants/help';

export const HelpIndexPage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto">
      {/* ヘッダー */}
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          📖 ヘルプセンター
        </h1>
        <p className="text-gray-600">
          物件データの入力方法を確認できます
        </p>
      </div>

      {/* カテゴリカード */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {HELP_CATEGORIES.map((category) => (
          <Link
            key={category.id}
            to={`/help/${category.id}`}
            className="block p-6 bg-white rounded-xl border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all duration-200 group"
          >
            <div className="flex items-start gap-4">
              {/* アイコン */}
              <div className="text-3xl flex-shrink-0">
                {category.icon}
              </div>

              {/* テキスト */}
              <div className="flex-1 min-w-0">
                <h2 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                  {category.title}
                </h2>
                <p className="text-sm text-gray-500 mt-1">
                  {category.description}
                </p>
              </div>

              {/* 矢印 */}
              <div className="text-gray-400 group-hover:text-blue-500 group-hover:translate-x-1 transition-all">
                →
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* フッター */}
      <div className="mt-8 text-center text-sm text-gray-400">
        お探しの情報が見つからない場合は管理者にお問い合わせください
      </div>
    </div>
  );
};

export default HelpIndexPage;
