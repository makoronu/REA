/**
 * ヘルプ詳細ページ
 * アコーディオン形式でMDコンテンツを表示
 */

import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { ParsedHelp, HelpSection } from '../../types/help';
import { getHelpCategoryById } from '../../constants/help';
import { fetchAndParseMarkdown } from '../../utils/markdownParser';

/** アコーディオンアイテム */
interface AccordionItemProps {
  title: string;
  content: string;
  isOpen: boolean;
  onToggle: () => void;
}

const AccordionItem: React.FC<AccordionItemProps> = ({
  title,
  content,
  isOpen,
  onToggle,
}) => {
  return (
    <div className="border border-gray-200 rounded-lg mb-2 overflow-hidden">
      {/* ヘッダー */}
      <button
        onClick={onToggle}
        className="w-full px-4 py-3 flex items-center justify-between bg-white hover:bg-gray-50 transition-colors text-left"
      >
        <span className="font-medium text-gray-900">{title}</span>
        <span
          className={`text-gray-400 transition-transform duration-200 ${
            isOpen ? 'rotate-180' : ''
          }`}
        >
          ▼
        </span>
      </button>

      {/* コンテンツ */}
      {isOpen && (
        <div className="px-4 py-4 bg-gray-50 border-t border-gray-200">
          <div className="prose prose-sm max-w-none prose-gray">
            <ReactMarkdown
              components={{
                // スタイルカスタマイズ
                p: ({ children }) => (
                  <p className="mb-3 text-gray-700 leading-relaxed">{children}</p>
                ),
                ul: ({ children }) => (
                  <ul className="list-disc pl-5 mb-3 space-y-1">{children}</ul>
                ),
                li: ({ children }) => (
                  <li className="text-gray-700">{children}</li>
                ),
                strong: ({ children }) => (
                  <strong className="font-semibold text-gray-900">{children}</strong>
                ),
                table: ({ children }) => (
                  <div className="overflow-x-auto mb-3">
                    <table className="min-w-full border border-gray-300 text-sm">
                      {children}
                    </table>
                  </div>
                ),
                th: ({ children }) => (
                  <th className="border border-gray-300 px-3 py-2 bg-gray-100 font-medium text-left">
                    {children}
                  </th>
                ),
                td: ({ children }) => (
                  <td className="border border-gray-300 px-3 py-2">{children}</td>
                ),
              }}
            >
              {content}
            </ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
};

/** セクション表示 */
interface SectionProps {
  section: HelpSection;
  openItems: Set<string>;
  onToggleItem: (itemId: string) => void;
}

const Section: React.FC<SectionProps> = ({ section, openItems, onToggleItem }) => {
  return (
    <div className="mb-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
        <span className="w-1 h-5 bg-blue-500 rounded-full" />
        {section.title}
      </h2>
      <div>
        {section.items.map((item) => (
          <AccordionItem
            key={item.id}
            title={item.title}
            content={item.content}
            isOpen={openItems.has(item.id)}
            onToggle={() => onToggleItem(item.id)}
          />
        ))}
      </div>
    </div>
  );
};

/** メインコンポーネント */
export const HelpDetailPage: React.FC = () => {
  const { categoryId } = useParams<{ categoryId: string }>();
  const [parsedHelp, setParsedHelp] = useState<ParsedHelp | null>(null);
  const [openItems, setOpenItems] = useState<Set<string>>(new Set());
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const category = categoryId ? getHelpCategoryById(categoryId) : undefined;

  useEffect(() => {
    const loadContent = async () => {
      if (!category) {
        setError('カテゴリが見つかりません');
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError(null);
        const data = await fetchAndParseMarkdown(category.file);
        setParsedHelp(data);
      } catch (err) {
        setError('コンテンツの読み込みに失敗しました');
        console.error('Failed to load help content:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadContent();
  }, [category]);

  const handleToggleItem = (itemId: string) => {
    setOpenItems((prev) => {
      const next = new Set(prev);
      if (next.has(itemId)) {
        next.delete(itemId);
      } else {
        next.add(itemId);
      }
      return next;
    });
  };

  const handleExpandAll = () => {
    if (!parsedHelp) return;
    const allIds = new Set<string>();
    parsedHelp.sections.forEach((section) => {
      section.items.forEach((item) => allIds.add(item.id));
    });
    setOpenItems(allIds);
  };

  const handleCollapseAll = () => {
    setOpenItems(new Set());
  };

  // ローディング
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-500">読み込み中...</div>
      </div>
    );
  }

  // エラー
  if (error || !parsedHelp) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          {error || 'エラーが発生しました'}
        </div>
        <Link
          to="/help"
          className="inline-block mt-4 text-blue-600 hover:underline"
        >
          ← ヘルプセンターに戻る
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* パンくずリスト */}
      <div className="mb-4 text-sm">
        <Link to="/help" className="text-blue-600 hover:underline">
          ヘルプセンター
        </Link>
        <span className="mx-2 text-gray-400">/</span>
        <span className="text-gray-600">{category?.title}</span>
      </div>

      {/* ヘッダー */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-3xl">{category?.icon}</span>
          <h1 className="text-2xl font-bold text-gray-900">
            {parsedHelp.title}
          </h1>
        </div>
        <p className="text-gray-600">{parsedHelp.description}</p>
      </div>

      {/* 操作ボタン */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={handleExpandAll}
          className="px-3 py-1.5 text-sm text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
        >
          すべて開く
        </button>
        <button
          onClick={handleCollapseAll}
          className="px-3 py-1.5 text-sm text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
        >
          すべて閉じる
        </button>
      </div>

      {/* セクション一覧 */}
      {parsedHelp.sections.map((section) => (
        <Section
          key={section.id}
          section={section}
          openItems={openItems}
          onToggleItem={handleToggleItem}
        />
      ))}

      {/* フッター */}
      <div className="mt-8 pt-4 border-t border-gray-200">
        <Link
          to="/help"
          className="text-blue-600 hover:underline flex items-center gap-1"
        >
          ← ヘルプセンターに戻る
        </Link>
      </div>
    </div>
  );
};

export default HelpDetailPage;
