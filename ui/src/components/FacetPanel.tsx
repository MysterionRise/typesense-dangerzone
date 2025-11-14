/**
 * FacetPanel Component
 * Displays faceted filters for refining search results
 */

import {
  RefinementList,
  RangeInput,
  ClearRefinements,
  CurrentRefinements,
} from 'react-instantsearch';

export default function FacetPanel() {
  return (
    <div>
      <h3>Filters</h3>

      {/* Current Refinements */}
      <div style={{ marginBottom: '20px' }}>
        <CurrentRefinements
          classNames={{
            root: 'current-refinements',
            list: 'refinements-list',
            item: 'refinement-item',
            label: 'refinement-label',
            delete: 'refinement-delete',
          }}
        />
      </div>

      {/* Clear All */}
      <div style={{ marginBottom: '20px' }}>
        <ClearRefinements
          translations={{
            resetButtonText: '🗑️ Clear All Filters',
          }}
          classNames={{
            root: 'clear-refinements',
            button: 'clear-button',
          }}
        />
      </div>

      {/* Brand Facet */}
      <div style={{ marginBottom: '25px' }}>
        <h4 style={{ marginBottom: '10px', fontSize: '0.95rem' }}>Brand</h4>
        <RefinementList
          attribute="brand"
          limit={8}
          showMore={true}
          showMoreLimit={20}
          searchable={true}
          searchablePlaceholder="Search brands..."
          classNames={{
            root: 'refinement-list',
            list: 'facet-list',
            item: 'facet-item',
            selectedItem: 'facet-item-selected',
            label: 'facet-label',
            checkbox: 'facet-checkbox',
            count: 'facet-count',
            showMore: 'facet-show-more',
          }}
        />
      </div>

      {/* Category Facet */}
      <div style={{ marginBottom: '25px' }}>
        <h4 style={{ marginBottom: '10px', fontSize: '0.95rem' }}>Category</h4>
        <RefinementList
          attribute="categories"
          limit={10}
          classNames={{
            root: 'refinement-list',
            list: 'facet-list',
            item: 'facet-item',
            selectedItem: 'facet-item-selected',
            label: 'facet-label',
            checkbox: 'facet-checkbox',
            count: 'facet-count',
          }}
        />
      </div>

      {/* Tags Facet */}
      <div style={{ marginBottom: '25px' }}>
        <h4 style={{ marginBottom: '10px', fontSize: '0.95rem' }}>Tags</h4>
        <RefinementList
          attribute="tags"
          limit={6}
          showMore={true}
          showMoreLimit={15}
          classNames={{
            root: 'refinement-list',
            list: 'facet-list',
            item: 'facet-item',
            selectedItem: 'facet-item-selected',
            label: 'facet-label',
            checkbox: 'facet-checkbox',
            count: 'facet-count',
            showMore: 'facet-show-more',
          }}
        />
      </div>

      {/* Price Range */}
      <div style={{ marginBottom: '25px' }}>
        <h4 style={{ marginBottom: '10px', fontSize: '0.95rem' }}>Price Range</h4>
        <RangeInput
          attribute="price"
          classNames={{
            root: 'range-input',
            form: 'range-form',
            input: 'range-input-field',
            submit: 'range-submit',
          }}
        />
      </div>

      {/* Availability */}
      <div style={{ marginBottom: '25px' }}>
        <h4 style={{ marginBottom: '10px', fontSize: '0.95rem' }}>Availability</h4>
        <RefinementList
          attribute="available"
          classNames={{
            root: 'refinement-list',
            list: 'facet-list',
            item: 'facet-item',
            selectedItem: 'facet-item-selected',
            label: 'facet-label',
            checkbox: 'facet-checkbox',
            count: 'facet-count',
          }}
        />
      </div>

      {/* Color */}
      <div style={{ marginBottom: '25px' }}>
        <h4 style={{ marginBottom: '10px', fontSize: '0.95rem' }}>Color</h4>
        <RefinementList
          attribute="color"
          limit={8}
          classNames={{
            root: 'refinement-list',
            list: 'facet-list',
            item: 'facet-item',
            selectedItem: 'facet-item-selected',
            label: 'facet-label',
            checkbox: 'facet-checkbox',
            count: 'facet-count',
          }}
        />
      </div>

      <style jsx>{`
        :global(.current-refinements) {
          font-size: 0.85rem;
        }

        :global(.refinements-list) {
          list-style: none;
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
        }

        :global(.refinement-item) {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          background: #e0e0f0;
          padding: 4px 10px;
          border-radius: 12px;
          font-size: 0.8rem;
        }

        :global(.refinement-delete) {
          background: none;
          border: none;
          cursor: pointer;
          font-size: 1rem;
          color: #666;
        }

        :global(.clear-button) {
          width: 100%;
          padding: 10px;
          background: #f5f5f5;
          border: 1px solid #e0e0e0;
          border-radius: 6px;
          cursor: pointer;
          font-size: 0.9rem;
          transition: all 0.2s;
        }

        :global(.clear-button:hover) {
          background: #e0e0e0;
        }

        :global(.facet-list) {
          list-style: none;
        }

        :global(.facet-item) {
          margin-bottom: 8px;
        }

        :global(.facet-item-selected) {
          font-weight: 600;
        }

        :global(.facet-label) {
          display: flex;
          align-items: center;
          cursor: pointer;
          font-size: 0.9rem;
        }

        :global(.facet-checkbox) {
          margin-right: 8px;
        }

        :global(.facet-count) {
          margin-left: auto;
          background: #f0f0f0;
          padding: 2px 8px;
          border-radius: 10px;
          font-size: 0.8rem;
          color: #666;
        }

        :global(.facet-show-more) {
          margin-top: 10px;
          background: none;
          border: none;
          color: #667eea;
          cursor: pointer;
          font-size: 0.85rem;
          font-weight: 600;
        }

        :global(.range-form) {
          display: flex;
          gap: 8px;
          align-items: center;
        }

        :global(.range-input-field) {
          width: 80px;
          padding: 6px 8px;
          border: 1px solid #e0e0e0;
          border-radius: 4px;
          font-size: 0.9rem;
        }

        :global(.range-submit) {
          padding: 6px 12px;
          background: #667eea;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.85rem;
        }
      `}</style>
    </div>
  );
}
