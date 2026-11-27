export interface Cube {
  name: string
  title: string
  description: string
  measures: string[]
  dimensions: string[]
}

let token: string | null = null

export function setToken(t: string | null) {
  token = t
}

export function getToken() {
  return token
}

export async function login(username: string, password: string): Promise<string> {
  const r = await fetch('/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  if (!r.ok) throw new Error(`login failed (${r.status})`)
  const j = await r.json()
  token = j.token
  return j.token
}

function authHeaders(): Record<string, string> {
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function listCubes(): Promise<Cube[]> {
  const r = await fetch('/api/cubes', { headers: authHeaders() })
  if (!r.ok) throw new Error(`cubes: ${r.status}`)
  return r.json()
}

export async function runQuery(query: Record<string, unknown>): Promise<Record<string, string>[]> {
  const r = await fetch('/api/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ query }),
  })
  if (!r.ok) throw new Error(`query: ${r.status}`)
  const j = await r.json()
  return j.data
}
