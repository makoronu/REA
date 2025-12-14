# app/crud/property.py
"""
旧CRUD - 非推奨

このファイルはメタデータ駆動に移行したため使用しない。
CRUD操作は app/crud/generic.py の GenericCRUD を使用すること。

後方互換性のために残しているが、新規開発では使用禁止。
"""

# NOTE: 旧コードは削除済み。
# GenericCRUD を使用してください。

from app.crud.generic import GenericCRUD

__all__ = ["GenericCRUD"]
