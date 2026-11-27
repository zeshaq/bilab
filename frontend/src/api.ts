export interface Cube {
  name: string
  title: string
  description: string
  measures: string[]
  dimensions: string[]
}

export async function listCubes(): Promise<Cube[]> {
  const r = await fetch('/api/cubes')
  if (!r.ok) throw new Error(`cubes: ${r.status}`)
  return r.json()
}

export async function runQuery(query: Record<string, unknown>): Promise<Record<string, string>[]> {
  const r = await fetch('/api/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  })
  if (!r.ok) throw new Error(`query: ${r.status}`)
  const j = await r.json()
  return j.data
}
