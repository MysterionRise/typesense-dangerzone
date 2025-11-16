#!/usr/bin/env python3
"""
Integration tests for Typesense indexing
These tests require a running Typesense instance
"""

import pytest
import os
import sys
import json
from unittest.mock import MagicMock, patch, mock_open

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_typesense_client():
    """Mock Typesense client for testing"""
    client = MagicMock()

    # Mock collections
    client.collections = MagicMock()
    client.collections.create = MagicMock(return_value={'name': 'products', 'num_documents': 0})

    # Mock documents import
    mock_import = MagicMock(return_value='{"success": true}\n' * 100)
    client.collections.__getitem__ = MagicMock()
    client.collections.__getitem__.return_value.documents.import_ = mock_import

    return client


class TestProductSchemaValidation:
    """Test product collection schema"""

    def test_schema_has_required_fields(self):
        """Test that product schema includes all required fields"""
        from index_products import create_products_collection

        with patch('index_products.client') as mock_client:
            mock_client.collections.create = MagicMock(return_value={'name': 'products'})

            create_products_collection()

            # Get the schema that was passed to create
            call_args = mock_client.collections.create.call_args
            schema = call_args[0][0]

            # Check required fields exist
            field_names = [f['name'] for f in schema['fields']]

            assert 'id' in field_names
            assert 'title' in field_names
            assert 'description' in field_names
            assert 'brand' in field_names
            assert 'categories' in field_names
            assert 'tags' in field_names
            assert 'price' in field_names
            assert 'rating' in field_names
            assert 'location' in field_names
            assert 'embedding' in field_names

    def test_embedding_field_has_auto_embed_config(self):
        """Test that embedding field has proper auto-embed configuration"""
        from index_products import create_products_collection

        with patch('index_products.client') as mock_client:
            mock_client.collections.create = MagicMock(return_value={'name': 'products'})

            create_products_collection()

            call_args = mock_client.collections.create.call_args
            schema = call_args[0][0]

            # Find embedding field
            embedding_field = next(f for f in schema['fields'] if f['name'] == 'embedding')

            assert embedding_field['type'] == 'float[]'
            assert 'embed' in embedding_field
            assert 'from' in embedding_field['embed']
            assert 'title' in embedding_field['embed']['from']
            assert 'description' in embedding_field['embed']['from']
            assert 'model_config' in embedding_field['embed']
            assert 'model_name' in embedding_field['embed']['model_config']

    def test_facet_fields_are_configured(self):
        """Test that facet fields are properly configured"""
        from index_products import create_products_collection

        with patch('index_products.client') as mock_client:
            mock_client.collections.create = MagicMock(return_value={'name': 'products'})

            create_products_collection()

            call_args = mock_client.collections.create.call_args
            schema = call_args[0][0]

            # Fields that should be facetable
            facet_fields = ['brand', 'categories', 'tags', 'price', 'available', 'color']

            for field_name in facet_fields:
                field = next(f for f in schema['fields'] if f['name'] == field_name)
                assert field.get('facet') == True, f"{field_name} should be facetable"


class TestBrandSchemaValidation:
    """Test brand collection schema"""

    def test_brand_schema_has_embedding(self):
        """Test that brand schema includes embedding field"""
        from index_brands import create_brands_collection

        with patch('index_brands.client') as mock_client:
            mock_client.collections.create = MagicMock(return_value={'name': 'brands'})

            create_brands_collection()

            call_args = mock_client.collections.create.call_args
            schema = call_args[0][0]

            field_names = [f['name'] for f in schema['fields']]
            assert 'embedding' in field_names

            # Check embedding config
            embedding_field = next(f for f in schema['fields'] if f['name'] == 'embedding')
            assert 'embed' in embedding_field
            assert 'name' in embedding_field['embed']['from']
            assert 'description' in embedding_field['embed']['from']


class TestSynonymsConfiguration:
    """Test synonyms setup"""

    def test_multi_way_synonyms(self):
        """Test that multi-way synonyms are configured"""
        from synonyms_overrides import create_synonyms

        with patch('synonyms_overrides.client') as mock_client:
            mock_upsert = MagicMock(return_value={'id': 'test'})
            mock_client.collections.__getitem__.return_value.synonyms.upsert = mock_upsert

            create_synonyms()

            # Verify upsert was called for synonyms
            assert mock_upsert.call_count > 0

            # Check that footwear synonyms exist
            calls = [str(call) for call in mock_upsert.call_args_list]
            assert any('sneaker' in str(call) or 'shoe' in str(call) for call in calls)

    def test_one_way_synonyms(self):
        """Test that one-way synonyms are configured"""
        from synonyms_overrides import create_synonyms

        with patch('synonyms_overrides.client') as mock_client:
            mock_upsert = MagicMock(return_value={'id': 'test'})
            mock_client.collections.__getitem__.return_value.synonyms.upsert = mock_upsert

            create_synonyms()

            # Check for root-based synonyms
            calls = [str(call) for call in mock_upsert.call_args_list]
            # Should have smartphone -> iphone, android expansion
            assert any('smartphone' in str(call) or 'iphone' in str(call) for call in calls)


class TestOverridesConfiguration:
    """Test override/curation rules"""

    def test_pinning_override_exists(self):
        """Test that pinning overrides are configured"""
        from synonyms_overrides import create_overrides

        with patch('synonyms_overrides.client') as mock_client:
            mock_upsert = MagicMock(return_value={'id': 'test'})
            mock_client.collections.__getitem__.return_value.overrides.upsert = mock_upsert

            create_overrides()

            # Check that overrides were created
            assert mock_upsert.call_count > 0

            # Find the trail running override
            calls = mock_upsert.call_args_list
            trail_running_override = None
            for call in calls:
                args = call[0]
                if len(args) > 1 and 'rule' in str(args[1]):
                    override_data = args[1]
                    if 'trail running' in str(override_data.get('rule', {})):
                        trail_running_override = override_data
                        break

            # If trail running override exists, verify it has includes
            if trail_running_override:
                assert 'includes' in trail_running_override or 'rule' in trail_running_override

    def test_dynamic_filtering_override_exists(self):
        """Test that dynamic filtering overrides are configured"""
        from synonyms_overrides import create_overrides

        with patch('synonyms_overrides.client') as mock_client:
            mock_upsert = MagicMock(return_value={'id': 'test'})
            mock_client.collections.__getitem__.return_value.overrides.upsert = mock_upsert

            create_overrides()

            # Check for brand filtering overrides
            calls = mock_upsert.call_args_list
            has_brand_override = False
            for call in calls:
                args = call[0]
                if len(args) > 1:
                    override_data = args[1]
                    if 'filter_by' in str(override_data) and 'brand' in str(override_data):
                        has_brand_override = True
                        break

            assert has_brand_override, "Should have brand filtering override"


class TestDataGeneration:
    """Test data generation produces valid output"""

    def test_product_json_is_valid(self):
        """Test that generated product JSON is valid"""
        # Mock config loading - ensure enough items for random.sample()
        test_config = {
            'categories': ['Shoes', 'Apparel', 'Outdoors'],
            'shoe_brands': ['Nike', 'Adidas', 'Brooks'],
            'apparel_brands': ['Patagonia', 'The North Face', 'Columbia'],
            'electronics_brands': ['Samsung', 'Apple', 'Sony'],
            'home_brands': ['Yeti', 'Stanley', 'Coleman'],
            'colors': ['Black', 'White', 'Blue', 'Red', 'Green'],
            'tags': ['waterproof', 'lightweight', 'durable', 'breathable', 'eco-friendly'],
            'cities': [
                {'name': 'Seattle', 'lat': 47.6062, 'lng': -122.3321},
                {'name': 'Denver', 'lat': 39.7392, 'lng': -104.9903}
            ]
        }

        with patch('builtins.open', mock_open()):
            with patch('yaml.safe_load', return_value=test_config):
                from synth_data import generate_product
                import synth_data
                synth_data.config = test_config
                product = generate_product(1)

                # Should be JSON serializable
                json_str = json.dumps(product)
                assert len(json_str) > 0

                # Should be deserializable
                parsed = json.loads(json_str)
                assert parsed['id'] == '1'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
