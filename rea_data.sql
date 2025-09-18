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
-- Data for Name: properties; Type: TABLE DATA; Schema: public; Owner: rea_user
--

SET SESSION AUTHORIZATION DEFAULT;

ALTER TABLE public.properties DISABLE TRIGGER ALL;

COPY public.properties (id, company_property_number, external_property_id, property_name, property_name_kana, property_name_public, property_type, investment_property, sales_status, publication_status, affiliated_group, priority_score, property_url, sale_price, price_per_tsubo, price_status, tax_type, yield_rate, current_yield, management_fee, repair_reserve_fund, repair_reserve_fund_base, parking_fee, housing_insurance, current_status, delivery_date, delivery_timing, move_in_consultation, transaction_type, brokerage_fee, commission_split_ratio, brokerage_contract_date, listing_start_date, listing_confirmation_date, contractor_company_name, contractor_contact_person, contractor_phone, contractor_email, contractor_address, contractor_license_number, property_manager_name, internal_memo, created_at, updated_at) FROM stdin;
\.


ALTER TABLE public.properties ENABLE TRIGGER ALL;

--
-- Data for Name: amenities; Type: TABLE DATA; Schema: public; Owner: rea_user
--

ALTER TABLE public.amenities DISABLE TRIGGER ALL;

COPY public.amenities (id, property_id, facilities, property_features, notes, transportation, other_transportation, elementary_school_name, elementary_school_distance, junior_high_school_name, junior_high_school_distance, convenience_store_distance, supermarket_distance, general_hospital_distance, shopping_street_distance, drugstore_distance, park_distance, bank_distance, other_facility_name, other_facility_distance, renovations, energy_consumption_min, energy_consumption_max, insulation_performance_min, insulation_performance_max, utility_cost_min, utility_cost_max, created_at, updated_at) FROM stdin;
\.


ALTER TABLE public.amenities ENABLE TRIGGER ALL;

--
-- Data for Name: building_info; Type: TABLE DATA; Schema: public; Owner: rea_user
--

ALTER TABLE public.building_info DISABLE TRIGGER ALL;

COPY public.building_info (id, property_id, building_structure, construction_date, building_floors_above, building_floors_below, total_units, total_site_area, building_area, total_floor_area, exclusive_area, balcony_area, area_measurement_type, room_floor, direction, room_count, room_type, floor_plans, floor_plan_notes, management_type, management_company, management_association, building_manager, parking_availability, parking_type, parking_capacity, parking_distance, parking_notes, created_at, updated_at) FROM stdin;
\.


ALTER TABLE public.building_info ENABLE TRIGGER ALL;

--
-- Data for Name: building_structure; Type: TABLE DATA; Schema: public; Owner: rea_user
--

ALTER TABLE public.building_structure DISABLE TRIGGER ALL;

COPY public.building_structure (id, label, group_name, homes_id, created_at, updated_at) FROM stdin;
wood	木造	木造系	\N	2025-07-23 11:21:57.290869	2025-07-23 11:21:57.290869
steel	鉄骨造	鉄骨系	\N	2025-07-23 11:21:57.290869	2025-07-23 11:21:57.290869
rc	RC造	コンクリート系	\N	2025-07-23 11:21:57.290869	2025-07-23 11:21:57.290869
src	SRC造	コンクリート系	\N	2025-07-23 11:21:57.290869	2025-07-23 11:21:57.290869
pc	PC造	コンクリート系	\N	2025-07-23 11:21:57.290869	2025-07-23 11:21:57.290869
hpc	HPC造	コンクリート系	\N	2025-07-23 11:21:57.290869	2025-07-23 11:21:57.290869
lgs	軽量鉄骨造	鉄骨系	\N	2025-07-23 11:21:57.290869	2025-07-23 11:21:57.290869
cbb	コンクリートブロック造	コンクリート系	\N	2025-07-23 11:21:57.290869	2025-07-23 11:21:57.290869
alc	ALC造	その他	\N	2025-07-23 11:21:57.290869	2025-07-23 11:21:57.290869
pcpanel	PCパネル造	コンクリート系	\N	2025-07-23 11:21:57.290869	2025-07-23 11:21:57.290869
log	ログハウス	木造系	\N	2025-07-23 11:21:57.290869	2025-07-23 11:21:57.290869
other	その他	その他	\N	2025-07-23 11:21:57.290869	2025-07-23 11:21:57.290869
\.


ALTER TABLE public.building_structure ENABLE TRIGGER ALL;

--
-- Data for Name: column_labels; Type: TABLE DATA; Schema: public; Owner: rea_user
--

ALTER TABLE public.column_labels DISABLE TRIGGER ALL;

COPY public.column_labels (table_name, column_name, japanese_label, description, data_type, is_required, display_order, group_name, input_type, max_length, enum_values, created_at, updated_at) FROM stdin;
properties	id	ID	プライマリキー		\N	1	システム	\N	\N		2025-07-28 07:16:19.178402	2025-07-28 07:16:19.178406
properties	company_property_number	自社物件番号	社内管理番号		\N	2	基本情報	\N	\N		2025-07-28 07:16:19.182635	2025-07-28 07:16:19.182636
properties	external_property_id	外部連携ID	外部システムID		\N	3	基本情報	\N	\N		2025-07-28 07:16:19.183268	2025-07-28 07:16:19.183269
properties	property_name	物件名	物件の正式名称		\N	4	基本情報	\N	\N		2025-07-28 07:16:19.183675	2025-07-28 07:16:19.183676
properties	property_name_kana	物件名カナ	カナ表記		\N	5	基本情報	\N	\N		2025-07-28 07:16:19.184066	2025-07-28 07:16:19.184067
properties	property_name_public	物件名公開	物件名を公開するか	boolean	\N	6	基本情報	\N	\N		2025-07-28 07:16:19.18429	2025-07-28 07:16:19.18429
properties	property_type	物件種別			\N	7	基本情報	\N	\N	1:マンション,2:一戸建て,3:土地,4:その他	2025-07-28 07:16:19.184511	2025-07-28 07:16:19.184511
properties	investment_property	投資物件			\N	8	基本情報	\N	\N	0:実需,1:投資	2025-07-28 07:16:19.184712	2025-07-28 07:16:19.184712
properties	sales_status	販売状況			\N	9	基本情報	\N	\N	1:販売中,2:商談中,3:成約済み,4:販売終了	2025-07-28 07:16:19.184931	2025-07-28 07:16:19.184932
properties	publication_status	公開状態			\N	10	基本情報	\N	\N	1:公開,2:非公開,3:限定公開	2025-07-28 07:16:19.185196	2025-07-28 07:16:19.185197
properties	affiliated_group	所属グループ	支店・グループ名		\N	11	基本情報	\N	\N		2025-07-28 07:16:19.185399	2025-07-28 07:16:19.1854
properties	priority_score	優先度スコア	表示優先度		\N	12	基本情報	\N	\N		2025-07-28 07:16:19.185733	2025-07-28 07:16:19.185734
properties	property_url	物件詳細URL	物件詳細ページのURL		\N	13	基本情報	\N	\N		2025-07-28 07:16:19.185938	2025-07-28 07:16:19.185938
properties	sale_price	売買価格	販売価格（円）		\N	14	価格情報	\N	\N		2025-07-28 07:16:19.186111	2025-07-28 07:16:19.186111
properties	price_per_tsubo	坪単価	1坪あたりの価格		\N	15	価格情報	\N	\N		2025-07-28 07:16:19.187266	2025-07-28 07:16:19.187267
properties	price_status	価格状態			\N	16	価格情報	\N	\N	1:確定,2:相談,3:応相談	2025-07-28 07:16:19.187514	2025-07-28 07:16:19.187514
properties	tax_type	税込/税抜	価格の税表示		\N	17	価格情報	\N	\N		2025-07-28 07:16:19.187747	2025-07-28 07:16:19.187748
properties	yield_rate	表面利回り	投資物件の利回り(%)		\N	18	価格情報	\N	\N		2025-07-28 07:16:19.187943	2025-07-28 07:16:19.187943
properties	current_yield	現行利回り	現在の利回り(%)		\N	19	価格情報	\N	\N		2025-07-28 07:16:19.188146	2025-07-28 07:16:19.188147
properties	management_fee	管理費	マンションの管理費		\N	20	価格情報	\N	\N		2025-07-28 07:16:19.188331	2025-07-28 07:16:19.188331
properties	repair_reserve_fund	修繕積立金	マンションの修繕積立金		\N	21	価格情報	\N	\N		2025-07-28 07:16:19.188516	2025-07-28 07:16:19.188517
properties	repair_reserve_fund_base	修繕積立基金	一時金		\N	22	価格情報	\N	\N		2025-07-28 07:16:19.188683	2025-07-28 07:16:19.188683
properties	parking_fee	駐車場使用料	月額駐車場代		\N	23	価格情報	\N	\N		2025-07-28 07:16:19.188876	2025-07-28 07:16:19.188876
properties	housing_insurance	住宅保険料	年間保険料		\N	24	価格情報	\N	\N		2025-07-28 07:16:19.189062	2025-07-28 07:16:19.189063
properties	current_status	現況			\N	25	契約条件	\N	\N	1:空家,2:居住中,3:賃貸中,9:その他	2025-07-28 07:16:19.189274	2025-07-28 07:16:19.189274
properties	delivery_date	引渡予定日	引渡し予定日	date	\N	26	契約条件	\N	\N		2025-07-28 07:16:19.18957	2025-07-28 07:16:19.189575
properties	delivery_timing	引渡時期			\N	27	契約条件	\N	\N	1:即時,2:相談,3:期日指定	2025-07-28 07:16:19.189837	2025-07-28 07:16:19.189838
properties	move_in_consultation	引渡時期相談内容	相談内容の詳細		\N	28	契約条件	\N	\N		2025-07-28 07:16:19.190049	2025-07-28 07:16:19.19005
properties	transaction_type	取引態様			\N	29	契約条件	\N	\N	1:売主,2:代理,3:専任媒介,4:一般媒介,5:専属専任	2025-07-28 07:16:19.190259	2025-07-28 07:16:19.190259
properties	brokerage_fee	仲介手数料	仲介手数料（円）		\N	30	契約条件	\N	\N		2025-07-28 07:16:19.190514	2025-07-28 07:16:19.190515
properties	commission_split_ratio	分配率（客付分）	業者間の手数料分配率(%)		\N	31	契約条件	\N	\N		2025-07-28 07:16:19.191	2025-07-28 07:16:19.191
properties	brokerage_contract_date	媒介契約日	媒介契約締結日	date	\N	32	契約条件	\N	\N		2025-07-28 07:16:19.191239	2025-07-28 07:16:19.191239
properties	listing_start_date	掲載開始日	広告掲載開始日	date	\N	33	契約条件	\N	\N		2025-07-28 07:16:19.191468	2025-07-28 07:16:19.191469
properties	listing_confirmation_date	掲載確認日	最終確認日	date	\N	34	契約条件	\N	\N		2025-07-28 07:16:19.191693	2025-07-28 07:16:19.191694
properties	contractor_company_name	元請会社名	元請会社の正式名称		\N	35	元請会社	\N	\N		2025-07-28 07:16:19.191862	2025-07-28 07:16:19.191863
properties	contractor_contact_person	担当者名	元請会社の担当者		\N	36	元請会社	\N	\N		2025-07-28 07:16:19.192064	2025-07-28 07:16:19.192065
properties	contractor_phone	電話番号	元請会社の電話番号		\N	37	元請会社	\N	\N		2025-07-28 07:16:19.192238	2025-07-28 07:16:19.192239
properties	contractor_email	メールアドレス	元請会社のメール		\N	38	元請会社	\N	\N		2025-07-28 07:16:19.192426	2025-07-28 07:16:19.192427
properties	contractor_address	会社住所	元請会社の所在地		\N	39	元請会社	\N	\N		2025-07-28 07:16:19.192603	2025-07-28 07:16:19.192604
properties	contractor_license_number	宅建免許番号	宅地建物取引業免許番号		\N	40	元請会社	\N	\N		2025-07-28 07:16:19.192789	2025-07-28 07:16:19.19279
properties	property_manager_name	社内担当者	社内の物件担当者		\N	41	管理情報	\N	\N		2025-07-28 07:16:19.192961	2025-07-28 07:16:19.192962
properties	internal_memo	社内メモ	社内用の備考		\N	42	管理情報	\N	\N		2025-07-28 07:16:19.193176	2025-07-28 07:16:19.193177
properties	created_at	作成日時	レコード作成日時		\N	43	システム	\N	\N		2025-07-28 07:16:19.193418	2025-07-28 07:16:19.193418
properties	updated_at	更新日時	レコード更新日時		\N	44	システム	\N	\N		2025-07-28 07:16:19.193987	2025-07-28 07:16:19.193989
land_info	id	ID	プライマリキー		\N	1	システム	\N	\N		2025-07-28 07:16:19.194349	2025-07-28 07:16:19.19435
land_info	property_id	物件ID	物件への外部キー		\N	2	システム	\N	\N		2025-07-28 07:16:19.194641	2025-07-28 07:16:19.194642
land_info	postal_code	郵便番号	郵便番号（ハイフン付き）		\N	3	所在地	\N	\N		2025-07-28 07:16:19.194923	2025-07-28 07:16:19.194924
land_info	address_code	所在地コード	住所コード		\N	4	所在地	\N	\N		2025-07-28 07:16:19.195243	2025-07-28 07:16:19.195245
land_info	prefecture	都道府県	都道府県名		\N	5	所在地	\N	\N		2025-07-28 07:16:19.195553	2025-07-28 07:16:19.195554
land_info	city	市区町村	市区町村名		\N	6	所在地	\N	\N		2025-07-28 07:16:19.195849	2025-07-28 07:16:19.195849
land_info	address	町名番地	町名・番地		\N	7	所在地	\N	\N		2025-07-28 07:16:19.196115	2025-07-28 07:16:19.196116
land_info	address_detail	建物名・部屋番号	建物名・部屋番号（非公開）		\N	8	所在地	\N	\N		2025-07-28 07:16:19.196395	2025-07-28 07:16:19.196396
land_info	latitude	緯度	緯度情報		\N	9	所在地	\N	\N		2025-07-28 07:16:19.196634	2025-07-28 07:16:19.196634
land_info	longitude	経度	経度情報		\N	10	所在地	\N	\N		2025-07-28 07:16:19.196934	2025-07-28 07:16:19.196934
land_info	land_area	土地面積	土地面積（㎡）		\N	11	土地詳細	\N	\N		2025-07-28 07:16:19.19738	2025-07-28 07:16:19.197384
land_info	land_area_measurement	計測方式			\N	12	土地詳細	\N	\N	1:公簿,2:実測,3:私測	2025-07-28 07:16:19.197726	2025-07-28 07:16:19.197727
land_info	land_category	地目	土地の地目		\N	13	土地詳細	\N	\N		2025-07-28 07:16:19.198016	2025-07-28 07:16:19.198016
land_info	use_district	用途地域			\N	14	土地詳細	\N	\N	1:第一種低層住居専用,2:第二種低層住居専用,3:第一種中高層住居専用,4:第二種中高層住居専用,5:第一種住居,6:第二種住居,7:準住居,8:近隣商業,9:商業,10:準工業,11:工業,12:工業専用	2025-07-28 07:16:19.198291	2025-07-28 07:16:19.198292
land_info	city_planning	都市計画	都市計画区域		\N	15	土地詳細	\N	\N		2025-07-28 07:16:19.198658	2025-07-28 07:16:19.198659
land_info	building_coverage_ratio	建ぺい率	建ぺい率（%）		\N	16	土地詳細	\N	\N		2025-07-28 07:16:19.199037	2025-07-28 07:16:19.199038
land_info	floor_area_ratio	容積率	容積率（%）		\N	17	土地詳細	\N	\N		2025-07-28 07:16:19.199341	2025-07-28 07:16:19.199342
land_info	land_rights	土地権利			\N	18	土地詳細	\N	\N	1:所有権,2:借地権,3:定期借地権,4:地上権	2025-07-28 07:16:19.199618	2025-07-28 07:16:19.199619
land_info	land_rent	借地料	借地料（円/月）		\N	19	土地詳細	\N	\N		2025-07-28 07:16:19.199953	2025-07-28 07:16:19.199954
land_info	land_ownership_ratio	土地持分	土地の共有持分		\N	20	土地詳細	\N	\N		2025-07-28 07:16:19.20025	2025-07-28 07:16:19.200251
land_info	private_road_area	私道負担面積	私道負担面積（㎡）		\N	21	土地詳細	\N	\N		2025-07-28 07:16:19.200596	2025-07-28 07:16:19.200599
land_info	private_road_ratio	私道負担割合	私道の共有持分		\N	22	土地詳細	\N	\N		2025-07-28 07:16:19.201106	2025-07-28 07:16:19.201107
land_info	setback	セットバック			\N	23	土地詳細	\N	\N	0:不要,1:要,2:セットバック済	2025-07-28 07:16:19.201484	2025-07-28 07:16:19.201485
land_info	setback_amount	セットバック量	セットバック面積（㎡）		\N	24	土地詳細	\N	\N		2025-07-28 07:16:19.201944	2025-07-28 07:16:19.201946
land_info	land_transaction_notice	国土法届出			\N	25	土地詳細	\N	\N	0:不要,1:要,2:届出済	2025-07-28 07:16:19.202262	2025-07-28 07:16:19.20227
land_info	legal_restrictions	法令上の制限	その他法令制限		\N	26	土地詳細	\N	\N		2025-07-28 07:16:19.202549	2025-07-28 07:16:19.202553
land_info	road_info	接道情報	接道の詳細情報（JSON）	jsonb	\N	27	接道	\N	\N		2025-07-28 07:16:19.202828	2025-07-28 07:16:19.202829
land_info	created_at	作成日時	レコード作成日時		\N	28	システム	\N	\N		2025-07-28 07:16:19.203126	2025-07-28 07:16:19.203127
land_info	updated_at	更新日時	レコード更新日時		\N	29	システム	\N	\N		2025-07-28 07:16:19.203386	2025-07-28 07:16:19.203387
building_info	id	ID	プライマリキー		\N	1	システム	\N	\N		2025-07-28 07:16:19.203663	2025-07-28 07:16:19.203664
building_info	property_id	物件ID	物件への外部キー		\N	2	システム	\N	\N		2025-07-28 07:16:19.203978	2025-07-28 07:16:19.203978
building_info	building_structure	建物構造			\N	3	建物基本	\N	\N	1:木造,2:鉄骨造,3:RC造,4:SRC造,5:軽量鉄骨,6:ALC,9:その他	2025-07-28 07:16:19.204254	2025-07-28 07:16:19.204255
building_info	construction_date	築年月	建築年月	date	\N	4	建物基本	\N	\N		2025-07-28 07:16:19.204588	2025-07-28 07:16:19.204591
building_info	building_floors_above	地上階数	地上階数		\N	5	建物基本	\N	\N		2025-07-28 07:16:19.20489	2025-07-28 07:16:19.204891
building_info	building_floors_below	地下階数	地下階数		\N	6	建物基本	\N	\N		2025-07-28 07:16:19.205251	2025-07-28 07:16:19.205253
building_info	total_units	総戸数	マンションの総戸数		\N	7	建物基本	\N	\N		2025-07-28 07:16:19.205626	2025-07-28 07:16:19.205627
building_info	total_site_area	敷地全体面積	敷地全体の面積（㎡）		\N	8	建物基本	\N	\N		2025-07-28 07:16:19.205887	2025-07-28 07:16:19.205888
building_info	building_area	建築面積	建築面積（㎡）		\N	9	面積	\N	\N		2025-07-28 07:16:19.206133	2025-07-28 07:16:19.206133
building_info	total_floor_area	延床面積	延床面積（㎡）		\N	10	面積	\N	\N		2025-07-28 07:16:19.206389	2025-07-28 07:16:19.206389
building_info	exclusive_area	専有面積	専有面積（㎡）		\N	11	面積	\N	\N		2025-07-28 07:16:19.206631	2025-07-28 07:16:19.206632
building_info	balcony_area	バルコニー面積	バルコニー面積（㎡）		\N	12	面積	\N	\N		2025-07-28 07:16:19.206901	2025-07-28 07:16:19.206902
building_info	area_measurement_type	面積計測方式			\N	13	面積	\N	\N	1:壁芯,2:内法,3:登記簿	2025-07-28 07:16:19.207133	2025-07-28 07:16:19.207133
building_info	room_floor	所在階	部屋の所在階		\N	14	居住情報	\N	\N		2025-07-28 07:16:19.20737	2025-07-28 07:16:19.20737
building_info	direction	向き			\N	15	居住情報	\N	\N	1:北,2:北東,3:東,4:南東,5:南,6:南西,7:西,8:北西	2025-07-28 07:16:19.207611	2025-07-28 07:16:19.207612
building_info	room_count	間取り部屋数	部屋数		\N	16	居住情報	\N	\N		2025-07-28 07:16:19.207844	2025-07-28 07:16:19.207844
building_info	room_type	間取りタイプ			\N	17	居住情報	\N	\N	1:R,2:K,3:DK,4:LDK,5:SLDK,6:その他	2025-07-28 07:16:19.208092	2025-07-28 07:16:19.208093
building_info	floor_plans	間取り詳細	間取りの詳細情報（JSON）	jsonb	\N	18	居住情報	\N	\N		2025-07-28 07:16:19.208356	2025-07-28 07:16:19.208357
building_info	floor_plan_notes	間取り備考	間取りの補足説明		\N	19	居住情報	\N	\N		2025-07-28 07:16:19.208612	2025-07-28 07:16:19.208612
building_info	management_type	管理形態			\N	20	管理情報	\N	\N	1:自主管理,2:管理会社委託,3:一部委託,9:その他	2025-07-28 07:16:19.208858	2025-07-28 07:16:19.208859
building_info	management_company	管理会社名	管理会社の名称		\N	21	管理情報	\N	\N		2025-07-28 07:16:19.209144	2025-07-28 07:16:19.209145
building_info	management_association	管理組合			\N	22	管理情報	\N	\N	0:無,1:有	2025-07-28 07:16:19.209395	2025-07-28 07:16:19.209396
building_info	building_manager	管理人			\N	23	管理情報	\N	\N	1:常駐,2:日勤,3:巡回,4:自主管理,9:無	2025-07-28 07:16:19.209643	2025-07-28 07:16:19.209647
building_info	parking_availability	駐車場			\N	24	駐車場	\N	\N	1:無,2:有(無料),3:有(有料),4:近隣(無料),5:近隣(有料)	2025-07-28 07:16:19.209864	2025-07-28 07:16:19.209865
building_info	parking_type	駐車場種別			\N	25	駐車場	\N	\N	1:平置き,2:機械式,3:立体,9:その他	2025-07-28 07:16:19.210075	2025-07-28 07:16:19.210076
building_info	parking_capacity	駐車可能台数	駐車可能台数		\N	26	駐車場	\N	\N		2025-07-28 07:16:19.210309	2025-07-28 07:16:19.210309
building_info	parking_distance	駐車場距離	駐車場までの距離（m）		\N	27	駐車場	\N	\N		2025-07-28 07:16:19.210563	2025-07-28 07:16:19.210564
building_info	parking_notes	駐車場備考	駐車場の補足情報		\N	28	駐車場	\N	\N		2025-07-28 07:16:19.210806	2025-07-28 07:16:19.210806
building_info	created_at	作成日時	レコード作成日時		\N	29	システム	\N	\N		2025-07-28 07:16:19.211073	2025-07-28 07:16:19.211074
building_info	updated_at	更新日時	レコード更新日時		\N	30	システム	\N	\N		2025-07-28 07:16:19.211329	2025-07-28 07:16:19.21133
amenities	id	ID	プライマリキー		\N	1	システム	\N	\N		2025-07-28 07:16:19.211581	2025-07-28 07:16:19.211581
amenities	property_id	物件ID	物件への外部キー		\N	2	システム	\N	\N		2025-07-28 07:16:19.211884	2025-07-28 07:16:19.211885
amenities	facilities	設備	設備一覧（JSON配列）	jsonb	\N	3	設備	\N	\N		2025-07-28 07:16:19.212128	2025-07-28 07:16:19.212129
amenities	property_features	物件の特徴	セールスポイント		\N	4	設備	\N	\N		2025-07-28 07:16:19.212433	2025-07-28 07:16:19.212434
amenities	notes	その他特記事項	補足説明		\N	5	設備	\N	\N		2025-07-28 07:16:19.212684	2025-07-28 07:16:19.212685
amenities	transportation	交通情報	最寄り駅情報（JSON）	jsonb	\N	6	交通	\N	\N		2025-07-28 07:16:19.212898	2025-07-28 07:16:19.212898
amenities	other_transportation	その他交通	その他の交通手段		\N	7	交通	\N	\N		2025-07-28 07:16:19.213125	2025-07-28 07:16:19.213127
amenities	elementary_school_name	小学校名	学区の小学校名		\N	8	周辺施設	\N	\N		2025-07-28 07:16:19.213449	2025-07-28 07:16:19.21345
amenities	elementary_school_distance	小学校距離	小学校までの距離（m）		\N	9	周辺施設	\N	\N		2025-07-28 07:16:19.213684	2025-07-28 07:16:19.213685
amenities	junior_high_school_name	中学校名	学区の中学校名		\N	10	周辺施設	\N	\N		2025-07-28 07:16:19.213904	2025-07-28 07:16:19.213904
amenities	junior_high_school_distance	中学校距離	中学校までの距離（m）		\N	11	周辺施設	\N	\N		2025-07-28 07:16:19.214154	2025-07-28 07:16:19.214155
amenities	convenience_store_distance	コンビニ距離	最寄りコンビニまでの距離（m）		\N	12	周辺施設	\N	\N		2025-07-28 07:16:19.214463	2025-07-28 07:16:19.214465
amenities	supermarket_distance	スーパー距離	最寄りスーパーまでの距離（m）		\N	13	周辺施設	\N	\N		2025-07-28 07:16:19.21487	2025-07-28 07:16:19.214872
amenities	general_hospital_distance	総合病院距離	総合病院までの距離（m）		\N	14	周辺施設	\N	\N		2025-07-28 07:16:19.215196	2025-07-28 07:16:19.215197
amenities	shopping_street_distance	商店街距離	商店街までの距離（m）		\N	15	周辺施設	\N	\N		2025-07-28 07:16:19.215438	2025-07-28 07:16:19.215438
amenities	drugstore_distance	ドラッグストア距離	ドラッグストアまでの距離（m）		\N	16	周辺施設	\N	\N		2025-07-28 07:16:19.215652	2025-07-28 07:16:19.215652
amenities	park_distance	公園距離	最寄り公園までの距離（m）		\N	17	周辺施設	\N	\N		2025-07-28 07:16:19.215882	2025-07-28 07:16:19.215883
amenities	bank_distance	銀行距離	最寄り銀行までの距離（m）		\N	18	周辺施設	\N	\N		2025-07-28 07:16:19.216082	2025-07-28 07:16:19.216083
amenities	other_facility_name	その他施設名	その他の重要施設		\N	19	周辺施設	\N	\N		2025-07-28 07:16:19.216289	2025-07-28 07:16:19.21629
amenities	other_facility_distance	その他施設距離	その他施設までの距離（m）		\N	20	周辺施設	\N	\N		2025-07-28 07:16:19.216524	2025-07-28 07:16:19.216524
amenities	renovations	リフォーム履歴	リフォーム履歴（JSON）	jsonb	\N	21	リフォーム	\N	\N		2025-07-28 07:16:19.216728	2025-07-28 07:16:19.216729
amenities	energy_consumption_min	エネルギー消費性能(最小)	省エネ性能の下限値		\N	22	エコ性能	\N	\N		2025-07-28 07:16:19.216951	2025-07-28 07:16:19.216952
amenities	energy_consumption_max	エネルギー消費性能(最大)	省エネ性能の上限値		\N	23	エコ性能	\N	\N		2025-07-28 07:16:19.217202	2025-07-28 07:16:19.217202
amenities	insulation_performance_min	断熱性能(最小)	断熱性能の下限値		\N	24	エコ性能	\N	\N		2025-07-28 07:16:19.217451	2025-07-28 07:16:19.217452
amenities	insulation_performance_max	断熱性能(最大)	断熱性能の上限値		\N	25	エコ性能	\N	\N		2025-07-28 07:16:19.217695	2025-07-28 07:16:19.217696
amenities	utility_cost_min	目安光熱費(最小)	月額光熱費の下限（円）		\N	26	エコ性能	\N	\N		2025-07-28 07:16:19.21801	2025-07-28 07:16:19.218011
amenities	utility_cost_max	目安光熱費(最大)	月額光熱費の上限（円）		\N	27	エコ性能	\N	\N		2025-07-28 07:16:19.218289	2025-07-28 07:16:19.21829
amenities	created_at	作成日時	レコード作成日時		\N	28	システム	\N	\N		2025-07-28 07:16:19.218543	2025-07-28 07:16:19.218544
amenities	updated_at	更新日時	レコード更新日時		\N	29	システム	\N	\N		2025-07-28 07:16:19.218785	2025-07-28 07:16:19.218786
property_images	id	ID	プライマリキー		\N	1	システム	\N	\N		2025-07-28 07:16:19.219084	2025-07-28 07:16:19.219085
property_images	property_id	物件ID	物件への外部キー		\N	2	システム	\N	\N		2025-07-28 07:16:19.219399	2025-07-28 07:16:19.2194
property_images	image_type	画像種別			\N	3	画像情報	\N	\N	01:外観,02:間取図,03:居室,04:キッチン,05:風呂,06:トイレ,07:洗面,08:設備,09:玄関,10:バルコニー,11:眺望,12:共用部,13:周辺環境,14:その他	2025-07-28 07:16:19.219691	2025-07-28 07:16:19.219692
property_images	file_path	ファイルパス	ローカルファイルパス		\N	4	画像情報	\N	\N		2025-07-28 07:16:19.220025	2025-07-28 07:16:19.220027
property_images	file_url	公開URL	画像の公開URL		\N	5	画像情報	\N	\N		2025-07-28 07:16:19.220332	2025-07-28 07:16:19.220333
property_images	display_order	表示順	表示順序		\N	6	画像情報	\N	\N		2025-07-28 07:16:19.220606	2025-07-28 07:16:19.220607
property_images	caption	キャプション	画像の説明文		\N	7	画像情報	\N	\N		2025-07-28 07:16:19.220947	2025-07-28 07:16:19.220948
property_images	is_public	公開フラグ	画像を公開するか	boolean	\N	8	画像情報	\N	\N		2025-07-28 07:16:19.22119	2025-07-28 07:16:19.221192
property_images	uploaded_at	アップロード日時	画像のアップロード日時		\N	9	画像情報	\N	\N		2025-07-28 07:16:19.221489	2025-07-28 07:16:19.22149
property_images	created_at	作成日時	レコード作成日時		\N	10	システム	\N	\N		2025-07-28 07:16:19.221891	2025-07-28 07:16:19.221894
property_images	updated_at	更新日時	レコード更新日時		\N	11	システム	\N	\N		2025-07-28 07:16:19.222275	2025-07-28 07:16:19.222276
\.


ALTER TABLE public.column_labels ENABLE TRIGGER ALL;

--
-- Data for Name: current_status; Type: TABLE DATA; Schema: public; Owner: rea_user
--

ALTER TABLE public.current_status DISABLE TRIGGER ALL;

COPY public.current_status (id, label, group_name, homes_id, created_at, updated_at) FROM stdin;
vacant	空室	\N	\N	2025-07-23 11:21:57.291798	2025-07-23 11:21:57.291798
vacant_scheduled	空予定	\N	\N	2025-07-23 11:21:57.291798	2025-07-23 11:21:57.291798
rented	賃貸中	\N	\N	2025-07-23 11:21:57.291798	2025-07-23 11:21:57.291798
occupied	居住中	\N	\N	2025-07-23 11:21:57.291798	2025-07-23 11:21:57.291798
office_use	事務所使用	\N	\N	2025-07-23 11:21:57.291798	2025-07-23 11:21:57.291798
under_construction	建築中	\N	\N	2025-07-23 11:21:57.291798	2025-07-23 11:21:57.291798
completed	完成済	\N	\N	2025-07-23 11:21:57.291798	2025-07-23 11:21:57.291798
undecided	未定	\N	\N	2025-07-23 11:21:57.291798	2025-07-23 11:21:57.291798
other	その他	\N	\N	2025-07-23 11:21:57.291798	2025-07-23 11:21:57.291798
\.


ALTER TABLE public.current_status ENABLE TRIGGER ALL;

--
-- Data for Name: equipment_master; Type: TABLE DATA; Schema: public; Owner: rea_user
--

ALTER TABLE public.equipment_master DISABLE TRIGGER ALL;

COPY public.equipment_master (id, item_name, tab_group, display_name, data_type, dependent_items, remarks, homes_id, created_at, updated_at) FROM stdin;
elevator	エレベーター	建物設備	エレベーター	\N	\N	\N	\N	2025-07-23 11:21:57.294677	2025-07-23 11:21:57.294677
auto_lock	オートロック	建物設備	オートロック	\N	\N	\N	\N	2025-07-23 11:21:57.294677	2025-07-23 11:21:57.294677
delivery_box	宅配ボックス	建物設備	宅配ボックス	\N	\N	\N	\N	2025-07-23 11:21:57.294677	2025-07-23 11:21:57.294677
trash_24h	24時間ゴミ出し可	建物設備	24時間ゴミ出し可	\N	\N	\N	\N	2025-07-23 11:21:57.294677	2025-07-23 11:21:57.294677
bike_parking	駐輪場	建物設備	駐輪場	\N	\N	\N	\N	2025-07-23 11:21:57.294677	2025-07-23 11:21:57.294677
motorcycle_parking	バイク置場	建物設備	バイク置場	\N	\N	\N	\N	2025-07-23 11:21:57.294677	2025-07-23 11:21:57.294677
system_kitchen	システムキッチン	室内設備	システムキッチン	\N	\N	\N	\N	2025-07-23 11:21:57.294677	2025-07-23 11:21:57.294677
gas_stove	ガスコンロ	室内設備	ガスコンロ	\N	\N	\N	\N	2025-07-23 11:21:57.294677	2025-07-23 11:21:57.294677
ih_stove	IHコンロ	室内設備	IHコンロ	\N	\N	\N	\N	2025-07-23 11:21:57.294677	2025-07-23 11:21:57.294677
bathroom_dryer	浴室乾燥機	室内設備	浴室乾燥機	\N	\N	\N	\N	2025-07-23 11:21:57.294677	2025-07-23 11:21:57.294677
reheating_bath	追焚機能	室内設備	追焚機能	\N	\N	\N	\N	2025-07-23 11:21:57.294677	2025-07-23 11:21:57.294677
washlet	温水洗浄便座	室内設備	温水洗浄便座	\N	\N	\N	\N	2025-07-23 11:21:57.294677	2025-07-23 11:21:57.294677
air_conditioner	エアコン	室内設備	エアコン	\N	\N	\N	\N	2025-07-23 11:21:57.294677	2025-07-23 11:21:57.294677
floor_heating	床暖房	室内設備	床暖房	\N	\N	\N	\N	2025-07-23 11:21:57.294677	2025-07-23 11:21:57.294677
\.


ALTER TABLE public.equipment_master ENABLE TRIGGER ALL;

--
-- Data for Name: floor_plan_room_types; Type: TABLE DATA; Schema: public; Owner: rea_user
--

ALTER TABLE public.floor_plan_room_types DISABLE TRIGGER ALL;

COPY public.floor_plan_room_types (id, label, group_name, homes_id, created_at, updated_at) FROM stdin;
r	R	\N	\N	2025-07-23 11:21:57.293751	2025-07-23 11:21:57.293751
k	K	\N	\N	2025-07-23 11:21:57.293751	2025-07-23 11:21:57.293751
dk	DK	\N	\N	2025-07-23 11:21:57.293751	2025-07-23 11:21:57.293751
ldk	LDK	\N	\N	2025-07-23 11:21:57.293751	2025-07-23 11:21:57.293751
sldk	SLDK	\N	\N	2025-07-23 11:21:57.293751	2025-07-23 11:21:57.293751
l	L	\N	\N	2025-07-23 11:21:57.293751	2025-07-23 11:21:57.293751
d	D	\N	\N	2025-07-23 11:21:57.293751	2025-07-23 11:21:57.293751
s	S	\N	\N	2025-07-23 11:21:57.293751	2025-07-23 11:21:57.293751
other	その他	\N	\N	2025-07-23 11:21:57.293751	2025-07-23 11:21:57.293751
\.


ALTER TABLE public.floor_plan_room_types ENABLE TRIGGER ALL;

--
-- Data for Name: image_types; Type: TABLE DATA; Schema: public; Owner: rea_user
--

ALTER TABLE public.image_types DISABLE TRIGGER ALL;

COPY public.image_types (id, label, group_name, homes_id, created_at, updated_at) FROM stdin;
exterior	外観	建物外部	\N	2025-07-23 11:21:57.294186	2025-07-23 11:21:57.294186
floorplan	間取図	図面	\N	2025-07-23 11:21:57.294186	2025-07-23 11:21:57.294186
room	居室	室内	\N	2025-07-23 11:21:57.294186	2025-07-23 11:21:57.294186
kitchen	キッチン	室内	\N	2025-07-23 11:21:57.294186	2025-07-23 11:21:57.294186
bath	風呂	室内	\N	2025-07-23 11:21:57.294186	2025-07-23 11:21:57.294186
toilet	トイレ	室内	\N	2025-07-23 11:21:57.294186	2025-07-23 11:21:57.294186
washroom	洗面	室内	\N	2025-07-23 11:21:57.294186	2025-07-23 11:21:57.294186
equipment	設備	室内	\N	2025-07-23 11:21:57.294186	2025-07-23 11:21:57.294186
entrance	玄関	室内	\N	2025-07-23 11:21:57.294186	2025-07-23 11:21:57.294186
balcony	バルコニー	建物外部	\N	2025-07-23 11:21:57.294186	2025-07-23 11:21:57.294186
view	眺望	その他	\N	2025-07-23 11:21:57.294186	2025-07-23 11:21:57.294186
common	共用部	建物共用	\N	2025-07-23 11:21:57.294186	2025-07-23 11:21:57.294186
surrounding	周辺環境	周辺	\N	2025-07-23 11:21:57.294186	2025-07-23 11:21:57.294186
parking	駐車場	建物外部	\N	2025-07-23 11:21:57.294186	2025-07-23 11:21:57.294186
garden	庭	建物外部	\N	2025-07-23 11:21:57.294186	2025-07-23 11:21:57.294186
living	リビング	室内	\N	2025-07-23 11:21:57.294186	2025-07-23 11:21:57.294186
bedroom	寝室	室内	\N	2025-07-23 11:21:57.294186	2025-07-23 11:21:57.294186
closet	収納	室内	\N	2025-07-23 11:21:57.294186	2025-07-23 11:21:57.294186
hallway	廊下	室内	\N	2025-07-23 11:21:57.294186	2025-07-23 11:21:57.294186
aerial	航空写真	その他	\N	2025-07-23 11:21:57.294186	2025-07-23 11:21:57.294186
map	地図	その他	\N	2025-07-23 11:21:57.294186	2025-07-23 11:21:57.294186
other	その他	その他	\N	2025-07-23 11:21:57.294186	2025-07-23 11:21:57.294186
\.


ALTER TABLE public.image_types ENABLE TRIGGER ALL;

--
-- Data for Name: land_info; Type: TABLE DATA; Schema: public; Owner: rea_user
--

ALTER TABLE public.land_info DISABLE TRIGGER ALL;

COPY public.land_info (id, property_id, postal_code, address_code, prefecture, city, address, address_detail, latitude, longitude, land_area, land_area_measurement, land_category, use_district, city_planning, building_coverage_ratio, floor_area_ratio, land_rights, land_rent, land_ownership_ratio, private_road_area, private_road_ratio, setback, setback_amount, land_transaction_notice, legal_restrictions, road_info, created_at, updated_at) FROM stdin;
\.


ALTER TABLE public.land_info ENABLE TRIGGER ALL;

--
-- Data for Name: land_rights; Type: TABLE DATA; Schema: public; Owner: rea_user
--

ALTER TABLE public.land_rights DISABLE TRIGGER ALL;

COPY public.land_rights (id, label, group_name, homes_id, created_at, updated_at) FROM stdin;
ownership	所有権	所有権	\N	2025-07-23 11:21:57.293266	2025-07-23 11:21:57.293266
leasehold	借地権	借地権	\N	2025-07-23 11:21:57.293266	2025-07-23 11:21:57.293266
fixed_leasehold	定期借地権	借地権	\N	2025-07-23 11:21:57.293266	2025-07-23 11:21:57.293266
general_fixed	一般定期借地権	借地権	\N	2025-07-23 11:21:57.293266	2025-07-23 11:21:57.293266
business_fixed	事業用定期借地権	借地権	\N	2025-07-23 11:21:57.293266	2025-07-23 11:21:57.293266
building_transfer	建物譲渡特約付借地権	借地権	\N	2025-07-23 11:21:57.293266	2025-07-23 11:21:57.293266
old_leasehold	旧法借地権	借地権	\N	2025-07-23 11:21:57.293266	2025-07-23 11:21:57.293266
surface	地上権	その他	\N	2025-07-23 11:21:57.293266	2025-07-23 11:21:57.293266
rental	賃借権	その他	\N	2025-07-23 11:21:57.293266	2025-07-23 11:21:57.293266
usage	使用貸借権	その他	\N	2025-07-23 11:21:57.293266	2025-07-23 11:21:57.293266
sectional	区分地上権	その他	\N	2025-07-23 11:21:57.293266	2025-07-23 11:21:57.293266
other	その他	その他	\N	2025-07-23 11:21:57.293266	2025-07-23 11:21:57.293266
\.


ALTER TABLE public.land_rights ENABLE TRIGGER ALL;

--
-- Data for Name: property_equipment; Type: TABLE DATA; Schema: public; Owner: rea_user
--

ALTER TABLE public.property_equipment DISABLE TRIGGER ALL;

COPY public.property_equipment (id, property_id, equipment_id, value, created_at, updated_at) FROM stdin;
\.


ALTER TABLE public.property_equipment ENABLE TRIGGER ALL;

--
-- Data for Name: property_images; Type: TABLE DATA; Schema: public; Owner: rea_user
--

ALTER TABLE public.property_images DISABLE TRIGGER ALL;

COPY public.property_images (id, property_id, image_type, file_path, file_url, display_order, caption, is_public, uploaded_at, created_at, updated_at) FROM stdin;
\.


ALTER TABLE public.property_images ENABLE TRIGGER ALL;

--
-- Data for Name: property_types; Type: TABLE DATA; Schema: public; Owner: rea_user
--

ALTER TABLE public.property_types DISABLE TRIGGER ALL;

COPY public.property_types (id, label, group_name, homes_id, created_at, updated_at) FROM stdin;
apartment	アパート	居住用	\N	2025-07-23 11:21:57.292411	2025-07-23 11:21:57.292411
mansion	マンション	居住用	\N	2025-07-23 11:21:57.292411	2025-07-23 11:21:57.292411
detached	一戸建て	居住用	\N	2025-07-23 11:21:57.292411	2025-07-23 11:21:57.292411
terrace	テラスハウス	居住用	\N	2025-07-23 11:21:57.292411	2025-07-23 11:21:57.292411
townhouse	タウンハウス	居住用	\N	2025-07-23 11:21:57.292411	2025-07-23 11:21:57.292411
store	店舗	事業用	\N	2025-07-23 11:21:57.292411	2025-07-23 11:21:57.292411
office	事務所	事業用	\N	2025-07-23 11:21:57.292411	2025-07-23 11:21:57.292411
warehouse	倉庫	事業用	\N	2025-07-23 11:21:57.292411	2025-07-23 11:21:57.292411
factory	工場	事業用	\N	2025-07-23 11:21:57.292411	2025-07-23 11:21:57.292411
parking	駐車場	その他	\N	2025-07-23 11:21:57.292411	2025-07-23 11:21:57.292411
land	土地	その他	\N	2025-07-23 11:21:57.292411	2025-07-23 11:21:57.292411
building	一棟売りビル	投資用	\N	2025-07-23 11:21:57.292411	2025-07-23 11:21:57.292411
apartment_building	一棟売りアパート	投資用	\N	2025-07-23 11:21:57.292411	2025-07-23 11:21:57.292411
mansion_building	一棟売りマンション	投資用	\N	2025-07-23 11:21:57.292411	2025-07-23 11:21:57.292411
\.


ALTER TABLE public.property_types ENABLE TRIGGER ALL;

--
-- Data for Name: zoning_districts; Type: TABLE DATA; Schema: public; Owner: rea_user
--

ALTER TABLE public.zoning_districts DISABLE TRIGGER ALL;

COPY public.zoning_districts (id, label, group_name, homes_id, created_at, updated_at) FROM stdin;
1st_low_res	第一種低層住居専用地域	住居系	\N	2025-07-23 11:21:57.292869	2025-07-23 11:21:57.292869
2nd_low_res	第二種低層住居専用地域	住居系	\N	2025-07-23 11:21:57.292869	2025-07-23 11:21:57.292869
1st_mid_res	第一種中高層住居専用地域	住居系	\N	2025-07-23 11:21:57.292869	2025-07-23 11:21:57.292869
2nd_mid_res	第二種中高層住居専用地域	住居系	\N	2025-07-23 11:21:57.292869	2025-07-23 11:21:57.292869
1st_res	第一種住居地域	住居系	\N	2025-07-23 11:21:57.292869	2025-07-23 11:21:57.292869
2nd_res	第二種住居地域	住居系	\N	2025-07-23 11:21:57.292869	2025-07-23 11:21:57.292869
quasi_res	準住居地域	住居系	\N	2025-07-23 11:21:57.292869	2025-07-23 11:21:57.292869
neighbor_com	近隣商業地域	商業系	\N	2025-07-23 11:21:57.292869	2025-07-23 11:21:57.292869
commercial	商業地域	商業系	\N	2025-07-23 11:21:57.292869	2025-07-23 11:21:57.292869
quasi_ind	準工業地域	工業系	\N	2025-07-23 11:21:57.292869	2025-07-23 11:21:57.292869
industrial	工業地域	工業系	\N	2025-07-23 11:21:57.292869	2025-07-23 11:21:57.292869
excl_ind	工業専用地域	工業系	\N	2025-07-23 11:21:57.292869	2025-07-23 11:21:57.292869
undesignated	指定なし	その他	\N	2025-07-23 11:21:57.292869	2025-07-23 11:21:57.292869
urbanization_control	市街化調整区域	その他	\N	2025-07-23 11:21:57.292869	2025-07-23 11:21:57.292869
\.


ALTER TABLE public.zoning_districts ENABLE TRIGGER ALL;

--
-- Name: amenities_id_seq; Type: SEQUENCE SET; Schema: public; Owner: rea_user
--

SELECT pg_catalog.setval('public.amenities_id_seq', 1, false);


--
-- Name: building_info_id_seq; Type: SEQUENCE SET; Schema: public; Owner: rea_user
--

SELECT pg_catalog.setval('public.building_info_id_seq', 1, false);


--
-- Name: land_info_id_seq; Type: SEQUENCE SET; Schema: public; Owner: rea_user
--

SELECT pg_catalog.setval('public.land_info_id_seq', 1, false);


--
-- Name: properties_id_seq; Type: SEQUENCE SET; Schema: public; Owner: rea_user
--

SELECT pg_catalog.setval('public.properties_id_seq', 1, false);


--
-- Name: property_equipment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: rea_user
--

SELECT pg_catalog.setval('public.property_equipment_id_seq', 1, false);


--
-- Name: property_images_id_seq; Type: SEQUENCE SET; Schema: public; Owner: rea_user
--

SELECT pg_catalog.setval('public.property_images_id_seq', 1, false);


--
-- PostgreSQL database dump complete
--

