// Learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom'

// Mock environment variables
process.env.NEXT_PUBLIC_TYPESENSE_HOST = 'localhost'
process.env.NEXT_PUBLIC_TYPESENSE_PORT = '8108'
process.env.NEXT_PUBLIC_TYPESENSE_PROTOCOL = 'http'
process.env.NEXT_PUBLIC_TYPESENSE_SEARCH_ONLY_API_KEY = 'test_key'
