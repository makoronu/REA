/**
 * FormHeader: 固定ヘッダーコンポーネント
 *
 * ステータスバー（案件・公開）、公開バリデーションエラーバナー、
 * タブヘッダーボタンを表示する。DynamicFormから切り出し。
 */
import React from 'react';
import { UseStatusSyncReturn } from './useStatusSync';
import { TabGroup } from './buildTabGroups';
import { PUBLICATION_STATUS } from '../../constants';

interface FormHeaderProps {
  formData: { updated_at?: string; [key: string]: any };
  statusSync: UseStatusSyncReturn;
  submitForm: () => Promise<void>;
  autoSave: boolean;
  activeTab: number;
  setActiveTab: (index: number) => void;
  tabGroups: TabGroup[];
}

export const FormHeader: React.FC<FormHeaderProps> = ({
  formData,
  statusSync,
  submitForm,
  autoSave,
  activeTab,
  setActiveTab,
  tabGroups,
}) => {
  const {
    salesStatusConfig,
    publicationStatusConfig,
    publicationValidationError,
    setPublicationValidationError,
    setShowValidationErrorModal,
    currentSalesStatus,
    currentPublicationStatus,
    isPublicationEditable,
    handleSalesStatusChange,
    handlePublicationStatusChange,
  } = statusSync;

  return (
    <div style={{
      position: 'sticky',
      top: '57px',
      zIndex: 50,
      backgroundColor: 'var(--color-bg, #FAFAFA)',
      paddingTop: '8px',
      paddingBottom: '8px',
      marginLeft: '-16px',
      marginRight: '-16px',
      paddingLeft: '16px',
      paddingRight: '16px',
    }}>
      {/* 最終更新日時（編集時のみ・日本時間） */}
      {formData.updated_at && (
        <div style={{
          fontSize: '11px',
          color: '#9CA3AF',
          marginBottom: '8px',
          textAlign: 'right',
        }}>
          最終更新: {new Date(formData.updated_at).toLocaleString('ja-JP', {
            timeZone: 'Asia/Tokyo',
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
          })}
        </div>
      )}

      {/* ステータスバー - 二段レイアウト */}
      <div style={{
        marginBottom: '12px',
        padding: '8px 12px',
        backgroundColor: '#fff',
        borderRadius: '8px',
        boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)',
      }}>
        {/* 上段：案件ステータス */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
          <span style={{ fontSize: '11px', color: '#9CA3AF', fontWeight: 500, width: '32px' }}>案件</span>
          <div style={{ display: 'flex', gap: '3px', flexWrap: 'wrap' }}>
            {Object.entries(salesStatusConfig).map(([status, config]) => (
              <button
                key={status}
                type="button"
                onClick={() => handleSalesStatusChange(status)}
                style={{
                  padding: '3px 8px',
                  borderRadius: '4px',
                  border: currentSalesStatus === status ? `1.5px solid ${config.color}` : '1px solid #E5E7EB',
                  backgroundColor: currentSalesStatus === status ? config.bg : 'transparent',
                  color: currentSalesStatus === status ? config.color : '#9CA3AF',
                  fontSize: '11px',
                  fontWeight: currentSalesStatus === status ? 600 : 400,
                  cursor: 'pointer',
                  transition: 'all 100ms',
                }}
              >
                {config.label}
              </button>
            ))}
          </div>
        </div>

        {/* 下段：公開ステータス + 保存ボタン */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontSize: '11px', color: '#9CA3AF', fontWeight: 500, width: '32px' }}>公開</span>
            <div style={{ display: 'flex', gap: '3px' }}>
              {Object.entries(publicationStatusConfig).map(([status, config]) => {
                const isDisabled = !isPublicationEditable && status !== PUBLICATION_STATUS.PRIVATE;
                return (
                  <button
                    key={status}
                    type="button"
                    onClick={() => !isDisabled && handlePublicationStatusChange(status)}
                    disabled={isDisabled}
                    style={{
                      padding: '3px 8px',
                      borderRadius: '4px',
                      border: currentPublicationStatus === status ? `1.5px solid ${config.color}` : '1px solid #E5E7EB',
                      backgroundColor: currentPublicationStatus === status ? config.bg : 'transparent',
                      color: currentPublicationStatus === status ? config.color : (isDisabled ? '#D1D5DB' : '#9CA3AF'),
                      fontSize: '11px',
                      fontWeight: currentPublicationStatus === status ? 600 : 400,
                      cursor: isDisabled ? 'not-allowed' : 'pointer',
                      transition: 'all 100ms',
                      opacity: isDisabled ? 0.5 : 1,
                    }}
                  >
                    {config.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* 保存ボタン */}
          {!autoSave && (
            <button
              type="button"
              disabled={!!publicationValidationError}
              onClick={async () => {
                try {
                  await submitForm();
                  setPublicationValidationError(null);
                  setShowValidationErrorModal(false);
                } catch (err: any) {
                  if (err?.type === 'publication_validation') {
                    setPublicationValidationError({
                      message: err.message,
                      groups: err.groups,
                    });
                    setShowValidationErrorModal(true);
                  }
                }
              }}
              style={{
                backgroundColor: publicationValidationError ? '#9CA3AF' : '#10B981',
                color: '#fff',
                border: 'none',
                padding: '5px 16px',
                borderRadius: '4px',
                cursor: publicationValidationError ? 'not-allowed' : 'pointer',
                fontWeight: 600,
                fontSize: '11px',
                transition: 'all 100ms',
                opacity: publicationValidationError ? 0.7 : 1,
              }}
              onMouseOver={(e) => {
                if (!publicationValidationError) {
                  e.currentTarget.style.backgroundColor = '#059669';
                }
              }}
              onMouseOut={(e) => {
                if (!publicationValidationError) {
                  e.currentTarget.style.backgroundColor = '#10B981';
                }
              }}
            >
              保存
            </button>
          )}
        </div>
      </div>

      {/* 公開バリデーションエラー表示 */}
      {publicationValidationError && (
        <div style={{
          marginBottom: '12px',
          padding: '10px 14px',
          borderRadius: '8px',
          fontSize: '13px',
          backgroundColor: '#FEF2F2',
          border: '1px solid #FECACA',
          color: '#991B1B',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '16px' }}>⚠️</span>
              <span>{publicationValidationError.message}</span>
            </div>
            <button
              type="button"
              onClick={() => setShowValidationErrorModal(true)}
              style={{
                backgroundColor: '#DC2626',
                color: '#fff',
                border: 'none',
                padding: '4px 12px',
                borderRadius: '4px',
                fontSize: '12px',
                fontWeight: 500,
                cursor: 'pointer',
              }}
            >
              詳細を見る
            </button>
          </div>
        </div>
      )}

      {/* タブヘッダー */}
      <div style={{ overflowX: 'auto' }}>
        <div style={{ display: 'flex', gap: '6px', minWidth: 'max-content', paddingBottom: '4px' }}>
          {tabGroups.map((tabGroup, index) => (
            <button
              key={tabGroup.tableName}
              type="button"
              onClick={() => {
                setActiveTab(index);
                window.scrollTo({ top: 0, behavior: 'smooth' });
              }}
              style={{
                backgroundColor: activeTab === index ? '#3B82F6' : '#fff',
                color: activeTab === index ? '#ffffff' : '#6B7280',
                border: activeTab === index ? 'none' : '1px solid #E5E7EB',
                padding: '6px 12px',
                borderRadius: '6px',
                fontSize: '13px',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 150ms',
                whiteSpace: 'nowrap',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                boxShadow: activeTab === index ? '0 2px 4px rgba(59, 130, 246, 0.3)' : 'none',
              }}
              onMouseEnter={(e) => {
                if (activeTab !== index) {
                  e.currentTarget.style.backgroundColor = '#F3F4F6';
                }
              }}
              onMouseLeave={(e) => {
                if (activeTab !== index) {
                  e.currentTarget.style.backgroundColor = '#fff';
                }
              }}
            >
              <span>{tabGroup.tableIcon}</span>
              {tabGroup.tableLabel}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
