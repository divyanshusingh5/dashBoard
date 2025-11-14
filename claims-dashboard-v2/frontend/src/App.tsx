import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from './lib/api'

function App() {
  const [dbStatus, setDbStatus] = useState<any>(null)

  // Fetch health status
  useEffect(() => {
    api.get('/health')
      .then(res => setDbStatus(res.data))
      .catch(err => console.error('Health check failed:', err))
  }, [])

  // Fetch KPIs
  const { data: kpis, isLoading, error } = useQuery({
    queryKey: ['kpis'],
    queryFn: async () => {
      const response = await api.get('/api/v1/claims/kpis')
      return response.data
    },
  })

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8">
          <h1 className="text-4xl font-bold mb-2">
            Claims Analytics Dashboard v2.0
          </h1>
          <p className="text-gray-400">
            Dual database support • Clean architecture • Production ready
          </p>
        </header>

        {/* Status Card */}
        {dbStatus && (
          <div className="bg-gray-800 rounded-lg p-6 mb-8 border border-gray-700">
            <h2 className="text-xl font-semibold mb-4">System Status</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-gray-400 text-sm">Status</p>
                <p className="text-lg font-semibold">
                  {dbStatus.status === 'healthy' ? (
                    <span className="text-green-400">✅ Healthy</span>
                  ) : (
                    <span className="text-red-400">❌ Unhealthy</span>
                  )}
                </p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Database</p>
                <p className="text-lg font-semibold capitalize">
                  {dbStatus.database?.type}
                </p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Connection</p>
                <p className="text-lg font-semibold">
                  {dbStatus.database?.connected ? (
                    <span className="text-green-400">Connected</span>
                  ) : (
                    <span className="text-red-400">Disconnected</span>
                  )}
                </p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Version</p>
                <p className="text-lg font-semibold">{dbStatus.version}</p>
              </div>
            </div>
          </div>
        )}

        {/* KPIs Card */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-xl font-semibold mb-4">Key Performance Indicators</h2>

          {isLoading && (
            <p className="text-gray-400">Loading KPIs...</p>
          )}

          {error && (
            <p className="text-red-400">Error loading KPIs: {String(error)}</p>
          )}

          {kpis && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div>
                <p className="text-gray-400 text-sm mb-1">Total Claims</p>
                <p className="text-3xl font-bold">
                  {kpis.total_claims?.toLocaleString() || 0}
                </p>
              </div>
              <div>
                <p className="text-gray-400 text-sm mb-1">Avg Settlement</p>
                <p className="text-3xl font-bold">
                  ${(kpis.avg_settlement || 0).toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-gray-400 text-sm mb-1">Avg Days</p>
                <p className="text-3xl font-bold">
                  {Math.round(kpis.avg_days || 0)}
                </p>
              </div>
              <div>
                <p className="text-gray-400 text-sm mb-1">Avg Variance</p>
                <p className="text-3xl font-bold">
                  {(kpis.avg_variance || 0).toFixed(2)}%
                </p>
              </div>
              <div>
                <p className="text-gray-400 text-sm mb-1">High Variance</p>
                <p className="text-2xl font-bold text-yellow-400">
                  {(kpis.high_variance_pct || 0).toFixed(2)}%
                </p>
              </div>
              <div>
                <p className="text-gray-400 text-sm mb-1">Overprediction</p>
                <p className="text-2xl font-bold text-blue-400">
                  {(kpis.overprediction_rate || 0).toFixed(2)}%
                </p>
              </div>
              <div>
                <p className="text-gray-400 text-sm mb-1">Underprediction</p>
                <p className="text-2xl font-bold text-purple-400">
                  {(kpis.underprediction_rate || 0).toFixed(2)}%
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <footer className="mt-8 text-center text-gray-500 text-sm">
          <p>
            Claims Analytics Dashboard v2.0 • Built with FastAPI + React + {dbStatus?.database?.type || 'Database'}
          </p>
          <p className="mt-2">
            <a href="/docs" className="text-blue-400 hover:underline">API Documentation</a>
            {' • '}
            <a href="https://github.com/anthropics/claude-code" className="text-blue-400 hover:underline">
              Built with Claude Code
            </a>
          </p>
        </footer>
      </div>
    </div>
  )
}

export default App
