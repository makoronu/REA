"""
メタデータ駆動バリデーション

column_labelsテーブルのis_updatable, is_required, data_type等を使用して
入力データを自動的にバリデーション・フィルタリングする。

使い方:
    from shared.validators import MetadataValidator

    validator = MetadataValidator(db_session)

    # 更新不可カラムを除外
    filtered = validator.filter_updatable('properties', data)

    # バリデーション実行
    errors = validator.validate('properties', data)
"""

from typing import Dict, Any, List, Set, Optional, Tuple
from functools import lru_cache


class MetadataValidator:
    """メタデータ駆動のバリデーター"""

    def __init__(self, db_session=None):
        """
        Args:
            db_session: SQLAlchemyセッション（Noneの場合は直接接続）
        """
        self.db = db_session
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _get_column_metadata(self, table_name: str) -> Dict[str, Dict[str, Any]]:
        """
        テーブルのカラムメタデータを取得（キャッシュ付き）

        Returns:
            {column_name: {is_updatable, is_required, data_type, ...}}
        """
        if table_name in self._cache:
            return self._cache[table_name]

        if self.db is None:
            from shared.database import READatabase
            db = READatabase()
            conn = db.get_connection()
            cur = conn.cursor()
        else:
            from sqlalchemy import text
            result = self.db.execute(text("""
                SELECT column_name, is_updatable, is_required, data_type,
                       input_type, japanese_label
                FROM column_labels
                WHERE table_name = :table_name
            """), {"table_name": table_name})

            metadata = {}
            for row in result:
                metadata[row.column_name] = {
                    'is_updatable': row.is_updatable,
                    'is_required': row.is_required,
                    'data_type': row.data_type,
                    'input_type': row.input_type,
                    'label': row.japanese_label,
                }
            self._cache[table_name] = metadata
            return metadata

        try:
            cur.execute("""
                SELECT column_name, is_updatable, is_required, data_type,
                       input_type, japanese_label
                FROM column_labels
                WHERE table_name = %s
            """, (table_name,))

            metadata = {}
            for row in cur.fetchall():
                metadata[row[0]] = {
                    'is_updatable': row[1],
                    'is_required': row[2],
                    'data_type': row[3],
                    'input_type': row[4],
                    'label': row[5],
                }
            self._cache[table_name] = metadata
            return metadata
        finally:
            cur.close()
            conn.close()

    def get_updatable_columns(self, table_name: str) -> Set[str]:
        """更新可能なカラム名のセットを取得"""
        metadata = self._get_column_metadata(table_name)
        return {col for col, info in metadata.items() if info.get('is_updatable', True)}

    def get_non_updatable_columns(self, table_name: str) -> Set[str]:
        """更新不可カラム名のセットを取得"""
        metadata = self._get_column_metadata(table_name)
        return {col for col, info in metadata.items() if not info.get('is_updatable', True)}

    def filter_updatable(self, table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新不可カラムを除外したデータを返す

        Args:
            table_name: テーブル名
            data: 入力データ

        Returns:
            更新可能カラムのみ含むデータ
        """
        updatable = self.get_updatable_columns(table_name)

        # メタデータに定義されていないカラムも除外（安全側に倒す）
        # ただし、column_labelsに未登録のカラムは通す（新規カラム対応）
        metadata = self._get_column_metadata(table_name)

        filtered = {}
        for key, value in data.items():
            # メタデータにあって更新可能、またはメタデータに未登録
            if key in updatable or key not in metadata:
                # ただしシステムカラムは常に除外
                if key not in {'id', 'property_id', 'created_at', 'updated_at'}:
                    filtered[key] = value

        return filtered

    def validate(self, table_name: str, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        データをバリデーション

        Args:
            table_name: テーブル名
            data: 入力データ

        Returns:
            エラーリスト [{'field': 'xxx', 'message': 'yyy'}, ...]
        """
        errors = []
        metadata = self._get_column_metadata(table_name)

        for col_name, col_info in metadata.items():
            value = data.get(col_name)

            # 必須チェック
            if col_info.get('is_required') and (value is None or value == ''):
                label = col_info.get('label') or col_name
                errors.append({
                    'field': col_name,
                    'message': f'{label}は必須です'
                })

            # 型チェック（値がある場合のみ）
            if value is not None and value != '':
                data_type = col_info.get('data_type')
                type_error = self._validate_type(value, data_type, col_name)
                if type_error:
                    errors.append(type_error)

        return errors

    def _validate_type(self, value: Any, data_type: str, col_name: str) -> Optional[Dict[str, str]]:
        """型バリデーション"""
        if data_type is None:
            return None

        try:
            if data_type in ('integer', 'bigint', 'smallint'):
                if not isinstance(value, (int, float)) and value != '':
                    int(value)  # 変換テスト
            elif data_type in ('numeric', 'decimal', 'real', 'double precision'):
                if not isinstance(value, (int, float)) and value != '':
                    float(value)
            elif data_type == 'boolean':
                if not isinstance(value, bool) and value not in ('true', 'false', '0', '1', 0, 1):
                    return {'field': col_name, 'message': f'{col_name}は真偽値である必要があります'}
        except (ValueError, TypeError):
            return {'field': col_name, 'message': f'{col_name}の型が不正です（期待: {data_type}）'}

        return None

    def filter_and_validate(self, table_name: str, data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, str]]]:
        """
        フィルタリングとバリデーションを同時実行

        Returns:
            (filtered_data, errors)
        """
        filtered = self.filter_updatable(table_name, data)
        errors = self.validate(table_name, filtered)
        return filtered, errors


# シングルトンインスタンス（キャッシュ共有用）
_validator_instance: Optional[MetadataValidator] = None


def get_validator(db_session=None) -> MetadataValidator:
    """バリデーターインスタンスを取得"""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = MetadataValidator(db_session)
    elif db_session is not None:
        _validator_instance.db = db_session
    return _validator_instance


def filter_updatable(table_name: str, data: Dict[str, Any], db_session=None) -> Dict[str, Any]:
    """ショートカット関数: 更新不可カラムを除外"""
    return get_validator(db_session).filter_updatable(table_name, data)


def validate_input(table_name: str, data: Dict[str, Any], db_session=None) -> List[Dict[str, str]]:
    """ショートカット関数: バリデーション実行"""
    return get_validator(db_session).validate(table_name, data)
