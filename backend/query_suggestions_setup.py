#!/usr/bin/env python3
"""
Setup Query Suggestions and Analytics
Configures analytics rules and creates query suggestions collection.
"""

import os
import time
import typesense

# Configuration
TYPESENSE_HOST = os.getenv('TYPESENSE_HOST', 'typesense')
TYPESENSE_PORT = os.getenv('TYPESENSE_PORT', '8108')
TYPESENSE_PROTOCOL = os.getenv('TYPESENSE_PROTOCOL', 'http')
TYPESENSE_API_KEY = os.getenv('TYPESENSE_API_KEY', 'xyz123_demo_key_change_in_production')

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


def create_analytics_rules():
    """
    Create analytics rules to track query events.

    Analytics capture search queries and clicks to power:
    - Query suggestions (autocomplete)
    - Popular searches
    - Search analytics and reporting
    - Personalization (with user tracking)

    UI should send X-TYPESENSE-USER-ID header for user-level analytics.
    """
    print("=" * 60)
    print("📊 Creating Analytics Rules")
    print("=" * 60)

    rules = [
        {
            'name': 'product_search_queries',
            'type': 'popular_queries',
            'params': {
                'source': {
                    'collections': ['products'],
                },
                'destination': {
                    'collection': 'product_queries',
                },
                'limit': 1000,  # Track top 1000 queries
            }
        },
    ]

    for rule in rules:
        try:
            # Create analytics rule
            client.analytics.rules.upsert(rule['name'], rule)
            print(f"✅ Analytics rule: {rule['name']}")
            print(f"   Type: {rule['type']}")
            print(f"   Tracking: {', '.join(rule['params']['source']['collections'])}")

        except Exception as e:
            print(f"⚠️  Analytics rule '{rule['name']}': {e}")
            print(f"   (Analytics may require Typesense v0.25+)")

    print()


def create_suggestions_collection():
    """
    Create and populate suggestions collection for autocomplete.

    This collection will be populated by analytics or can be seeded manually.
    """
    print("=" * 60)
    print("💡 Creating Query Suggestions Collection")
    print("=" * 60)

    schema = {
        'name': 'product_suggestions',
        'fields': [
            {'name': 'q', 'type': 'string'},  # The query suggestion
            {'name': 'count', 'type': 'int32', 'optional': True},  # How many times searched
        ],
    }

    try:
        # Drop existing
        try:
            client.collections['product_suggestions'].delete()
            print("   ♻️  Deleted existing suggestions collection")
        except Exception:
            pass

        # Create collection
        client.collections.create(schema)
        print("✅ Suggestions collection created")

        # Seed with common queries
        seed_suggestions()

    except Exception as e:
        print(f"❌ Error creating suggestions collection: {e}")


def seed_suggestions():
    """Seed the suggestions collection with popular/common queries."""
    print("\n📝 Seeding suggestions...")

    # Common search queries for demo
    suggestions = [
        # Shoes
        'running shoes',
        'trail running shoes',
        'hiking boots',
        'nike shoes',
        'waterproof shoes',
        'lightweight running shoes',

        # Apparel
        'rain jacket',
        'fleece jacket',
        'base layer',
        'hiking pants',
        'winter jacket',
        'patagonia jacket',

        # Outdoors
        'camping tent',
        'backpack',
        'sleeping bag',
        'trekking poles',
        'headlamp',
        'camping gear',

        # Electronics
        'gps watch',
        'fitness tracker',
        'action camera',
        'wireless earbuds',
        'smart watch',
        'bluetooth speaker',

        # Home
        'water bottle',
        'insulated bottle',
        'cooler',
        'yeti',
        'camping chair',

        # Brand searches
        'nike',
        'adidas',
        'patagonia',
        'the north face',
        'columbia',

        # Feature searches
        'waterproof',
        'lightweight',
        'breathable',
        'eco friendly',
        'on sale',
        'bestseller',
    ]

    docs = []
    for i, query in enumerate(suggestions, 1):
        docs.append({
            'q': query,
            'count': 1000 - (i * 10),  # Decreasing popularity
        })

    try:
        # Import suggestions
        import json
        ndjson = '\n'.join(json.dumps(doc) for doc in docs)

        result = client.collections['product_suggestions'].documents.import_(
            ndjson,
            {'action': 'upsert'}
        )

        print(f"✅ Seeded {len(suggestions)} query suggestions")

    except Exception as e:
        print(f"⚠️  Error seeding suggestions: {e}")


def create_demo_analytics_events():
    """
    Simulate some analytics events for demo purposes.

    In production, these events come from the UI via search API calls
    with X-TYPESENSE-USER-ID header.
    """
    print("\n" + "=" * 60)
    print("🎭 Simulating Analytics Events (Demo)")
    print("=" * 60)

    demo_queries = [
        'trail running shoes',
        'nike',
        'waterproof jacket',
        'camping tent',
        'gps watch',
    ]

    print("ℹ️  In production, analytics events are captured automatically")
    print("   when UI sends search requests with X-TYPESENSE-USER-ID header")
    print()
    print("   Example queries that would be tracked:")
    for q in demo_queries:
        print(f"   - {q}")

    print()


def main():
    """Main execution flow."""
    print("\n" + "=" * 60)
    print("🔍 Query Suggestions & Analytics Setup")
    print("=" * 60)
    print()

    # Create analytics rules (if supported)
    try:
        create_analytics_rules()
    except Exception as e:
        print(f"⚠️  Analytics features not available: {e}\n")

    # Create and seed suggestions
    create_suggestions_collection()

    # Info about analytics
    create_demo_analytics_events()

    print("=" * 60)
    print("✅ Query Suggestions configured!")
    print("=" * 60)
    print()
    print("💡 UI Integration:")
    print("   1. On keypress, query 'product_suggestions' collection")
    print("   2. Use 'q' field with prefix search: q:=<user_input>*")
    print("   3. Display suggestions in dropdown")
    print("   4. Send X-TYPESENSE-USER-ID header to track user queries")
    print("=" * 60)
    print()


if __name__ == '__main__':
    main()
