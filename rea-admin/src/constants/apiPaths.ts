// APIパス定数
// ハードコーディング撲滅：全APIパスをここで一元管理
// バックエンドのエンドポイントと同期すること

export const API_PATHS = {
  // 地理情報
  GEO: {
    GEOCODE: '/geo/geocode',
    ZONING: '/geo/zoning',
    ZONING_LEGEND: '/geo/zoning/legend',
    ZONING_GEOJSON: '/geo/zoning/geojson',
    URBAN_PLANNING: '/geo/urban-planning',
    URBAN_PLANNING_GEOJSON: '/geo/urban-planning/geojson',
    SCHOOL_DISTRICTS: '/geo/school-districts',
    NEAREST_STATIONS: '/geo/nearest-stations',
    NEAREST_BUS_STOPS: '/geo/nearest-bus-stops',
    NEAREST_FACILITIES: '/geo/nearest-facilities-by-category',
  },

  // 登記インポート
  TOUKI: {
    LIST: '/touki/list',
    UPLOAD: '/touki/upload',
    RECORDS_LIST: '/touki/records/list',
    RECORDS_APPLY: '/touki/records/apply-to-property',
    RECORDS_CREATE: '/touki/records/create-property',
    parse: (importId: number) => `/touki/${importId}/parse`,
    record: (recordId: number) => `/touki/records/${recordId}`,
  },

  // 管理者機能
  ADMIN: {
    PROPERTY_TYPES: '/admin/property-types',
    FIELD_VISIBILITY: '/admin/field-visibility',
    FIELD_VISIBILITY_BULK: '/admin/field-visibility/bulk',
  },

  // ユーザー管理
  USERS: {
    LIST: '/users',
    ROLES: '/users/roles',
    detail: (userId: number) => `/users/${userId}`,
  },

  // 外部連携
  INTEGRATIONS: {
    LIST: '/integrations/',
    SYNC_SUMMARY: '/integrations/sync-summary',
    SYNC_STATUS: '/integrations/sync-status',
    BULK_SYNC: '/integrations/bulk-sync',
    detail: (code: string) => `/integrations/${code}`,
  },

  // 不動産情報ライブラリ
  REINFOLIB: {
    REGULATIONS: '/reinfolib/regulations',
    tile: (layerCode: string) => `/reinfolib/tile/${layerCode}`,
  },

  // ZOHO連携
  ZOHO: {
    CALLBACK: '/zoho/callback',
    sync: (id: number) => `/zoho/sync/${id}`,
  },

  // 設備
  EQUIPMENT: {
    GROUPED: '/equipment/grouped',
  },

  // 物件
  PROPERTIES: {
    validatePublication: (id: number) => `/properties/${id}/validate-publication`,
  },

  // ポータル
  PORTAL: {
    HOMES_EXPORT: '/portal/homes/export',
  },

  // メタデータ
  METADATA: {
    BASE: '/metadata',
  },
} as const;
