# app/models/property.py
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Property(Base):
    __tablename__ = "properties"

    # 基本情報
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, comment="物件名")
    price = Column(Float, nullable=False, comment="価格")
    price_unit = Column(String(20), default="その他", comment="価格単位")

    # 🏢 元請会社情報（新規追加）
    contractor_company_name = Column(String(200), nullable=True, comment="元請会社名")
    contractor_contact_person = Column(String(100), nullable=True, comment="担当者名")
    contractor_phone = Column(String(20), nullable=True, comment="電話番号")
    contractor_email = Column(String(200), nullable=True, comment="メールアドレス")
    contractor_address = Column(String(500), nullable=True, comment="会社住所")
    contractor_license_number = Column(String(50), nullable=True, comment="宅建免許番号")

    # 物件詳細
    property_type = Column(String(50), nullable=True, comment="物件種別")
    building_structure = Column(String(50), nullable=True, comment="建物構造")
    floors_total = Column(Integer, nullable=True, comment="総階数")
    floor_current = Column(Integer, nullable=True, comment="現在階")

    # 面積・間取り
    area_building = Column(Float, nullable=True, comment="建物面積（㎡）")
    area_land = Column(Float, nullable=True, comment="土地面積（㎡）")
    layout = Column(String(20), nullable=True, comment="間取り")
    rooms = Column(Integer, nullable=True, comment="部屋数")

    # 築年・駅情報
    built_year = Column(Integer, nullable=True, comment="築年")
    station_name = Column(String(100), nullable=True, comment="最寄り駅")
    station_walk_time = Column(Integer, nullable=True, comment="徒歩時間（分）")
    station_line = Column(String(100), nullable=True, comment="路線名")

    # 住所
    prefecture = Column(String(50), nullable=True, comment="都道府県")
    city = Column(String(100), nullable=True, comment="市区町村")
    address = Column(String(255), nullable=True, comment="詳細住所")

    # JSON型フィールド
    equipments = Column(JSON, nullable=True, comment="設備一覧（配列）")
    images = Column(JSON, nullable=True, comment="画像URL一覧（配列）")

    # ホームズ連携
    homes_id = Column(String(100), nullable=True, unique=True, comment="ホームズ物件ID")
    homes_url = Column(String(500), nullable=True, comment="ホームズURL")

    # 管理情報
    description = Column(Text, nullable=True, comment="物件説明")
    is_active = Column(Boolean, default=True, nullable=False, comment="掲載中フラグ")
    source = Column(String(50), default="homes", nullable=False, comment="取得元")
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="作成日時")
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=True, comment="更新日時"
    )

    def __repr__(self):
        return f"<Property(id={self.id}, title='{self.title}', contractor='{self.contractor_company_name}', price={self.price})>"
