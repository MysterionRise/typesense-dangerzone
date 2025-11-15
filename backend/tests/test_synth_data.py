#!/usr/bin/env python3
"""
Tests for synthetic data generation
"""

import pytest
import sys
import os
from unittest.mock import patch, mock_open, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock config before importing synth_data
TEST_CONFIG = {
    'categories': ['Shoes', 'Apparel', 'Outdoors', 'Electronics', 'Home'],
    'shoe_brands': ['Nike', 'Adidas', 'Brooks'],
    'apparel_brands': ['Patagonia', 'The North Face', 'Columbia'],
    'electronics_brands': ['Samsung', 'Apple', 'Sony'],
    'home_brands': ['Yeti', 'Stanley', 'Coleman'],
    'colors': ['Black', 'White', 'Blue', 'Red'],
    'tags': ['waterproof', 'breathable', 'lightweight'],
    'cities': [
        {'name': 'Seattle', 'lat': 47.6062, 'lng': -122.3321},
        {'name': 'Denver', 'lat': 39.7392, 'lng': -104.9903},
    ]
}

# Mock the config loading
with patch('builtins.open', mock_open()):
    with patch('yaml.safe_load', return_value=TEST_CONFIG):
        from synth_data import (
            generate_product_title,
            generate_description,
            get_brand_for_category,
            generate_product,
            generate_brand,
        )

# Replace the actual config with our test config
import synth_data
synth_data.config = TEST_CONFIG


class TestProductTitleGeneration:
    """Test product title generation"""

    def test_generates_title_with_brand_and_category(self):
        """Test that title includes brand and category"""
        title = generate_product_title('Shoes', 'Nike')
        assert 'Nike' in title
        assert any(word in title for word in ['Trail', 'Running', 'Shoes', 'Hiking', 'Athletic', 'Sneakers'])

    def test_different_categories_produce_different_titles(self):
        """Test that different categories produce contextually appropriate titles"""
        shoe_title = generate_product_title('Shoes', 'Nike')
        electronics_title = generate_product_title('Electronics', 'Samsung')

        assert 'Nike' in shoe_title
        assert 'Samsung' in electronics_title
        # Shoes should have shoe-related terms
        assert any(word in shoe_title.lower() for word in ['shoe', 'boot', 'sneaker'])


class TestDescriptionGeneration:
    """Test product description generation"""

    def test_generates_non_empty_description(self):
        """Test that description is generated and not empty"""
        description = generate_description('Nike Pro Running Shoes', 'Shoes')
        assert len(description) > 50  # Should be a substantial description
        assert 'Nike Pro Running Shoes' in description

    def test_description_contains_features(self):
        """Test that description contains feature descriptions"""
        description = generate_description('Outdoor Jacket', 'Apparel')
        # Should contain some feature-related words
        assert any(word in description.lower() for word in [
            'material', 'fabric', 'construction', 'design', 'feature'
        ])


class TestBrandSelection:
    """Test brand selection for categories"""

    def test_returns_appropriate_brand_for_category(self):
        """Test that appropriate brands are returned for categories"""
        shoe_brand = get_brand_for_category('Shoes')
        assert shoe_brand in TEST_CONFIG['shoe_brands']

        apparel_brand = get_brand_for_category('Apparel')
        assert apparel_brand in TEST_CONFIG['apparel_brands']


class TestProductGeneration:
    """Test full product generation"""

    def test_generates_valid_product(self):
        """Test that a valid product document is generated"""
        product = generate_product(1)

        # Check required fields
        assert product['id'] == '1'
        assert 'title' in product
        assert 'description' in product
        assert 'brand' in product
        assert 'categories' in product
        assert isinstance(product['categories'], list)
        assert 'tags' in product
        assert isinstance(product['tags'], list)
        assert 'price' in product
        assert isinstance(product['price'], float)
        assert product['price'] > 0
        assert 'rating' in product
        assert 2.5 <= product['rating'] <= 5.0
        assert 'available' in product
        assert isinstance(product['available'], bool)
        assert 'location' in product
        assert isinstance(product['location'], list)
        assert len(product['location']) == 2  # [lat, lng]

    def test_product_has_valid_geo_coordinates(self):
        """Test that product location is valid"""
        product = generate_product(42)

        lat, lng = product['location']
        # Should be near Seattle with some variance
        assert 46.0 < lat < 49.0  # Reasonable latitude range
        assert -123.5 < lng < -121.0  # Reasonable longitude range


class TestBrandGeneration:
    """Test brand generation"""

    def test_generates_valid_brand(self):
        """Test that a valid brand document is generated"""
        brand = generate_brand(1, 'Nike')

        assert brand['id'] == '1'
        assert brand['name'] == 'Nike'
        assert 'description' in brand
        assert len(brand['description']) > 20
        assert 'country' in brand
        assert 'founded_year' in brand
        assert 1950 <= brand['founded_year'] <= 2020
        assert 'product_count' in brand
        assert brand['product_count'] > 0

    def test_brand_description_for_known_brands(self):
        """Test that known brands get custom descriptions"""
        nike_brand = generate_brand(1, 'Nike')
        assert 'Nike' in nike_brand['description'] or 'athletic' in nike_brand['description'].lower()


class TestDataConsistency:
    """Test data consistency and validity"""

    def test_products_have_consistent_schema(self):
        """Test that all products have consistent schema"""
        products = [generate_product(i) for i in range(10)]

        # All products should have the same keys
        keys = set(products[0].keys())
        for product in products[1:]:
            assert set(product.keys()) == keys

    def test_seeded_random_produces_deterministic_results(self):
        """Test that random seed produces consistent results"""
        import random
        from faker import Faker

        # Reset random seed
        random.seed(42)
        Faker.seed(42)

        product1 = generate_product(1)

        # Reset seed again
        random.seed(42)
        Faker.seed(42)

        product2 = generate_product(1)

        # Products should be identical with same seed
        assert product1['title'] == product2['title']
        assert product1['price'] == product2['price']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
