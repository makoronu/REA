/**
 * LegalChecklistField: 重要事項説明 法令制限チェックリスト
 *
 * マスターオプション(legal_regulation)からカテゴリ別の法令一覧を取得し、
 * グループ別チェックボックスで表示する。
 * 保存形式: JSONB文字列配列（法令名）例: ["農地法", "水防法"]
 */
import React, { useState, useEffect } from 'react';
import { Controller, useFormContext } from 'react-hook-form';
import { api } from '../../services/api';
import { API_PATHS } from '../../constants/apiPaths';

interface LegalOption {
  value: string;
  label: string;
  metadata?: { group?: string };
}

interface LegalChecklistFieldProps {
  disabled?: boolean;
}

export const LegalChecklistField: React.FC<LegalChecklistFieldProps> = ({ disabled = false }) => {
  const { control } = useFormContext();
  const [options, setOptions] = useState<LegalOption[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const response = await api.get(API_PATHS.METADATA.options('legal_regulation'));
        setOptions(response.data || []);
      } catch {
        // マスターデータ取得失敗時は空リスト（UIにチェック項目が出ない）
        setOptions([]);
      } finally {
        setIsLoading(false);
      }
    };
    void fetchOptions();
  }, []);

  // グループ別に分類
  const grouped = options.reduce((acc, opt) => {
    const group = opt.metadata?.group || 'その他';
    if (!acc[group]) acc[group] = [];
    acc[group].push(opt);
    return acc;
  }, {} as Record<string, LegalOption[]>);

  if (isLoading) {
    return <div style={{ padding: '8px 0', fontSize: '13px', color: '#9CA3AF' }}>読み込み中...</div>;
  }

  if (options.length === 0) {
    return <div style={{ padding: '8px 0', fontSize: '13px', color: '#9CA3AF' }}>法令データが取得できませんでした</div>;
  }

  return (
    <Controller
      name="legal_regulations_checked"
      control={control}
      render={({ field }) => {
        // 保存形式: 法令名の文字列配列 ["農地法", "水防法"]
        const checkedItems: string[] = Array.isArray(field.value) ? field.value : [];

        const toggleItem = (label: string) => {
          const newItems = checkedItems.includes(label)
            ? checkedItems.filter(item => item !== label)
            : [...checkedItems, label];
          field.onChange(newItems);
        };

        const totalCount = options.length;
        const checkedCount = checkedItems.length;

        return (
          <div>
            {/* サマリー */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '12px',
              padding: '8px 12px',
              backgroundColor: checkedCount === totalCount ? '#D1FAE5' : '#F3F4F6',
              borderRadius: '6px',
              fontSize: '13px',
            }}>
              <span style={{ color: '#374151' }}>
                {checkedCount}/{totalCount} 項目確認済み
              </span>
              {checkedCount === totalCount && (
                <span style={{ color: '#059669', fontWeight: 500 }}>全項目確認完了</span>
              )}
            </div>

            {/* グループ別チェックリスト */}
            {Object.entries(grouped).map(([groupName, items]) => {
              const groupChecked = items.filter(item => checkedItems.includes(item.label)).length;
              return (
                <div key={groupName} style={{ marginBottom: '12px' }}>
                  <div style={{
                    fontSize: '13px',
                    fontWeight: 600,
                    color: '#374151',
                    marginBottom: '6px',
                    display: 'flex',
                    justifyContent: 'space-between',
                  }}>
                    <span>{groupName}</span>
                    <span style={{ fontSize: '11px', color: '#9CA3AF', fontWeight: 400 }}>
                      {groupChecked}/{items.length}
                    </span>
                  </div>
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(2, 1fr)',
                    gap: '4px',
                  }}>
                    {items.map(item => {
                      const isChecked = checkedItems.includes(item.label);
                      return (
                        <label
                          key={item.value}
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px',
                            padding: '4px 8px',
                            borderRadius: '4px',
                            cursor: disabled ? 'not-allowed' : 'pointer',
                            backgroundColor: isChecked ? '#EFF6FF' : 'transparent',
                            fontSize: '12px',
                            color: isChecked ? '#1D4ED8' : '#4B5563',
                          }}
                        >
                          <input
                            type="checkbox"
                            checked={isChecked}
                            onChange={() => toggleItem(item.label)}
                            disabled={disabled}
                            style={{ width: '14px', height: '14px', accentColor: '#3B82F6' }}
                          />
                          <span>{item.label}</span>
                        </label>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        );
      }}
    />
  );
};
