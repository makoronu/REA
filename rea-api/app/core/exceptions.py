"""
REA カスタム例外クラス

HTTPExceptionを直接使う代わりに、意味のあるカスタム例外を使用することで：
- エラーハンドリングの一貫性を確保
- エラーメッセージの標準化
- デバッグ効率の向上
"""
from typing import Any, Optional


class REAException(Exception):
    """REA基底例外"""
    status_code: int = 500
    detail: str = "内部エラーが発生しました"

    def __init__(self, detail: Optional[str] = None, **kwargs: Any):
        self.detail = detail or self.__class__.detail
        self.extra = kwargs
        super().__init__(self.detail)


class ResourceNotFound(REAException):
    """リソース未検出例外"""
    status_code = 404
    detail = "リソースが見つかりません"

    def __init__(self, resource_type: str, resource_id: Any = None):
        self.resource_type = resource_type
        self.resource_id = resource_id
        if resource_id:
            detail = f"{resource_type} (ID: {resource_id}) が見つかりません"
        else:
            detail = f"{resource_type}が見つかりません"
        super().__init__(detail)


class ValidationError(REAException):
    """バリデーションエラー"""
    status_code = 400
    detail = "入力値が不正です"

    def __init__(self, field: str = None, message: str = None):
        self.field = field
        if field and message:
            detail = f"{field}: {message}"
        elif message:
            detail = message
        else:
            detail = self.__class__.detail
        super().__init__(detail)


class ConfigurationError(REAException):
    """設定エラー"""
    status_code = 400
    detail = "設定が不正です"


class ExternalServiceError(REAException):
    """外部サービスエラー（外部API等）"""
    status_code = 502
    detail = "外部サービスへの接続に失敗しました"

    def __init__(self, service_name: str, message: str = None):
        self.service_name = service_name
        detail = f"{service_name}: {message}" if message else f"{service_name}への接続に失敗しました"
        super().__init__(detail)


class DatabaseError(REAException):
    """データベースエラー"""
    status_code = 500
    detail = "データベース操作に失敗しました"


class DuplicateError(REAException):
    """重複エラー"""
    status_code = 409
    detail = "既に存在します"

    def __init__(self, resource_type: str, identifier: Any = None):
        self.resource_type = resource_type
        self.identifier = identifier
        if identifier:
            detail = f"{resource_type} ({identifier}) は既に存在します"
        else:
            detail = f"{resource_type}は既に存在します"
        super().__init__(detail)
