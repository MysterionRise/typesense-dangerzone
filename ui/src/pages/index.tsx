import { useState, useMemo } from 'react';
import { InstantSearch, Configure } from 'react-instantsearch';
import { createTypesenseAdapter } from '../lib/typesenseAdapter';
import HybridSearch from '../components/HybridSearch';
import FacetPanel from '../components/FacetPanel';
import GeoControls from '../components/GeoControls';
import SearchResults from '../components/SearchResults';

export default function Home() {
  // Hybrid search controls
  const [alpha, setAlpha] = useState(0.3);
  const [numTypos, setNumTypos] = useState(2);
  const [prefixEnabled, setPrefixEnabled] = useState(true);
  const [rerankHybrid, setRerankHybrid] = useState(false);
  const [distanceThreshold, setDistanceThreshold] = useState(0.35);
  const [currentTab, setCurrentTab] = useState<'products' | 'brands'>('products');

  // API Key selection (scoped key demo)
  const [apiKeyMode, setApiKeyMode] = useState<'public' | 'scoped'>('public');

  // Geo search state
  const [geoEnabled, setGeoEnabled] = useState(false);
  const [geoLat, setGeoLat] = useState(47.6062); // Seattle
  const [geoLng, setGeoLng] = useState(-122.3321);
  const [geoRadius, setGeoRadius] = useState(50);

  // Create adapter with current settings
  const typesenseAdapter = useMemo(() => {
    const additionalParams: Record<string, any> = {
      num_typos: numTypos,
      prefix: prefixEnabled,
    };

    // Add vector distance threshold
    const vectorQuery = rerankHybrid
      ? `embedding:([], alpha: ${alpha}, distance_threshold: ${distanceThreshold}, rerank_hybrid_matches: true)`
      : `embedding:([], alpha: ${alpha}, distance_threshold: ${distanceThreshold})`;

    additionalParams.vector_query = vectorQuery;

    // Add geo filter if enabled
    if (geoEnabled) {
      additionalParams.filter_by = `location:(${geoLat}, ${geoLng}, ${geoRadius} km)`;
      additionalParams.sort_by = `location(${geoLat}, ${geoLng}):asc,_text_match:desc`;
    }

    // Scoped key demo: filter to specific category
    if (apiKeyMode === 'scoped') {
      const existingFilter = additionalParams.filter_by || '';
      additionalParams.filter_by = existingFilter
        ? `${existingFilter} && categories:=Apparel`
        : 'categories:=Apparel';
    }

    return createTypesenseAdapter(alpha, additionalParams);
  }, [alpha, numTypos, prefixEnabled, rerankHybrid, distanceThreshold, geoEnabled, geoLat, geoLng, geoRadius, apiKeyMode]);

  return (
    <div>
      {/* Header */}
      <header className="header">
        <div className="container">
          <h1>🏔️ Acme Outfitters</h1>
          <p>Discover your next adventure with hybrid search powered by Typesense</p>
        </div>
      </header>

      <div className="container">
        {/* Search Controls */}
        <div className="search-controls">
          {/* Hybrid Search Parameters */}
          <div className="controls-grid">
            {/* Alpha Slider */}
            <div className="control-group">
              <label>
                Semantic Weight (Alpha): <span className="control-value">{alpha.toFixed(2)}</span>
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={alpha}
                onChange={(e) => setAlpha(parseFloat(e.target.value))}
              />
              <span className="text-muted">
                {alpha < 0.3 ? '🔤 Keyword-focused' : alpha > 0.6 ? '🧠 Semantic-focused' : '⚖️ Balanced'}
              </span>
            </div>

            {/* Distance Threshold */}
            <div className="control-group">
              <label>
                Distance Threshold: <span className="control-value">{distanceThreshold.toFixed(2)}</span>
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={distanceThreshold}
                onChange={(e) => setDistanceThreshold(parseFloat(e.target.value))}
              />
              <span className="text-muted">Lower = stricter semantic match</span>
            </div>

            {/* Typo Tolerance */}
            <div className="control-group">
              <label>
                Typo Tolerance: <span className="control-value">{numTypos}</span>
              </label>
              <input
                type="range"
                min="0"
                max="2"
                step="1"
                value={numTypos}
                onChange={(e) => setNumTypos(parseInt(e.target.value))}
              />
              <span className="text-muted">0 = exact match, 2 = lenient</span>
            </div>

            {/* Prefix Toggle */}
            <div className="control-group">
              <label>
                <input
                  type="checkbox"
                  checked={prefixEnabled}
                  onChange={(e) => setPrefixEnabled(e.target.checked)}
                />
                {' '}Prefix Search (Autocomplete)
              </label>
              <span className="text-muted">Match partial words</span>
            </div>

            {/* Rerank Hybrid */}
            <div className="control-group">
              <label>
                <input
                  type="checkbox"
                  checked={rerankHybrid}
                  onChange={(e) => setRerankHybrid(e.target.checked)}
                />
                {' '}Rerank Hybrid Matches
              </label>
              <span className="text-muted">Advanced semantic reranking</span>
            </div>

            {/* API Key Mode */}
            <div className="control-group">
              <label>Demo Mode:</label>
              <select
                value={apiKeyMode}
                onChange={(e) => setApiKeyMode(e.target.value as 'public' | 'scoped')}
                style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
              >
                <option value="public">All Products</option>
                <option value="scoped">Scoped (Apparel Only)</option>
              </select>
              <span className="text-muted">Test scoped API keys</span>
            </div>
          </div>

          {/* Geo Controls */}
          <GeoControls
            enabled={geoEnabled}
            onEnabledChange={setGeoEnabled}
            lat={geoLat}
            lng={geoLng}
            radius={geoRadius}
            onLatChange={setGeoLat}
            onLngChange={setGeoLng}
            onRadiusChange={setGeoRadius}
          />
        </div>

        {/* InstantSearch Integration */}
        <InstantSearch
          searchClient={typesenseAdapter.searchClient}
          indexName="products"
        >
          <Configure
            hitsPerPage={20}
            attributesToSnippet={['description:30']}
          />

          {/* Main Layout */}
          <div className="main-layout">
            {/* Sidebar - Facets */}
            <aside className="sidebar">
              <FacetPanel />
            </aside>

            {/* Main Content - Search and Results */}
            <main>
              {/* Search Box with Suggestions */}
              <HybridSearch />

              {/* Results */}
              <div className="results-container" style={{ marginTop: '20px' }}>
                <SearchResults />
              </div>
            </main>
          </div>
        </InstantSearch>
      </div>

      {/* Info Footer */}
      <footer style={{
        marginTop: '40px',
        padding: '30px',
        background: '#fff',
        borderTop: '1px solid #e0e0e0',
        textAlign: 'center',
        color: '#666'
      }}>
        <p>
          <strong>💡 Hybrid Search Demo</strong> - Powered by Typesense v29 with auto-embedding
        </p>
        <p style={{ marginTop: '10px', fontSize: '0.9rem' }}>
          Try: "trail running shoes", "nike", "waterproof jacket", "camping gear near me"
        </p>
      </footer>
    </div>
  );
}
