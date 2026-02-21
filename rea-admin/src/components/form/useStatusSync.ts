/**
 * useStatusSync: ステータス管理フック
 *
 * 案件ステータス・公開ステータスの色設定取得、変更ハンドラー、
 * 公開バリデーション状態を管理する。DynamicFormから切り出し。
 */
import { useState, useEffect } from 'react';
import React from 'react';
import { UseFormReturn } from 'react-hook-form';
import { metadataService } from '../../services/metadataService';
import { API_PATHS } from '../../constants/apiPaths';
import { api } from '../../services/api';
import { PUBLICATION_STATUS, SALES_STATUS } from '../../constants';

interface StatusConfig {
  label: string;
  color: string;
  bg: string;
}

interface PublicationValidationError {
  message: string;
  groups: Record<string, string[]>;
}

interface UseStatusSyncParams {
  form: UseFormReturn<any>;
  formData: any;
}

export interface UseStatusSyncReturn {
  salesStatusConfig: Record<string, StatusConfig>;
  publicationStatusConfig: Record<string, StatusConfig>;
  publicationValidationError: PublicationValidationError | null;
  setPublicationValidationError: React.Dispatch<React.SetStateAction<PublicationValidationError | null>>;
  showValidationErrorModal: boolean;
  setShowValidationErrorModal: React.Dispatch<React.SetStateAction<boolean>>;
  currentSalesStatus: string;
  currentPublicationStatus: string;
  isPublicationEditable: boolean;
  handleSalesStatusChange: (newStatus: string) => void;
  handlePublicationStatusChange: (newStatus: string) => Promise<void>;
}

export const useStatusSync = ({ form, formData }: UseStatusSyncParams): UseStatusSyncReturn => {
  const [salesStatusConfig, setSalesStatusConfig] = useState<Record<string, StatusConfig>>({});
  const [publicationStatusConfig, setPublicationStatusConfig] = useState<Record<string, StatusConfig>>({});
  const [publicationValidationError, setPublicationValidationError] = useState<PublicationValidationError | null>(null);
  const [showValidationErrorModal, setShowValidationErrorModal] = useState(false);

  // フィルターオプション（ステータス色含む）をAPIから取得
  useEffect(() => {
    const fetchStatusConfigs = async () => {
      try {
        const options = await metadataService.getFilterOptions();

        if (options.sales_status) {
          const config: Record<string, StatusConfig> = {};
          for (const opt of options.sales_status) {
            config[opt.value] = {
              label: opt.label,
              color: opt.color || '#6B7280',
              bg: opt.bg || '#F3F4F6',
            };
          }
          setSalesStatusConfig(config);
        }

        if (options.publication_status) {
          const config: Record<string, StatusConfig> = {};
          for (const opt of options.publication_status) {
            config[opt.value] = {
              label: opt.label,
              color: opt.color || '#6B7280',
              bg: opt.bg || '#F3F4F6',
            };
          }
          setPublicationStatusConfig(config);
        }
      } catch (error) {
        console.error('Failed to fetch status configs:', error);
      }
    };

    fetchStatusConfigs();
  }, []);

  // 公開前確認バリデーション用の個別watch
  const watchedPubStatus = form.watch('publication_status');
  const watchedPropId = form.watch('id');

  // 初期バリデーション実行フラグ
  const initialValidationRan = React.useRef(false);

  // 公開前確認ステータス時の初期バリデーション実行
  useEffect(() => {
    if (initialValidationRan.current) return;
    if (watchedPubStatus !== PUBLICATION_STATUS.PRE_CHECK || !watchedPropId) return;

    initialValidationRan.current = true;

    const runInitialValidation = async () => {
      try {
        const response = await api.get(
          `${API_PATHS.PROPERTIES.validatePublication(watchedPropId)}?target_status=${encodeURIComponent(PUBLICATION_STATUS.PUBLIC)}`
        );
        const result = response.data;
        if (!result.is_valid) {
          setPublicationValidationError({
            message: result.message,
            groups: result.groups,
          });
        }
      } catch (err) {
        console.error('Initial validation check failed:', err);
        setPublicationValidationError({
          message: 'バリデーションチェックに失敗しました',
          groups: {},
        });
      }
    };
    runInitialValidation();
  }, [watchedPropId, watchedPubStatus]);

  const currentSalesStatus = formData.sales_status || SALES_STATUS.ASSESSMENT;
  const currentPublicationStatus = formData.publication_status || PUBLICATION_STATUS.PRIVATE;
  const isPublicationEditable = [SALES_STATUS.SELLING, SALES_STATUS.NEGOTIATING].includes(currentSalesStatus);

  const handleSalesStatusChange = (newStatus: string) => {
    form.setValue('sales_status', newStatus, { shouldDirty: true });
  };

  const handlePublicationStatusChange = async (newStatus: string) => {
    form.setValue('publication_status', newStatus, { shouldDirty: true });
    setPublicationValidationError(null);
    setShowValidationErrorModal(false);

    if (([PUBLICATION_STATUS.PUBLIC, PUBLICATION_STATUS.MEMBER] as string[]).includes(newStatus) && formData.id) {
      try {
        const response = await api.get(
          `${API_PATHS.PROPERTIES.validatePublication(formData.id)}?target_status=${encodeURIComponent(newStatus)}`
        );
        const result = response.data;
        if (!result.is_valid) {
          setPublicationValidationError({
            message: result.message,
            groups: result.groups,
          });
          form.setValue('publication_status', PUBLICATION_STATUS.PRE_CHECK, { shouldDirty: true });
        }
      } catch (err) {
        console.error('Publication validation check failed:', err);
      }
    }
  };

  return {
    salesStatusConfig,
    publicationStatusConfig,
    publicationValidationError,
    setPublicationValidationError,
    showValidationErrorModal,
    setShowValidationErrorModal,
    currentSalesStatus,
    currentPublicationStatus,
    isPublicationEditable,
    handleSalesStatusChange,
    handlePublicationStatusChange,
  };
};
