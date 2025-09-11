// 分割テーブル対応の物件サービス
import { api } from './api';
import { PropertyMain, PropertyContract, PropertyFullData } from '../types/propertyTables.types';

export const propertyFullService = {
  // 統合データ取得
  async getPropertyFullData(id: number): Promise<PropertyFullData> {
    try {
      const [mainResponse, contractResponse] = await Promise.all([
        api.get(`/properties/${id}`),
        api.get(`/properties_contract?property_id=${id}`)
      ]);

      return {
        main: mainResponse.data,
        contract: contractResponse.data[0] || null
      };
    } catch (error) {
      console.error('統合データ取得エラー:', error);
      throw error;
    }
  },

  // 統合データ保存
  async createPropertyFullData(data: PropertyFullData): Promise<PropertyFullData> {
    try {
      const mainResponse = await api.post('/properties', data.main);
      const propertyId = mainResponse.data.id;

      if (data.contract) {
        const contractData = { ...data.contract, property_id: propertyId };
        await api.post('/properties_contract', contractData);
      }

      return await this.getPropertyFullData(propertyId);
    } catch (error) {
      console.error('統合データ作成エラー:', error);
      throw error;
    }
  }
};

