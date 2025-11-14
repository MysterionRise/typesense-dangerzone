/**
 * HybridSearch Component
 * Search box with query suggestions (autocomplete)
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { SearchBox } from 'react-instantsearch';
import { getQuerySuggestions } from '../lib/api';

export default function HybridSearch() {
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  // Fetch suggestions based on input
  const fetchSuggestions = useCallback(async (query: string) => {
    if (query.length < 2) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    try {
      const results = await getQuerySuggestions(query);
      setSuggestions(results);
      setShowSuggestions(results.length > 0);
    } catch (error) {
      console.error('Error fetching suggestions:', error);
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, []);

  // Debounced suggestions fetch
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (suggestionsRef.current && !suggestionsRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div style={{ position: 'relative' }} ref={suggestionsRef}>
      <SearchBox
        placeholder="Search products... (e.g., trail running shoes, nike jacket, waterproof)"
        searchAsYouType={true}
        onInput={(e) => {
          const query = (e.target as HTMLInputElement).value;
          fetchSuggestions(query);
        }}
        onKeyDown={(e) => {
          if (e.key === 'ArrowDown') {
            e.preventDefault();
            setSelectedIndex((prev) => Math.min(prev + 1, suggestions.length - 1));
          } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            setSelectedIndex((prev) => Math.max(prev - 1, -1));
          } else if (e.key === 'Enter' && selectedIndex >= 0) {
            e.preventDefault();
            const suggestion = suggestions[selectedIndex];
            (e.target as HTMLInputElement).value = suggestion;
            setShowSuggestions(false);
          } else if (e.key === 'Escape') {
            setShowSuggestions(false);
          }
        }}
        classNames={{
          root: 'search-box-root',
          form: 'search-box-form',
          input: 'search-box-input',
          submit: 'search-box-submit',
          reset: 'search-box-reset',
        }}
      />

      {/* Query Suggestions Dropdown */}
      {showSuggestions && suggestions.length > 0 && (
        <div className="suggestions-dropdown">
          {suggestions.map((suggestion, index) => (
            <div
              key={suggestion}
              className={`suggestion-item ${index === selectedIndex ? 'selected' : ''}`}
              onClick={() => {
                const input = document.querySelector('.search-box-input') as HTMLInputElement;
                if (input) {
                  input.value = suggestion;
                  input.dispatchEvent(new Event('input', { bubbles: true }));
                }
                setShowSuggestions(false);
              }}
              style={{
                background: index === selectedIndex ? '#f0f0f0' : 'transparent',
              }}
            >
              🔍 {suggestion}
            </div>
          ))}
        </div>
      )}

      <style jsx>{`
        :global(.search-box-root) {
          width: 100%;
        }

        :global(.search-box-form) {
          display: flex;
          gap: 8px;
        }

        :global(.search-box-input) {
          flex: 1;
          padding: 14px 20px;
          font-size: 1rem;
          border: 2px solid #e0e0e0;
          border-radius: 8px;
          outline: none;
          transition: all 0.2s;
        }

        :global(.search-box-input:focus) {
          border-color: #667eea;
          box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        :global(.search-box-submit) {
          padding: 14px 24px;
          background: #667eea;
          color: white;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-weight: 600;
          transition: background 0.2s;
        }

        :global(.search-box-submit:hover) {
          background: #5568d3;
        }

        :global(.search-box-reset) {
          padding: 14px 20px;
          background: #e0e0e0;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          transition: background 0.2s;
        }

        :global(.search-box-reset:hover) {
          background: #d0d0d0;
        }
      `}</style>
    </div>
  );
}
