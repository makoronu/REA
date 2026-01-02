"""
汎用CRUD - メタデータ駆動

column_labelsテーブルをベースに、全てのテーブルに対して
動的にCRUD操作を行う。ハードコードなし。
"""
import json
from typing import Any, Dict, List, Optional, Set
from sqlalchemy import text
from sqlalchemy.orm import Session


def _serialize_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """dict/listをJSON文字列に変換（JSONB型対応）"""
    result = {}
    for key, value in data.items():
        if isinstance(value, (dict, list)):
            result[key] = json.dumps(value, ensure_ascii=False)
        else:
            result[key] = value
    return result


class GenericCRUD:
    """
    メタデータ駆動の汎用CRUD

    使用例:
        crud = GenericCRUD(db)

        # 取得
        property = crud.get("properties", 1)

        # 一覧
        properties = crud.get_list("properties", skip=0, limit=100)

        # 作成
        new_property = crud.create("properties", {"property_name": "テスト物件"})

        # 更新
        crud.update("properties", 1, {"sale_price": 10000000})

        # 削除
        crud.delete("properties", 1)
    """

    # 操作を許可するテーブル（セキュリティ）
    ALLOWED_TABLES: Set[str] = {
        "properties",
        "building_info",
        "land_info",
        "property_images",
        "property_locations",
        "property_registries",
    }

    # システムカラム - 廃止予定（column_labels.is_updatable=falseで管理）
    # 後方互換のため残すが、新コードは_get_updatable_columns()を使用すること
    SYSTEM_COLUMNS: Set[str] = {
        "id",
        "created_at",
        "updated_at",
    }

    def __init__(self, db: Session):
        self.db = db
        self._column_cache: Dict[str, List[str]] = {}

    def _get_valid_columns(self, table_name: str) -> List[str]:
        """
        column_labelsから有効なカラム一覧を取得（キャッシュ付き）
        """
        if table_name in self._column_cache:
            return self._column_cache[table_name]

        result = self.db.execute(
            text("""
                SELECT column_name
                FROM column_labels
                WHERE table_name = :table_name
                ORDER BY display_order, column_name
            """),
            {"table_name": table_name}
        )
        columns = [row[0] for row in result]
        self._column_cache[table_name] = columns
        return columns

    def _get_updatable_columns(self, table_name: str) -> Set[str]:
        """
        column_labelsから更新可能なカラム一覧を取得
        is_updatable = true のカラムのみ返す
        """
        cache_key = f"{table_name}_updatable"
        if cache_key in self._column_cache:
            return set(self._column_cache[cache_key])

        result = self.db.execute(
            text("""
                SELECT column_name
                FROM column_labels
                WHERE table_name = :table_name
                AND is_updatable = true
            """),
            {"table_name": table_name}
        )
        columns = [row[0] for row in result]
        self._column_cache[cache_key] = columns
        return set(columns)

    def _get_db_columns(self, table_name: str) -> List[str]:
        """
        実際のDBカラム一覧を取得
        """
        result = self.db.execute(
            text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = :table_name
                ORDER BY ordinal_position
            """),
            {"table_name": table_name}
        )
        return [row[0] for row in result]

    def _validate_table(self, table_name: str) -> None:
        """テーブル名のバリデーション（SQLインジェクション対策）"""
        if table_name not in self.ALLOWED_TABLES:
            raise ValueError(f"Table '{table_name}' is not allowed")

    def _filter_data(self, table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        有効なカラムのみをフィルタリング（メタデータ駆動）

        フィルタ条件:
        1. column_labelsに登録されている
        2. 実際にDBに存在する
        3. is_updatable = true である
        """
        updatable_columns = self._get_updatable_columns(table_name)
        db_columns = set(self._get_db_columns(table_name))

        # 有効 = column_labelsでis_updatable=true AND 実際にDBに存在
        allowed = updatable_columns & db_columns

        return {k: v for k, v in data.items() if k in allowed}

    def get(self, table_name: str, id: int) -> Optional[Dict[str, Any]]:
        """
        単一レコード取得
        """
        self._validate_table(table_name)

        columns = self._get_db_columns(table_name)
        columns_str = ", ".join(columns)
        result = self.db.execute(
            text(f"SELECT {columns_str} FROM {table_name} WHERE id = :id AND deleted_at IS NULL"),
            {"id": id}
        ).fetchone()

        if result is None:
            return None

        return dict(result._mapping)

    def get_full(self, property_id: int) -> Optional[Dict[str, Any]]:
        """
        物件の全データを取得（properties + 関連テーブル）
        住所はproperty_locationsを優先、その他はpropertiesを優先
        """
        # properties 取得
        result = self.get("properties", property_id)
        if result is None:
            return None

        # property_locations を最優先で取得（住所の正規化されたソース）
        loc_columns = self._get_db_columns("property_locations")
        loc_columns_str = ", ".join(loc_columns)
        location = self.db.execute(
            text(f"SELECT {loc_columns_str} FROM property_locations WHERE property_id = :pid AND deleted_at IS NULL"),
            {"pid": property_id}
        ).fetchone()

        if location:
            location_dict = dict(location._mapping)
            # 住所関連カラムはproperty_locationsの値で上書き
            address_columns = ['postal_code', 'prefecture', 'city', 'address',
                               'address_detail', 'latitude', 'longitude']
            for key in address_columns:
                if key in location_dict and location_dict[key] is not None:
                    result[key] = location_dict[key]

        # 関連テーブルを取得してマージ
        related_tables = ["building_info", "land_info"]

        for table_name in related_tables:
            rel_columns = self._get_db_columns(table_name)
            rel_columns_str = ", ".join(rel_columns)
            related = self.db.execute(
                text(f"SELECT {rel_columns_str} FROM {table_name} WHERE property_id = :pid AND deleted_at IS NULL"),
                {"pid": property_id}
            ).fetchone()

            if related:
                related_dict = dict(related._mapping)
                for key, value in related_dict.items():
                    # システムカラムはスキップ
                    if key in ['id', 'property_id', 'created_at', 'updated_at']:
                        continue
                    # 既に値がある場合は上書きしない（propertiesを優先）
                    # ただし、propertiesに該当カラムがない場合は追加
                    if key not in result or result[key] is None:
                        result[key] = value

        # datetime型を文字列に変換
        for key in ['created_at', 'updated_at']:
            if key in result and result[key] is not None:
                result[key] = str(result[key])

        return result

    def get_list(
        self,
        table_name: str,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        range_filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "id",
        sort_order: str = "desc",
    ) -> List[Dict[str, Any]]:
        """
        一覧取得（フィルタリング・ソート対応）

        range_filters: 範囲フィルタ（例: {"sale_price__gte": 1000, "sale_price__lte": 5000}）
        """
        self._validate_table(table_name)

        # 有効なカラムを確認
        valid_columns = set(self._get_db_columns(table_name))

        # ソートカラムの検証
        if sort_by not in valid_columns:
            sort_by = "id"
        if sort_order not in ("asc", "desc"):
            sort_order = "desc"

        # クエリ構築
        columns_str = ", ".join(valid_columns)
        query = f"SELECT {columns_str} FROM {table_name}"
        params: Dict[str, Any] = {}
        conditions = ["deleted_at IS NULL"]  # 論理削除されていないレコードのみ

        # フィルタリング
        if filters:
            for i, (key, value) in enumerate(filters.items()):
                if key in valid_columns and value is not None:
                    param_name = f"filter_{i}"
                    if isinstance(value, str) and '%' in value:
                        conditions.append(f"{key} ILIKE :{param_name}")
                    else:
                        conditions.append(f"{key} = :{param_name}")
                    params[param_name] = value

        # 範囲フィルタリング（sale_price__gte, sale_price__lte など）
        if range_filters:
            for i, (key, value) in enumerate(range_filters.items()):
                if value is not None:
                    if "__gte" in key:
                        col_name = key.replace("__gte", "")
                        if col_name in valid_columns:
                            param_name = f"range_{i}"
                            conditions.append(f"{col_name} >= :{param_name}")
                            params[param_name] = value
                    elif "__lte" in key:
                        col_name = key.replace("__lte", "")
                        if col_name in valid_columns:
                            param_name = f"range_{i}"
                            conditions.append(f"{col_name} <= :{param_name}")
                            params[param_name] = value

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # ソート
        query += f" ORDER BY {sort_by} {sort_order}"

        # ページネーション
        query += " OFFSET :skip LIMIT :limit"
        params["skip"] = skip
        params["limit"] = limit

        result = self.db.execute(text(query), params)
        return [dict(row._mapping) for row in result]

    def create(self, table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        レコード作成
        """
        self._validate_table(table_name)
        filtered_data = self._filter_data(table_name, data)

        if not filtered_data:
            raise ValueError("No valid data to insert")

        # JSONB型対応
        serialized_data = _serialize_data(filtered_data)
        columns = list(serialized_data.keys())
        placeholders = [f":{col}" for col in columns]

        query = f"""
            INSERT INTO {table_name} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            RETURNING *
        """

        result = self.db.execute(text(query), serialized_data).fetchone()
        self.db.commit()

        return dict(result._mapping)

    def update(self, table_name: str, id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        レコード更新
        """
        self._validate_table(table_name)
        filtered_data = self._filter_data(table_name, data)

        if not filtered_data:
            # 更新データがない場合は現在のデータを返す
            return self.get(table_name, id)

        # JSONB型対応
        serialized_data = _serialize_data(filtered_data)
        set_clause = ", ".join([f"{col} = :{col}" for col in serialized_data.keys()])
        serialized_data["id"] = id

        query = f"""
            UPDATE {table_name}
            SET {set_clause}, updated_at = NOW()
            WHERE id = :id
            RETURNING *
        """

        result = self.db.execute(text(query), serialized_data).fetchone()
        self.db.commit()

        if result is None:
            return None

        return dict(result._mapping)

    def update_full(self, property_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        物件の全データを更新（properties + 関連テーブル）
        住所データはproperty_locationsに保存
        """
        # 住所関連カラム（property_locationsに保存）
        address_columns = {'postal_code', 'prefecture', 'city', 'address',
                          'address_detail', 'latitude', 'longitude'}

        # 各テーブルのカラムを取得
        table_columns: Dict[str, Set[str]] = {}
        for table_name in ["properties", "building_info", "land_info"]:
            table_columns[table_name] = set(self._get_db_columns(table_name))

        # データを各テーブルに振り分け
        table_data: Dict[str, Dict[str, Any]] = {
            "properties": {},
            "building_info": {},
            "land_info": {},
            "property_locations": {},
        }

        for key, value in data.items():
            # システムカラムはスキップ（メタデータ駆動: is_updatable=falseで定義）
            # 各テーブルの_filter_data()で最終フィルタされるが、ここでも早期除外
            if key in {'id', 'created_at', 'updated_at'}:
                continue

            # 住所関連はproperty_locationsへ
            if key in address_columns:
                table_data["property_locations"][key] = value
                # propertiesにも同期（移行期間中の互換性）
                if key in table_columns["properties"]:
                    table_data["properties"][key] = value
            # propertiesを優先
            elif key in table_columns["properties"]:
                table_data["properties"][key] = value
            elif key in table_columns["building_info"]:
                table_data["building_info"][key] = value
            elif key in table_columns["land_info"]:
                table_data["land_info"][key] = value

        # properties を更新
        if table_data["properties"]:
            self.update("properties", property_id, table_data["properties"])

        # property_locations を更新（存在しなければ作成）
        if table_data["property_locations"]:
            existing_loc = self.db.execute(
                text("SELECT id FROM property_locations WHERE property_id = :pid"),
                {"pid": property_id}
            ).fetchone()

            if existing_loc:
                self._update_related("property_locations", existing_loc[0], table_data["property_locations"])
            else:
                table_data["property_locations"]["property_id"] = property_id
                self._create_related("property_locations", table_data["property_locations"])

        # 関連テーブルを更新（存在しなければ作成）
        for table_name in ["building_info", "land_info"]:
            if not table_data[table_name]:
                continue

            # 既存レコードを確認
            existing = self.db.execute(
                text(f"SELECT id FROM {table_name} WHERE property_id = :pid"),
                {"pid": property_id}
            ).fetchone()

            if existing:
                # 更新
                self._update_related(table_name, existing[0], table_data[table_name])
            else:
                # 新規作成
                table_data[table_name]["property_id"] = property_id
                self._create_related(table_name, table_data[table_name])

        self.db.commit()
        return self.get_full(property_id)

    def _update_related(self, table_name: str, id: int, data: Dict[str, Any]) -> None:
        """
        関連テーブルの更新（内部用）

        メタデータ駆動: is_updatable=true のカラムのみ更新可能
        """
        if not data:
            return

        # メタデータ駆動フィルタリング（is_updatable=trueのカラムのみ）
        filtered_data = self._filter_data(table_name, data)
        if not filtered_data:
            return

        processed_data = _serialize_data(filtered_data)
        set_clause = ", ".join([f"{col} = :{col}" for col in processed_data.keys()])
        processed_data["id"] = id

        self.db.execute(
            text(f"UPDATE {table_name} SET {set_clause}, updated_at = NOW() WHERE id = :id"),
            processed_data
        )

    def _create_related(self, table_name: str, data: Dict[str, Any]) -> None:
        """関連テーブルの作成（内部用）"""
        if not data:
            return

        processed_data = _serialize_data(data)
        columns = list(processed_data.keys())
        placeholders = [f":{col}" for col in columns]

        self.db.execute(
            text(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"),
            processed_data
        )

    def delete(self, table_name: str, id: int, deleted_by: str = None) -> bool:
        """
        レコード論理削除（deleted_atを設定）
        """
        self._validate_table(table_name)

        result = self.db.execute(
            text(f"""
                UPDATE {table_name}
                SET deleted_at = NOW(), updated_by = :deleted_by
                WHERE id = :id AND deleted_at IS NULL
                RETURNING id
            """),
            {"id": id, "deleted_by": deleted_by}
        ).fetchone()

        self.db.commit()
        return result is not None

    def search(
        self,
        table_name: str,
        search_term: str,
        search_columns: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 100,
        range_filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        全文検索（指定カラムまたはテキストカラム全てを対象）

        range_filters: 範囲フィルタ（例: {"sale_price__gte": 1000, "sale_price__lte": 5000}）
        """
        self._validate_table(table_name)

        valid_columns = set(self._get_db_columns(table_name))

        # 検索対象カラムを決定
        if search_columns:
            target_columns = [c for c in search_columns if c in valid_columns]
        else:
            # テキスト型カラムを自動検出
            result = self.db.execute(
                text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                    AND table_name = :table_name
                    AND data_type IN ('character varying', 'text', 'character')
                """),
                {"table_name": table_name}
            )
            target_columns = [row[0] for row in result]

        if not target_columns:
            return []

        # OR検索クエリ構築
        search_conditions = [f"{col} ILIKE :search" for col in target_columns]
        params = {"search": f"%{search_term}%", "skip": skip, "limit": limit}

        # 範囲フィルタリング
        range_conditions = []
        if range_filters:
            for i, (key, value) in enumerate(range_filters.items()):
                if value is not None:
                    if "__gte" in key:
                        col_name = key.replace("__gte", "")
                        if col_name in valid_columns:
                            param_name = f"range_{i}"
                            range_conditions.append(f"{col_name} >= :{param_name}")
                            params[param_name] = value
                    elif "__lte" in key:
                        col_name = key.replace("__lte", "")
                        if col_name in valid_columns:
                            param_name = f"range_{i}"
                            range_conditions.append(f"{col_name} <= :{param_name}")
                            params[param_name] = value

        # クエリ構築（論理削除されていないレコードのみ）
        where_clause = f"deleted_at IS NULL AND ({' OR '.join(search_conditions)})"
        if range_conditions:
            where_clause += f" AND {' AND '.join(range_conditions)}"

        columns_str = ", ".join(valid_columns)
        query = f"""
            SELECT {columns_str} FROM {table_name}
            WHERE {where_clause}
            ORDER BY id DESC
            OFFSET :skip LIMIT :limit
        """

        result = self.db.execute(text(query), params)

        return [dict(row._mapping) for row in result]
