/**
 * 登記情報カード
 * 表題部 + 甲区（所有権）+ 乙区（抵当権等）を表示
 */
import React, { useState, useEffect } from 'react';
import { Registry, KouEntry, OtsuEntry, registryService } from '../../services/registryService';

interface RegistryCardProps {
  registry: Registry;
  onEdit: (registry: Registry) => void;
  onDelete: (registry: Registry) => void;
  onAddKou?: (registry: Registry) => void;
  onAddOtsu?: (registry: Registry) => void;
}

export const RegistryCard: React.FC<RegistryCardProps> = ({
  registry,
  onEdit,
  onDelete,
  onAddKou,
  onAddOtsu
}) => {
  const [kouEntries, setKouEntries] = useState<KouEntry[]>([]);
  const [otsuEntries, setOtsuEntries] = useState<OtsuEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState(true);

  const isLand = registry.registry_type === '土地';
  const isBuilding = registry.registry_type === '建物';

  // 甲区・乙区エントリを取得
  useEffect(() => {
    const fetchEntries = async () => {
      setLoading(true);
      try {
        const [kou, otsu] = await Promise.all([
          registryService.getKouEntries(registry.id),
          registryService.getOtsuEntries(registry.id)
        ]);
        setKouEntries(kou);
        setOtsuEntries(otsu);
      } catch (err) {
        console.error('エントリ取得エラー:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchEntries();
  }, [registry.id]);

  // 床面積の表示
  const formatFloorAreas = () => {
    const areas: string[] = [];
    if (registry.floor_area_1f) areas.push(`1階 ${registry.floor_area_1f}㎡`);
    if (registry.floor_area_2f) areas.push(`2階 ${registry.floor_area_2f}㎡`);
    if (registry.floor_area_3f) areas.push(`3階 ${registry.floor_area_3f}㎡`);
    if (registry.floor_area_b1) areas.push(`地下1階 ${registry.floor_area_b1}㎡`);
    return areas.join(' / ');
  };

  // 金額フォーマット
  const formatAmount = (amount?: number) => {
    if (!amount) return '';
    return `${(amount / 10000).toLocaleString()}万円`;
  };

  return (
    <div className="border border-gray-200 rounded-lg bg-white hover:shadow-md transition-shadow">
      {/* ヘッダー */}
      <div
        className="flex items-center justify-between p-4 cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
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
          <span className="font-medium text-gray-900">
            {registry.location}
            {isLand && registry.chiban && ` ${registry.chiban}`}
            {isBuilding && registry.building_number && ` 家屋番号${registry.building_number}`}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={(e) => { e.stopPropagation(); onEdit(registry); }}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            編集
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); onDelete(registry); }}
            className="text-sm text-red-600 hover:text-red-800"
          >
            削除
          </button>
          <svg
            className={`w-5 h-5 text-gray-400 transition-transform ${expanded ? 'rotate-180' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      {expanded && (
        <div className="px-4 pb-4 space-y-4">
          {/* 表題部 */}
          <div className="bg-gray-50 rounded p-3">
            <div className="text-xs font-medium text-gray-500 mb-2">【表題部】</div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              {isLand && (
                <>
                  {registry.land_category && (
                    <div><span className="text-gray-500">地目:</span> {registry.land_category}</div>
                  )}
                  {registry.land_area && (
                    <div><span className="text-gray-500">地積:</span> {registry.land_area}㎡</div>
                  )}
                </>
              )}
              {isBuilding && (
                <>
                  {registry.building_type && (
                    <div><span className="text-gray-500">種類:</span> {registry.building_type}</div>
                  )}
                  {registry.building_structure && (
                    <div><span className="text-gray-500">構造:</span> {registry.building_structure}</div>
                  )}
                  {registry.floor_area_total && (
                    <div className="col-span-2">
                      <span className="text-gray-500">床面積:</span> {formatFloorAreas()}
                      {` (計 ${registry.floor_area_total}㎡)`}
                    </div>
                  )}
                  {registry.built_date && (
                    <div><span className="text-gray-500">新築日:</span> {registry.built_date}</div>
                  )}
                </>
              )}
            </div>
          </div>

          {/* 甲区（所有権） */}
          <div className="border-l-4 border-blue-400 pl-3">
            <div className="flex items-center justify-between mb-2">
              <div className="text-xs font-medium text-blue-600">【甲区】所有権</div>
              {onAddKou && (
                <button
                  onClick={() => onAddKou(registry)}
                  className="text-xs text-blue-600 hover:text-blue-800"
                >
                  + 追加
                </button>
              )}
            </div>
            {loading ? (
              <div className="text-sm text-gray-400">読み込み中...</div>
            ) : kouEntries.length === 0 ? (
              <div className="text-sm text-gray-400">登記なし</div>
            ) : (
              <div className="space-y-2">
                {kouEntries.map((entry) => (
                  <div
                    key={entry.id}
                    className={`text-sm p-2 rounded ${
                      entry.is_active ? 'bg-white border' : 'bg-gray-100 text-gray-400 line-through'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <span className="font-medium">順位{entry.rank_number}</span>
                      <span>{entry.purpose}</span>
                      {entry.is_active && <span className="text-green-600 text-xs">← 現在</span>}
                    </div>
                    <div className="text-gray-600 mt-1">
                      {entry.owner_name}
                      {entry.ownership_ratio && ` (持分: ${entry.ownership_ratio})`}
                    </div>
                    {entry.cause && (
                      <div className="text-xs text-gray-500">
                        原因: {entry.cause_date} {entry.cause}
                      </div>
                    )}
                    {entry.reception_number && (
                      <div className="text-xs text-gray-500">
                        受付: {entry.reception_date} {entry.reception_number}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* 乙区（抵当権等） */}
          <div className="border-l-4 border-orange-400 pl-3">
            <div className="flex items-center justify-between mb-2">
              <div className="text-xs font-medium text-orange-600">【乙区】抵当権等</div>
              {onAddOtsu && (
                <button
                  onClick={() => onAddOtsu(registry)}
                  className="text-xs text-orange-600 hover:text-orange-800"
                >
                  + 追加
                </button>
              )}
            </div>
            {loading ? (
              <div className="text-sm text-gray-400">読み込み中...</div>
            ) : otsuEntries.length === 0 ? (
              <div className="text-sm text-gray-400">登記なし</div>
            ) : (
              <div className="space-y-2">
                {otsuEntries.map((entry) => (
                  <div
                    key={entry.id}
                    className={`text-sm p-2 rounded ${
                      entry.is_active ? 'bg-white border' : 'bg-gray-100 text-gray-400 line-through'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <span className="font-medium">順位{entry.rank_number}</span>
                      <span>{entry.purpose}</span>
                      {!entry.is_active && <span className="text-red-400 text-xs">抹消</span>}
                    </div>
                    {entry.mortgagee_name && (
                      <div className="text-gray-600 mt-1">
                        抵当権者: {entry.mortgagee_name}
                      </div>
                    )}
                    {entry.debt_amount && (
                      <div className="text-gray-600">
                        債権額: {formatAmount(entry.debt_amount)}
                        {entry.interest_rate && ` / 利息: ${entry.interest_rate}`}
                      </div>
                    )}
                    {entry.maximum_amount && (
                      <div className="text-gray-600">
                        極度額: {formatAmount(entry.maximum_amount)}
                      </div>
                    )}
                    {entry.debtor_name && (
                      <div className="text-xs text-gray-500">
                        債務者: {entry.debtor_name}
                      </div>
                    )}
                    {entry.reception_number && (
                      <div className="text-xs text-gray-500">
                        受付: {entry.reception_date} {entry.reception_number}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* 備考 */}
          {registry.notes && (
            <div className="text-sm text-gray-600 border-t pt-2">
              <span className="text-gray-500">備考:</span> {registry.notes}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
