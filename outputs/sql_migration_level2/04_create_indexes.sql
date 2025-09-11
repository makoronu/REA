-- REA Database Split Level 2: Performance Indexes
-- Generated: 2025-07-21 16:02:13

BEGIN;

-- 🏗️ properties_building インデックス
CREATE INDEX IF NOT EXISTS idx_properties_building_property_id ON properties_building(property_id);
CREATE INDEX IF NOT EXISTS idx_properties_building_created_at ON properties_building(created_at);

-- 📍 properties_location インデックス
CREATE INDEX IF NOT EXISTS idx_properties_location_property_id ON properties_location(property_id);
CREATE INDEX IF NOT EXISTS idx_properties_location_created_at ON properties_location(created_at);
CREATE INDEX IF NOT EXISTS idx_properties_location_postal_code ON properties_location(postal_code);

-- 🚃 properties_transportation インデックス
CREATE INDEX IF NOT EXISTS idx_properties_transportation_property_id ON properties_transportation(property_id);
CREATE INDEX IF NOT EXISTS idx_properties_transportation_created_at ON properties_transportation(created_at);

-- 📝 properties_other インデックス
CREATE INDEX IF NOT EXISTS idx_properties_other_property_id ON properties_other(property_id);
CREATE INDEX IF NOT EXISTS idx_properties_other_created_at ON properties_other(created_at);

-- 🛣️ properties_roads インデックス
CREATE INDEX IF NOT EXISTS idx_properties_roads_property_id ON properties_roads(property_id);
CREATE INDEX IF NOT EXISTS idx_properties_roads_created_at ON properties_roads(created_at);

-- 🏠 properties_floor_plans インデックス
CREATE INDEX IF NOT EXISTS idx_properties_floor_plans_property_id ON properties_floor_plans(property_id);
CREATE INDEX IF NOT EXISTS idx_properties_floor_plans_created_at ON properties_floor_plans(created_at);

-- 💰 properties_pricing インデックス
CREATE INDEX IF NOT EXISTS idx_properties_pricing_property_id ON properties_pricing(property_id);
CREATE INDEX IF NOT EXISTS idx_properties_pricing_created_at ON properties_pricing(created_at);
CREATE INDEX IF NOT EXISTS idx_properties_pricing_price ON properties_pricing(price);

-- 📋 properties_contract インデックス
CREATE INDEX IF NOT EXISTS idx_properties_contract_property_id ON properties_contract(property_id);
CREATE INDEX IF NOT EXISTS idx_properties_contract_created_at ON properties_contract(created_at);

-- 🏫 properties_facilities インデックス
CREATE INDEX IF NOT EXISTS idx_properties_facilities_property_id ON properties_facilities(property_id);
CREATE INDEX IF NOT EXISTS idx_properties_facilities_created_at ON properties_facilities(created_at);

-- 📸 properties_images インデックス
CREATE INDEX IF NOT EXISTS idx_properties_images_property_id ON properties_images(property_id);
CREATE INDEX IF NOT EXISTS idx_properties_images_created_at ON properties_images(created_at);
CREATE INDEX IF NOT EXISTS idx_properties_images_image_type_1 ON properties_images(image_type_1);

COMMIT;
