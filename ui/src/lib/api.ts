/**
 * Direct Typesense API Client
 * For features not covered by InstantSearch adapter (multi-search, suggestions, etc.)
 */

import Typesense from 'typesense';

const TYPESENSE_CONFIG = {
  host: process.env.NEXT_PUBLIC_TYPESENSE_HOST || 'localhost',
  port: process.env.NEXT_PUBLIC_TYPESENSE_PORT || '8108',
  protocol: process.env.NEXT_PUBLIC_TYPESENSE_PROTOCOL || 'http',
  apiKey: process.env.NEXT_PUBLIC_TYPESENSE_SEARCH_ONLY_API_KEY || 'xyz123_demo_key_change_in_production',
};

// Create Typesense client
const client = new Typesense.Client({
  nodes: [
    {
      host: TYPESENSE_CONFIG.host,
      port: TYPESENSE_CONFIG.port,
      protocol: TYPESENSE_CONFIG.protocol,
    },
  ],
  apiKey: TYPESENSE_CONFIG.apiKey,
  connectionTimeoutSeconds: 10,
});

/**
 * Multi-search: Query multiple collections in one request
 */
export async function multiSearch(
  query: string,
  alpha: number = 0.3,
  additionalParams: Record<string, any> = {}
): Promise<any> {
  const searches = [
    {
      collection: 'products',
      q: query,
      query_by: 'title,description,embedding',
      vector_query: `embedding:([], alpha: ${alpha})`,
      per_page: 10,
      ...additionalParams,
    },
    {
      collection: 'brands',
      q: query,
      query_by: 'name,description,embedding',
      vector_query: `embedding:([], alpha: ${alpha * 1.5})`, // Higher alpha for brands
      per_page: 5,
    },
  ];

  const results = await client.multiSearch.perform({ searches });
  return results;
}

/**
 * Query suggestions (autocomplete)
 */
export async function getQuerySuggestions(prefix: string): Promise<string[]> {
  if (!prefix || prefix.length < 2) {
    return [];
  }

  try {
    const results = await client
      .collections('product_suggestions')
      .documents()
      .search({
        q: prefix,
        query_by: 'q',
        prefix: true,
        per_page: 8,
      });

    return results.hits?.map((hit: any) => hit.document.q) || [];
  } catch (error) {
    console.error('Error fetching suggestions:', error);
    return [];
  }
}

/**
 * Geo-search with radius filter
 */
export async function geoSearch(
  query: string,
  lat: number,
  lng: number,
  radiusKm: number,
  alpha: number = 0.3
): Promise<any> {
  const searchParams = {
    q: query || '*',
    query_by: 'title,description,embedding',
    vector_query: `embedding:([], alpha: ${alpha})`,
    filter_by: `location:(${lat}, ${lng}, ${radiusKm} km)`,
    sort_by: `location(${lat}, ${lng}):asc,_text_match:desc`,
    per_page: 20,
  };

  const results = await client
    .collections('products')
    .documents()
    .search(searchParams);

  return results;
}

export default client;
