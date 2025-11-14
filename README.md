# 🏔️ Typesense Hybrid Search Demo - Acme Outfitters

A comprehensive demonstration of **Typesense's hybrid search** capabilities combining keyword relevance with semantic search using auto-embedding. This full-stack demo showcases an e-commerce discovery experience with 30k synthetic products across multiple categories.

## ✨ Features Demonstrated

### 🧠 Core Search Features
- **Hybrid Search**: Blend keyword and semantic relevance with adjustable alpha weight (0.0-1.0)
- **Auto-Embedding**: Built-in embeddings using `ts/all-MiniLM-L12-v2` (no external ML service required)
- **Vector Search**: Semantic search on product titles, descriptions, and categories
- **Typo Tolerance**: Configurable fuzzy matching (0-2 typos)
- **Prefix Search**: Real-time autocomplete functionality
- **Drop Tokens Threshold**: Better handling of long conversational queries

### 🎛️ Advanced Features
- **Faceted Search**: Filter by brand, category, tags, price ranges, availability, color
- **Geo-Radius Search**: Filter products by location with radius in km ([lat, lng] format)
- **Synonyms**: Multi-way and one-way synonym support
- **Curation (Overrides)**:
  - Pin hero products to top positions
  - Dynamic brand filtering with token removal
  - Dynamic sorting rules
- **Query Suggestions**: Analytics-powered autocomplete
- **Multi-Search (Federated)**: Query products and brands simultaneously
- **Scoped API Keys**: Data access control (e.g., filter to specific categories)
- **Rank Fusion**: Configurable hybrid score blending
- **HNSW Tuning**: Vector index optimization options

### 🎨 UI Controls
- Real-time alpha slider for semantic weight tuning
- Distance threshold adjustment
- Rerank hybrid matches toggle
- Typo tolerance and prefix settings
- Geo-search with city presets and "Use My Location"
- API key mode switcher (public vs scoped)
- Query suggestions dropdown
- Comprehensive facet panel with searchable refinements

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local UI development, optional)
- 4GB RAM minimum (for Typesense + embeddings)

### One-Command Setup

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd typesense-hybrid-demo
   cp .env.example .env
   ```

2. **Launch everything**:
   ```bash
   docker compose up --build
   ```

   This will:
   - ✅ Start Typesense v29 on port 8108
   - ✅ Generate 30k products + 500 brands
   - ✅ Create collections with auto-embedding
   - ✅ Import data with bulk indexing
   - ✅ Configure synonyms, overrides, and analytics
   - ✅ Start Next.js UI on port 3000

3. **Access the demo**:
   - 🌐 **UI**: http://localhost:3000
   - 🔍 **Typesense API**: http://localhost:8108

### First Run Notes

⏱️ **First startup takes 5-10 minutes**:
- Model download: ~1-2GB for `ts/all-MiniLM-L12-v2`
- Data generation: ~30k products
- Embedding generation: Auto-computed on import

💡 Subsequent runs are much faster (model is cached).

## 📂 Project Structure

```
typesense-hybrid-demo/
├── docker-compose.yml          # Orchestration for all services
├── .env.example                # Environment configuration template
├── README.md                   # This file
│
├── backend/                    # Python data pipeline
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── seed_config.yml         # Data generation config
│   ├── synth_data.py           # Generate synthetic products/brands
│   ├── index_products.py       # Create products collection + import
│   ├── index_brands.py         # Create brands collection + import
│   ├── synonyms_overrides.py   # Configure synonyms & curation
│   ├── query_suggestions_setup.py  # Analytics & suggestions
│   └── sample_queries.http     # VS Code REST Client examples
│
├── ui/                         # Next.js React UI
│   ├── Dockerfile
│   ├── package.json
│   ├── next.config.js
│   ├── tsconfig.json
│   └── src/
│       ├── pages/
│       │   ├── _app.tsx
│       │   └── index.tsx       # Main search interface
│       ├── components/
│       │   ├── HybridSearch.tsx      # Search box + suggestions
│       │   ├── FacetPanel.tsx        # Filters sidebar
│       │   ├── GeoControls.tsx       # Geo-search controls
│       │   └── SearchResults.tsx     # Results grid + pagination
│       ├── lib/
│       │   ├── typesenseAdapter.ts   # InstantSearch adapter
│       │   └── api.ts                # Direct Typesense client
│       └── styles/
│           └── globals.css
│
└── data/                       # Generated data (gitignored)
    ├── products.ndjson
    ├── brands.ndjson
    └── search_key.txt
```

## 🔍 Try These Demo Searches

Open http://localhost:3000 and try:

### Basic Searches
- `trail running shoes` - Keyword + semantic matching
- `nike` - Triggers brand override (filters by Nike)
- `waterproof jacket` - Semantic understanding
- `camping gear` - Multi-category results

### Synonym Demos
- `sneaker` → matches "shoe", "trainer" via synonyms
- `smartphone` → expands to "iphone", "android"
- `tv` → matches "television", "display"

### Curated Queries
- `trail running` - Pins hero products to positions 1 & 2
- `bestseller` - Dynamic sorting by sales rank

### Geo Searches
1. Enable "Geo-Radius Search"
2. Select a city (e.g., Seattle)
3. Search `camping tent` - Results sorted by distance

### Conversational Queries
- `I need a waterproof jacket for hiking in the rain`
- `sustainable outdoor clothing for mountain adventures`

## 🎛️ Feature Controls Explained

### Alpha Slider (Semantic Weight)
- **0.0**: Pure keyword search (BM25)
- **0.3** (default): Balanced hybrid (30% semantic, 70% keyword)
- **0.7**: Semantic-focused
- **1.0**: Pure semantic/vector search

💡 **Rank Fusion**: Typesense uses RRF (Reciprocal Rank Fusion) to blend keyword and semantic scores. The `_text_match` score represents the fused result.

### Distance Threshold
- Filters out embeddings beyond similarity threshold
- **0.35** (default): Balanced
- Lower = stricter semantic matching
- Higher = more lenient

### Typo Tolerance
- **0**: Exact match only
- **1**: Allow 1 character typo
- **2** (default): Allow up to 2 typos

### Prefix Search
- **On** (default): Match partial words ("run" matches "running")
- **Off**: Exact word boundaries only

### Rerank Hybrid Matches
- Advanced semantic reranking of hybrid results
- Can improve quality for complex queries

### Geo-Radius Search
- **Filter**: `location:(lat, lng, radius km)`
- **Sort**: `location(lat, lng):asc` for distance sorting
- **Format**: Coordinates are `[latitude, longitude]`
- Use city presets or "Use My Location" button

### API Key Modes
- **Public**: All products visible
- **Scoped**: Filtered to `categories:=Apparel` (B2B demo)

## 🔧 Changing Embedding Models

In `backend/index_products.py`, modify the `model_config`:

### Built-in Models (No API Key Required)
```python
'model_config': {
    'model_name': 'ts/all-MiniLM-L12-v2',  # Default, 384d
    # 'model_name': 'ts/all-MiniLM-L6-v2',  # Faster, 384d
    # 'model_name': 'ts/e5-small-v2',       # Alternative, 384d
}
```

### OpenAI Embeddings
```python
'model_config': {
    'model_name': 'openai/text-embedding-3-small',
    'api_key': 'your_openai_key',
}
```

### Google Vertex AI
```python
'model_config': {
    'model_name': 'google/textembedding-gecko@latest',
    'project_id': 'your_project_id',
    'access_token': 'your_token',
}
```

## 📊 Collection Schemas

### Products Collection

```typescript
{
  name: 'products',
  enable_nested_fields: true,
  fields: [
    { name: 'id', type: 'string' },
    { name: 'title', type: 'string' },
    { name: 'description', type: 'string' },
    { name: 'brand', type: 'string', facet: true },
    { name: 'categories', type: 'string[]', facet: true },
    { name: 'tags', type: 'string[]', facet: true },
    { name: 'price', type: 'float', facet: true },
    { name: 'rating', type: 'float', sort: true },
    { name: 'available', type: 'bool', facet: true },
    { name: 'color', type: 'string', facet: true },
    { name: 'location', type: 'geopoint' },  // [lat, lng]

    // Auto-embedding field
    {
      name: 'embedding',
      type: 'float[]',
      embed: {
        from: ['title', 'description', 'categories'],
        model_config: { model_name: 'ts/all-MiniLM-L12-v2' }
      }
    }
  ],
  default_sorting_field: 'sales_rank'
}
```

## 🔍 Example Hybrid Query

```json
POST /collections/products/documents/search
{
  "q": "lightweight trail running shoes",
  "query_by": "title,description,embedding",
  "vector_query": "embedding:([], alpha: 0.45, distance_threshold: 0.35)",
  "facet_by": "brand,categories,tags,price(economy:[0,50],mid:[50,150],premium:[150,])",
  "filter_by": "available:=true && price:[50..200]",
  "sort_by": "_text_match:desc",
  "drop_tokens_threshold": 0,
  "num_typos": 2,
  "prefix": true,
  "per_page": 20
}
```

**Key Parameters**:
- `vector_query: "embedding:([], alpha: 0.45)"` - Auto-embed query, 45% semantic weight
- `_text_match:desc` - Sort by fused hybrid score
- `drop_tokens_threshold: 0` - Don't drop tokens for better conversational queries
- `distance_threshold: 0.35` - Filter low-similarity vectors

## 🔀 Multi-Search (Federated Search)

Query multiple collections in one request:

```json
POST /multi_search
{
  "searches": [
    {
      "collection": "products",
      "q": "patagonia",
      "query_by": "title,description,embedding",
      "vector_query": "embedding:([], alpha: 0.3)"
    },
    {
      "collection": "brands",
      "q": "patagonia",
      "query_by": "name,description,embedding",
      "vector_query": "embedding:([], alpha: 0.5)"
    }
  ]
}
```

**Note**: The UI demonstrates this with Products/Brands tabs (coming soon in UI code).

## 📖 Synonyms

Multi-way synonyms (all interchangeable):
```python
{
  'id': 'syn-footwear',
  'synonyms': ['sneaker', 'shoe', 'trainer', 'footwear']
}
```

One-way synonyms (root → expansions):
```python
{
  'id': 'syn-smartphone',
  'root': 'smartphone',
  'synonyms': ['iphone', 'android', 'mobile phone']
}
```

**Notes**:
- Synonyms don't apply inside exact phrase queries (`"quoted"`)
- Override rules take precedence over synonyms

## 🎯 Overrides (Curation)

### Pin Products
```python
{
  'id': 'override-trail-running-hero',
  'rule': { 'query': 'trail running', 'match': 'contains' },
  'includes': [
    {'id': '42', 'position': 1},
    {'id': '1337', 'position': 2}
  ]
}
```

### Dynamic Brand Filtering
```python
{
  'id': 'override-brand-nike',
  'rule': { 'query': 'nike', 'match': 'contains' },
  'filter_by': 'brand:=Nike',
  'remove_matched_tokens': True  # Remove "nike" from search
}
```

### Dynamic Sorting
```python
{
  'id': 'override-bestseller-sort',
  'rule': { 'query': 'bestseller', 'match': 'contains' },
  'sort_by': 'sales_rank:asc',
  'remove_matched_tokens': True
}
```

## 🔐 Security: API Keys

### Admin Key (Backend Only)
```bash
TYPESENSE_API_KEY=xyz123_demo_key_change_in_production
```

### Search-Only Key (UI)
Generated by `backend/index_products.py`:
```python
{
  'description': 'Search-only key for UI',
  'actions': ['documents:search'],
  'collections': ['products', 'brands']
}
```

### Scoped Key (Data Access Control)
```python
{
  'filter_by': 'categories:=Apparel',
  'expires_at': timestamp
}
```

💡 **Never expose admin keys to the browser!**

## ⚙️ Advanced Performance Tuning

### HNSW Index Parameters
In `backend/index_products.py`, add to embedding field:

```python
'hnsw_params': {
    'ef_construction': 300,  # Build quality (100-500)
    'M': 24                  # Graph connectivity (8-48)
}
```

**Trade-offs**:
- Higher `ef_construction` = better recall, slower indexing
- Higher `M` = better recall, more memory

### Flat Search Cutoff
For small datasets, bypass HNSW:
```json
{
  "vector_query": "embedding:([], alpha: 0.3, flat_search_cutoff: 50000)"
}
```

## 🧪 Testing with sample_queries.http

Use VS Code REST Client extension:

1. Open `backend/sample_queries.http`
2. Install "REST Client" extension
3. Click "Send Request" above any query

**Included Tests**:
- Basic keyword search
- Hybrid search with various alpha values
- Geo-radius search
- Curated queries (overrides)
- Synonym tests
- Multi-search
- Query suggestions
- Scoped API key demo

## 🐛 Troubleshooting

### Typesense container fails to start
- Ensure port 8108 is available
- Check Docker has at least 4GB RAM allocated

### Embeddings generation is slow
- First run downloads model (~1-2GB)
- Generation is CPU-intensive for 30k docs (~5-10 min)
- Consider reducing `NUM_PRODUCTS` in `.env` for testing

### UI can't connect to Typesense
- Ensure `NEXT_PUBLIC_TYPESENSE_HOST=localhost`
- Check Typesense is healthy: `curl http://localhost:8108/health`

### No search results
- Verify data import succeeded: Check backend container logs
- Test API directly: Use `sample_queries.http`

### Suggestions not working
- Check `product_suggestions` collection exists
- Verify query: `GET /collections/product_suggestions/documents/search?q=run&query_by=q&prefix=true`

## 📚 Learn More

- [Typesense Documentation](https://typesense.org/docs/)
- [Vector Search Guide](https://typesense.org/docs/guide/vector-search.html)
- [Hybrid Search](https://typesense.org/docs/guide/semantic-search.html#hybrid-search)
- [Auto-Embedding](https://typesense.org/docs/guide/semantic-search.html#auto-embedding)
- [Synonyms](https://typesense.org/docs/guide/synonyms.html)
- [Overrides](https://typesense.org/docs/guide/curation.html)
- [Geo Search](https://typesense.org/docs/guide/geoSearch.html)
- [InstantSearch Adapter](https://github.com/typesense/typesense-instantsearch-adapter)

## 🎓 Key Takeaways

1. **Hybrid Search** blends keyword precision with semantic understanding
2. **Alpha tuning** lets you balance relevance for different use cases
3. **Auto-embedding** eliminates external ML dependencies
4. **Overrides** enable merchandising without reindexing
5. **Synonyms** improve recall for common alternate terms
6. **Geo-search** enables location-aware discovery
7. **Scoped keys** provide data access control

## 📄 License

MIT License - See LICENSE file

## 🤝 Contributing

This is a demo repository. For production use cases, consider:
- Using environment-specific API keys
- Implementing rate limiting
- Adding authentication
- Monitoring and logging
- Scaling Typesense cluster
- Optimizing embedding model selection

---

**Built with**:
- [Typesense](https://typesense.org/) v29 - Fast, typo-tolerant search engine
- [Next.js](https://nextjs.org/) 14 - React framework
- [React InstantSearch](https://www.algolia.com/doc/guides/building-search-ui/what-is-instantsearch/react/) - Search UI components
- [Python](https://www.python.org/) 3.11 - Data pipeline
- [Faker](https://faker.readthedocs.io/) - Synthetic data generation

---

**Happy Searching! 🔍✨**
