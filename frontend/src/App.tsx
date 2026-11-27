import { useEffect, useMemo, useState } from 'react'
import { listCubes, login, runQuery, setToken, type Cube } from './api'
import { MetricCard } from './components/MetricCard'
import { BarChart } from './components/BarChart'

const fmt = (n: number) => n.toLocaleString('en-US', { maximumFractionDigits: 0 })
const fmtMoney = (n: number) => 'BDT ' + n.toLocaleString('en-US', { maximumFractionDigits: 2 })

function LoginForm({ onLogin }: { onLogin: (u: string, p: string) => Promise<void> }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await onLogin(username, password)
    } catch (err) {
      setError(String(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="login">
      <h2>Sign in</h2>
      <p className="login-hint">
        bilab runs every query as you. Demo identities (lab Keycloak realm): ayesha.analyst
        (amounts masked) or rahim.engineer (full access).
      </p>
      <form onSubmit={submit}>
        <input
          placeholder="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoFocus
        />
        <input
          placeholder="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="submit" disabled={busy || !username || !password}>
          {busy ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
      {error && <div className="error">Login failed: {error}</div>}
    </div>
  )
}

export default function App() {
  const [signedIn, setSignedIn] = useState(false)
  const [cubes, setCubes] = useState<Cube[]>([])
  const [error, setError] = useState<string | null>(null)
  const [kpis, setKpis] = useState<Record<string, string>>({})
  const [channelData, setChannelData] = useState<Record<string, string>[]>([])
  const [dimension, setDimension] = useState('transactions.channel')
  const [exploreData, setExploreData] = useState<Record<string, string>[]>([])

  useEffect(() => {
    if (!signedIn) return
    listCubes().then(setCubes).catch((e) => setError(String(e)))
    runQuery({
      measures: ['transactions.total_amount', 'transactions.count', 'transactions.distinct_accounts'],
    })
      .then((d) => {
        const r = d[0]
        setKpis((k) => ({
          ...k,
          total_amount: fmtMoney(Number(r['transactions.total_amount'])),
          count: fmt(Number(r['transactions.count'])),
          accounts: fmt(Number(r['transactions.distinct_accounts'])),
        }))
      })
      .catch((e) => setError(String(e)))
    runQuery({ measures: ['branches.count'] })
      .then((d) => setKpis((k) => ({ ...k, branches: fmt(Number(d[0]['branches.count'])) })))
      .catch((e) => setError(String(e)))
    runQuery({ measures: ['transactions.count'], dimensions: ['transactions.channel'] })
      .then(setChannelData)
      .catch((e) => setError(String(e)))
  }, [signedIn])

  useEffect(() => {
    if (!signedIn) return
    runQuery({
      measures: ['transactions.count'],
      dimensions: [dimension],
      order: { 'transactions.count': 'desc' },
      limit: 5000,
    })
      .then(setExploreData)
      .catch((e) => setError(String(e)))
  }, [dimension, signedIn])

  const dimensions = useMemo(
    () => cubes.find((c) => c.name === 'transactions')?.dimensions ?? [],
    [cubes],
  )

  const handleLogin = async (u: string, p: string) => {
    await login(u, p)
    setSignedIn(true)
  }

  const handleLogout = () => {
    setToken(null)
    setSignedIn(false)
    setKpis({})
    setChannelData([])
    setExploreData([])
    setCubes([])
    setError(null)
  }

  if (!signedIn) {
    return (
      <div className="app">
        <header>
          <h1>bilab</h1>
          <span className="subtitle">semantic layer · live lab data</span>
        </header>
        <LoginForm onLogin={handleLogin} />
      </div>
    )
  }

  return (
    <div className="app">
      <header>
        <h1>bilab</h1>
        <span className="subtitle">semantic layer · live lab data</span>
        <button className="logout" onClick={handleLogout}>
          Sign out
        </button>
      </header>
      {error && <div className="error">Error: {error}</div>}

      <section className="kpis">
        <MetricCard label="Total amount" value={kpis.total_amount ?? '…'} />
        <MetricCard label="Transactions" value={kpis.count ?? '…'} />
        <MetricCard label="Distinct accounts" value={kpis.accounts ?? '…'} />
        <MetricCard label="Branches" value={kpis.branches ?? '…'} />
      </section>

      <section className="panel">
        <BarChart
          title="Transactions by channel"
          data={channelData}
          xKey="transactions.channel"
          yKey="transactions.count"
        />
      </section>

      <section className="panel">
        <h2>Explore</h2>
        <label className="explore-control">
          Dimension{' '}
          <select value={dimension} onChange={(e) => setDimension(e.target.value)}>
            {dimensions.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </label>
        <BarChart
          title={`Transactions by ${dimension.split('.').pop()}`}
          data={exploreData}
          xKey={dimension}
          yKey="transactions.count"
        />
      </section>
    </div>
  )
}
