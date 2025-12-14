/**
 * 登記事項証明書インポートページ
 *
 * 機能:
 * - PDFアップロード
 * - PDFパース
 * - 登記レコード一覧表示
 * - 物件登録
 */
import { useState, useEffect, useRef } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005';

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
  filename: string;
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
  const [creating, setCreatingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
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
      const recordsRes = await fetch(`${API_URL}/api/v1/touki/records/list`);
      if (!recordsRes.ok) throw new Error('登記レコードの取得に失敗しました');
      const recordsData = await recordsRes.json();
      setRecords(recordsData.items || []);

      // インポート一覧を取得
      const importsRes = await fetch(`${API_URL}/api/v1/touki/list`);
      if (!importsRes.ok) throw new Error('インポート一覧の取得に失敗しました');
      const importsData = await importsRes.json();
      setImports(importsData.imports || []);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  // PDFアップロード
  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);
    setError(null);
    setSuccess(null);

    try {
      for (const file of Array.from(files)) {
        const formData = new FormData();
        formData.append('file', file);

        const res = await fetch(`${API_URL}/api/v1/touki/upload`, {
          method: 'POST',
          body: formData,
        });

        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || 'アップロードに失敗しました');
        }
      }
      setSuccess(`${files.length}件のPDFをアップロードしました`);
      await loadData();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  // PDFパース
  const handleParse = async (importId: number) => {
    setParsingId(importId);
    setError(null);
    setSuccess(null);

    try {
      const res = await fetch(`${API_URL}/api/v1/touki/parse/${importId}`, {
        method: 'POST',
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'パースに失敗しました');
      }

      setSuccess('PDFを解析しました');
      await loadData();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setParsingId(null);
    }
  };

  // 物件登録
  const handleCreateProperty = async (record: ToukiRecord) => {
    setCreatingId(record.id);
    setError(null);
    setSuccess(null);

    try {
      const payload = record.document_type === 'land'
        ? { land_touki_record_id: record.id }
        : { building_touki_record_id: record.id };

      const res = await fetch(`${API_URL}/api/v1/touki/records/create-property`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || '物件登録に失敗しました');
      }

      const result = await res.json();
      setSuccess(`物件ID ${result.property_id} を登録しました`);

      // 編集ページを新しいタブで開く
      window.open(`/properties/${result.property_id}/edit`, '_blank');
    } catch (e: any) {
      setError(e.message);
    } finally {
      setCreatingId(null);
    }
  };

  // 登記レコード削除
  const handleDeleteRecord = async (recordId: number) => {
    if (!confirm('この登記レコードを削除しますか？')) return;

    setError(null);
    try {
      const res = await fetch(`${API_URL}/api/v1/touki/records/${recordId}`, {
        method: 'DELETE',
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || '削除に失敗しました');
      }

      await loadData();
    } catch (e: any) {
      setError(e.message);
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

      {/* PDFアップロード */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <h2 className="text-lg font-medium mb-3">PDFアップロード</h2>
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition cursor-pointer">
            <span>📄 PDFを選択</span>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              multiple
              onChange={handleUpload}
              disabled={uploading}
              className="hidden"
            />
          </label>
          {uploading && (
            <span className="text-gray-500 flex items-center gap-2">
              <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
              アップロード中...
            </span>
          )}
        </div>
        <p className="mt-2 text-sm text-gray-500">
          登記事項証明書のPDFファイルをアップロードしてください。複数ファイル可。
        </p>
      </div>

      {/* 未パースのインポート */}
      {imports.filter(i => i.status === 'pending').length > 0 && (
        <div className="mb-6">
          <h2 className="text-lg font-medium mb-3">未解析のPDF</h2>
          <div className="border rounded-lg divide-y">
            {imports.filter(i => i.status === 'pending').map(imp => (
              <div key={imp.id} className="p-3 flex items-center justify-between">
                <div>
                  <span className="font-medium">{imp.filename}</span>
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
          <h2 className="text-lg font-medium">登記レコード ({records.length}件)</h2>
          <button
            onClick={loadData}
            className="px-3 py-1 text-sm bg-gray-100 rounded hover:bg-gray-200"
          >
            更新
          </button>
        </div>

        {records.length === 0 ? (
          <div className="p-8 text-center text-gray-500 border rounded-lg">
            登記レコードがありません。PDFをアップロード・解析してください。
          </div>
        ) : (
          <div className="border rounded-lg divide-y">
            {records.map(record => (
              <div key={record.id} className="p-4">
                <div className="flex items-start justify-between">
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
                          所有者:
                          {record.owners.map((owner, i) => (
                            <span key={i} className="ml-2">
                              {owner.name}
                              {owner.share && ` (${owner.share})`}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* アクション */}
                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => handleCreateProperty(record)}
                      disabled={creating === record.id}
                      className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition disabled:opacity-50"
                    >
                      {creating === record.id ? '登録中...' : '物件登録'}
                    </button>
                    <button
                      onClick={() => handleDeleteRecord(record.id)}
                      className="px-3 py-1 text-red-600 border border-red-200 rounded hover:bg-red-50 transition"
                    >
                      削除
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 使い方 */}
      <div className="p-4 bg-gray-50 rounded-lg text-sm text-gray-600">
        <h3 className="font-medium text-gray-800 mb-2">使い方</h3>
        <ol className="list-decimal list-inside space-y-1">
          <li>登記事項証明書のPDFをアップロード</li>
          <li>「解析」ボタンでPDFの内容を読み取り</li>
          <li>読み取った情報を確認</li>
          <li>「物件登録」ボタンで物件DBに登録</li>
        </ol>
      </div>
    </div>
  );
}
