#!/usr/bin/env python3
"""
Index Brands into Typesense
Creates brands collection with auto-embedding for federated/multi-search demo.
"""

import os
import json
import time
from typing import Dict, Any
import typesense

# Configuration
TYPESENSE_HOST = os.getenv('TYPESENSE_HOST', 'typesense')
TYPESENSE_PORT = os.getenv('TYPESENSE_PORT', '8108')
TYPESENSE_PROTOCOL = os.getenv('TYPESENSE_PROTOCOL', 'http')
TYPESENSE_API_KEY = os.getenv('TYPESENSE_API_KEY', 'xyz123_demo_key_change_in_production')
DATA_FILE = '/data/brands.ndjson'

# Initialize Typesense client
client = typesense.Client({
    'nodes': [{
        'host': TYPESENSE_HOST,
        'port': TYPESENSE_PORT,
        'protocol': TYPESENSE_PROTOCOL,
    }],
    'api_key': TYPESENSE_API_KEY,
    'connection_timeout_seconds': 10,
})


def create_brands_collection() -> Dict[str, Any]:
    """Create brands collection with auto-embedding for semantic brand search."""

    schema = {
        'name': 'brands',
        'fields': [
            {'name': 'id', 'type': 'string'},
            {'name': 'name', 'type': 'string', 'facet': True},
            {'name': 'description', 'type': 'string'},
            {'name': 'country', 'type': 'string', 'facet': True},
            {'name': 'founded_year', 'type': 'int32', 'facet': True},
            {'name': 'product_count', 'type': 'int32', 'sort': True},
            {'name': 'avg_rating', 'type': 'float', 'sort': True},

            # Auto-embedding for semantic brand search
            {
                'name': 'embedding',
                'type': 'float[]',
                'embed': {
                    'from': ['name', 'description'],
                    'model_config': {
                        'model_name': 'ts/all-MiniLM-L12-v2',
                    }
                }
            },
        ],
        'default_sorting_field': 'product_count',
    }

    print(f"🏷️  Creating 'brands' collection with auto-embedding...")

    try:
        # Drop existing collection if it exists
        try:
            client.collections['brands'].delete()
            print("   ♻️  Deleted existing 'brands' collection")
        except Exception:
            pass

        # Create collection
        result = client.collections.create(schema)
        print(f"✅ Collection created successfully")
        return result

    except Exception as e:
        print(f"❌ Error creating collection: {e}")
        raise


def import_brands() -> None:
    """Import brands from NDJSON file."""
    print(f"\n📥 Importing brands from {DATA_FILE}...")

    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"Data file not found: {DATA_FILE}")

    # Read NDJSON file
    with open(DATA_FILE, 'r') as f:
        brands_ndjson = f.read()

    # Count documents
    num_brands = len(brands_ndjson.strip().split('\n'))
    print(f"   Documents to import: {num_brands:,}")

    start_time = time.time()

    try:
        result = client.collections['brands'].documents.import_(
            brands_ndjson,
            {'action': 'create', 'batch_size': 100}
        )

        results = [json.loads(line) for line in result.split('\n') if line.strip()]
        success_count = sum(1 for r in results if r.get('success'))
        failure_count = len(results) - success_count

        elapsed = time.time() - start_time

        print(f"\n✅ Import complete in {elapsed:.1f}s")
        print(f"   Successful: {success_count:,}")
        if failure_count > 0:
            print(f"   ⚠️  Failed: {failure_count}")

    except Exception as e:
        print(f"❌ Import error: {e}")
        raise


def main():
    """Main execution flow."""
    print("=" * 60)
    print("🏷️  Typesense Brands Indexing")
    print("=" * 60)

    time.sleep(1)

    create_brands_collection()
    import_brands()

    print("\n" + "=" * 60)
    print("✅ Brands indexing complete!")
    print("   Use multi_search to query products + brands together")
    print("=" * 60)


if __name__ == '__main__':
    main()
