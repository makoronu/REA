# app/models/property.py
"""
SQLAlchemy Base定義のみ

注意: このファイルはAlembicマイグレーション用にBaseクラスを提供するためだけに存在する。
CRUD操作はGenericCRUDを使用し、このモデルは使用しない。

メタデータ駆動: 全てのカラム定義はcolumn_labelsテーブルで管理する。
"""
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# NOTE: 以前はここに Property クラスがあったが、メタデータ駆動に移行したため削除。
# CRUD操作は app/crud/generic.py の GenericCRUD を使用すること。
