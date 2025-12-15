/**
 * 登記情報カード
 * 土地/建物の登記情報を1枚のカードで表示
 */
import React from 'react';
import { Registry } from '../../services/registryService';

interface RegistryCardProps {
  registry: Registry;
  onEdit: (registry: Registry) => void;
  onDelete: (registry: Registry) => void;
}

export const RegistryCard: React.FC<RegistryCardProps> = ({
  registry,
  onEdit,
  onDelete
}) => {
  const isLand = registry.registry_type === '土地';
  const isBuilding = registry.registry_type === '建物';

  // 床面積の表示
  const formatFloorAreas = () => {
    const areas: string[] = [];
    if (registry.floor_area_1f) areas.push(`1階 ${registry.floor_area_1f}㎡`);
    if (registry.floor_area_2f) areas.push(`2階 ${registry.floor_area_2f}㎡`);
    if (registry.floor_area_3f) areas.push(`3階 ${registry.floor_area_3f}㎡`);
    return areas.join(' / ');
  };

  return (
    <div className="border border-gray-200 rounded-lg p-4 bg-white hover:shadow-md transition-shadow">
      {/* ヘッダー */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span
            className={`px-2 py-1 text-xs font-medium rounded ${
              isLand
                ? 'bg-green-100 text-green-800'
                : 'bg-blue-100 text-blue-800'
            }`}
          >
            {registry.registry_type}
          </span>
          {registry.registration_number && (
            <span className="text-xs text-gray-500">
              登記番号: {registry.registration_number}
            </span>
          )}
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => onEdit(registry)}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            編集
          </button>
          <button
            onClick={() => onDelete(registry)}
            className="text-sm text-red-600 hover:text-red-800"
          >
            削除
          </button>
        </div>
      </div>

      {/* 表題部 */}
      <div className="space-y-2 text-sm">
        {/* 所在 */}
        {registry.location && (
          <div className="flex">
            <span className="text-gray-500 w-20 flex-shrink-0">所在</span>
            <span className="text-gray-900">{registry.location}</span>
          </div>
        )}

        {/* 土地情報 */}
        {isLand && (
          <>
            {registry.chiban && (
              <div className="flex">
                <span className="text-gray-500 w-20 flex-shrink-0">地番</span>
                <span className="text-gray-900">{registry.chiban}</span>
              </div>
            )}
            <div className="flex gap-6">
              {registry.land_category && (
                <div className="flex">
                  <span className="text-gray-500 w-12 flex-shrink-0">地目</span>
                  <span className="text-gray-900">{registry.land_category}</span>
                </div>
              )}
              {registry.land_area && (
                <div className="flex">
                  <span className="text-gray-500 w-12 flex-shrink-0">地積</span>
                  <span className="text-gray-900">{registry.land_area}㎡</span>
                </div>
              )}
            </div>
          </>
        )}

        {/* 建物情報 */}
        {isBuilding && (
          <>
            {registry.building_number && (
              <div className="flex">
                <span className="text-gray-500 w-20 flex-shrink-0">家屋番号</span>
                <span className="text-gray-900">{registry.building_number}</span>
              </div>
            )}
            <div className="flex gap-6">
              {registry.building_type && (
                <div className="flex">
                  <span className="text-gray-500 w-12 flex-shrink-0">種類</span>
                  <span className="text-gray-900">{registry.building_type}</span>
                </div>
              )}
              {registry.building_structure && (
                <div className="flex">
                  <span className="text-gray-500 w-12 flex-shrink-0">構造</span>
                  <span className="text-gray-900">{registry.building_structure}</span>
                </div>
              )}
            </div>
            {registry.floor_area_total && (
              <div className="flex">
                <span className="text-gray-500 w-20 flex-shrink-0">床面積</span>
                <span className="text-gray-900">
                  {formatFloorAreas()}
                  {registry.floor_area_total && ` (計 ${registry.floor_area_total}㎡)`}
                </span>
              </div>
            )}
            {registry.built_date && (
              <div className="flex">
                <span className="text-gray-500 w-20 flex-shrink-0">新築日</span>
                <span className="text-gray-900">{registry.built_date}</span>
              </div>
            )}
          </>
        )}
      </div>

      {/* 所有権（甲区） */}
      {registry.owner_name && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <div className="text-xs text-gray-400 mb-1">甲区（所有権）</div>
          <div className="flex text-sm">
            <span className="text-gray-500 w-20 flex-shrink-0">所有者</span>
            <span className="text-gray-900">
              {registry.owner_name}
              {registry.ownership_ratio && ` （持分: ${registry.ownership_ratio}）`}
            </span>
          </div>
          {registry.owner_address && (
            <div className="flex text-sm">
              <span className="text-gray-500 w-20 flex-shrink-0">住所</span>
              <span className="text-gray-900">{registry.owner_address}</span>
            </div>
          )}
        </div>
      )}

      {/* 抵当権（乙区） */}
      {registry.mortgage_holder && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <div className="text-xs text-gray-400 mb-1">乙区（抵当権）</div>
          <div className="flex text-sm">
            <span className="text-gray-500 w-20 flex-shrink-0">抵当権者</span>
            <span className="text-gray-900">{registry.mortgage_holder}</span>
          </div>
          {registry.mortgage_amount && (
            <div className="flex text-sm">
              <span className="text-gray-500 w-20 flex-shrink-0">債権額</span>
              <span className="text-gray-900">
                {registry.mortgage_amount.toLocaleString()}円
              </span>
            </div>
          )}
        </div>
      )}

      {/* 備考 */}
      {registry.notes && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <div className="text-xs text-gray-400 mb-1">備考</div>
          <div className="text-sm text-gray-700 whitespace-pre-wrap">
            {registry.notes}
          </div>
        </div>
      )}
    </div>
  );
};
