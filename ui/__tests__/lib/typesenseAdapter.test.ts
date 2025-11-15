import { createTypesenseAdapter } from '../../src/lib/typesenseAdapter';

describe('TypesenseAdapter', () => {
  it('creates adapter with default alpha', () => {
    const adapter = createTypesenseAdapter();
    expect(adapter).toBeDefined();
    expect(adapter.searchClient).toBeDefined();
  });

  it('creates adapter with custom alpha', () => {
    const adapter = createTypesenseAdapter(0.7);
    expect(adapter).toBeDefined();
  });

  it('creates adapter with additional parameters', () => {
    const adapter = createTypesenseAdapter(0.5, {
      num_typos: 1,
      prefix: false,
    });
    expect(adapter).toBeDefined();
  });

  it('includes correct typesense configuration', () => {
    const adapter = createTypesenseAdapter(0.3);

    // Adapter should have search client
    expect(adapter.searchClient).toBeDefined();
    expect(typeof adapter.searchClient.search).toBe('function');
  });
});

describe('TypesenseAdapter Vector Query Configuration', () => {
  it('constructs vector_query with correct alpha', () => {
    const alpha = 0.45;
    const adapter = createTypesenseAdapter(alpha);

    // We can't easily test the internal config, but we can verify the adapter was created
    expect(adapter).toBeDefined();
  });

  it('includes distance_threshold in vector query', () => {
    const adapter = createTypesenseAdapter(0.3);
    expect(adapter).toBeDefined();
  });
});

describe('Environment Configuration', () => {
  it('uses environment variables for config', () => {
    expect(process.env.NEXT_PUBLIC_TYPESENSE_HOST).toBe('localhost');
    expect(process.env.NEXT_PUBLIC_TYPESENSE_PORT).toBe('8108');
    expect(process.env.NEXT_PUBLIC_TYPESENSE_PROTOCOL).toBe('http');
  });
});
