/**
 * Typesense InstantSearch Adapter Configuration
 *
 * This adapter bridges Algolia's InstantSearch UI with Typesense's search API.
 * It handles hybrid search, faceting, filtering, and all advanced features.
 */

import TypesenseInstantsearchAdapter from 'typesense-instantsearch-adapter';

// Typesense configuration from environment
const TYPESENSE_CONFIG = {
  host: process.env.NEXT_PUBLIC_TYPESENSE_HOST || 'localhost',
  port: process.env.NEXT_PUBLIC_TYPESENSE_PORT || '8108',
  protocol: process.env.NEXT_PUBLIC_TYPESENSE_PROTOCOL || 'http',
  apiKey: process.env.NEXT_PUBLIC_TYPESENSE_SEARCH_ONLY_API_KEY || 'xyz123_demo_key_change_in_production',
};

/**
 * Create Typesense adapter with hybrid search configuration
 *
 * @param alpha - Semantic weight (0.0 = keyword only, 1.0 = semantic only)
 * @param additionalParams - Additional search parameters
 */
export function createTypesenseAdapter(
  alpha: number = 0.3,
  additionalParams: Record<string, any> = {}
) {
  const adapter = new TypesenseInstantsearchAdapter({
    server: {
      apiKey: TYPESENSE_CONFIG.apiKey,
      nodes: [
        {
          host: TYPESENSE_CONFIG.host,
          port: TYPESENSE_CONFIG.port,
          protocol: TYPESENSE_CONFIG.protocol,
        },
      ],
    },
    // Additional search parameters that will be sent with every request
    additionalSearchParameters: {
      // Hybrid search: query both text fields and embedding field
      query_by: 'title,description,embedding',

      // Vector query with auto-embedding
      // [] means Typesense will auto-embed the query text
      // alpha controls semantic vs keyword weight (0.0-1.0)
      // distance_threshold filters out embeddings beyond similarity threshold
      vector_query: `embedding:([], alpha: ${alpha}, distance_threshold: 0.35)`,

      // Sort by hybrid match score (fusion of keyword + semantic)
      sort_by: '_text_match:desc',

      // Drop tokens threshold: 0 = don't drop query tokens even if no results
      // Better for conversational/long queries
      drop_tokens_threshold: 0,

      // Typo tolerance (0-2)
      num_typos: 2,

      // Prefix search (autocomplete)
      prefix: true,

      // Merge additional params
      ...additionalParams,
    },
  });

  return adapter;
}

/**
 * Create adapter for multi-search (federated search)
 */
export function createMultiSearchAdapter(
  alpha: number = 0.3,
  collections: string[] = ['products', 'brands']
) {
  // Multi-search requires different configuration
  // For simplicity, we'll use the main adapter and handle multi-search via API
  return createTypesenseAdapter(alpha);
}

export default createTypesenseAdapter;
