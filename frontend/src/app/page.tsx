'use client'

import { useState } from 'react'

interface BacktestResult {
  ticker: string
  strategy: string
  performance: {
    total_return?: number
    sharpe_ratio?: number
    max_drawdown?: number
    win_rate?: number
    total_trades?: number
    [key: string]: any
  }
}

export default function Home() {
  const [ticker, setTicker] = useState('')
  const [result, setResult] = useState<BacktestResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleBacktest = async () => {
    if (!ticker.trim()) {
      setError('Please enter a valid ticker symbol')
      return
    }
    
    setLoading(true)
    setError(null)
    setResult(null)
    
    try {
      const res = await fetch(`http://127.0.0.1:8000/backtest/${ticker.toUpperCase()}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`)
      }
      
      const data = await res.json()
      setResult(data)
    } catch (err) {
      setError('Failed to run backtest. Please check your connection and try again.')
      console.error('Backtest error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !loading) {
      handleBacktest()
    }
  }

  const formatMetric = (value: any, type: 'percentage' | 'number' | 'ratio' = 'number') => {
    if (value === null || value === undefined) return 'N/A'
    
    switch (type) {
      case 'percentage':
        return `${(value * 100).toFixed(2)}%`
      case 'ratio':
        return value.toFixed(3)
      default:
        return typeof value === 'number' ? value.toFixed(2) : value.toString()
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header Section */}
      <header className="relative z-10 pt-8 pb-6">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-4 tracking-tight">
              ⚡ ALGONEX
            </h1>
            <p className="text-xl md:text-2xl text-blue-200 font-light">
              Algorithmic Trading Platform
            </p>
            <div className="mt-2 h-1 w-24 bg-gradient-to-r from-blue-400 to-cyan-400 mx-auto rounded-full"></div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        <div className="grid gap-8 lg:grid-cols-2">
          
          {/* Backtest Panel */}
          <div className="backdrop-blur-xl bg-white/10 rounded-2xl border border-white/20 shadow-2xl p-8">
            <h2 className="text-2xl font-semibold text-white mb-6 flex items-center">
              <span className="mr-3">📊</span>
              Backtest Strategy
            </h2>
            
            <div className="space-y-6">
              <div>
                <label htmlFor="ticker" className="block text-sm font-medium text-blue-200 mb-2">
                  Stock Ticker
                </label>
                <input
                  id="ticker"
                  type="text"
                  value={ticker}
                  onChange={(e) => setTicker(e.target.value.toUpperCase())}
                  onKeyPress={handleKeyPress}
                  placeholder="Enter ticker (e.g., AAPL, MSFT, GOOGL)"
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-blue-300/60 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all duration-200"
                  disabled={loading}
                />
              </div>
              
              <button
                onClick={handleBacktest}
                disabled={loading || !ticker.trim()}
                className="w-full px-6 py-3 bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 disabled:from-gray-500 disabled:to-gray-600 text-white font-semibold rounded-xl transition-all duration-200 transform hover:scale-105 disabled:transform-none disabled:cursor-not-allowed shadow-lg"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Running Backtest...
                  </span>
                ) : (
                  '🚀 Run Backtest'
                )}
              </button>
              
              {error && (
                <div className="p-4 bg-red-500/20 border border-red-400/30 rounded-xl text-red-200 text-sm">
                  ⚠️ {error}
                </div>
              )}
            </div>
          </div>

          {/* Results Panel */}
          <div className="backdrop-blur-xl bg-white/10 rounded-2xl border border-white/20 shadow-2xl p-8">
            <h2 className="text-2xl font-semibold text-white mb-6 flex items-center">
              <span className="mr-3">📈</span>
              Performance Results
            </h2>
            
            {result ? (
              <div className="space-y-6">
                {/* Header Info */}
                <div className="bg-white/5 rounded-xl p-4 border border-white/10">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-blue-200 font-medium">Ticker</span>
                    <span className="text-white font-bold text-lg">{result.ticker}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-blue-200 font-medium">Strategy</span>
                    <span className="text-white font-semibold">{result.strategy}</span>
                  </div>
                </div>

                {/* Performance Metrics */}
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(result.performance).map(([key, value]) => (
                    <div key={key} className="bg-white/5 rounded-xl p-4 border border-white/10">
                      <div className="text-blue-200 text-sm font-medium mb-1 capitalize">
                        {key.replace(/_/g, ' ')}
                      </div>
                      <div className="text-white font-bold text-lg">
                        {formatMetric(value, 
                          key.includes('return') || key.includes('rate') ? 'percentage' :
                          key.includes('ratio') ? 'ratio' : 'number'
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Raw Data Toggle */}
                <details className="bg-white/5 rounded-xl border border-white/10">
                  <summary className="p-4 text-blue-200 font-medium cursor-pointer hover:text-white transition-colors">
                    📋 View Raw Data
                  </summary>
                  <div className="p-4 border-t border-white/10">
                    <pre className="text-xs text-blue-100 bg-black/20 rounded-lg p-3 overflow-x-auto">
                      {JSON.stringify(result, null, 2)}
                    </pre>
                  </div>
                </details>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-64 text-center">
                <div className="text-6xl mb-4">📊</div>
                <p className="text-blue-200 text-lg mb-2">No Results Yet</p>
                <p className="text-blue-300/60 text-sm">
                  Enter a ticker symbol and run a backtest to see performance metrics
                </p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 py-8 mt-8">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <p className="text-blue-300/60 text-sm">
              Built with ❤️ by <span className="text-blue-400 font-semibold">ALGONEX</span>
            </p>
            <p className="text-blue-300/40 text-xs mt-1">
              Advanced Algorithmic Trading Platform
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
