#!/usr/bin/env python3
"""
Index Products into Typesense
Creates collection schema with auto-embedding and imports product data.
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
DATA_FILE = '/data/products.ndjson'

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


def create_products_collection() -> Dict[str, Any]:
    """
    Create products collection with auto-embedding field.

    Auto-embedding configuration:
    - The 'embedding' field is a float[] with embed.from fields
    - Typesense will automatically generate embeddings on write and query
    - Built-in model: ts/all-MiniLM-L12-v2 (384 dimensions)
    - Alternative models: ts/all-MiniLM-L6-v2, ts/e5-small-v2, ts/multi-qa-MiniLM-L6-cos-v1
    - For OpenAI/Vertex: change model_config to use API-based models
    """

    schema = {
        'name': 'products',
        'enable_nested_fields': True,  # Enable for future extensibility
        'fields': [
            # Primary fields
            {'name': 'id', 'type': 'string'},
            {'name': 'title', 'type': 'string'},
            {'name': 'description', 'type': 'string'},

            # Faceted fields
            {'name': 'brand', 'type': 'string', 'facet': True},
            {'name': 'categories', 'type': 'string[]', 'facet': True},
            {'name': 'tags', 'type': 'string[]', 'facet': True},
            {'name': 'color', 'type': 'string', 'facet': True},
            {'name': 'available', 'type': 'bool', 'facet': True},

            # Numeric/sortable fields
            {'name': 'price', 'type': 'float', 'facet': True},
            {'name': 'rating', 'type': 'float', 'sort': True},
            {'name': 'inventory', 'type': 'int32'},
            {'name': 'sales_rank', 'type': 'int32', 'sort': True},
            {'name': 'created_at', 'type': 'int64'},

            # Geo field for location-based searches
            # Format: [lat, lng]
            {'name': 'location', 'type': 'geopoint'},

            # Image
            {'name': 'image_url', 'type': 'string'},

            # Auto-embedding field
            # Typesense will automatically generate embeddings from title, description, categories
            # On search, pass vector_query: "embedding:([], alpha: 0.3)" to auto-embed the query
            {
                'name': 'embedding',
                'type': 'float[]',
                'embed': {
                    'from': ['title', 'description', 'categories'],
                    'model_config': {
                        # Built-in models (no external API required):
                        # - ts/all-MiniLM-L12-v2 (384d, best quality)
                        # - ts/all-MiniLM-L6-v2 (384d, faster)
                        # - ts/e5-small-v2 (384d, alternative)
                        # - ts/multi-qa-MiniLM-L6-cos-v1 (384d, optimized for Q&A)
                        #
                        # To use OpenAI instead:
                        # "model_name": "openai/text-embedding-3-small",
                        # "api_key": "your_openai_key"
                        #
                        # To use Vertex AI:
                        # "model_name": "google/textembedding-gecko@latest",
                        # "project_id": "your_project",
                        # "access_token": "your_token"
                        'model_name': 'ts/all-MiniLM-L12-v2',
                    }
                },
                # Optional: HNSW index tuning for large datasets
                # Higher values = better recall, slower indexing, more memory
                # Defaults: ef_construction=200, M=16
                # 'hnsw_params': {
                #     'ef_construction': 300,  # 100-500 typical range
                #     'M': 24,                 # 8-48 typical range
                # }
            },
        ],
        'default_sorting_field': 'sales_rank',
    }

    print(f"📋 Creating 'products' collection with auto-embedding...")
    print(f"   Model: ts/all-MiniLM-L12-v2 (384 dimensions)")
    print(f"   Embedding from: title, description, categories")

    try:
        # Drop existing collection if it exists
        try:
            client.collections['products'].delete()
            print("   ♻️  Deleted existing 'products' collection")
        except Exception:
            pass

        # Create collection
        result = client.collections.create(schema)
        print(f"✅ Collection created successfully")
        return result

    except Exception as e:
        print(f"❌ Error creating collection: {e}")
        raise


def import_products() -> None:
    """Import products from NDJSON file using bulk import."""
    print(f"\n📥 Importing products from {DATA_FILE}...")

    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"Data file not found: {DATA_FILE}")

    # Read NDJSON file
    with open(DATA_FILE, 'r') as f:
        products_ndjson = f.read()

    # Count documents
    num_products = len(products_ndjson.strip().split('\n'))
    print(f"   Documents to import: {num_products:,}")

    # Bulk import with progress tracking
    print("   Importing... (this may take a few minutes due to auto-embedding)")
    start_time = time.time()

    try:
        # Import in batches for better error handling
        result = client.collections['products'].documents.import_(
            products_ndjson,
            {
                'action': 'create',
                'batch_size': 500,  # Smaller batches for embedding generation
            }
        )

        # Parse import results
        results = [json.loads(line) for line in result.split('\n') if line.strip()]
        success_count = sum(1 for r in results if r.get('success'))
        failure_count = len(results) - success_count

        elapsed = time.time() - start_time

        print(f"\n✅ Import complete in {elapsed:.1f}s")
        print(f"   Successful: {success_count:,}")
        if failure_count > 0:
            print(f"   ⚠️  Failed: {failure_count}")
            # Show first few failures
            failures = [r for r in results if not r.get('success')][:5]
            for fail in failures:
                print(f"      Error: {fail.get('error')}")

    except Exception as e:
        print(f"❌ Import error: {e}")
        raise


def create_search_only_key() -> str:
    """
    Create a search-only scoped API key for the UI.
    This key has no write permissions.
    """
    print(f"\n🔑 Creating search-only API key...")

    try:
        search_key = client.keys.create({
            'description': 'Search-only key for UI',
            'actions': ['documents:search'],
            'collections': ['products', 'brands'],
        })

        key_value = search_key['value']
        print(f"✅ Search-only key created: {key_value[:20]}...")

        # Write to file for UI to use
        with open('/data/search_key.txt', 'w') as f:
            f.write(key_value)

        return key_value

    except Exception as e:
        print(f"⚠️  Could not create search key: {e}")
        # Return admin key as fallback (not recommended for production!)
        return TYPESENSE_API_KEY


def create_scoped_api_key() -> str:
    """
    Create a scoped API key for B2B demo.
    This key restricts access to only Workwear category.
    """
    print(f"\n🔐 Creating scoped API key (Workwear only)...")

    try:
        # Scoped keys are created client-side by embedding filter_by
        # This is a demo - in production, generate server-side
        scoped_params = {
            'filter_by': 'categories:=Apparel',
            'expires_at': int(time.time()) + 86400 * 365,  # 1 year
        }

        # Note: For actual scoped key generation, you'd use client.keys.generate_scoped_search_key()
        # Here we document the pattern
        print(f"   Scoped filter: categories:=Apparel")
        print(f"   (Use this pattern in UI to demonstrate access control)")

        with open('/data/scoped_key_params.json', 'w') as f:
            json.dump(scoped_params, f)

        return "scoped_key_demo"

    except Exception as e:
        print(f"⚠️  Note: {e}")
        return ""


def main():
    """Main execution flow."""
    print("=" * 60)
    print("🚀 Typesense Products Indexing")
    print("=" * 60)

    # Wait a moment for Typesense to be fully ready
    time.sleep(2)

    # Create collection
    create_products_collection()

    # Import data
    import_products()

    # Create API keys
    create_search_only_key()
    create_scoped_api_key()

    print("\n" + "=" * 60)
    print("✅ Products indexing complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
