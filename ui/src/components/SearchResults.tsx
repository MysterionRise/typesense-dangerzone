/**
 * SearchResults Component
 * Displays search results with pagination and stats
 */

import { Hits, Pagination, Stats, SortBy } from 'react-instantsearch';

function Hit({ hit }: { hit: any }) {
  return (
    <div className="product-card">
      <img
        src={hit.image_url}
        alt={hit.title}
        className="product-image"
      />
      <div className="product-info">
        <div className="product-brand">{hit.brand}</div>
        <h3 className="product-title">{hit.title}</h3>
        <div className="product-price">${hit.price.toFixed(2)}</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
          <div className="product-rating">
            {'⭐'.repeat(Math.round(hit.rating))} {hit.rating.toFixed(1)}
          </div>
          {hit.available ? (
            <span className="badge badge-success">In Stock</span>
          ) : (
            <span className="badge badge-warning">Out of Stock</span>
          )}
        </div>
        <div style={{ fontSize: '0.85rem', color: '#666', marginBottom: '8px' }}>
          {hit.categories?.join(' • ')}
        </div>
        {hit.tags && hit.tags.length > 0 && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
            {hit.tags.slice(0, 3).map((tag: string) => (
              <span
                key={tag}
                style={{
                  fontSize: '0.75rem',
                  padding: '2px 6px',
                  background: '#f0f0f0',
                  borderRadius: '3px',
                  color: '#666',
                }}
              >
                {tag}
              </span>
            ))}
          </div>
        )}
        {/* Show match score if available */}
        {hit._textMatch && (
          <div style={{
            marginTop: '8px',
            fontSize: '0.75rem',
            color: '#667eea',
            fontWeight: 600,
          }}>
            Match: {(hit._textMatch * 100).toFixed(0)}%
          </div>
        )}
      </div>
    </div>
  );
}

export default function SearchResults() {
  return (
    <div>
      {/* Stats and Sort */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '20px',
        flexWrap: 'wrap',
        gap: '15px',
      }}>
        <Stats
          classNames={{
            root: 'stats-root',
            text: 'stats-text',
          }}
        />

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <label style={{ fontSize: '0.9rem', fontWeight: 600 }}>Sort by:</label>
          <SortBy
            items={[
              { label: 'Relevance', value: 'products' },
              { label: 'Price: Low to High', value: 'products/sort/price:asc' },
              { label: 'Price: High to Low', value: 'products/sort/price:desc' },
              { label: 'Rating: High to Low', value: 'products/sort/rating:desc' },
              { label: 'Best Sellers', value: 'products/sort/sales_rank:asc' },
            ]}
            classNames={{
              root: 'sort-by-root',
              select: 'sort-by-select',
            }}
          />
        </div>
      </div>

      {/* Results Grid */}
      <Hits
        hitComponent={Hit}
        classNames={{
          root: 'hits-root',
          list: 'product-grid',
          item: 'hit-item',
        }}
      />

      {/* Pagination */}
      <div style={{ marginTop: '30px', display: 'flex', justifyContent: 'center' }}>
        <Pagination
          padding={2}
          showFirst={true}
          showLast={true}
          classNames={{
            root: 'pagination-root',
            list: 'pagination-list',
            item: 'pagination-item',
            selectedItem: 'pagination-item-selected',
            link: 'pagination-link',
          }}
        />
      </div>

      <style jsx>{`
        :global(.stats-text) {
          font-size: 0.95rem;
          color: #666;
        }

        :global(.sort-by-select) {
          padding: 8px 12px;
          border: 1px solid #e0e0e0;
          border-radius: 6px;
          font-size: 0.9rem;
          cursor: pointer;
          background: white;
        }

        :global(.hits-root) {
          margin: 0;
        }

        :global(.hit-item) {
          list-style: none;
        }

        :global(.pagination-list) {
          display: flex;
          list-style: none;
          gap: 8px;
        }

        :global(.pagination-item) {
          display: inline-block;
        }

        :global(.pagination-link) {
          display: block;
          padding: 8px 14px;
          border: 1px solid #e0e0e0;
          border-radius: 6px;
          text-decoration: none;
          color: #333;
          transition: all 0.2s;
        }

        :global(.pagination-link:hover) {
          background: #f5f5f5;
          border-color: #667eea;
          color: #667eea;
        }

        :global(.pagination-item-selected .pagination-link) {
          background: #667eea;
          color: white;
          border-color: #667eea;
        }
      `}</style>
    </div>
  );
}
