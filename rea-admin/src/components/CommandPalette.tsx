import { useEffect, useState, useCallback, useRef } from 'react';
import { Command } from 'cmdk';
import { useNavigate } from 'react-router-dom';
import { propertyService } from '../services/propertyService';
import { metadataService } from '../services/metadataService';
import { Property } from '../types/property';
import { parseJapanesePrice, formatPrice } from '../constants';
import { STORAGE_KEYS } from '../constants/storage';

// フィルターオプションの型
interface FilterOption {
  value: string;
  label: string;
}

// 検索履歴の型
interface SearchHistory {
  query: string;
  timestamp: number;
}

// 価格パース（constants.tsから）
const parsePrice = parseJapanesePrice;

// 検索クエリをパース（メタデータ駆動）
const parseSearchQuery = (
  query: string,
  statusOptions: FilterOption[],
  propertyTypeOptions: FilterOption[]
): {
  keywords: string[];
  priceMin?: number;
  priceMax?: number;
  propertyType?: string;
  status?: string;
} => {
  const result: ReturnType<typeof parseSearchQuery> = { keywords: [] };
  const parts = query.split(/\s+/).filter(Boolean);

  // ステータス値のセットを作成（メタデータから）
  const statusValues = new Set(statusOptions.map(opt => opt.value));

  // 物件種別のマッピング（部分一致対応）
  const propertyTypeMap: Record<string, string> = {};
  propertyTypeOptions.forEach(opt => {
    propertyTypeMap[opt.value] = opt.value;
    propertyTypeMap[opt.label] = opt.value;
  });
  // 別名も追加
  propertyTypeMap['戸建'] = '一戸建て';
  propertyTypeMap['戸建て'] = '一戸建て';
  propertyTypeMap['中古戸建'] = '一戸建て';
  propertyTypeMap['売地'] = '土地';

  for (const part of parts) {
    // 価格範囲（1000~2000, 1000万~2000万）
    const rangeMatch = part.match(/(\d+(?:\.\d+)?万?億?)[-~〜](\d+(?:\.\d+)?万?億?)/);
    if (rangeMatch) {
      result.priceMin = parsePrice(rangeMatch[1]) || undefined;
      result.priceMax = parsePrice(rangeMatch[2]) || undefined;
      continue;
    }

    // 価格以下（~1000万, 1000万以下）
    const maxMatch = part.match(/[~〜]?(\d+(?:\.\d+)?万?億?)以?下?$/);
    if (maxMatch && (part.includes('以下') || part.startsWith('~') || part.startsWith('〜'))) {
      result.priceMax = parsePrice(maxMatch[1]) || undefined;
      continue;
    }

    // 価格以上（1000万~, 1000万以上）
    const minMatch = part.match(/^(\d+(?:\.\d+)?万?億?)[~〜]?以?上?/);
    if (minMatch && (part.includes('以上') || part.endsWith('~') || part.endsWith('〜'))) {
      result.priceMin = parsePrice(minMatch[1]) || undefined;
      continue;
    }

    // 物件種別（メタデータ駆動）
    if (propertyTypeMap[part]) {
      result.propertyType = propertyTypeMap[part];
      continue;
    }

    // ステータス（メタデータ駆動）
    if (statusValues.has(part)) {
      result.status = part;
      continue;
    }

    // それ以外はキーワード
    result.keywords.push(part);
  }

  return result;
};

// 検索履歴の最大件数
const MAX_HISTORY = 10;

// 検索履歴を取得
const getSearchHistory = (): SearchHistory[] => {
  try {
    const data = localStorage.getItem(STORAGE_KEYS.SEARCH_HISTORY);
    return data ? JSON.parse(data) : [];
  } catch {
    return [];
  }
};

// 検索履歴を保存
const saveSearchHistory = (query: string) => {
  if (!query.trim()) return;
  const history = getSearchHistory().filter(h => h.query !== query);
  history.unshift({ query, timestamp: Date.now() });
  localStorage.setItem(STORAGE_KEYS.SEARCH_HISTORY, JSON.stringify(history.slice(0, MAX_HISTORY)));
};

interface CommandPaletteProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const CommandPalette = ({ open, onOpenChange }: CommandPaletteProps) => {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [results, setResults] = useState<Property[]>([]);
  const [loading, setLoading] = useState(false);
  const [_selectedIndex, _setSelectedIndex] = useState(0);
  const [history, setHistory] = useState<SearchHistory[]>([]);
  const searchTimeout = useRef<NodeJS.Timeout>();

  // メタデータ駆動のフィルターオプション
  const [filterOptions, setFilterOptions] = useState<{
    sales_status: FilterOption[];
    property_type_simple: FilterOption[];
  }>({
    sales_status: [],
    property_type_simple: [],
  });

  // フィルターオプションをメタデータから取得
  useEffect(() => {
    const loadFilterOptions = async () => {
      try {
        const options = await metadataService.getFilterOptions();
        setFilterOptions({
          sales_status: options.sales_status || [],
          property_type_simple: options.property_type_simple || [],
        });
      } catch (err) {
        console.error('フィルターオプション取得エラー:', err);
      }
    };
    loadFilterOptions();
  }, []);

  // 履歴を読み込み
  useEffect(() => {
    if (open) {
      setHistory(getSearchHistory());
      setSearch('');
      setResults([]);
      _setSelectedIndex(0);
    }
  }, [open]);

  // 検索実行（メタデータ駆動）
  const executeSearch = useCallback(async (query: string) => {
    if (!query.trim()) {
      setResults([]);
      return;
    }

    setLoading(true);
    try {
      const parsed = parseSearchQuery(query, filterOptions.sales_status, filterOptions.property_type_simple);
      const params: any = {
        limit: 10,
      };

      if (parsed.keywords.length > 0) {
        params.search = parsed.keywords.join(' ');
      }
      if (parsed.priceMin) params.sale_price_min = parsed.priceMin;
      if (parsed.priceMax) params.sale_price_max = parsed.priceMax;
      if (parsed.propertyType) params.property_type = parsed.propertyType;
      if (parsed.status) params.sales_status = parsed.status;

      const data = await propertyService.getProperties(params);
      setResults(data);
      _setSelectedIndex(0);
    } catch (err) {
      console.error('検索エラー:', err);
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, [filterOptions]);

  // デバウンス検索
  useEffect(() => {
    if (searchTimeout.current) {
      clearTimeout(searchTimeout.current);
    }
    searchTimeout.current = setTimeout(() => {
      executeSearch(search);
    }, 150);
    return () => {
      if (searchTimeout.current) clearTimeout(searchTimeout.current);
    };
  }, [search, executeSearch]);

  // 価格フォーマット（constants.tsのformatPriceを使用）
  const formatPriceDisplay = (price?: number) => {
    if (!price) return '-';
    return formatPrice(price);
  };

  // 物件を選択
  const selectProperty = (property: Property) => {
    saveSearchHistory(search);
    onOpenChange(false);
    navigate(`/properties/${property.id}/edit`);
  };

  // 履歴から検索
  const searchFromHistory = (query: string) => {
    setSearch(query);
  };

  // コマンド実行
  const executeCommand = (command: string) => {
    saveSearchHistory(command);
    onOpenChange(false);

    switch (command) {
      case '/new':
        navigate('/properties/new');
        break;
      case '/list':
        navigate('/properties');
        break;
      default:
        if (command.startsWith('/edit ')) {
          const id = command.replace('/edit ', '').trim();
          if (id) navigate(`/properties/${id}/edit`);
        }
    }
  };

  // コマンドかどうか判定
  const isCommand = search.startsWith('/');

  return (
    <Command.Dialog
      open={open}
      onOpenChange={onOpenChange}
      label="コマンドパレット"
      className="fixed inset-0 z-50"
    >
      {/* オーバーレイ */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm"
        onClick={() => onOpenChange(false)}
      />

      {/* パレット本体 */}
      <div className="fixed top-[20%] left-1/2 -translate-x-1/2 w-full max-w-2xl">
        <div className="bg-white rounded-2xl shadow-2xl overflow-hidden border border-gray-200">
          {/* 検索入力 */}
          <div className="flex items-center px-4 border-b border-gray-100">
            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <Command.Input
              value={search}
              onValueChange={setSearch}
              placeholder="物件を検索... (例: 北見 1000万以下 戸建)"
              className="flex-1 px-4 py-4 text-lg outline-none placeholder:text-gray-400"
              autoFocus
            />
            {loading && (
              <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            )}
            <kbd className="hidden sm:inline-flex items-center px-2 py-1 text-xs text-gray-400 bg-gray-100 rounded ml-2">
              ESC
            </kbd>
          </div>

          {/* 結果リスト */}
          <Command.List className="max-h-[400px] overflow-y-auto p-2">
            {/* ローディング */}
            {loading && search && (
              <div className="px-4 py-8 text-center text-gray-500">
                検索中...
              </div>
            )}

            {/* コマンドモード */}
            {isCommand && !loading && (
              <Command.Group heading="コマンド">
                <Command.Item
                  value="/new"
                  onSelect={() => executeCommand('/new')}
                  className="flex items-center gap-3 px-4 py-3 rounded-lg cursor-pointer data-[selected=true]:bg-blue-50 hover:bg-gray-50"
                >
                  <span className="w-8 h-8 flex items-center justify-center bg-green-100 text-green-600 rounded-lg">+</span>
                  <div>
                    <div className="font-medium text-gray-900">新規物件登録</div>
                    <div className="text-sm text-gray-500">/new</div>
                  </div>
                </Command.Item>
                <Command.Item
                  value="/list"
                  onSelect={() => executeCommand('/list')}
                  className="flex items-center gap-3 px-4 py-3 rounded-lg cursor-pointer data-[selected=true]:bg-blue-50 hover:bg-gray-50"
                >
                  <span className="w-8 h-8 flex items-center justify-center bg-blue-100 text-blue-600 rounded-lg">☰</span>
                  <div>
                    <div className="font-medium text-gray-900">物件一覧</div>
                    <div className="text-sm text-gray-500">/list</div>
                  </div>
                </Command.Item>
              </Command.Group>
            )}

            {/* 検索結果 */}
            {!isCommand && results.length > 0 && (
              <Command.Group heading={`検索結果 (${results.length}件)`}>
                {results.map((property) => (
                  <Command.Item
                    key={property.id}
                    value={`${property.id} ${property.property_name}`}
                    onSelect={() => selectProperty(property)}
                    className="flex items-center gap-3 px-4 py-3 rounded-lg cursor-pointer data-[selected=true]:bg-blue-50 hover:bg-gray-50 group"
                  >
                    <span className="w-10 h-10 flex items-center justify-center bg-gray-100 text-gray-600 rounded-lg text-sm font-medium">
                      {property.company_property_number || property.id}
                    </span>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-gray-900 truncate">
                        {property.property_name || '(名称なし)'}
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-500">
                        <span className="font-semibold text-gray-700">{formatPriceDisplay(property.sale_price)}</span>
                        <span>·</span>
                        <span>{property.property_type?.replace(/【.*?】/, '') || '-'}</span>
                        {property.sales_status && (
                          <>
                            <span>·</span>
                            <span className={
                              property.sales_status === '販売中' ? 'text-green-600' :
                              property.sales_status === '成約済' ? 'text-blue-600' : ''
                            }>
                              {property.sales_status}
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                    <div className="hidden group-hover:flex items-center gap-1 text-xs text-gray-400">
                      <kbd className="px-1.5 py-0.5 bg-gray-100 rounded">Enter</kbd>
                      <span>で編集</span>
                    </div>
                  </Command.Item>
                ))}
              </Command.Group>
            )}

            {/* 検索履歴 */}
            {!isCommand && !search && history.length > 0 && (
              <Command.Group heading="最近の検索">
                {history.map((h, i) => (
                  <Command.Item
                    key={i}
                    value={`history-${h.query}`}
                    onSelect={() => searchFromHistory(h.query)}
                    className="flex items-center gap-3 px-4 py-3 rounded-lg cursor-pointer data-[selected=true]:bg-blue-50 hover:bg-gray-50"
                  >
                    <span className="w-8 h-8 flex items-center justify-center text-gray-400">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </span>
                    <span className="text-gray-700">{h.query}</span>
                  </Command.Item>
                ))}
              </Command.Group>
            )}

            {/* 空状態 */}
            {!isCommand && search && !loading && results.length === 0 && (
              <div className="px-4 py-8 text-center text-gray-500">
                <div className="text-lg mb-2">該当する物件がありません</div>
                <div className="text-sm">検索条件を変えてお試しください</div>
              </div>
            )}

            {/* ヒント */}
            {!search && history.length === 0 && (
              <div className="px-4 py-6 text-center text-gray-500">
                <div className="text-sm mb-4">検索のヒント</div>
                <div className="flex flex-wrap justify-center gap-2 text-xs">
                  <span className="px-2 py-1 bg-gray-100 rounded">北見</span>
                  <span className="px-2 py-1 bg-gray-100 rounded">1000万以下</span>
                  <span className="px-2 py-1 bg-gray-100 rounded">戸建</span>
                  <span className="px-2 py-1 bg-gray-100 rounded">販売中</span>
                  <span className="px-2 py-1 bg-gray-100 rounded">/new</span>
                </div>
              </div>
            )}
          </Command.List>

          {/* フッター */}
          <div className="flex items-center justify-between px-4 py-2 border-t border-gray-100 bg-gray-50 text-xs text-gray-500">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 bg-white border rounded shadow-sm">↑↓</kbd>
                移動
              </span>
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 bg-white border rounded shadow-sm">Enter</kbd>
                選択
              </span>
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 bg-white border rounded shadow-sm">ESC</kbd>
                閉じる
              </span>
            </div>
            <div>
              <kbd className="px-1.5 py-0.5 bg-white border rounded shadow-sm">⌘K</kbd>
              でいつでも開く
            </div>
          </div>
        </div>
      </div>
    </Command.Dialog>
  );
};

export default CommandPalette;
