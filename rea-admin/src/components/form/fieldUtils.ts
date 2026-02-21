/**
 * fieldUtils: フォームフィールド共通ユーティリティ
 *
 * FieldFactory / SelectionFields / PostalCodeField 等で共有する定数・関数
 */
import type { CSSProperties } from 'react';

// 読み取り専用フィールド一覧
export const READONLY_FIELDS = ['homes_record_id'];

// データ型から入力タイプを推測
export const getInputTypeFromDataType = (dataType?: string): string => {
  if (!dataType) return 'text';
  const lowerType = dataType.toLowerCase();
  if (lowerType.includes('int') || lowerType.includes('numeric') || lowerType.includes('decimal')) return 'number';
  if (lowerType.includes('bool')) return 'checkbox';
  if (lowerType.includes('date') && !lowerType.includes('datetime')) return 'date';
  if (lowerType.includes('datetime') || lowerType.includes('timestamp')) return 'datetime';
  return 'text';
};

// 共通インプットスタイル - 枠線なし、下線のみ
export const inputBaseStyle: CSSProperties = {
  width: '100%',
  padding: '12px 0',
  fontSize: '15px',
  backgroundColor: 'transparent',
  border: 'none',
  borderBottom: '1.5px solid #E5E7EB',
  borderRadius: 0,
  outline: 'none',
  transition: 'border-color 150ms, box-shadow 150ms',
};
