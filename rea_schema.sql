--
-- PostgreSQL database dump
--

-- Dumped from database version 15.13 (Debian 15.13-1.pgdg120+1)
-- Dumped by pg_dump version 15.13 (Debian 15.13-1.pgdg120+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: area_measurement_type_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.area_measurement_type_enum AS ENUM (
    '1:壁芯',
    '2:内法',
    '3:登記簿'
);


--
-- Name: building_area_measurement_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.building_area_measurement_enum AS ENUM (
    '壁芯',
    '内法',
    '登記簿'
);


--
-- Name: building_manager_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.building_manager_enum AS ENUM (
    '1:常駐',
    '2:日勤',
    '3:巡回',
    '4:自主管理',
    '9:無'
);


--
-- Name: building_structure_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.building_structure_enum AS ENUM (
    '1:木造',
    '2:鉄骨造',
    '3:RC造',
    '4:SRC造',
    '5:軽量鉄骨',
    '6:ALC',
    '9:その他'
);


--
-- Name: contract_period_type_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.contract_period_type_enum AS ENUM (
    '普通借家契約',
    '定期借家契約'
);


--
-- Name: contract_type_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.contract_type_enum AS ENUM (
    '賃貸',
    '売買',
    '賃貸・売買両方可'
);


--
-- Name: current_status_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.current_status_enum AS ENUM (
    '1:空家',
    '2:居住中',
    '3:賃貸中',
    '9:その他'
);


--
-- Name: delivery_timing_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.delivery_timing_enum AS ENUM (
    '1:即時',
    '2:相談',
    '3:期日指定'
);


--
-- Name: designated_road_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.designated_road_enum AS ENUM (
    '無',
    '有'
);


--
-- Name: direction_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.direction_enum AS ENUM (
    '1:北',
    '2:北東',
    '3:東',
    '4:南東',
    '5:南',
    '6:南西',
    '7:西',
    '8:北西'
);


--
-- Name: floor_plan_type_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.floor_plan_type_enum AS ENUM (
    'R',
    'K',
    'DK',
    'LDK',
    'S',
    'L',
    'D',
    'LK',
    'SDK',
    'SLDK',
    'その他'
);


--
-- Name: image_type_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.image_type_enum AS ENUM (
    '01:外観',
    '02:間取図',
    '03:居室',
    '04:キッチン',
    '05:風呂',
    '06:トイレ',
    '07:洗面',
    '08:設備',
    '09:玄関',
    '10:バルコニー',
    '11:眺望',
    '12:共用部',
    '13:周辺環境',
    '14:その他'
);


--
-- Name: investment_property_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.investment_property_enum AS ENUM (
    '0:実需',
    '1:投資'
);


--
-- Name: land_area_measurement_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.land_area_measurement_enum AS ENUM (
    '1:公簿',
    '2:実測',
    '3:私測'
);


--
-- Name: land_rights_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.land_rights_enum AS ENUM (
    '1:所有権',
    '2:借地権',
    '3:定期借地権',
    '4:地上権'
);


--
-- Name: land_transaction_notice_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.land_transaction_notice_enum AS ENUM (
    '0:不要',
    '1:要',
    '2:届出済'
);


--
-- Name: management_association_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.management_association_enum AS ENUM (
    '0:無',
    '1:有'
);


--
-- Name: management_type_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.management_type_enum AS ENUM (
    '1:自主管理',
    '2:管理会社委託',
    '3:一部委託',
    '9:その他'
);


--
-- Name: move_in_period_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.move_in_period_enum AS ENUM (
    '上旬',
    '中旬',
    '下旬'
);


--
-- Name: move_in_timing_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.move_in_timing_enum AS ENUM (
    '即時',
    '相談',
    '期日指定'
);


--
-- Name: parking_availability_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.parking_availability_enum AS ENUM (
    '1:無',
    '2:有(無料)',
    '3:有(有料)',
    '4:近隣(無料)',
    '5:近隣(有料)'
);


--
-- Name: parking_type_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.parking_type_enum AS ENUM (
    '1:平置き',
    '2:機械式',
    '3:立体',
    '9:その他'
);


--
-- Name: price_status_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.price_status_enum AS ENUM (
    '1:確定',
    '2:相談',
    '3:応相談'
);


--
-- Name: property_name_public_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.property_name_public_enum AS ENUM (
    '非公開',
    '公開'
);


--
-- Name: property_publication_type_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.property_publication_type_enum AS ENUM (
    '一般公開',
    '会員限定',
    '自社限定',
    '非公開'
);


--
-- Name: property_type_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.property_type_enum AS ENUM (
    '1:マンション',
    '2:一戸建て',
    '3:土地',
    '4:その他'
);


--
-- Name: publication_status_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.publication_status_enum AS ENUM (
    '1:公開',
    '2:非公開',
    '3:限定公開'
);


--
-- Name: road_direction_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.road_direction_enum AS ENUM (
    '北',
    '北東',
    '東',
    '南東',
    '南',
    '南西',
    '西',
    '北西'
);


--
-- Name: road_frontage_status_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.road_frontage_status_enum AS ENUM (
    '一方',
    '二方（角地）',
    '三方',
    '四方',
    '接道なし'
);


--
-- Name: road_type_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.road_type_enum AS ENUM (
    '国道',
    '都道府県道',
    '市区町村道',
    '私道',
    '位置指定道路',
    '開発道路',
    'その他'
);


--
-- Name: room_type_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.room_type_enum AS ENUM (
    '1:R',
    '2:K',
    '3:DK',
    '4:LDK',
    '5:SLDK',
    '6:その他'
);


--
-- Name: sales_status_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.sales_status_enum AS ENUM (
    '1:販売中',
    '2:商談中',
    '3:成約済み',
    '4:販売終了'
);


--
-- Name: setback_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.setback_enum AS ENUM (
    '0:不要',
    '1:要',
    '2:セットバック済'
);


--
-- Name: tax_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.tax_enum AS ENUM (
    '税込',
    '税抜',
    '非課税'
);


--
-- Name: tenant_placement_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.tenant_placement_enum AS ENUM (
    '不可',
    '可'
);


--
-- Name: topography_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.topography_enum AS ENUM (
    '平坦',
    '高台',
    '低地',
    'ひな壇',
    '傾斜地',
    '不整形地',
    'その他'
);


--
-- Name: transaction_type_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.transaction_type_enum AS ENUM (
    '1:売主',
    '2:代理',
    '3:専任媒介',
    '4:一般媒介',
    '5:専属専任'
);


--
-- Name: use_district_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.use_district_enum AS ENUM (
    '1:第一種低層住居専用',
    '2:第二種低層住居専用',
    '3:第一種中高層住居専用',
    '4:第二種中高層住居専用',
    '5:第一種住居',
    '6:第二種住居',
    '7:準住居',
    '8:近隣商業',
    '9:商業',
    '10:準工業',
    '11:工業',
    '12:工業専用'
);


--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: amenities; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.amenities (
    id integer NOT NULL,
    property_id integer,
    facilities jsonb,
    property_features text,
    notes text,
    transportation jsonb,
    other_transportation character varying(500),
    elementary_school_name character varying(100),
    elementary_school_distance integer,
    junior_high_school_name character varying(100),
    junior_high_school_distance integer,
    convenience_store_distance integer,
    supermarket_distance integer,
    general_hospital_distance integer,
    shopping_street_distance integer,
    drugstore_distance integer,
    park_distance integer,
    bank_distance integer,
    other_facility_name character varying(100),
    other_facility_distance integer,
    renovations jsonb,
    energy_consumption_min integer,
    energy_consumption_max integer,
    insulation_performance_min integer,
    insulation_performance_max integer,
    utility_cost_min integer,
    utility_cost_max integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: amenities_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.amenities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: amenities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.amenities_id_seq OWNED BY public.amenities.id;


--
-- Name: building_info; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.building_info (
    id integer NOT NULL,
    property_id integer,
    building_structure public.building_structure_enum,
    construction_date date,
    building_floors_above integer,
    building_floors_below integer,
    total_units integer,
    total_site_area numeric(10,2),
    building_area numeric(10,2),
    total_floor_area numeric(10,2),
    exclusive_area numeric(10,2),
    balcony_area numeric(10,2),
    area_measurement_type public.area_measurement_type_enum,
    room_floor integer,
    direction public.direction_enum,
    room_count integer,
    room_type public.room_type_enum,
    floor_plans jsonb,
    floor_plan_notes text,
    management_type public.management_type_enum,
    management_company character varying(255),
    management_association public.management_association_enum,
    building_manager public.building_manager_enum,
    parking_availability public.parking_availability_enum,
    parking_type public.parking_type_enum,
    parking_capacity integer,
    parking_distance integer,
    parking_notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: building_info_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.building_info_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: building_info_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.building_info_id_seq OWNED BY public.building_info.id;


--
-- Name: building_structure; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.building_structure (
    id character varying(20) NOT NULL,
    label character varying(100) NOT NULL,
    group_name character varying(100),
    homes_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: column_labels; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.column_labels (
    table_name character varying(100) NOT NULL,
    column_name character varying(100) NOT NULL,
    japanese_label character varying(200) NOT NULL,
    description text,
    data_type character varying(100),
    is_required boolean,
    display_order integer,
    group_name character varying(100),
    input_type character varying(50),
    max_length integer,
    enum_values text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: current_status; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.current_status (
    id character varying(30) NOT NULL,
    label character varying(100) NOT NULL,
    group_name character varying(100),
    homes_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: equipment_master; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.equipment_master (
    id character varying(50) NOT NULL,
    item_name character varying(100) NOT NULL,
    tab_group character varying(100),
    display_name character varying(100),
    data_type character varying(50),
    dependent_items text,
    remarks text,
    homes_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: floor_plan_room_types; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.floor_plan_room_types (
    id character varying(20) NOT NULL,
    label character varying(100) NOT NULL,
    group_name character varying(100),
    homes_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: image_types; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.image_types (
    id character varying(30) NOT NULL,
    label character varying(100) NOT NULL,
    group_name character varying(100),
    homes_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: land_info; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.land_info (
    id integer NOT NULL,
    property_id integer,
    postal_code character varying(10),
    address_code integer,
    prefecture character varying(10),
    city character varying(50),
    address character varying(255),
    address_detail character varying(255),
    latitude numeric(10,8),
    longitude numeric(11,8),
    land_area numeric(10,2),
    land_area_measurement public.land_area_measurement_enum,
    land_category character varying(50),
    use_district public.use_district_enum,
    city_planning character varying(100),
    building_coverage_ratio numeric(5,2),
    floor_area_ratio numeric(5,2),
    land_rights public.land_rights_enum,
    land_rent integer,
    land_ownership_ratio character varying(50),
    private_road_area numeric(10,2),
    private_road_ratio character varying(50),
    setback public.setback_enum,
    setback_amount numeric(5,2),
    land_transaction_notice public.land_transaction_notice_enum,
    legal_restrictions text,
    road_info jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: land_info_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.land_info_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: land_info_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.land_info_id_seq OWNED BY public.land_info.id;


--
-- Name: land_rights; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.land_rights (
    id character varying(30) NOT NULL,
    label character varying(100) NOT NULL,
    group_name character varying(100),
    homes_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: properties; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.properties (
    id integer NOT NULL,
    company_property_number character varying(50),
    external_property_id character varying(50),
    property_name character varying(255) NOT NULL,
    property_name_kana character varying(255),
    property_name_public boolean DEFAULT true,
    property_type public.property_type_enum,
    investment_property public.investment_property_enum DEFAULT '0:実需'::public.investment_property_enum,
    sales_status public.sales_status_enum DEFAULT '1:販売中'::public.sales_status_enum,
    publication_status public.publication_status_enum DEFAULT '1:公開'::public.publication_status_enum,
    affiliated_group character varying(100),
    priority_score integer DEFAULT 0,
    property_url character varying(500),
    sale_price bigint,
    price_per_tsubo integer,
    price_status public.price_status_enum DEFAULT '1:確定'::public.price_status_enum,
    tax_type character varying(20),
    yield_rate numeric(5,2),
    current_yield numeric(5,2),
    management_fee integer,
    repair_reserve_fund integer,
    repair_reserve_fund_base integer,
    parking_fee integer,
    housing_insurance integer,
    current_status public.current_status_enum,
    delivery_date date,
    delivery_timing public.delivery_timing_enum,
    move_in_consultation text,
    transaction_type public.transaction_type_enum,
    brokerage_fee integer,
    commission_split_ratio numeric(5,2),
    brokerage_contract_date date,
    listing_start_date date,
    listing_confirmation_date date,
    contractor_company_name character varying(255),
    contractor_contact_person character varying(100),
    contractor_phone character varying(20),
    contractor_email character varying(255),
    contractor_address character varying(500),
    contractor_license_number character varying(50),
    property_manager_name character varying(100),
    internal_memo text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: properties_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.properties_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: properties_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.properties_id_seq OWNED BY public.properties.id;


--
-- Name: property_equipment; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.property_equipment (
    id bigint NOT NULL,
    property_id bigint NOT NULL,
    equipment_id character varying(50) NOT NULL,
    value character varying(10),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: property_equipment_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.property_equipment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: property_equipment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.property_equipment_id_seq OWNED BY public.property_equipment.id;


--
-- Name: property_images; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.property_images (
    id integer NOT NULL,
    property_id integer,
    image_type public.image_type_enum,
    file_path character varying(500),
    file_url character varying(500),
    display_order integer,
    caption text,
    is_public boolean DEFAULT true,
    uploaded_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: property_images_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.property_images_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: property_images_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.property_images_id_seq OWNED BY public.property_images.id;


--
-- Name: property_types; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.property_types (
    id character varying(40) NOT NULL,
    label character varying(100) NOT NULL,
    group_name character varying(100),
    homes_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: zoning_districts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.zoning_districts (
    id character varying(40) NOT NULL,
    label character varying(100) NOT NULL,
    group_name character varying(100),
    homes_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: amenities id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.amenities ALTER COLUMN id SET DEFAULT nextval('public.amenities_id_seq'::regclass);


--
-- Name: building_info id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.building_info ALTER COLUMN id SET DEFAULT nextval('public.building_info_id_seq'::regclass);


--
-- Name: land_info id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.land_info ALTER COLUMN id SET DEFAULT nextval('public.land_info_id_seq'::regclass);


--
-- Name: properties id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.properties ALTER COLUMN id SET DEFAULT nextval('public.properties_id_seq'::regclass);


--
-- Name: property_equipment id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.property_equipment ALTER COLUMN id SET DEFAULT nextval('public.property_equipment_id_seq'::regclass);


--
-- Name: property_images id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.property_images ALTER COLUMN id SET DEFAULT nextval('public.property_images_id_seq'::regclass);


--
-- Name: amenities amenities_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.amenities
    ADD CONSTRAINT amenities_pkey PRIMARY KEY (id);


--
-- Name: building_info building_info_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.building_info
    ADD CONSTRAINT building_info_pkey PRIMARY KEY (id);


--
-- Name: building_structure building_structure_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.building_structure
    ADD CONSTRAINT building_structure_pkey PRIMARY KEY (id);


--
-- Name: column_labels column_labels_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.column_labels
    ADD CONSTRAINT column_labels_pkey PRIMARY KEY (table_name, column_name);


--
-- Name: current_status current_status_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.current_status
    ADD CONSTRAINT current_status_pkey PRIMARY KEY (id);


--
-- Name: equipment_master equipment_master_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.equipment_master
    ADD CONSTRAINT equipment_master_pkey PRIMARY KEY (id);


--
-- Name: floor_plan_room_types floor_plan_room_types_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.floor_plan_room_types
    ADD CONSTRAINT floor_plan_room_types_pkey PRIMARY KEY (id);


--
-- Name: image_types image_types_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.image_types
    ADD CONSTRAINT image_types_pkey PRIMARY KEY (id);


--
-- Name: land_info land_info_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.land_info
    ADD CONSTRAINT land_info_pkey PRIMARY KEY (id);


--
-- Name: land_rights land_rights_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.land_rights
    ADD CONSTRAINT land_rights_pkey PRIMARY KEY (id);


--
-- Name: properties properties_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.properties
    ADD CONSTRAINT properties_pkey PRIMARY KEY (id);


--
-- Name: property_equipment property_equipment_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.property_equipment
    ADD CONSTRAINT property_equipment_pkey PRIMARY KEY (id);


--
-- Name: property_images property_images_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.property_images
    ADD CONSTRAINT property_images_pkey PRIMARY KEY (id);


--
-- Name: property_types property_types_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.property_types
    ADD CONSTRAINT property_types_pkey PRIMARY KEY (id);


--
-- Name: zoning_districts zoning_districts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.zoning_districts
    ADD CONSTRAINT zoning_districts_pkey PRIMARY KEY (id);


--
-- Name: idx_amenities_property; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_amenities_property ON public.amenities USING btree (property_id);


--
-- Name: idx_building_info_property; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_building_info_property ON public.building_info USING btree (property_id);


--
-- Name: idx_land_info_property; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_land_info_property ON public.land_info USING btree (property_id);


--
-- Name: idx_properties_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_properties_status ON public.properties USING btree (sales_status);


--
-- Name: idx_properties_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_properties_type ON public.properties USING btree (property_type);


--
-- Name: idx_property_images_order; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_property_images_order ON public.property_images USING btree (property_id, display_order);


--
-- Name: idx_property_images_property; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_property_images_property ON public.property_images USING btree (property_id);


--
-- Name: column_labels update_column_labels_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_column_labels_updated_at BEFORE UPDATE ON public.column_labels FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: amenities amenities_property_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.amenities
    ADD CONSTRAINT amenities_property_id_fkey FOREIGN KEY (property_id) REFERENCES public.properties(id) ON DELETE CASCADE;


--
-- Name: building_info building_info_property_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.building_info
    ADD CONSTRAINT building_info_property_id_fkey FOREIGN KEY (property_id) REFERENCES public.properties(id) ON DELETE CASCADE;


--
-- Name: property_equipment fk_property_equipment_equipment; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.property_equipment
    ADD CONSTRAINT fk_property_equipment_equipment FOREIGN KEY (equipment_id) REFERENCES public.equipment_master(id);


--
-- Name: land_info land_info_property_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.land_info
    ADD CONSTRAINT land_info_property_id_fkey FOREIGN KEY (property_id) REFERENCES public.properties(id) ON DELETE CASCADE;


--
-- Name: property_images property_images_property_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.property_images
    ADD CONSTRAINT property_images_property_id_fkey FOREIGN KEY (property_id) REFERENCES public.properties(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

