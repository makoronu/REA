/**
 * PostalCodeField: 郵便番号フィールド（住所自動入力機能付き）
 *
 * 7桁入力時に自動でzipcloud APIを叩き、住所をフォームに反映する
 */
import React, { useState } from 'react';
import { Controller, useFormContext } from 'react-hook-form';
import { ColumnWithLabel } from '../../services/metadataService';
import { geoService } from '../../services/geoService';
import { MESSAGE_TIMEOUT_MS } from '../../constants';

interface PostalCodeFieldProps {
  column: ColumnWithLabel;
  disabled: boolean;
}

export const PostalCodeField: React.FC<PostalCodeFieldProps> = ({ column, disabled }) => {
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
      setTimeout(() => setSearchStatus('idle'), MESSAGE_TIMEOUT_MS);
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
