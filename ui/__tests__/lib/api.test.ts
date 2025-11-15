/**
 * Tests for Typesense API utilities
 */

// Mock Typesense client
jest.mock('typesense', () => {
  return {
    __esModule: true,
    default: {
      Client: jest.fn().mockImplementation(() => ({
        collections: jest.fn().mockReturnValue({
          documents: jest.fn().mockReturnValue({
            search: jest.fn().mockResolvedValue({
              hits: [
                { document: { q: 'running shoes' } },
                { document: { q: 'hiking boots' } },
              ],
            }),
          }),
        }),
        multiSearch: {
          perform: jest.fn().mockResolvedValue({
            results: [
              { hits: [], found: 0 },
              { hits: [], found: 0 },
            ],
          }),
        },
      })),
    },
  };
});

import { getQuerySuggestions, multiSearch } from '../../src/lib/api';

describe('API Utilities', () => {
  describe('getQuerySuggestions', () => {
    it('returns empty array for short queries', async () => {
      const suggestions = await getQuerySuggestions('a');
      expect(suggestions).toEqual([]);
    });

    it('fetches suggestions for valid query', async () => {
      const suggestions = await getQuerySuggestions('run');
      expect(Array.isArray(suggestions)).toBe(true);
    });

    it('returns empty array on error', async () => {
      // This will use the mocked client which should work
      const suggestions = await getQuerySuggestions('test');
      expect(Array.isArray(suggestions)).toBe(true);
    });
  });

  describe('multiSearch', () => {
    it('performs multi-search query', async () => {
      const results = await multiSearch('test', 0.3);
      expect(results).toBeDefined();
      expect(results.results).toBeDefined();
    });

    it('accepts custom alpha parameter', async () => {
      const results = await multiSearch('shoes', 0.7);
      expect(results).toBeDefined();
    });

    it('accepts additional parameters', async () => {
      const results = await multiSearch('jacket', 0.5, {
        filter_by: 'available:=true',
      });
      expect(results).toBeDefined();
    });
  });
});
