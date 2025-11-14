#!/usr/bin/env python3
"""
Synthetic Data Generator for Acme Outfitters
Generates realistic e-commerce product and brand data for Typesense hybrid search demo.
"""

import json
import random
import os
from typing import List, Dict, Any
from faker import Faker
import yaml

# Configuration
NUM_PRODUCTS = int(os.getenv('NUM_PRODUCTS', 30000))
NUM_BRANDS = int(os.getenv('NUM_BRANDS', 500))
RANDOM_SEED = int(os.getenv('RANDOM_SEED', 42))
OUTPUT_DIR = '/data'

# Initialize Faker with seed for reproducibility
fake = Faker()
Faker.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

# Load configuration
with open('/app/seed_config.yml', 'r') as f:
    config = yaml.safe_load(f)


def generate_product_title(category: str, brand: str) -> str:
    """Generate realistic product titles based on category."""
    templates = {
        'Shoes': [
            f"{brand} {{}} Trail Running Shoes",
            f"{brand} {{}} Hiking Boots",
            f"{brand} {{}} Athletic Sneakers",
            f"{brand} {{}} Walking Shoes",
            f"{brand} {{}} Cross Training Shoes",
        ],
        'Apparel': [
            f"{brand} {{}} Jacket",
            f"{brand} {{}} Base Layer Top",
            f"{brand} {{}} Hiking Pants",
            f"{brand} {{}} Fleece Pullover",
            f"{brand} {{}} Rain Jacket",
            f"{brand} {{}} T-Shirt",
            f"{brand} {{}} Shorts",
        ],
        'Outdoors': [
            f"{brand} {{}} Tent",
            f"{brand} {{}} Sleeping Bag",
            f"{brand} {{}} Backpack",
            f"{brand} {{}} Camping Stove",
            f"{brand} {{}} Trekking Poles",
            f"{brand} {{}} Headlamp",
        ],
        'Electronics': [
            f"{brand} {{}} GPS Watch",
            f"{brand} {{}} Action Camera",
            f"{brand} {{}} Bluetooth Speaker",
            f"{brand} {{}} Fitness Tracker",
            f"{brand} {{}} Smartphone",
            f"{brand} {{}} Wireless Earbuds",
            f"{brand} {{}} Smart TV",
        ],
        'Home': [
            f"{brand} {{}} Insulated Bottle",
            f"{brand} {{}} Cooler",
            f"{brand} {{}} Travel Mug",
            f"{brand} {{}} Camping Chair",
            f"{brand} {{}} Cookware Set",
        ],
    }

    modifiers = ['Pro', 'Ultra', 'Max', 'Elite', 'Sport', 'Adventure', 'Explorer',
                 'Summit', 'Trail', 'Peak', 'Quest', 'Voyager', 'Nomad']

    template = random.choice(templates.get(category, templates['Apparel']))
    modifier = random.choice(modifiers)

    return template.format(modifier)


def generate_description(title: str, category: str) -> str:
    """Generate compelling product descriptions."""
    features = {
        'Shoes': [
            'Lightweight construction with superior cushioning',
            'Advanced traction outsole for all-terrain grip',
            'Breathable mesh upper with reinforced toe cap',
            'Responsive midsole technology for energy return',
            'Water-resistant treatment to keep feet dry',
        ],
        'Apparel': [
            'Made from sustainable recycled materials',
            'Moisture-wicking fabric keeps you comfortable',
            'Four-way stretch for unrestricted movement',
            'UPF 50+ sun protection',
            'Articulated fit for enhanced mobility',
        ],
        'Outdoors': [
            'Engineered for extreme conditions',
            'Ultra-lightweight and packable design',
            'Weather-resistant construction',
            'Ergonomic design for all-day comfort',
            'Durable materials built to last',
        ],
        'Electronics': [
            'Latest generation processor for peak performance',
            'Extended battery life up to 20 hours',
            'Crystal-clear display with high resolution',
            'Wireless connectivity and smart features',
            'Rugged design tested to military standards',
        ],
        'Home': [
            'Premium stainless steel construction',
            'Keeps beverages cold for 24 hours, hot for 12',
            'BPA-free and dishwasher safe',
            'Leak-proof lid with easy carry handle',
            'Sustainable and eco-friendly materials',
        ],
    }

    category_features = features.get(category, features['Apparel'])
    selected_features = random.sample(category_features, k=min(3, len(category_features)))

    description = f"{title} - {'. '.join(selected_features)}. "
    description += f"Perfect for {random.choice(['outdoor adventures', 'daily activities', 'fitness enthusiasts', 'weekend warriors', 'professionals'])}."

    return description


def get_brand_for_category(category: str) -> str:
    """Get appropriate brand for category."""
    brand_map = {
        'Shoes': config['shoe_brands'],
        'Apparel': config['apparel_brands'],
        'Electronics': config['electronics_brands'],
        'Home': config['home_brands'],
        'Outdoors': config['apparel_brands'] + config['home_brands'],
    }
    return random.choice(brand_map.get(category, config['apparel_brands']))


def generate_product(product_id: int) -> Dict[str, Any]:
    """Generate a single product with realistic attributes."""
    category = random.choice(config['categories'])
    brand = get_brand_for_category(category)
    title = generate_product_title(category, brand)

    # Select a city for store location
    city = random.choice(config['cities'])
    # Add small random offset to lat/lng for variety
    lat = city['lat'] + random.uniform(-0.5, 0.5)
    lng = city['lng'] + random.uniform(-0.5, 0.5)

    # Generate price based on category and brand
    base_prices = {
        'Shoes': (80, 250),
        'Apparel': (40, 300),
        'Outdoors': (50, 600),
        'Electronics': (100, 1200),
        'Home': (20, 150),
    }
    price_range = base_prices.get(category, (50, 200))
    price = round(random.uniform(*price_range), 2)

    # Rating follows a skewed distribution (mostly 3.5-5.0)
    rating = round(random.triangular(2.5, 5.0, 4.5), 1)

    # Availability (90% available)
    available = random.random() < 0.9

    # Tags (2-5 random tags)
    num_tags = random.randint(2, 5)
    tags = random.sample(config['tags'], num_tags)

    # Categories can have subcategories
    categories = [category]
    if random.random() < 0.3:
        subcategories = {
            'Shoes': ['Running', 'Hiking', 'Casual', 'Training'],
            'Apparel': ['Tops', 'Bottoms', 'Outerwear', 'Baselayers'],
            'Outdoors': ['Camping', 'Hiking', 'Climbing', 'Backpacking'],
            'Electronics': ['Wearables', 'Audio', 'Cameras', 'Mobile'],
            'Home': ['Kitchen', 'Storage', 'Furniture', 'Decor'],
        }
        if category in subcategories:
            categories.append(random.choice(subcategories[category]))

    product = {
        'id': str(product_id),
        'title': title,
        'description': generate_description(title, category),
        'brand': brand,
        'categories': categories,
        'tags': tags,
        'price': price,
        'rating': rating,
        'available': available,
        'color': random.choice(config['colors']),
        'location': [lat, lng],  # [lat, lng] format for Typesense
        'inventory': random.randint(0, 500) if available else 0,
        'sales_rank': random.randint(1, 100000),
        'created_at': fake.unix_time(),
        'image_url': f"https://picsum.photos/seed/{product_id}/400/400",
    }

    return product


def generate_brand(brand_id: int, brand_name: str) -> Dict[str, Any]:
    """Generate brand information with description for semantic search."""
    descriptions = {
        'Nike': 'Leading athletic footwear and apparel brand known for innovation in sports performance',
        'Patagonia': 'Outdoor clothing company committed to environmental sustainability and quality gear',
        'Apple': 'Technology innovator creating premium smartphones, tablets, and consumer electronics',
        'Yeti': 'Premium coolers and drinkware designed for outdoor adventures and durability',
    }

    # Generic description if not in map
    generic_desc = f"{brand_name} is a trusted brand offering high-quality products for {random.choice(['outdoor enthusiasts', 'athletes', 'adventurers', 'everyday users', 'professionals'])}."

    brand = {
        'id': str(brand_id),
        'name': brand_name,
        'description': descriptions.get(brand_name, generic_desc),
        'country': fake.country(),
        'founded_year': random.randint(1950, 2020),
        'product_count': random.randint(50, 5000),
        'avg_rating': round(random.uniform(3.5, 5.0), 1),
    }

    return brand


def main():
    """Generate synthetic data and write to NDJSON files."""
    print(f"🎲 Generating {NUM_PRODUCTS:,} products and {NUM_BRANDS} brands...")
    print(f"   Random seed: {RANDOM_SEED}")

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Generate products
    products_file = os.path.join(OUTPUT_DIR, 'products.ndjson')
    print(f"📦 Generating products → {products_file}")

    with open(products_file, 'w') as f:
        for i in range(1, NUM_PRODUCTS + 1):
            product = generate_product(i)
            f.write(json.dumps(product) + '\n')

            if i % 5000 == 0:
                print(f"   Generated {i:,} / {NUM_PRODUCTS:,} products...")

    print(f"✅ Products complete: {NUM_PRODUCTS:,} items")

    # Generate brands
    brands_file = os.path.join(OUTPUT_DIR, 'brands.ndjson')
    print(f"🏷️  Generating brands → {brands_file}")

    # Collect all unique brands from config
    all_brands = set()
    for brand_list in [config['shoe_brands'], config['apparel_brands'],
                       config['electronics_brands'], config['home_brands']]:
        all_brands.update(brand_list)

    all_brands = sorted(list(all_brands))

    # Add some extra generic brands to reach NUM_BRANDS
    while len(all_brands) < NUM_BRANDS:
        all_brands.append(f"{fake.company()} {random.choice(['Sports', 'Outdoor', 'Gear', 'Co.', 'Industries'])}")

    with open(brands_file, 'w') as f:
        for i, brand_name in enumerate(all_brands[:NUM_BRANDS], 1):
            brand = generate_brand(i, brand_name)
            f.write(json.dumps(brand) + '\n')

    print(f"✅ Brands complete: {len(all_brands[:NUM_BRANDS])} items")
    print(f"\n🎉 Data generation complete!")
    print(f"   Products: {products_file}")
    print(f"   Brands: {brands_file}")


if __name__ == '__main__':
    main()
