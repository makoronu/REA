"""
マイソク生成のテスト
"""

import pytest
import sys
from pathlib import Path

# rea-flyerをパスに追加
rea_flyer_path = Path(__file__).parent.parent
sys.path.insert(0, str(rea_flyer_path))

# sharedもパスに追加
shared_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(shared_path))

from generators.maisoku import MaisokuGenerator


class TestMaisokuGenerator:
    """マイソク生成のテストケース"""

    @pytest.fixture
    def generator(self):
        """ジェネレータのフィクスチャ"""
        return MaisokuGenerator()

    @pytest.fixture
    def sample_property_data(self):
        """サンプル物件データ"""
        return {
            'id': 1,
            'property_name': 'テスト物件',
            'property_type': 'detached',
            'sale_price': 35000000,
            'address': '北海道札幌市中央区大通1-1-1',
            'nearest_station': '大通駅 徒歩5分',
            'building_info': {
                'total_floor_area': 100.5,
                'floor_plan': '4LDK',
                'structure': 'wood',
                'floors_above': 2,
                'construction_date': '2010-03-01',
            },
            'land_info': {
                'land_area': 150.0,
                'use_district': 1,
                'building_coverage_ratio': 60,
                'floor_area_ratio': 200,
            },
            'images': [
                {'image_url': 'https://example.com/image1.jpg', 'display_order': 1},
                {'image_url': 'https://example.com/image2.jpg', 'display_order': 2},
            ]
        }

    def test_get_template_type(self, generator):
        """テンプレートタイプ取得テスト"""
        assert generator.get_template_type() == 'maisoku'

    def test_select_template(self, generator):
        """テンプレート自動選択テスト"""
        assert generator.select_template('land') == 'land'
        assert generator.select_template('detached') == 'detached'
        assert generator.select_template('house') == 'detached'
        assert generator.select_template('apartment') == 'apartment'
        assert generator.select_template('mansion') == 'apartment'
        assert generator.select_template('investment') == 'investment'
        assert generator.select_template('unknown') == 'detached'  # デフォルト

    def test_extract_property_data(self, generator, sample_property_data):
        """物件データ抽出テスト"""
        flat = generator.extract_property_data(sample_property_data)

        assert flat['property_name'] == 'テスト物件'
        assert flat['sale_price'] == 35000000
        assert flat['total_floor_area'] == 100.5
        assert flat['land_area'] == 150.0

    def test_get_images(self, generator, sample_property_data):
        """画像取得テスト"""
        images = generator.get_images(sample_property_data, max_images=2)

        assert len(images) == 2
        assert images[0] == 'https://example.com/image1.jpg'
        assert images[1] == 'https://example.com/image2.jpg'

    def test_generate_basic(self, generator, sample_property_data):
        """基本生成テスト"""
        svg = generator.generate(sample_property_data)

        assert '<?xml version="1.0" encoding="UTF-8"?>' in svg
        assert '<svg' in svg
        assert '</svg>' in svg


class TestMaisokuTemplateConfig:
    """テンプレート設定テスト"""

    @pytest.fixture
    def generator(self):
        return MaisokuGenerator()

    def test_load_templates(self, generator):
        """テンプレート読み込みテスト"""
        templates = generator.templates

        assert 'maisoku' in templates
        assert 'chirashi' in templates
        assert 'land' in templates['maisoku']
        assert 'detached' in templates['maisoku']

    def test_load_field_mappings(self, generator):
        """フィールドマッピング読み込みテスト"""
        mappings = generator.field_mappings

        assert 'fields' in mappings
        assert 'price' in mappings['fields']
        assert 'land_area' in mappings['fields']

    def test_load_output_settings(self, generator):
        """出力設定読み込みテスト"""
        settings = generator.output_settings

        assert 'output' in settings
        assert 'paper_sizes' in settings
        assert 'fonts' in settings


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
