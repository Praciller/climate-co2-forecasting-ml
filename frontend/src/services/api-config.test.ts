import { describe, expect, it } from 'vitest'

import { resolveApiBase } from './api-config'

describe('resolveApiBase', () => {
  it('uses the local API during development by default', () => {
    expect(resolveApiBase({ PROD: false })).toBe('http://localhost:8000')
  })

  it('uses the same-origin API in production by default', () => {
    expect(resolveApiBase({ PROD: true })).toBe('/api')
  })

  it('gives an explicit API URL precedence in every mode', () => {
    expect(
      resolveApiBase({ PROD: true, VITE_API_URL: 'https://api.example.test/' }),
    ).toBe('https://api.example.test')
  })
})
