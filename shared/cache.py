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
        """master_optionsから選択肢を取得（キャッシュ付き）

        master_category_code → master_options (source='rea') から取得
        """
        cache_key = f'enum_{table_name}_{column_name}'
        cached = self.get(cache_key)
        if cached is not None:
            return cached

        with READatabase.cursor() as (cur, conn):
            # master_category_codeを取得
            cur.execute("""
                SELECT master_category_code
                FROM column_labels
                WHERE table_name = %s AND column_name = %s
            """, (table_name, column_name))
            row = cur.fetchone()

            if not row or not row[0]:
                return None

            master_category_code = row[0]
            options = []

            # master_optionsから取得
            cur.execute("""
                SELECT mo.option_code, mo.option_value
                FROM master_options mo
                JOIN master_categories mc ON mo.category_id = mc.id
                WHERE mc.category_code = %s AND mo.source = 'rea' AND mo.is_active = true
                ORDER BY mo.display_order
            """, (master_category_code,))
            for opt_row in cur.fetchall():
                code = opt_row[0].replace('rea_', '')  # rea_1 → 1
                options.append({"value": code, "label": opt_row[1]})

        if options:
            self.set(cache_key, options)
        return options if options else None

    def get_filter_options(self) -> Dict[str, List[Dict[str, Any]]]:
        """フィルターオプションを取得（キャッシュ付き）

        master_category_code → master_options (source='rea') から取得
        """
        cache_key = 'filter_options'
        cached = self.get(cache_key)
        if cached is not None:
            return cached

        filter_options: Dict[str, List[Dict[str, Any]]] = {}

        with READatabase.cursor() as (cur, conn):
            # column_labelsからフィルター用フィールドの選択肢を取得
            cur.execute("""
                SELECT column_name, master_category_code
                FROM column_labels
                WHERE table_name = 'properties'
                AND column_name IN ('sales_status', 'publication_status')
                AND master_category_code IS NOT NULL
            """)

            for row in cur.fetchall():
                column_name = row[0]
                master_category_code = row[1]

                # master_optionsから取得
                cur.execute("""
                    SELECT mo.option_value
                    FROM master_options mo
                    JOIN master_categories mc ON mo.category_id = mc.id
                    WHERE mc.category_code = %s AND mo.source = 'rea' AND mo.is_active = true
                    ORDER BY mo.display_order
                """, (master_category_code,))
                options = [
                    {"value": opt_row[0], "label": opt_row[0]}
                    for opt_row in cur.fetchall()
                ]
                if options:
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
