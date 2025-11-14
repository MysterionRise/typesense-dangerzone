#!/usr/bin/env python3
"""
Configure Synonyms and Overrides (Curation) in Typesense
Demonstrates multi-way synonyms, one-way synonyms, and dynamic overrides.
"""

import os
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


def create_synonyms():
    """
    Create synonym definitions for better search recall.

    Notes:
    - Multi-way synonyms: all terms are interchangeable
    - One-way synonyms: root term expands to include synonyms
    - Synonyms don't apply inside exact phrase queries (quotes) or filters
    - Override rules take precedence over synonyms
    """
    print("=" * 60)
    print("📖 Creating Synonyms")
    print("=" * 60)

    synonyms = [
        # Multi-way synonyms (all interchangeable)
        {
            'id': 'syn-footwear',
            'synonyms': ['sneaker', 'shoe', 'trainer', 'footwear'],
        },
        {
            'id': 'syn-jacket',
            'synonyms': ['jacket', 'coat', 'parka', 'windbreaker'],
        },
        {
            'id': 'syn-backpack',
            'synonyms': ['backpack', 'rucksack', 'pack', 'daypack'],
        },
        {
            'id': 'syn-tv',
            'synonyms': ['tv', 'television', 'display', 'monitor'],
        },

        # One-way synonyms (root => synonyms)
        # When user searches "smartphone", also match "iphone" and "android"
        {
            'id': 'syn-smartphone',
            'root': 'smartphone',
            'synonyms': ['iphone', 'android', 'mobile phone', 'cell phone'],
        },
        {
            'id': 'syn-laptop',
            'root': 'laptop',
            'synonyms': ['notebook', 'macbook', 'chromebook'],
        },

        # Locale-specific example
        {
            'id': 'syn-color-us',
            'root': 'color',
            'synonyms': ['colour'],  # US to UK spelling
            'locale': 'en',
        },
    ]

    for syn in synonyms:
        try:
            # Upsert synonym (create or update)
            client.collections['products'].synonyms.upsert(syn['id'], syn)

            syn_type = 'One-way' if 'root' in syn else 'Multi-way'
            terms = syn.get('synonyms', [])
            if 'root' in syn:
                terms = [syn['root']] + terms

            print(f"✅ {syn_type}: {', '.join(terms)}")

        except Exception as e:
            print(f"❌ Error creating synonym '{syn['id']}': {e}")

    print()


def create_overrides():
    """
    Create curation rules (overrides) for query manipulation.

    Override capabilities:
    - Pin specific documents to top positions (includes.position)
    - Hide documents from results (excludes)
    - Dynamic filtering based on query tokens (filter_by + remove_matched_tokens)
    - Dynamic sorting (sort_by)
    - Replace query (replace_query)

    Precedence: Overrides are applied before synonyms.
    """
    print("=" * 60)
    print("🎯 Creating Overrides (Curation)")
    print("=" * 60)

    overrides = [
        # 1. Pin hero products for "trail running"
        {
            'id': 'override-trail-running-hero',
            'rule': {
                'query': 'trail running',
                'match': 'contains',  # Matches if query contains "trail running"
            },
            'includes': [
                # Pin specific product IDs to positions 1 and 2
                {'id': '42', 'position': 1},
                {'id': '1337', 'position': 2},
            ],
            # Optional: filter_curated_hits controls if pinned docs must match query
            # 'filter_curated_hits': False,  # Default: true (pinned docs must match)
        },

        # 2. Hide out-of-scope product
        {
            'id': 'override-hide-discontinued',
            'rule': {
                'query': 'trail running',
                'match': 'contains',
            },
            'excludes': [
                {'id': '999'},  # Hide discontinued product
            ],
        },

        # 3. Dynamic filtering by brand (remove token from query)
        # When query contains "nike", filter by brand and remove "nike" from search terms
        {
            'id': 'override-brand-nike',
            'rule': {
                'query': 'nike',
                'match': 'contains',
            },
            'filter_by': 'brand:=Nike',
            'remove_matched_tokens': True,  # Remove "nike" from query string
        },

        # 4. Dynamic filtering - Adidas
        {
            'id': 'override-brand-adidas',
            'rule': {
                'query': 'adidas',
                'match': 'contains',
            },
            'filter_by': 'brand:=Adidas',
            'remove_matched_tokens': True,
        },

        # 5. Dynamic filtering - Patagonia
        {
            'id': 'override-brand-patagonia',
            'rule': {
                'query': 'patagonia',
                'match': 'contains',
            },
            'filter_by': 'brand:=Patagonia',
            'remove_matched_tokens': True,
        },

        # 6. Dynamic sorting example
        # When query contains "bestseller", sort by sales_rank instead of default
        {
            'id': 'override-bestseller-sort',
            'rule': {
                'query': 'bestseller',
                'match': 'contains',
            },
            'sort_by': 'sales_rank:asc',  # Lower rank = better seller
            'remove_matched_tokens': True,
        },

        # 7. Dynamic filtering for "on sale" queries
        {
            'id': 'override-sale',
            'rule': {
                'query': 'sale',
                'match': 'exact',
            },
            'filter_by': 'tags:=sale',
            'remove_matched_tokens': True,
        },

        # 8. Exact match override for premium products
        {
            'id': 'override-premium',
            'rule': {
                'query': 'premium',
                'match': 'exact',
            },
            'filter_by': 'price:>150',
            'remove_matched_tokens': True,
        },
    ]

    for override in overrides:
        try:
            client.collections['products'].overrides.upsert(override['id'], override)

            rule_desc = f"{override['rule']['match']} '{override['rule']['query']}'"
            actions = []

            if 'includes' in override:
                actions.append(f"pin {len(override['includes'])} docs")
            if 'excludes' in override:
                actions.append(f"hide {len(override['excludes'])} docs")
            if 'filter_by' in override:
                actions.append(f"filter: {override['filter_by']}")
            if 'sort_by' in override:
                actions.append(f"sort: {override['sort_by']}")

            print(f"✅ {override['id']}")
            print(f"   Rule: {rule_desc}")
            print(f"   Actions: {', '.join(actions)}")

        except Exception as e:
            print(f"❌ Error creating override '{override['id']}': {e}")

    print()


def create_search_presets():
    """
    Create Search Presets for A/B testing different relevance configurations.

    Presets allow you to define named search configurations server-side
    and reference them by name in queries, enabling A/B testing without
    redeploying the UI.
    """
    print("=" * 60)
    print("🔬 Creating Search Presets (A/B Testing)")
    print("=" * 60)

    presets = [
        # Preset 1: Keyword-focused (lower semantic alpha)
        {
            'name': 'listing_view_v1',
            'value': {
                'query_by': 'title,description,embedding',
                'sort_by': '_text_match:desc,sales_rank:asc',
                'facet_by': 'brand,categories,tags,price',
                'max_facet_values': 50,
                # Lower alpha = more keyword weight
                'vector_query': 'embedding:([], alpha: 0.2)',
            }
        },
        # Preset 2: Semantic-focused (higher alpha)
        {
            'name': 'listing_view_v2',
            'value': {
                'query_by': 'title,description,embedding',
                'sort_by': '_text_match:desc,rating:desc',
                'facet_by': 'brand,categories,tags,price',
                'max_facet_values': 50,
                # Higher alpha = more semantic weight
                'vector_query': 'embedding:([], alpha: 0.5, distance_threshold: 0.3)',
                'drop_tokens_threshold': 0,  # Better for conversational queries
            }
        },
    ]

    for preset in presets:
        try:
            # Note: Presets API may vary by Typesense version
            # This demonstrates the concept; check docs for exact API
            client.presets.upsert(preset['name'], preset)

            alpha = preset['value'].get('vector_query', '').split('alpha:')[1].split(',')[0].strip() if 'alpha:' in preset['value'].get('vector_query', '') else 'N/A'
            print(f"✅ {preset['name']}")
            print(f"   Alpha: {alpha}, Sort: {preset['value']['sort_by'].split(',')[0]}")

        except Exception as e:
            # Presets may not be available in all Typesense versions
            print(f"⚠️  Preset '{preset['name']}': {e}")
            print(f"   (Presets may require Typesense v0.25+)")

    print()


def main():
    """Main execution flow."""
    print("\n" + "=" * 60)
    print("🎨 Typesense Advanced Features Setup")
    print("=" * 60)
    print()

    create_synonyms()
    create_overrides()

    try:
        create_search_presets()
    except Exception as e:
        print(f"⚠️  Search presets not available: {e}\n")

    print("=" * 60)
    print("✅ Synonyms and Overrides configured!")
    print("=" * 60)
    print()
    print("💡 Try these queries to see features in action:")
    print("   - 'nike shoes' → filters by brand automatically")
    print("   - 'trail running' → pins hero products to top")
    print("   - 'sneaker' → matches 'shoe', 'trainer' via synonyms")
    print("   - 'smartphone' → expands to iphone, android")
    print("=" * 60)
    print()


if __name__ == '__main__':
    main()
