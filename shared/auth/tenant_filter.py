# テナント分離フィルタ（SQLインジェクション対策済み）
from typing import Tuple, List, Any


class TenantFilter:
    """
    テナント分離フィルタ

    全クエリでorganization_idによるフィルタを適用。
    super_adminは全テナントアクセス可能。
    """

    @staticmethod
    def get_condition(current_user: dict) -> Tuple[str, List[Any]]:
        """
        WHERE句の条件文とパラメータを返す

        Args:
            current_user: 認証済みユーザー情報
                - role_code: str
                - organization_id: int

        Returns:
            (条件文字列, パラメータリスト)

        Usage:
            condition, params = TenantFilter.get_condition(user)
            query = f"SELECT * FROM properties WHERE {condition}"
            cursor.execute(query, params)
        """
        if current_user.get('role_code') == 'super_admin':
            return ("1=1", [])
        return ("organization_id = %s", [current_user['organization_id']])

    @staticmethod
    def get_condition_with_alias(
        current_user: dict,
        table_alias: str
    ) -> Tuple[str, List[Any]]:
        """
        テーブルエイリアス付きの条件を返す

        Args:
            current_user: 認証済みユーザー情報
            table_alias: テーブルエイリアス（例: 'p'）

        Returns:
            (条件文字列, パラメータリスト)

        Usage:
            condition, params = TenantFilter.get_condition_with_alias(user, 'p')
            query = f"SELECT * FROM properties p WHERE {condition}"
        """
        if current_user.get('role_code') == 'super_admin':
            return ("1=1", [])
        return (f"{table_alias}.organization_id = %s", [current_user['organization_id']])

    @staticmethod
    def validate_access(resource_org_id: int, current_user: dict) -> bool:
        """
        リソースへのアクセス権をチェック

        Args:
            resource_org_id: リソースのorganization_id
            current_user: 認証済みユーザー情報

        Returns:
            アクセス可能ならTrue
        """
        if current_user.get('role_code') == 'super_admin':
            return True
        return resource_org_id == current_user.get('organization_id')

    @staticmethod
    def get_org_id_for_insert(current_user: dict, explicit_org_id: int = None) -> int:
        """
        INSERT時に使用するorganization_idを返す

        Args:
            current_user: 認証済みユーザー情報
            explicit_org_id: super_adminが明示的に指定する組織ID

        Returns:
            organization_id

        Raises:
            ValueError: super_adminが組織を指定しなかった場合
        """
        if current_user.get('role_code') == 'super_admin':
            if explicit_org_id is None:
                raise ValueError("super_adminは組織IDを明示的に指定してください")
            return explicit_org_id
        return current_user['organization_id']
