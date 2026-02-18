/**
 * 登記事項証明書インポートページ
 *
 * 機能:
 * - PDFアップロード
 * - PDFパース
 * - 登記レコード一覧表示
 * - 物件登録
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import { API_PATHS } from '../../constants/apiPaths';
import { api } from '../../services/api';

// 型定義
interface Owner {
  name: string;
  share?: string;
  address?: string;
  acquisition_date?: string;
  acquisition_reason?: string;
}

interface ToukiRecord {
  id: number;
  real_estate_number: string;
  document_type: 'land' | 'building' | 'unit';
  location: string;
  lot_number?: string;
  land_category?: string;
  land_area_m2?: number;
  building_number?: string;
  building_type?: string;
  structure?: string;
  floor_area_m2?: number;
  floor_areas?: Record<string, number>;
  construction_date?: string;
  owners: Owner[];
  created_at: string;
}

interface ToukiImport {
  id: number;
  file_name: string;
  status: string;
  parsed_at?: string;
  created_at: string;
}

export default function ToukiImportPage() {
  // 状態
  const [records, setRecords] = useState<ToukiRecord[]>([]);
  const [imports, setImports] = useState<ToukiImport[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [parsing, setParsingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [registering, setRegistering] = useState(false);
  const [showApplyModal, setShowApplyModal] = useState(false);
  const [applyPropertyId, setApplyPropertyId] = useState<string>('');
  const [applying, setApplying] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 初回読み込み
  useEffect(() => {
    loadData();
  }, []);

  // データ読み込み
  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      // 登記レコード一覧を取得
      const recordsRes = await api.get(API_PATHS.TOUKI.RECORDS_LIST);
      setRecords(recordsRes.data.items || []);

      // インポート一覧を取得
      const importsRes = await api.get(API_PATHS.TOUKI.LIST);
      setImports(importsRes.data.imports || []);
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  };

  // PDFアップロード（共通処理）
  const uploadFiles = useCallback(async (files: File[]) => {
    const pdfFiles = files.filter(f => f.name.toLowerCase().endsWith('.pdf'));
    if (pdfFiles.length === 0) {
      setError('PDFファイルを選択してください');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(null);

    try {
      for (const file of pdfFiles) {
        const formData = new FormData();
        formData.append('file', file);

        await api.post(API_PATHS.TOUKI.UPLOAD, formData);
      }
      setSuccess(`${pdfFiles.length}件のPDFをアップロードしました`);
      await loadData();
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  }, []);

  // ファイル選択
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      uploadFiles(Array.from(files));
    }
  };

  // ドラッグ&ドロップ
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      uploadFiles(files);
    }
  }, [uploadFiles]);

  // PDFパース
  const handleParse = async (importId: number) => {
    setParsingId(importId);
    setError(null);
    setSuccess(null);

    try {
      const res = await api.post(API_PATHS.TOUKI.parse(importId));

      const recordIds = res.data.touki_record_ids || [];

      setSuccess(`解析完了: ${recordIds.length}件の登記レコードを作成しました`);
      await loadData();
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setParsingId(null);
    }
  };


  // 登記レコード削除
  const handleDeleteRecord = async (recordId: number) => {
    if (!confirm('この登記レコードを削除しますか？')) return;

    setError(null);
    try {
      await api.delete(API_PATHS.TOUKI.record(recordId));

      await loadData();
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message);
    }
  };

  // 既存物件に反映（反映後、登記レコードは削除）
  const handleApplyToProperty = async () => {
    const propertyId = parseInt(applyPropertyId);
    if (!propertyId || isNaN(propertyId)) {
      setError('物件IDを入力してください');
      return;
    }

    if (selectedIds.size === 0) {
      setError('登記を選択してください');
      return;
    }

    setApplying(true);
    setError(null);
    setSuccess(null);

    try {
      const res = await api.post(API_PATHS.TOUKI.RECORDS_APPLY, {
        property_id: propertyId,
        touki_record_ids: Array.from(selectedIds)
      });

      setSuccess(res.data.message);
      setShowApplyModal(false);
      setApplyPropertyId('');
      setSelectedIds(new Set());
      await loadData();

      // 物件編集ページを開く
      window.open(`/properties/${propertyId}/edit`, '_blank');
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setApplying(false);
    }
  };

  // 選択トグル
  const toggleSelect = (id: number) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  // 全選択/全解除
  const toggleSelectAll = () => {
    if (selectedIds.size === records.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(records.map(r => r.id)));
    }
  };

  // 選択した登記をまとめて物件登録
  const handleBulkRegister = async () => {
    if (selectedIds.size === 0) {
      setError('登記を選択してください');
      return;
    }

    setRegistering(true);
    setError(null);
    setSuccess(null);

    try {
      const res = await api.post(API_PATHS.TOUKI.RECORDS_CREATE, {
        touki_record_ids: Array.from(selectedIds)
      });

      const result = res.data;

      // 登記レコードを削除（一時データなので）
      for (const id of selectedIds) {
        await api.delete(API_PATHS.TOUKI.record(id));
      }

      setSuccess(result.message);
      setSelectedIds(new Set());
      await loadData();

      // 編集ページを新しいタブで開く
      window.open(`/properties/${result.property_id}/edit`, '_blank');
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setRegistering(false);
    }
  };

  // 種別表示
  const getDocTypeLabel = (type: string) => {
    switch (type) {
      case 'land': return '土地';
      case 'building': return '建物';
      case 'unit': return '区分建物';
      default: return type;
    }
  };

  // ローディング中
  if (loading) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">登記取込</h1>
        <div className="flex items-center gap-2 text-gray-500">
          <div className="animate-spin h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full"></div>
          読み込み中...
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-5xl">
      <h1 className="text-2xl font-bold mb-4">登記取込</h1>

      {/* メッセージ表示 */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}
      {success && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
          {success}
        </div>
      )}

      {/* PDFアップロード（ドラッグ&ドロップ対応） */}
      <div className="mb-6">
        <h2 className="text-lg font-medium mb-3">PDFアップロード</h2>
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`
            border-2 border-dashed rounded-lg p-8 text-center transition-colors
            ${isDragging
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 bg-gray-50 hover:border-gray-400'
            }
            ${uploading ? 'opacity-50 pointer-events-none' : 'cursor-pointer'}
          `}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            multiple
            onChange={handleFileSelect}
            disabled={uploading}
            className="hidden"
          />

          {uploading ? (
            <div className="flex flex-col items-center gap-2">
              <div className="animate-spin h-8 w-8 border-3 border-blue-500 border-t-transparent rounded-full"></div>
              <span className="text-gray-600">アップロード中...</span>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-2">
              <div className="text-4xl">📄</div>
              <div className="text-gray-700 font-medium">
                PDFファイルをドラッグ&ドロップ
              </div>
              <div className="text-gray-500 text-sm">
                または<span className="text-blue-600 underline">クリックして選択</span>
              </div>
              <div className="text-gray-400 text-xs mt-2">
                複数ファイル対応
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 未パースのインポート */}
      {imports.filter(i => i.status === 'uploaded').length > 0 && (
        <div className="mb-6">
          <h2 className="text-lg font-medium mb-3">未解析のPDF</h2>
          <div className="border rounded-lg divide-y">
            {imports.filter(i => i.status === 'uploaded').map(imp => (
              <div key={imp.id} className="p-3 flex items-center justify-between">
                <div>
                  <span className="font-medium">{imp.file_name}</span>
                  <span className="ml-2 text-xs text-gray-500">
                    {new Date(imp.created_at).toLocaleString('ja-JP')}
                  </span>
                </div>
                <button
                  onClick={() => handleParse(imp.id)}
                  disabled={parsing === imp.id}
                  className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 transition disabled:opacity-50"
                >
                  {parsing === imp.id ? '解析中...' : '解析'}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 登記レコード一覧 */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-4">
            <h2 className="text-lg font-medium">取込待ち ({records.length}件)</h2>
            {records.length > 0 && (
              <button
                onClick={toggleSelectAll}
                className="px-2 py-1 text-xs bg-gray-100 rounded hover:bg-gray-200"
              >
                {selectedIds.size === records.length ? '全解除' : '全選択'}
              </button>
            )}
          </div>
          <button
            onClick={loadData}
            className="px-3 py-1 text-sm bg-gray-100 rounded hover:bg-gray-200"
          >
            更新
          </button>
        </div>

        {/* アクションバー */}
        {selectedIds.size > 0 && (
          <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center justify-between flex-wrap gap-3">
              <div>
                <span className="font-medium text-blue-800">
                  {selectedIds.size}件の登記を選択中
                </span>
                <span className="ml-2 text-sm text-blue-600">
                  （土地{records.filter(r => selectedIds.has(r.id) && r.document_type === 'land').length}筆、
                  建物{records.filter(r => selectedIds.has(r.id) && r.document_type !== 'land').length}棟）
                </span>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setShowApplyModal(true)}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium"
                >
                  既存物件へ反映
                </button>
                <button
                  onClick={handleBulkRegister}
                  disabled={registering}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 font-medium"
                >
                  {registering ? '登録中...' : '新規物件登録'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 既存物件へ反映モーダル */}
        {showApplyModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-96 max-w-[90vw]">
              <h3 className="text-lg font-bold mb-4">既存物件へ登記情報を反映</h3>
              <p className="text-sm text-gray-600 mb-4">
                選択した{selectedIds.size}件の登記情報を既存物件に反映します。
                土地情報・建物情報が更新されます。
              </p>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  物件ID
                </label>
                <input
                  type="number"
                  value={applyPropertyId}
                  onChange={(e) => setApplyPropertyId(e.target.value)}
                  placeholder="例: 2480"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  autoFocus
                />
              </div>
              <div className="flex gap-2 justify-end">
                <button
                  onClick={() => {
                    setShowApplyModal(false);
                    setApplyPropertyId('');
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
                >
                  キャンセル
                </button>
                <button
                  onClick={handleApplyToProperty}
                  disabled={applying || !applyPropertyId}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition disabled:opacity-50"
                >
                  {applying ? '反映中...' : '反映する'}
                </button>
              </div>
            </div>
          </div>
        )}

        {records.length === 0 ? (
          <div className="p-8 text-center text-gray-500 border rounded-lg">
            取込待ちデータがありません。PDFをアップロードしてください。
          </div>
        ) : (
          <div className="border rounded-lg divide-y">
            {records.map(record => (
              <label
                key={record.id}
                className={`block p-4 cursor-pointer transition ${
                  selectedIds.has(record.id) ? 'bg-blue-50' : 'hover:bg-gray-50'
                }`}
              >
                <div className="flex items-start gap-3">
                  {/* チェックボックス */}
                  <input
                    type="checkbox"
                    checked={selectedIds.has(record.id)}
                    onChange={() => toggleSelect(record.id)}
                    className="mt-1 w-5 h-5 rounded border-gray-300"
                  />

                  <div className="flex-1">
                    {/* ヘッダー */}
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`px-2 py-0.5 text-xs rounded ${
                        record.document_type === 'land'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-blue-100 text-blue-700'
                      }`}>
                        {getDocTypeLabel(record.document_type)}
                      </span>
                      <span className="text-sm text-gray-500">
                        不動産番号: {record.real_estate_number || '-'}
                      </span>
                    </div>

                    {/* 所在 */}
                    <div className="font-medium mb-2">{record.location}</div>

                    {/* 詳細情報 */}
                    <div className="text-sm text-gray-600 space-y-1">
                      {record.document_type === 'land' ? (
                        <>
                          {record.lot_number && <div>地番: {record.lot_number}</div>}
                          {record.land_category && <div>地目: {record.land_category}</div>}
                          {record.land_area_m2 && <div>地積: {record.land_area_m2}㎡</div>}
                        </>
                      ) : (
                        <>
                          {record.building_number && <div>家屋番号: {record.building_number}</div>}
                          {record.structure && <div>構造: {record.structure}</div>}
                          {record.floor_area_m2 && <div>床面積: {record.floor_area_m2}㎡</div>}
                          {record.floor_areas && Object.keys(record.floor_areas).length > 0 && (
                            <div>
                              階別床面積:
                              {Object.entries(record.floor_areas).map(([floor, area]) => (
                                <span key={floor} className="ml-2">{floor}: {area}㎡</span>
                              ))}
                            </div>
                          )}
                        </>
                      )}

                      {/* 所有者 */}
                      {record.owners && record.owners.length > 0 && (
                        <div className="mt-2 pt-2 border-t">
                          <div className="font-medium text-gray-700 mb-1">所有者情報</div>
                          {record.owners.map((owner, i) => (
                            <div key={i} className="ml-2 mb-1">
                              <div>氏名: {owner.name}{owner.share && ` (持分: ${owner.share})`}</div>
                              {owner.address && <div className="text-gray-500">住所: {owner.address}</div>}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* 破棄ボタン */}
                  <button
                    onClick={(e) => { e.preventDefault(); handleDeleteRecord(record.id); }}
                    className="px-3 py-1 text-gray-400 hover:text-red-500 transition text-sm"
                    title="この登記を破棄"
                  >
                    ✕
                  </button>
                </div>
              </label>
            ))}
          </div>
        )}
      </div>

      {/* 使い方 */}
      <div className="p-4 bg-gray-50 rounded-lg text-sm text-gray-600">
        <h3 className="font-medium text-gray-800 mb-2">使い方</h3>
        <ol className="list-decimal list-inside space-y-1">
          <li>登記事項証明書のPDFをドラッグ&ドロップ（複数可）</li>
          <li>「解析」ボタンでPDFの内容を読み取り</li>
          <li>1物件にまとめたい登記をチェックで選択（土地数筆＋建物1棟）</li>
          <li>「まとめて物件登録」ボタンで物件DBに登録</li>
        </ol>
        <p className="mt-2 text-xs text-gray-500">
          ※ 登記データは物件登録後に自動削除されます
        </p>
      </div>
    </div>
  );
}
