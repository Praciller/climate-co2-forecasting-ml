export interface ApiEnvironment {
  VITE_API_URL?: string
  PROD: boolean
}

export function resolveApiBase(env: ApiEnvironment): string {
  const explicit = env.VITE_API_URL?.trim()
  if (explicit) return explicit.replace(/\/+$/, '')
  return env.PROD ? '/api' : 'http://localhost:8000'
}
