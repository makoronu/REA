import React, { useState } from 'react';
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
import { geoService } from '../../services/geoService';

interface FieldFactoryProps {
  column: ColumnWithLabel;
  disabled?: boolean;
}

// 共通インプットスタイル - 枠線なし、下線のみ
const inputBaseStyle: React.CSSProperties = {
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

const selectStyle: React.CSSProperties = {
  ...inputBaseStyle,
  cursor: 'pointer',
  appearance: 'none',
  backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%236B7280'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E")`,
  backgroundRepeat: 'no-repeat',
  backgroundPosition: 'right 0 center',
  backgroundSize: '20px',
  paddingRight: '28px',
};

// ENUM値をパースする関数
const parseEnumValues = (enumString: string): { value: string; label: string }[] => {
  if (!enumString) return [];
  const options = enumString.split(',').map(item => item.trim());
  return options.map(option => {
    const [value, label] = option.split(':').map(s => s.trim());
    return { value: value || option, label: label || option };
  });
};

// 郵便番号フィールド - 住所自動入力機能付き
const PostalCodeField: React.FC<{ column: ColumnWithLabel; disabled: boolean }> = ({ column, disabled }) => {
  const { control, setValue } = useFormContext();
  const [isSearching, setIsSearching] = useState(false);
  const [searchStatus, setSearchStatus] = useState<'idle' | 'success' | 'notfound'>('idle');

  const handlePostalCodeChange = async (value: string, fieldOnChange: (value: string) => void) => {
    fieldOnChange(value);

    // ハイフンを除去して7桁になったら自動検索
    const cleanCode = value.replace(/[^0-9]/g, '');
    if (cleanCode.length === 7) {
      setIsSearching(true);
      setSearchStatus('idle');

      const result = await geoService.searchByPostalCode(value);

      if (result) {
        // 住所フィールドに自動入力
        setValue('prefecture', result.address1, { shouldDirty: true });
        setValue('city', result.address2, { shouldDirty: true });
        setValue('address', result.address3, { shouldDirty: true });
        // 土地情報テーブルにもあれば
        setValue('land_prefecture', result.address1, { shouldDirty: true });
        setValue('land_city', result.address2, { shouldDirty: true });
        setValue('land_address', result.address3, { shouldDirty: true });
        setSearchStatus('success');
      } else {
        setSearchStatus('notfound');
      }

      setIsSearching(false);

      // 3秒後にステータスをリセット
      setTimeout(() => setSearchStatus('idle'), 3000);
    }
  };

  return (
    <Controller
      name={column.column_name}
      control={control}
      render={({ field }) => (
        <div style={{ position: 'relative' }}>
          <input
            {...field}
            type="text"
            id={column.column_name}
            placeholder="123-4567"
            disabled={disabled}
            onChange={(e) => handlePostalCodeChange(e.target.value, field.onChange)}
            style={{
              width: '100%',
              padding: '12px 0',
              paddingRight: '100px',
              fontSize: '15px',
              backgroundColor: 'transparent',
              border: 'none',
              borderBottom: '1.5px solid #E5E7EB',
              borderRadius: 0,
              outline: 'none',
              transition: 'border-color 150ms',
            }}
            onFocus={(e) => e.target.style.borderBottomColor = '#3B82F6'}
            onBlur={(e) => e.target.style.borderBottomColor = '#E5E7EB'}
          />
          {/* ステータス表示 */}
          <div style={{
            position: 'absolute',
            right: 0,
            top: '50%',
            transform: 'translateY(-50%)',
            fontSize: '12px',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
          }}>
            {isSearching && (
              <span style={{ color: '#3B82F6' }}>検索中...</span>
            )}
            {searchStatus === 'success' && (
              <span style={{ color: '#10B981' }}>✓ 住所入力済</span>
            )}
            {searchStatus === 'notfound' && (
              <span style={{ color: '#F59E0B' }}>見つかりません</span>
            )}
          </div>
        </div>
      )}
    />
  );
};

// データ型から入力タイプを推測
const getInputTypeFromDataType = (dataType?: string): string => {
  if (!dataType) return 'text';
  const lowerType = dataType.toLowerCase();
  if (lowerType.includes('int') || lowerType.includes('numeric') || lowerType.includes('decimal')) return 'number';
  if (lowerType.includes('bool')) return 'checkbox';
  if (lowerType.includes('date') && !lowerType.includes('datetime')) return 'date';
  if (lowerType.includes('datetime') || lowerType.includes('timestamp')) return 'datetime';
  return 'text';
};

export const FieldFactory: React.FC<FieldFactoryProps> = ({ column, disabled = false }) => {
  const { control, formState: { errors } } = useFormContext();
  const error = errors[column.column_name];

  // システム管理フィールドを非表示
  const hiddenFields = ['id', 'property_id', 'created_at', 'updated_at'];
  if (hiddenFields.includes(column.column_name)) return null;

  // 読み取り専用
  const readOnlyFields = ['homes_record_id'];
  const isReadOnly = readOnlyFields.includes(column.column_name);

  // ラベル
  const renderLabel = () => (
    <label
      htmlFor={column.column_name}
      style={{
        display: 'block',
        fontSize: '13px',
        fontWeight: 500,
        color: '#6B7280',
        marginBottom: '4px',
      }}
    >
      {column.label_ja || column.column_name}
      {column.is_required && <span style={{ color: '#EF4444', marginLeft: '4px' }}>*</span>}
      {isReadOnly && <span style={{ color: '#9CA3AF', marginLeft: '8px', fontSize: '11px' }}>(読み取り専用)</span>}
    </label>
  );

  // ヘルプテキスト
  const renderHelpText = () => {
    if (!column.help_text && !column.description) return null;
    return (
      <p style={{ marginTop: '4px', fontSize: '12px', color: '#9CA3AF' }}>
        {column.help_text || column.description}
      </p>
    );
  };

  // エラー
  const renderError = () => {
    if (!error) return null;
    const errorMessage = typeof error === 'object' && 'message' in error
      ? String(error.message)
      : 'このフィールドは必須です';
    return (
      <p style={{ marginTop: '4px', fontSize: '12px', color: '#EF4444' }}>
        {errorMessage}
      </p>
    );
  };

  // フィールドレンダリング
  const renderField = () => {
    const enumSource = column.options;

    // ENUM型セレクト
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
                style={{
                  ...selectStyle,
                  borderBottomColor: error ? '#EF4444' : '#E5E7EB',
                  backgroundColor: isReadOnly ? '#F9FAFB' : 'transparent',
                }}
                onFocus={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#3B82F6'}
                onBlur={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#E5E7EB'}
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
                rows={3}
                style={{
                  ...inputBaseStyle,
                  resize: 'vertical',
                  minHeight: '80px',
                  borderBottomColor: error ? '#EF4444' : '#E5E7EB',
                  backgroundColor: isReadOnly ? '#F9FAFB' : 'transparent',
                }}
                onFocus={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#3B82F6'}
                onBlur={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#E5E7EB'}
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
                style={{
                  ...inputBaseStyle,
                  borderBottomColor: error ? '#EF4444' : '#E5E7EB',
                  backgroundColor: isReadOnly ? '#F9FAFB' : 'transparent',
                }}
                onFocus={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#3B82F6'}
                onBlur={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#E5E7EB'}
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
              <label style={{
                display: 'flex',
                alignItems: 'center',
                cursor: disabled || isReadOnly ? 'not-allowed' : 'pointer',
                padding: '8px 0',
              }}>
                <input
                  {...field}
                  type="checkbox"
                  id={column.column_name}
                  disabled={disabled || isReadOnly}
                  checked={field.value || false}
                  style={{
                    width: '18px',
                    height: '18px',
                    accentColor: '#3B82F6',
                    marginRight: '10px',
                  }}
                />
                <span style={{ fontSize: '14px', color: '#374151' }}>
                  {column.label_ja || column.column_name}
                </span>
              </label>
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
                disabled={disabled || isReadOnly}
                style={{
                  ...inputBaseStyle,
                  borderBottomColor: error ? '#EF4444' : '#E5E7EB',
                  backgroundColor: isReadOnly ? '#F9FAFB' : 'transparent',
                }}
                onFocus={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#3B82F6'}
                onBlur={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#E5E7EB'}
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
                disabled={disabled || isReadOnly}
                style={{
                  ...inputBaseStyle,
                  borderBottomColor: error ? '#EF4444' : '#E5E7EB',
                  backgroundColor: isReadOnly ? '#F9FAFB' : 'transparent',
                }}
                onFocus={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#3B82F6'}
                onBlur={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#E5E7EB'}
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
                style={{
                  ...inputBaseStyle,
                  borderBottomColor: error ? '#EF4444' : '#E5E7EB',
                  backgroundColor: isReadOnly ? '#F9FAFB' : 'transparent',
                }}
                onFocus={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#3B82F6'}
                onBlur={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#E5E7EB'}
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
                style={{
                  ...inputBaseStyle,
                  borderBottomColor: error ? '#EF4444' : '#E5E7EB',
                  backgroundColor: isReadOnly ? '#F9FAFB' : 'transparent',
                }}
                onFocus={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#3B82F6'}
                onBlur={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#E5E7EB'}
              />
            )}
          />
        );

      case 'postal_code':
        return <PostalCodeField column={column} disabled={disabled || isReadOnly} />;

      // JSON専用フィールド
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
                style={{
                  ...inputBaseStyle,
                  borderBottomColor: error ? '#EF4444' : '#E5E7EB',
                  backgroundColor: isReadOnly ? '#F9FAFB' : 'transparent',
                }}
                onFocus={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#3B82F6'}
                onBlur={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#E5E7EB'}
              />
            )}
          />
        );
    }
  };

  // checkboxは特別扱い
  if (column.input_type === 'checkbox' || (column.data_type && column.data_type.toLowerCase().includes('bool'))) {
    return (
      <div style={{ marginBottom: '16px' }}>
        {renderField()}
        {renderHelpText()}
        {renderError()}
      </div>
    );
  }

  return (
    <div style={{ marginBottom: '16px' }}>
      {renderLabel()}
      {renderField()}
      {renderHelpText()}
      {renderError()}
    </div>
  );
};

// =================================================================
// FieldGroup - 枠線なし
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
  const visibleColumns = columns.filter(col =>
    !['id', 'property_id', 'created_at', 'updated_at'].includes(col.column_name)
  );

  if (visibleColumns.length === 0) return null;

  // フィールドタイプ別分類
  const textareaFields = visibleColumns.filter(col => col.input_type === 'textarea');
  const checkboxFields = visibleColumns.filter(col =>
    col.input_type === 'checkbox' || col.data_type?.toLowerCase().includes('bool')
  );
  const jsonFields = visibleColumns.filter(col => col.input_type?.startsWith('json_'));
  const imageFields = visibleColumns.filter(col => col.input_type === 'images');
  const regularFields = visibleColumns.filter(col =>
    !textareaFields.includes(col) && !checkboxFields.includes(col) && !jsonFields.includes(col) && !imageFields.includes(col)
  );

  // グループアイコン
  const getGroupIcon = (groupName: string) => {
    const iconMap: Record<string, string> = {
      '基本情報': '🏠', '基本・取引情報': '🏠', '価格情報': '💰',
      '契約条件': '📋', '元請会社': '🏢', '土地情報': '🗺️',
      '建物情報': '🏗️', '設備・周辺環境': '🔧', '画像情報': '📸',
      '管理情報': '⚙️', 'システム': '⚙️'
    };
    return iconMap[groupName] || '📄';
  };

  return (
    <div style={{
      marginBottom: '32px',
      padding: '24px',
      backgroundColor: '#FAFAFA',
      borderRadius: '12px',
    }}>
      {/* グループヘッダー */}
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '24px' }}>
        <span style={{ fontSize: '24px', marginRight: '12px' }}>{getGroupIcon(groupName)}</span>
        <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#1A1A1A', margin: 0 }}>{groupName}</h3>
      </div>

      {/* 通常フィールド - 2列 */}
      {regularFields.length > 0 && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '24px',
          marginBottom: jsonFields.length > 0 || checkboxFields.length > 0 || textareaFields.length > 0 ? '24px' : 0,
        }}>
          {regularFields.map(column => (
            <div key={column.column_name}>
              <FieldFactory column={column} disabled={disabled} />
            </div>
          ))}
        </div>
      )}

      {/* チェックボックス群 - 3列 */}
      {checkboxFields.length > 0 && (
        <div style={{ marginBottom: jsonFields.length > 0 || textareaFields.length > 0 ? '24px' : 0 }}>
          <h4 style={{ fontSize: '13px', fontWeight: 600, color: '#6B7280', marginBottom: '12px' }}>設定項目</h4>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
            {checkboxFields.map(column => (
              <div key={column.column_name}>
                <FieldFactory column={column} disabled={disabled} />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* JSON専用フィールド - フル幅 */}
      {jsonFields.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: textareaFields.length > 0 || imageFields.length > 0 ? '24px' : 0 }}>
          {jsonFields.map(column => (
            <div key={column.column_name}>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#6B7280', marginBottom: '8px' }}>
                {column.label_ja || column.column_name}
              </label>
              <FieldFactory column={column} disabled={disabled} />
            </div>
          ))}
        </div>
      )}

      {/* 画像アップロード - フル幅 */}
      {imageFields.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: textareaFields.length > 0 ? '24px' : 0 }}>
          {imageFields.map(column => (
            <div key={column.column_name}>
              <FieldFactory column={column} disabled={disabled} />
            </div>
          ))}
        </div>
      )}

      {/* テキストエリア - フル幅 */}
      {textareaFields.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <h4 style={{ fontSize: '13px', fontWeight: 600, color: '#6B7280' }}>詳細項目</h4>
          {textareaFields.map(column => (
            <div key={column.column_name}>
              <FieldFactory column={column} disabled={disabled} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
