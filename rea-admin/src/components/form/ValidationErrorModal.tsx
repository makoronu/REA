/**
 * ValidationErrorModal: 公開バリデーションエラー詳細モーダル
 *
 * 公開に必要な未入力項目をグループ別に表示し、
 * グループクリックで該当タブへナビゲートする
 */
import React from 'react';

interface ValidationErrorModalProps {
  publicationValidationError: {
    message: string;
    groups: Record<string, string[]>;
  };
  onClose: () => void;
  onNavigateToField: (groupName: string) => void;
}

export const ValidationErrorModal: React.FC<ValidationErrorModalProps> = ({
  publicationValidationError,
  onClose,
  onNavigateToField,
}) => {
  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: '#fff',
          borderRadius: '12px',
          padding: '24px',
          maxWidth: '500px',
          width: '90%',
          maxHeight: '80vh',
          overflow: 'auto',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* モーダルヘッダー */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '20px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '24px' }}>⚠️</span>
            <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#DC2626', margin: 0 }}>
              公開に必要な項目が未入力です
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '24px',
              cursor: 'pointer',
              color: '#9CA3AF',
              padding: '4px',
            }}
          >
            ×
          </button>
        </div>

        {/* エラー内容（グループ別） */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {Object.entries(publicationValidationError.groups).map(([groupName, fields]) => (
            <div key={groupName} style={{
              backgroundColor: '#FEF2F2',
              borderRadius: '8px',
              padding: '12px 16px',
              border: '1px solid #FECACA',
            }}>
              <button
                type="button"
                onClick={() => onNavigateToField(groupName)}
                style={{
                  width: '100%',
                  textAlign: 'left',
                  background: 'none',
                  border: 'none',
                  padding: 0,
                  cursor: 'pointer',
                  fontSize: '13px',
                  fontWeight: 600,
                  color: '#B91C1C',
                  marginBottom: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                }}
              >
                <span>📋</span>
                {groupName}
                <span style={{ marginLeft: 'auto', fontSize: '11px', color: '#DC2626' }}>→移動</span>
              </button>
              <ul style={{
                margin: 0,
                paddingLeft: '20px',
                color: '#991B1B',
                fontSize: '13px',
              }}>
                {fields.map((field, idx) => (
                  <li key={idx} style={{ marginBottom: '4px' }}>{field}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* 閉じるボタン */}
        <div style={{ marginTop: '20px', textAlign: 'center' }}>
          <button
            type="button"
            onClick={onClose}
            style={{
              backgroundColor: '#6B7280',
              color: '#fff',
              border: 'none',
              padding: '10px 32px',
              borderRadius: '6px',
              fontSize: '14px',
              fontWeight: 500,
              cursor: 'pointer',
            }}
          >
            閉じる
          </button>
        </div>
      </div>
    </div>
  );
};
