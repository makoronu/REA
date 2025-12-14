"""
REAメタデータキャッシュ

頻繁にアクセスされるが変更が少ないデータをキャッシュする。
- property_types
- column_labels（選択肢情報）

キャッシュはTTL（Time To Live）で自動更新される。
"""
import time
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

from shared.database import READatabase
from shared.constants import PROPERTY_TYPE_GROUP_ORDER


class CacheEntry:
    """キャッシュエントリ"""
    def __init__(self, data: Any, ttl_seconds: int = 300):
        self.data = data
        self.ttl = ttl_seconds
        self.created_at = time.time()

    @property
    def is_expired(self) -> bool:
        return time.time() - self.created_at > self.ttl


class MetadataCache:
    """メタデータキャッシュ管理"""

    _instance: Optional['MetadataCache'] = None
    _cache: Dict[str, CacheEntry] = {}

    DEFAULT_TTL = 300  # 5分

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._cache = {}
        return cls._instance

    def get(self, key: str) -> Optional[Any]:
        """キャッシュから取得"""
        entry = self._cache.get(key)
        if entry and not entry.is_expired:
            return entry.data
        return None

    def set(self, key: str, data: Any, ttl: int = None) -> None:
        """キャッシュに保存"""
        self._cache[key] = CacheEntry(data, ttl or self.DEFAULT_TTL)

    def invalidate(self, key: str = None) -> None:
        """キャッシュを無効化"""
        if key:
            self._cache.pop(key, None)
        else:
            self._cache.clear()

    def get_property_types(self) -> List[Dict[str, str]]:
        """物件種別マスターを取得（キャッシュ付き）"""
        cache_key = 'property_types'
        cached = self.get(cache_key)
        if cached is not None:
            return cached

        # DBから取得
        with READatabase.cursor() as (cur, conn):
            cur.execute("""
                SELECT id, label, group_name
                FROM property_types
                ORDER BY
                    CASE group_name
                        WHEN '居住用' THEN 1
                        WHEN '事業用' THEN 2
                        WHEN '投資用' THEN 3
                        ELSE 4
                    END,
                    label
            """)
            result = [
                {"value": row[0], "label": row[1], "group": row[2]}
                for row in cur.fetchall()
            ]

        self.set(cache_key, result)
        return result

    def get_enum_options(self, table_name: str, column_name: str) -> Optional[List[Dict[str, str]]]:
        """column_labelsからENUM選択肢を取得（キャッシュ付き）"""
        cache_key = f'enum_{table_name}_{column_name}'
        cached = self.get(cache_key)
        if cached is not None:
            return cached

        with READatabase.cursor() as (cur, conn):
            cur.execute("""
                SELECT enum_values
                FROM column_labels
                WHERE table_name = %s AND column_name = %s
            """, (table_name, column_name))
            row = cur.fetchone()

            if not row or not row[0]:
                return None

            enum_values = row[0]
            options = []
            for item in enum_values.split(","):
                if ":" in item:
                    parts = item.split(":", 1)
                    options.append({"value": parts[1], "label": parts[1]})
                else:
                    options.append({"value": item, "label": item})

        self.set(cache_key, options)
        return options

    def get_filter_options(self) -> Dict[str, List[Dict[str, Any]]]:
        """フィルターオプションを取得（キャッシュ付き）"""
        cache_key = 'filter_options'
        cached = self.get(cache_key)
        if cached is not None:
            return cached

        filter_options: Dict[str, List[Dict[str, Any]]] = {}

        with READatabase.cursor() as (cur, conn):
            # column_labelsからフィルター用フィールドの選択肢を取得
            cur.execute("""
                SELECT column_name, enum_values
                FROM column_labels
                WHERE table_name = 'properties'
                AND column_name IN ('sales_status', 'publication_status', 'property_type')
                AND enum_values IS NOT NULL
            """)

            for row in cur.fetchall():
                column_name = row[0]
                enum_values = row[1]

                if enum_values:
                    options = []
                    for item in enum_values.split(","):
                        if ":" in item:
                            parts = item.split(":", 1)
                            options.append({"value": parts[1], "label": parts[1]})
                        else:
                            options.append({"value": item, "label": item})
                    filter_options[column_name] = options

        # property_typesも追加
        filter_options["property_type_simple"] = [
            {"value": pt["label"], "label": pt["label"], "group": pt["group"]}
            for pt in self.get_property_types()
        ]

        self.set(cache_key, filter_options)
        return filter_options


# シングルトンインスタンス
metadata_cache = MetadataCache()
