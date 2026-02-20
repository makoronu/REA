/**
 * useGeoFetch: GeoPanel用の周辺情報一括取得フック
 *
 * API呼び出し・レスポンスパース・初期選択設定を担当
 */
import { useState } from 'react';
import { api } from '../../services/api';
import { API_PATHS } from '../../constants/apiPaths';
import { GEO_SEARCH_CONFIG } from '../../constants';
import {
  SchoolCandidate, StationCandidate, BusStopCandidate, FacilityItem, FetchResults,
} from './GeoResultComponents';

interface SchoolSelection {
  elementary: string | null;
  elementaryMinutes: number | null;
  juniorHigh: string | null;
  juniorHighMinutes: number | null;
}

interface GeoFetchResult {
  isFetching: boolean;
  results: FetchResults | null;
  selectedStationIndices: Set<number>;
  selectedBusStopIndices: Set<number>;
  selectedFacilityIndices: Set<number>;
  schoolSelection: SchoolSelection;
  setSelectedStationIndices: React.Dispatch<React.SetStateAction<Set<number>>>;
  setSelectedBusStopIndices: React.Dispatch<React.SetStateAction<Set<number>>>;
  setSelectedFacilityIndices: React.Dispatch<React.SetStateAction<Set<number>>>;
  setSchoolSelection: React.Dispatch<React.SetStateAction<SchoolSelection>>;
  handleBulkFetch: (lat: number, lng: number) => Promise<void>;
  clearResults: () => void;
}

export const useGeoFetch = (): GeoFetchResult => {
  const [isFetching, setIsFetching] = useState(false);
  const [results, setResults] = useState<FetchResults | null>(null);

  const [selectedStationIndices, setSelectedStationIndices] = useState<Set<number>>(new Set());
  const [selectedBusStopIndices, setSelectedBusStopIndices] = useState<Set<number>>(new Set());
  const [selectedFacilityIndices, setSelectedFacilityIndices] = useState<Set<number>>(new Set());
  const [schoolSelection, setSchoolSelection] = useState<SchoolSelection>({
    elementary: null, elementaryMinutes: null,
    juniorHigh: null, juniorHighMinutes: null,
  });

  const clearResults = () => {
    setResults(null);
  };

  const handleBulkFetch = async (lat: number, lng: number) => {
    setIsFetching(true);
    const errors: string[] = [];

    const [schoolRes, stationRes, busRes, facilityRes] = await Promise.allSettled([
      api.get(API_PATHS.GEO.SCHOOL_DISTRICTS, { params: { lat, lng } }),
      api.get(API_PATHS.GEO.NEAREST_STATIONS, {
        params: { lat, lng, radius: GEO_SEARCH_CONFIG.STATION.RADIUS_M, limit: GEO_SEARCH_CONFIG.STATION.LIMIT }
      }),
      api.get(API_PATHS.GEO.NEAREST_BUS_STOPS, {
        params: { lat, lng, limit: GEO_SEARCH_CONFIG.BUS_STOP.LIMIT }
      }),
      api.get(API_PATHS.GEO.NEAREST_FACILITIES, {
        params: { lat, lng, limit_per_category: GEO_SEARCH_CONFIG.FACILITY.LIMIT_PER_CATEGORY }
      }),
    ]);

    // 学区
    let schools: FetchResults['schools'] = null;
    if (schoolRes.status === 'fulfilled') {
      const d = schoolRes.value.data;
      schools = { elementary: d.elementary || [], juniorHigh: d.junior_high || [] };
      const inDistrictElem = (d.elementary || []).find((s: SchoolCandidate) => s.is_in_district);
      const inDistrictJH = (d.junior_high || []).find((s: SchoolCandidate) => s.is_in_district);
      setSchoolSelection({
        elementary: inDistrictElem?.school_name || null,
        elementaryMinutes: inDistrictElem?.walk_minutes || null,
        juniorHigh: inDistrictJH?.school_name || null,
        juniorHighMinutes: inDistrictJH?.walk_minutes || null,
      });
    } else {
      errors.push('学区');
    }

    // 駅
    let stations: StationCandidate[] = [];
    if (stationRes.status === 'fulfilled') {
      stations = stationRes.value.data.stations || [];
    } else {
      errors.push('駅');
    }

    // バス
    let busStops: BusStopCandidate[] = [];
    if (busRes.status === 'fulfilled') {
      busStops = busRes.value.data.bus_stops || [];
    } else {
      errors.push('バス停');
    }

    // 施設
    const facilities: FacilityItem[] = [];
    if (facilityRes.status === 'fulfilled') {
      const catData = facilityRes.value.data.categories || {};
      Object.entries(catData).forEach(([catCode, catVal]: [string, any]) => {
        (catVal.facilities || []).forEach((f: any) => {
          facilities.push({
            id: f.id, name: f.name, category: catCode,
            category_name: catVal.category_name, address: f.address,
            distance_meters: f.distance_meters, walk_minutes: f.walk_minutes,
          });
        });
      });
    } else {
      errors.push('施設');
    }

    setResults({ schools, stations, busStops, facilities, errors });

    // デフォルト選択
    const stationLimit = GEO_SEARCH_CONFIG.PROPERTY_STATIONS.LIMIT;
    setSelectedStationIndices(new Set(stations.slice(0, stationLimit).map((_, i) => i)));

    const busLimit = GEO_SEARCH_CONFIG.PROPERTY_BUS_STOPS.LIMIT;
    setSelectedBusStopIndices(new Set(busStops.slice(0, busLimit).map((_, i) => i)));

    const facilityDefaults = new Set<number>();
    const seenCategories = new Set<string>();
    facilities.forEach((f, i) => {
      if (!seenCategories.has(f.category)) {
        seenCategories.add(f.category);
        facilityDefaults.add(i);
      }
    });
    setSelectedFacilityIndices(facilityDefaults);

    setIsFetching(false);
  };

  return {
    isFetching, results,
    selectedStationIndices, selectedBusStopIndices, selectedFacilityIndices,
    schoolSelection,
    setSelectedStationIndices, setSelectedBusStopIndices, setSelectedFacilityIndices,
    setSchoolSelection,
    handleBulkFetch, clearResults,
  };
};
