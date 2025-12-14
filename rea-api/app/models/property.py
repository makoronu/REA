# app/models/property.py
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, Numeric, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Property(Base):
    __tablename__ = "properties"

    # 基本情報
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_property_number = Column(String(50), nullable=True, comment="自社物件番号")
    external_property_id = Column(String(100), nullable=True, comment="外部物件ID")
    property_name = Column(String(255), nullable=True, comment="物件名")
    property_name_kana = Column(String(255), nullable=True, comment="物件名カナ")
    property_name_public = Column(String(255), nullable=True, comment="公開用物件名")
    property_type = Column(String(50), nullable=True, comment="物件種別")
    investment_property = Column(Boolean, default=False, comment="投資用物件フラグ")

    # ステータス
    sales_status = Column(String(50), nullable=True, comment="販売状況")
    publication_status = Column(String(50), nullable=True, comment="公開状況")
    affiliated_group = Column(String(100), nullable=True, comment="所属グループ")
    priority_score = Column(Integer, nullable=True, comment="優先度スコア")
    property_url = Column(String(500), nullable=True, comment="物件URL")

    # 所在地
    postal_code = Column(String(10), nullable=True, comment="郵便番号")
    prefecture = Column(String(20), nullable=True, comment="都道府県")
    city = Column(String(100), nullable=True, comment="市区町村")
    address = Column(String(200), nullable=True, comment="町域・番地")
    address_detail = Column(String(200), nullable=True, comment="建物名・部屋番号")
    latitude = Column(Numeric(10, 8), nullable=True, comment="緯度")
    longitude = Column(Numeric(11, 8), nullable=True, comment="経度")

    # 学区・交通
    elementary_school = Column(String(100), nullable=True, comment="小学校区")
    elementary_school_minutes = Column(Integer, nullable=True, comment="小学校徒歩分")
    junior_high_school = Column(String(100), nullable=True, comment="中学校区")
    junior_high_school_minutes = Column(Integer, nullable=True, comment="中学校徒歩分")

    # キャッチコピー・備考
    catch_copy = Column(Text, nullable=True, comment="キャッチコピー1")
    catch_copy2 = Column(Text, nullable=True, comment="キャッチコピー2")
    catch_copy3 = Column(Text, nullable=True, comment="キャッチコピー3")
    remarks = Column(Text, nullable=True, comment="備考")

    # ZOHO連携
    zoho_id = Column(String(50), nullable=True, comment="ZOHO ID")
    zoho_synced_at = Column(DateTime, nullable=True, comment="ZOHO同期日時")
    zoho_sync_status = Column(String(20), nullable=True, comment="ZOHO同期状態")

    # 価格情報
    sale_price = Column(Numeric(15, 2), nullable=True, comment="販売価格")
    price_per_tsubo = Column(Numeric(15, 2), nullable=True, comment="坪単価")
    price_status = Column(String(50), nullable=True, comment="価格状況")
    tax_type = Column(String(50), nullable=True, comment="税種別")

    # 利回り・費用
    yield_rate = Column(Numeric(5, 2), nullable=True, comment="利回り")
    current_yield = Column(Numeric(5, 2), nullable=True, comment="現行利回り")
    management_fee = Column(Numeric(10, 2), nullable=True, comment="管理費")
    repair_reserve_fund = Column(Numeric(10, 2), nullable=True, comment="修繕積立金")
    repair_reserve_fund_base = Column(Numeric(10, 2), nullable=True, comment="修繕積立基金")
    parking_fee = Column(Numeric(10, 2), nullable=True, comment="駐車場代")
    housing_insurance = Column(Numeric(10, 2), nullable=True, comment="住宅保険")

    # 入居・引渡し
    current_status = Column(String(50), nullable=True, comment="現況")
    delivery_date = Column(String(100), nullable=True, comment="引渡日")
    delivery_timing = Column(String(100), nullable=True, comment="引渡時期")
    move_in_consultation = Column(Boolean, default=False, comment="入居相談可")

    # 取引情報
    transaction_type = Column(String(50), nullable=True, comment="取引態様")
    brokerage_fee = Column(Numeric(10, 2), nullable=True, comment="仲介手数料")
    commission_split_ratio = Column(String(50), nullable=True, comment="手数料分配率")
    brokerage_contract_date = Column(DateTime, nullable=True, comment="媒介契約日")
    listing_start_date = Column(DateTime, nullable=True, comment="掲載開始日")
    listing_confirmation_date = Column(DateTime, nullable=True, comment="掲載確認日")

    # 元請会社情報
    contractor_company_name = Column(String(200), nullable=True, comment="元請会社名")
    contractor_contact_person = Column(String(100), nullable=True, comment="担当者名")
    contractor_phone = Column(String(20), nullable=True, comment="電話番号")
    contractor_email = Column(String(200), nullable=True, comment="メールアドレス")
    contractor_address = Column(String(500), nullable=True, comment="会社住所")
    contractor_license_number = Column(String(50), nullable=True, comment="宅建免許番号")

    # 管理情報
    property_manager_name = Column(String(100), nullable=True, comment="物件管理者名")
    internal_memo = Column(Text, nullable=True, comment="社内メモ")
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="作成日時")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=True, comment="更新日時")

    def __repr__(self):
        return f"<Property(id={self.id}, name='{self.property_name}', contractor='{self.contractor_company_name}')>"
