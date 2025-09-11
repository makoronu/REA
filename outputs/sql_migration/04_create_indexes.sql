-- REA Database Split: Performance Indexes
-- Generated: 2025-07-21 15:30:18

BEGIN;

-- 📍 properties_location インデックス
CREATE INDEX IF NOT EXISTS idx_properties_location_property_id ON properties_location(property_id);
CREATE INDEX IF NOT EXISTS idx_properties_location_created_at ON properties_location(created_at);
CREATE INDEX IF NOT EXISTS idx_properties_location_postal_code ON properties_location(postal_code);

-- 📝 properties_other インデックス
CREATE INDEX IF NOT EXISTS idx_properties_other_property_id ON properties_other(property_id);
CREATE INDEX IF NOT EXISTS idx_properties_other_created_at ON properties_other(created_at);

-- 🏗️ properties_building インデックス
CREATE INDEX IF NOT EXISTS idx_properties_building_property_id ON properties_building(property_id);
CREATE INDEX IF NOT EXISTS idx_properties_building_created_at ON properties_building(created_at);

-- 💰 properties_pricing インデックス
CREATE INDEX IF NOT EXISTS idx_properties_pricing_property_id ON properties_pricing(property_id);
CREATE INDEX IF NOT EXISTS idx_properties_pricing_created_at ON properties_pricing(created_at);
CREATE INDEX IF NOT EXISTS idx_properties_pricing_rent_price ON properties_pricing(rent_price);

-- 🏫 properties_facilities インデックス
CREATE INDEX IF NOT EXISTS idx_properties_facilities_property_id ON properties_facilities(property_id);
CREATE INDEX IF NOT EXISTS idx_properties_facilities_created_at ON properties_facilities(created_at);

-- 📋 properties_contract インデックス
CREATE INDEX IF NOT EXISTS idx_properties_contract_property_id ON properties_contract(property_id);
CREATE INDEX IF NOT EXISTS idx_properties_contract_created_at ON properties_contract(created_at);

-- 📸 properties_images インデックス
CREATE INDEX IF NOT EXISTS idx_properties_images_property_id ON properties_images(property_id);
CREATE INDEX IF NOT EXISTS idx_properties_images_created_at ON properties_images(created_at);

-- 🔧 properties_renovation インデックス
CREATE INDEX IF NOT EXISTS idx_properties_renovation_property_id ON properties_renovation(property_id);
CREATE INDEX IF NOT EXISTS idx_properties_renovation_created_at ON properties_renovation(created_at);

-- ⚡ properties_energy インデックス
CREATE INDEX IF NOT EXISTS idx_properties_energy_property_id ON properties_energy(property_id);
CREATE INDEX IF NOT EXISTS idx_properties_energy_created_at ON properties_energy(created_at);

COMMIT;
