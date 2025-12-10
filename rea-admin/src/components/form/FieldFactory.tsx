import React from 'react';
import { Controller, useFormContext } from 'react-hook-form';
import { ColumnWithLabel } from '../../services/metadataService';
import {
  RoadInfoEditor,
  FloorPlansEditor,
  FacilitiesEditor,
  TransportationEditor,
  RenovationsEditor
} from './JsonEditors';
import { ImageUploader } from './ImageUploader';

interface FieldFactoryProps {
  column: ColumnWithLabel;
  disabled?: boolean;
}

// ENUM値をパースする関数
const parseEnumValues = (enumString: string): { value: string; label: string }[] => {
  console.log('🔍 ENUM値デバッグ:', { enumString, type: typeof enumString });
  
  if (!enumString) return [];
  
  // "1:マンション,2:一戸建て,3:土地,4:その他" 形式をパース
  const options = enumString.split(',').map(item => item.trim());
  const parsed = options.map(option => {
    const [value, label] = option.split(':').map(s => s.trim());
    return { value: value || option, label: label || option };
  });
  
  console.log('✅ パース結果:', parsed);
  return parsed;
};

// データ型から入力タイプを推測
const getInputTypeFromDataType = (dataType?: string): string => {
  if (!dataType) return 'text';
  
  const lowerType = dataType.toLowerCase();
  if (lowerType.includes('int') || lowerType.includes('numeric') || lowerType.includes('decimal')) {
    return 'number';
  }
  if (lowerType.includes('bool')) {
    return 'checkbox';
  }
  if (lowerType.includes('date') && !lowerType.includes('datetime')) {
    return 'date';
  }
  if (lowerType.includes('datetime') || lowerType.includes('timestamp')) {
    return 'datetime';
  }
  if (lowerType.includes('text') || lowerType.includes('varchar')) {
    return 'text';
  }
  return 'text';
};

export const FieldFactory: React.FC<FieldFactoryProps> = ({ column, disabled = false }) => {
  const { control, formState: { errors } } = useFormContext();
  const error = errors[column.column_name];

  // システム管理フィールドを非表示にする
  const hiddenFields = ['id', 'property_id', 'created_at', 'updated_at'];
  if (hiddenFields.includes(column.column_name)) {
    return null;
  }

  // 読み取り専用フィールド
  const readOnlyFields = ['homes_record_id'];
  const isReadOnly = readOnlyFields.includes(column.column_name);

  // 共通のラベル要素
  const renderLabel = () => (
    <label 
      htmlFor={column.column_name} 
      className="block text-sm font-medium text-gray-700 mb-1"
    >
      {column.label_ja || column.column_name}
      {column.is_required && <span className="text-red-500 ml-1">*</span>}
      {isReadOnly && <span className="text-gray-500 ml-2 text-xs">(読み取り専用)</span>}
    </label>
  );

  // ヘルプテキスト
  const renderHelpText = () => {
    if (!column.help_text && !column.description) return null;
    return (
      <p className="mt-1 text-sm text-gray-500">
        {column.help_text || column.description}
      </p>
    );
  };

  // エラーメッセージ
  const renderError = () => {
    if (!error) return null;
    const errorMessage = typeof error === 'object' && 'message' in error
      ? String(error.message)
      : 'このフィールドは必須です';
    return (
      <p className="mt-1 text-sm text-red-600">
        {errorMessage}
      </p>
    );
  };

  // フィールドレンダリング
  const renderField = () => {
    // ENUM値の処理（optionsフィールドを使用）
    const enumSource = column.options;
    
    // USER-DEFINED型または optionsフィールドがある場合はセレクトボックス
    if ((column.data_type === 'USER-DEFINED' || enumSource) && 
        enumSource && 
        !enumSource.includes('マスター参照')) {
      
      const enumOptions = parseEnumValues(enumSource);
      if (enumOptions.length > 0) {
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <select
                {...field}
                id={column.column_name}
                disabled={disabled || isReadOnly}
                className={`block w-full rounded-md shadow-sm sm:text-sm ${
                  error 
                    ? 'border-red-300 focus:ring-red-500 focus:border-red-500' 
                    : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
                } ${isReadOnly ? 'bg-gray-100' : ''}`}
              >
                <option value="">選択してください</option>
                {enumOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            )}
          />
        );
      }
    }

    const inputType = column.input_type || getInputTypeFromDataType(column.data_type);

    switch (inputType) {
      case 'textarea':
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <textarea
                {...field}
                id={column.column_name}
                placeholder={column.placeholder}
                disabled={disabled || isReadOnly}
                rows={4}
                className={`block w-full rounded-md shadow-sm sm:text-sm ${
                  error 
                    ? 'border-red-300 focus:ring-red-500 focus:border-red-500' 
                    : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
                } ${isReadOnly ? 'bg-gray-100' : ''}`}
              />
            )}
          />
        );

      case 'number':
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <input
                {...field}
                type="number"
                id={column.column_name}
                placeholder={column.placeholder}
                disabled={disabled || isReadOnly}
                onChange={(e) => {
                  const value = e.target.value;
                  field.onChange(value === '' ? null : Number(value));
                }}
                className={`block w-full rounded-md shadow-sm sm:text-sm ${
                  error 
                    ? 'border-red-300 focus:ring-red-500 focus:border-red-500' 
                    : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
                } ${isReadOnly ? 'bg-gray-100' : ''}`}
              />
            )}
          />
        );

      case 'checkbox':
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <div className="flex items-center">
                <input
                  {...field}
                  type="checkbox"
                  id={column.column_name}
                  disabled={disabled || isReadOnly}
                  checked={field.value || false}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor={column.column_name} className="ml-2 text-sm text-gray-700">
                  {column.label_ja || column.column_name}
                </label>
              </div>
            )}
          />
        );

      case 'date':
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <input
                {...field}
                type="date"
                id={column.column_name}
                placeholder={column.placeholder}
                disabled={disabled || isReadOnly}
                className={`block w-full rounded-md shadow-sm sm:text-sm ${
                  error 
                    ? 'border-red-300 focus:ring-red-500 focus:border-red-500' 
                    : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
                } ${isReadOnly ? 'bg-gray-100' : ''}`}
              />
            )}
          />
        );

      case 'datetime':
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <input
                {...field}
                type="datetime-local"
                id={column.column_name}
                placeholder={column.placeholder}
                disabled={disabled || isReadOnly}
                className={`block w-full rounded-md shadow-sm sm:text-sm ${
                  error 
                    ? 'border-red-300 focus:ring-red-500 focus:border-red-500' 
                    : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
                } ${isReadOnly ? 'bg-gray-100' : ''}`}
              />
            )}
          />
        );

      case 'email':
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <input
                {...field}
                type="email"
                id={column.column_name}
                placeholder={column.placeholder || 'example@example.com'}
                disabled={disabled || isReadOnly}
                className={`block w-full rounded-md shadow-sm sm:text-sm ${
                  error 
                    ? 'border-red-300 focus:ring-red-500 focus:border-red-500' 
                    : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
                } ${isReadOnly ? 'bg-gray-100' : ''}`}
              />
            )}
          />
        );

      case 'tel':
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <input
                {...field}
                type="tel"
                id={column.column_name}
                placeholder={column.placeholder || '090-1234-5678'}
                disabled={disabled || isReadOnly}
                className={`block w-full rounded-md shadow-sm sm:text-sm ${
                  error
                    ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
                    : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
                } ${isReadOnly ? 'bg-gray-100' : ''}`}
              />
            )}
          />
        );

      // =================================================================
      // JSON専用フィールド
      // =================================================================

      // 接道情報（複数の接道を入力可能）
      case 'json_road_info':
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <RoadInfoEditor
                value={field.value || []}
                onChange={field.onChange}
                disabled={disabled || isReadOnly}
              />
            )}
          />
        );

      // 間取り詳細
      case 'json_floor_plans':
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <FloorPlansEditor
                value={field.value || []}
                onChange={field.onChange}
                disabled={disabled || isReadOnly}
              />
            )}
          />
        );

      // 設備リスト
      case 'json_facilities':
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <FacilitiesEditor
                value={field.value || []}
                onChange={field.onChange}
                disabled={disabled || isReadOnly}
              />
            )}
          />
        );

      // 交通情報（最寄り駅など）
      case 'json_transportation':
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <TransportationEditor
                value={field.value || []}
                onChange={field.onChange}
                disabled={disabled || isReadOnly}
              />
            )}
          />
        );

      // リフォーム履歴
      case 'json_renovations':
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <RenovationsEditor
                value={field.value || []}
                onChange={field.onChange}
                disabled={disabled || isReadOnly}
              />
            )}
          />
        );

      // 画像アップロード
      case 'images':
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <ImageUploader
                value={field.value || []}
                onChange={field.onChange}
                disabled={disabled || isReadOnly}
              />
            )}
          />
        );

      case 'text':
      default:
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <input
                {...field}
                type="text"
                id={column.column_name}
                placeholder={column.placeholder}
                disabled={disabled || isReadOnly}
                className={`block w-full rounded-md shadow-sm sm:text-sm ${
                  error 
                    ? 'border-red-300 focus:ring-red-500 focus:border-red-500' 
                    : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
                } ${isReadOnly ? 'bg-gray-100' : ''}`}
              />
            )}
          />
        );
    }
  };

  // checkboxは特別扱い（ラベルが含まれるため）
  if (column.input_type === 'checkbox' || (column.data_type && column.data_type.toLowerCase().includes('bool'))) {
    return (
      <div className="mb-4">
        {renderField()}
        {renderHelpText()}
        {renderError()}
      </div>
    );
  }

  // 通常のフィールド
  return (
    <div className="mb-4">
      {renderLabel()}
      {renderField()}
      {renderHelpText()}
      {renderError()}
    </div>
  );
};

// =================================================================
// 改良された FieldGroup - 確実に2列レイアウト
// =================================================================

interface FieldGroupProps {
  groupName: string;
  columns: ColumnWithLabel[];
  disabled?: boolean;
}

export const FieldGroup: React.FC<FieldGroupProps> = ({ 
  groupName, 
  columns, 
  disabled = false 
}) => {
  // システムフィールドを除外
  const visibleColumns = columns.filter(col => 
    !['id', 'property_id', 'created_at', 'updated_at'].includes(col.column_name)
  );

  if (visibleColumns.length === 0) return null;

  // フィールドタイプ別分類
  const textareaFields = visibleColumns.filter(col => col.input_type === 'textarea');
  const checkboxFields = visibleColumns.filter(col =>
    col.input_type === 'checkbox' || col.data_type?.toLowerCase().includes('bool')
  );
  // JSON専用フィールド（フル幅表示）
  const jsonFields = visibleColumns.filter(col =>
    col.input_type?.startsWith('json_')
  );
  // 画像アップロードフィールド（フル幅表示）
  const imageFields = visibleColumns.filter(col =>
    col.input_type === 'images'
  );
  const regularFields = visibleColumns.filter(col =>
    !textareaFields.includes(col) && !checkboxFields.includes(col) && !jsonFields.includes(col) && !imageFields.includes(col)
  );

  // グループアイコン
  const getGroupIcon = (groupName: string) => {
    const iconMap: Record<string, string> = {
      '基本情報': '🏠',
      '基本・取引情報': '🏠',
      '価格情報': '💰',
      '契約条件': '📋',
      '元請会社': '🏢',
      '土地情報': '🗺️',
      '建物情報': '🏗️',
      '設備・周辺環境': '🔧',
      '画像情報': '📸',
      '管理情報': '⚙️',
      'システム': '⚙️'
    };
    return iconMap[groupName] || '📄';
  };

  return (
    <div className="mb-8 p-6 bg-gray-50 rounded-lg">
      {/* グループヘッダー */}
      <div className="flex items-center mb-6">
        <span className="text-2xl mr-3">{getGroupIcon(groupName)}</span>
        <h3 className="text-xl font-semibold text-gray-900">{groupName}</h3>
      </div>

      {/* 通常フィールド - 絶対に2列レイアウト */}
      {regularFields.length > 0 && (
        <div className="mb-6">
          <div 
            className="grid gap-6"
            style={{ 
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: '1.5rem'
            }}
          >
            {regularFields.map(column => (
              <div key={column.column_name} className="w-full">
                <FieldFactory 
                  column={column} 
                  disabled={disabled}
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* チェックボックス群 - 強制3列レイアウト */}
      {checkboxFields.length > 0 && (
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-700 mb-3">設定項目</h4>
          <div 
            className="grid gap-4"
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(3, 1fr)',
              gap: '1rem'
            }}
          >
            {checkboxFields.map(column => (
              <div key={column.column_name} className="w-full">
                <FieldFactory 
                  column={column} 
                  disabled={disabled}
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* JSON専用フィールド - フル幅 */}
      {jsonFields.length > 0 && (
        <div className="space-y-4 mb-6">
          {jsonFields.map(column => (
            <div key={column.column_name} className="w-full">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {column.label_ja || column.column_name}
              </label>
              <FieldFactory
                column={column}
                disabled={disabled}
              />
            </div>
          ))}
        </div>
      )}

      {/* 画像アップロードフィールド - フル幅 */}
      {imageFields.length > 0 && (
        <div className="space-y-4 mb-6">
          {imageFields.map(column => (
            <div key={column.column_name} className="w-full">
              <FieldFactory
                column={column}
                disabled={disabled}
              />
            </div>
          ))}
        </div>
      )}

      {/* テキストエリア - フル幅 */}
      {textareaFields.length > 0 && (
        <div className="space-y-4">
          <h4 className="text-sm font-medium text-gray-700">詳細項目</h4>
          {textareaFields.map(column => (
            <div key={column.column_name} className="w-full">
              <FieldFactory
                column={column}
                disabled={disabled}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};