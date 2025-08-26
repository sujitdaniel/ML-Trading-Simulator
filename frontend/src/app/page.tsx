'use client'

import { useState, useEffect } from 'react'

interface Indicator {
  id: string
  name: string
  category: string
  description: string
  parameters: Parameter[]
}

interface Parameter {
  name: string
  type: 'number' | 'float' | 'integer'
  default: number
  min?: number
  max?: number
  step?: number
  description: string
}

interface BacktestConfig {
  ticker: string
  startDate: string
  endDate: string
  initialCapital: number
  strategyType: 'indicators' | 'ml' | 'hybrid'
  indicators: SelectedIndicator[]
  mlWeight?: number // Only for hybrid
  mlModel?: string // For ML/hybrid
}

interface SelectedIndicator {
  id: string
  name: string
  weight: number
  parameters: { [key: string]: number }
}

interface BacktestResult {
  ticker: string
  strategy: string
  dateRange: {
    start: string
    end: string
  }
  performance: {
    total_return?: number
    sharpe_ratio?: number
    max_drawdown?: number
    win_rate?: number
    total_trades?: number
    buy_trades?: number
    sell_trades?: number
    [key: string]: any
  }
  trades?: Array<{
    action: string
    date: string
    price: number
  }>
  ml_metrics?: { [key: string]: any }
}

// All available indicators with their parameters
const AVAILABLE_INDICATORS: Indicator[] = [
  {
    id: 'ma',
    name: 'Moving Average Crossover',
    category: 'Trend Following',
    description: 'Simple moving average crossover strategy',
    parameters: [
      { name: 'short_window', type: 'integer', default: 20, min: 5, max: 100, description: 'Short period' },
      { name: 'long_window', type: 'integer', default: 50, min: 10, max: 200, description: 'Long period' }
    ]
  },
  {
    id: 'rsi',
    name: 'Relative Strength Index',
    category: 'Momentum',
    description: 'Momentum oscillator measuring speed and magnitude of price changes',
    parameters: [
      { name: 'period', type: 'integer', default: 14, min: 5, max: 50, description: 'RSI period' },
      { name: 'overbought', type: 'integer', default: 70, min: 50, max: 90, description: 'Overbought threshold' },
      { name: 'oversold', type: 'integer', default: 30, min: 10, max: 50, description: 'Oversold threshold' }
    ]
  },
  {
    id: 'bollinger',
    name: 'Bollinger Bands',
    category: 'Volatility',
    description: 'Volatility indicator with upper and lower bands',
    parameters: [
      { name: 'window', type: 'integer', default: 20, min: 5, max: 100, description: 'Moving average period' },
      { name: 'num_std', type: 'float', default: 2.0, min: 0.5, max: 5.0, step: 0.1, description: 'Standard deviation multiplier' }
    ]
  },
  {
    id: 'macd',
    name: 'MACD',
    category: 'Trend Following',
    description: 'Moving Average Convergence Divergence',
    parameters: [
      { name: 'fast_period', type: 'integer', default: 12, min: 5, max: 50, description: 'Fast EMA period' },
      { name: 'slow_period', type: 'integer', default: 26, min: 10, max: 100, description: 'Slow EMA period' },
      { name: 'signal_period', type: 'integer', default: 9, min: 3, max: 20, description: 'Signal line period' }
    ]
  },
  {
    id: 'stochastic',
    name: 'Stochastic Oscillator',
    category: 'Momentum',
    description: 'Momentum oscillator comparing closing price to price range',
    parameters: [
      { name: 'k_period', type: 'integer', default: 14, min: 5, max: 50, description: '%K period' },
      { name: 'd_period', type: 'integer', default: 3, min: 1, max: 10, description: '%D period' },
      { name: 'overbought', type: 'integer', default: 80, min: 60, max: 95, description: 'Overbought threshold' },
      { name: 'oversold', type: 'integer', default: 20, min: 5, max: 40, description: 'Oversold threshold' }
    ]
  },
  {
    id: 'williams_r',
    name: 'Williams %R',
    category: 'Momentum',
    description: 'Momentum oscillator measuring overbought/oversold levels',
    parameters: [
      { name: 'period', type: 'integer', default: 14, min: 5, max: 50, description: 'Lookback period' },
      { name: 'overbought', type: 'integer', default: -20, min: -50, max: -10, description: 'Overbought threshold' },
      { name: 'oversold', type: 'integer', default: -80, min: -90, max: -50, description: 'Oversold threshold' }
    ]
  },
  {
    id: 'ema',
    name: 'Exponential Moving Average',
    category: 'Trend Following',
    description: 'Trend-following indicator using exponential moving averages',
    parameters: [
      { name: 'short_period', type: 'integer', default: 12, min: 5, max: 50, description: 'Short EMA period' },
      { name: 'long_period', type: 'integer', default: 26, min: 10, max: 100, description: 'Long EMA period' }
    ]
  },
  {
    id: 'vwap',
    name: 'VWAP',
    category: 'Volume',
    description: 'Volume Weighted Average Price for fair value assessment',
    parameters: [
      { name: 'period', type: 'integer', default: 20, min: 5, max: 100, description: 'Calculation period' }
    ]
  },
  {
    id: 'atr',
    name: 'Average True Range',
    category: 'Volatility',
    description: 'Volatility indicator for stop-loss and position sizing',
    parameters: [
      { name: 'period', type: 'integer', default: 14, min: 5, max: 50, description: 'ATR period' },
      { name: 'multiplier', type: 'float', default: 2.0, min: 0.5, max: 5.0, step: 0.1, description: 'Band multiplier' }
    ]
  },
  {
    id: 'fibonacci',
    name: 'Fibonacci Retracement',
    category: 'Support/Resistance',
    description: 'Support/resistance levels based on Fibonacci ratios',
    parameters: [
      { name: 'period', type: 'integer', default: 20, min: 10, max: 100, description: 'Swing calculation period' },
      { name: 'retracement_level', type: 'float', default: 0.618, min: 0.236, max: 0.786, step: 0.001, description: 'Fibonacci level' }
    ]
  }
]

export default function Home() {
  const [config, setConfig] = useState<BacktestConfig>({
    ticker: '',
    startDate: '',
    endDate: '',
    initialCapital: 10000,
    strategyType: 'indicators',
    indicators: [],
    mlWeight: 0.5,
    mlModel: 'logistic',
  })
  const [result, setResult] = useState<BacktestResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string>('All')

  // Set default date range (last 6 months)
  useEffect(() => {
    const endDate = new Date()
    const startDate = new Date()
    startDate.setMonth(endDate.getMonth() - 6)
    
    setConfig(prev => ({
      ...prev,
      startDate: startDate.toISOString().split('T')[0],
      endDate: endDate.toISOString().split('T')[0]
    }))
  }, [])

  const categories = ['All', ...Array.from(new Set(AVAILABLE_INDICATORS.map(ind => ind.category)))]

  const filteredIndicators = selectedCategory === 'All' 
    ? AVAILABLE_INDICATORS 
    : AVAILABLE_INDICATORS.filter(ind => ind.category === selectedCategory)

  const addIndicator = (indicator: Indicator) => {
    if (config.indicators.length >= 3) {
      setError('Maximum 3 indicators allowed')
      return
    }

    const defaultParams: { [key: string]: number } = {}
    indicator.parameters.forEach(param => {
      defaultParams[param.name] = param.default
    })

    const newIndicator: SelectedIndicator = {
      id: indicator.id,
      name: indicator.name,
      weight: 1.0 / (config.indicators.length + 1),
      parameters: defaultParams
    }

    setConfig(prev => ({
      ...prev,
      indicators: [...prev.indicators, newIndicator]
    }))
    setError(null)
  }

  const removeIndicator = (index: number) => {
    setConfig(prev => ({
      ...prev,
      indicators: prev.indicators.filter((_, i) => i !== index)
    }))
  }

  const updateIndicatorWeight = (index: number, weight: number) => {
    setConfig(prev => ({
      ...prev,
      indicators: prev.indicators.map((ind, i) => 
        i === index ? { ...ind, weight } : ind
      )
    }))
  }

  const updateIndicatorParameter = (indicatorIndex: number, paramName: string, value: number) => {
    setConfig(prev => ({
      ...prev,
      indicators: prev.indicators.map((ind, i) => 
        i === indicatorIndex 
          ? { ...ind, parameters: { ...ind.parameters, [paramName]: value } }
          : ind
      )
    }))
  }

  const normalizeWeights = () => {
    let totalWeight = config.indicators.reduce((sum, ind) => sum + ind.weight, 0)
    if (config.strategyType === 'hybrid') {
      totalWeight += config.mlWeight || 0
    }
    if (totalWeight > 0) {
      setConfig(prev => ({
        ...prev,
        indicators: prev.indicators.map(ind => ({
          ...ind,
          weight: ind.weight / totalWeight
        })),
        mlWeight: prev.mlWeight !== undefined ? (prev.mlWeight / totalWeight) : prev.mlWeight
      }))
    }
  }

  const ML_MODELS = [
    { value: 'logistic', label: 'Logistic Regression' },
    { value: 'random_forest', label: 'Random Forest' },
    { value: 'xgboost', label: 'XGBoost' },
    { value: 'gradient_boosting', label: 'Gradient Boosting' },
    { value: 'svm', label: 'Support Vector Machine (SVM)' },
    { value: 'knn', label: 'K-Nearest Neighbors (KNN)' },
    { value: 'lstm', label: 'LSTM (Deep Learning)' },
  ];

  const handleBacktest = async () => {
    if (!config.ticker.trim()) {
      setError('Please enter a valid ticker symbol')
      return
    }

    // Validate indicators only for indicator/hybrid strategy
    if ((config.strategyType === 'indicators' || config.strategyType === 'hybrid') && config.indicators.length === 0) {
      setError('Please select at least one indicator')
      return
    }

    if (!config.startDate || !config.endDate) {
      setError('Please select start and end dates')
      return
    }

    if (new Date(config.startDate) >= new Date(config.endDate)) {
      setError('Start date must be before end date')
      return
    }

    // Normalize weights before sending (only for indicator/hybrid strategy)
    if (config.strategyType === 'indicators' || config.strategyType === 'hybrid') {
      normalizeWeights()
    }
    
    setLoading(true)
    setError(null)
    setResult(null)
    
    try {
      let strategy = 'ma'
      if (config.strategyType === 'ml') strategy = 'ml'
      if (config.strategyType === 'hybrid') strategy = 'hybrid'

      const requestBody: any = {
        ticker: config.ticker.toUpperCase(),
        start_date: config.startDate,
        end_date: config.endDate,
        initial_capital: config.initialCapital,
        indicators: (config.strategyType === 'indicators' || config.strategyType === 'hybrid') ? config.indicators : []
      }
      if (config.strategyType === 'hybrid') {
        requestBody.ml_weight = config.mlWeight
      }
      if (config.strategyType === 'ml' || config.strategyType === 'hybrid') {
        requestBody.ml_model = config.mlModel || 'logistic'
      }

      // Import API configuration
      const { apiRequest } = await import('../config/api');
      
      console.log('🌐 Making API request to backend...');
      console.log('📤 Request body:', requestBody);
      
      const res = await apiRequest(`/backtest?strategy=${strategy}`, {
        method: 'POST',
        body: JSON.stringify(requestBody)
      })
      
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP error! status: ${res.status}`)
      }
      
      const data = await res.json()
      setResult(data)
    } catch (err) {
      console.error('Backtest error:', err);
      
      let errorMessage = 'Failed to run backtest. Please check your connection and try again.';
      
      if (err instanceof Error) {
        if (err.message === 'Failed to fetch') {
          errorMessage = 'Failed to connect to the backend API. Please ensure the backend server is running on http://localhost:8000';
        } else {
          errorMessage = err.message;
        }
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false)
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
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-4 tracking-tight">
              ⚡ ALGONEX
            </h1>
            <p className="text-xl md:text-2xl text-blue-200 font-light">
              Advanced Algorithmic Trading Platform
            </p>
            <div className="mt-2 h-1 w-24 bg-gradient-to-r from-blue-400 to-cyan-400 mx-auto rounded-full"></div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        <div className="grid gap-8 lg:grid-cols-3">
          
          {/* Configuration Panel */}
          <div className="lg:col-span-2 space-y-6">
            


            {/* Strategy Selection */}
            <div className="backdrop-blur-xl bg-white/10 rounded-2xl border border-white/20 shadow-2xl p-6">
              <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
                <span className="mr-3">🎯</span>
                Strategy Selection
              </h2>
              
              <div className="grid gap-4 md:grid-cols-3 mb-6">
                <div className="bg-white/5 rounded-lg p-4 border border-white/10 hover:border-blue-400/50 transition-all duration-200">
                  <label className="flex items-center cursor-pointer">
                    <input
                      type="radio"
                      name="strategy"
                      value="indicators"
                      checked={config.strategyType === 'indicators'}
                      onChange={(e) => setConfig(prev => ({ ...prev, strategyType: e.target.value as 'indicators' | 'ml' | 'hybrid' }))}
                      className="mr-3 text-blue-500 focus:ring-blue-400"
                    />
                    <div>
                      <div className="text-white font-medium">Indicator Strategy</div>
                      <div className="text-blue-300/60 text-sm">Traditional technical indicators</div>
                    </div>
                  </label>
                </div>
                
                <div className="bg-white/5 rounded-lg p-4 border border-white/10 hover:border-blue-400/50 transition-all duration-200">
                  <label className="flex items-center cursor-pointer">
                    <input
                      type="radio"
                      name="strategy"
                      value="ml"
                      checked={config.strategyType === 'ml'}
                      onChange={(e) => setConfig(prev => ({ ...prev, strategyType: e.target.value as 'indicators' | 'ml' | 'hybrid' }))}
                      className="mr-3 text-blue-500 focus:ring-blue-400"
                    />
                    <div>
                      <div className="text-white font-medium">Machine Learning Strategy</div>
                      <div className="text-blue-300/60 text-sm">AI-powered logistic regression</div>
                    </div>
                  </label>
                </div>

                <div className="bg-white/5 rounded-lg p-4 border border-white/10 hover:border-blue-400/50 transition-all duration-200">
                  <label className="flex items-center cursor-pointer">
                    <input
                      type="radio"
                      name="strategy"
                      value="hybrid"
                      checked={config.strategyType === 'hybrid'}
                      onChange={(e) => setConfig(prev => ({ ...prev, strategyType: e.target.value as 'indicators' | 'ml' | 'hybrid' }))}
                      className="mr-3 text-blue-500 focus:ring-blue-400"
                    />
                    <div>
                      <div className="text-white font-medium">Hybrid (ML + Indicators)</div>
                      <div className="text-blue-300/60 text-sm">Combine ML and indicator signals</div>
                    </div>
                  </label>
                </div>
              </div>
            </div>

            {/* Basic Settings */}
            <div className="backdrop-blur-xl bg-white/10 rounded-2xl border border-white/20 shadow-2xl p-6">
              <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
                <span className="mr-3">⚙️</span>
                Basic Settings
              </h2>
              
              <div className="grid gap-4 md:grid-cols-4">
                <div>
                  <label className="block text-sm font-medium text-blue-200 mb-2">
                    Stock Ticker
                  </label>
                  <input
                    type="text"
                    value={config.ticker}
                    onChange={(e) => setConfig(prev => ({ ...prev, ticker: e.target.value.toUpperCase() }))}
                    placeholder="AAPL, MSFT, GOOGL"
                    className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-blue-300/60 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all duration-200"
                    disabled={loading}
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-blue-200 mb-2">
                    Start Date
                  </label>
                  <input
                    type="date"
                    value={config.startDate}
                    onChange={(e) => setConfig(prev => ({ ...prev, startDate: e.target.value }))}
                    className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all duration-200"
                    disabled={loading}
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-blue-200 mb-2">
                    End Date
                  </label>
                  <input
                    type="date"
                    value={config.endDate}
                    onChange={(e) => setConfig(prev => ({ ...prev, endDate: e.target.value }))}
                    className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all duration-200"
                    disabled={loading}
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-blue-200 mb-2">
                    Initial Capital ($)
                  </label>
                  <input
                    type="number"
                    min="100"
                    step="100"
                    value={config.initialCapital}
                    onChange={(e) => setConfig(prev => ({ ...prev, initialCapital: parseFloat(e.target.value) || 10000 }))}
                    className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all duration-200"
                    disabled={loading}
                  />
                </div>
              </div>
            </div>

            {/* Indicator Selection - Only show for indicator or hybrid strategy */}
            {(config.strategyType === 'indicators' || config.strategyType === 'hybrid') && (
              <div className="backdrop-blur-xl bg-white/10 rounded-2xl border border-white/20 shadow-2xl p-6">
                <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
                  <span className="mr-3">📊</span>
                  Indicator Selection ({config.indicators.length}/3)
                </h2>
              
              {/* Category Filter */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-blue-200 mb-2">
                  Filter by Category
                </label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full md:w-64 px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all duration-200"
                >
                  {categories.map(category => (
                    <option key={category} value={category}>{category}</option>
                  ))}
                </select>
              </div>

              {/* Available Indicators */}
              <div className="grid gap-3 md:grid-cols-2">
                {filteredIndicators.map(indicator => (
                  <div key={indicator.id} className="bg-white/5 rounded-lg p-4 border border-white/10 hover:border-blue-400/50 transition-all duration-200">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h3 className="text-white font-medium">{indicator.name}</h3>
                        <p className="text-blue-300/60 text-sm">{indicator.category}</p>
                      </div>
                      <button
                        onClick={() => addIndicator(indicator)}
                        disabled={config.indicators.length >= 3 || config.indicators.some(ind => ind.id === indicator.id)}
                        className="px-3 py-1 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-600 text-white text-sm rounded-lg transition-colors duration-200 disabled:cursor-not-allowed"
                      >
                        {config.indicators.some(ind => ind.id === indicator.id) ? 'Added' : 'Add'}
                      </button>
                    </div>
                    <p className="text-blue-200/80 text-xs">{indicator.description}</p>
                  </div>
                ))}
              </div>
            </div>
            )}

            {/* Selected Indicators Configuration - Only show for indicator or hybrid strategy */}
            {(config.strategyType === 'indicators' || config.strategyType === 'hybrid') && config.indicators.length > 0 && (
              <div className="backdrop-blur-xl bg-white/10 rounded-2xl border border-white/20 shadow-2xl p-6">
                <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
                  <span className="mr-3">🔧</span>
                  Strategy Configuration
                </h2>
                
                <div className="space-y-4">
                  {config.indicators.map((indicator, index) => {
                    const indicatorDef = AVAILABLE_INDICATORS.find(ind => ind.id === indicator.id)!
                    return (
                      <div key={index} className="bg-white/5 rounded-lg p-4 border border-white/10">
                        <div className="flex justify-between items-center mb-3">
                          <h3 className="text-white font-medium">{indicator.name}</h3>
                          <button
                            onClick={() => removeIndicator(index)}
                            className="text-red-400 hover:text-red-300 transition-colors duration-200"
                          >
                            ✕ Remove
                          </button>
                        </div>
                        
                        {/* Weight Slider */}
                        <div className="mb-3">
                          <label className="block text-sm font-medium text-blue-200 mb-2">
                            Weight: {indicator.weight.toFixed(2)}
                          </label>
                          <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.01"
                            value={indicator.weight}
                            onChange={(e) => updateIndicatorWeight(index, parseFloat(e.target.value))}
                            className="w-full h-2 bg-white/20 rounded-lg appearance-none cursor-pointer slider"
                          />
                        </div>
                        
                        {/* Parameters */}
                        <div className="grid gap-3 md:grid-cols-2">
                          {indicatorDef.parameters.map(param => (
                            <div key={param.name}>
                              <label className="block text-sm font-medium text-blue-200 mb-1">
                                {param.description}
                              </label>
                              <input
                                type={param.type === 'float' ? 'number' : 'number'}
                                min={param.min}
                                max={param.max}
                                step={param.step || 1}
                                value={indicator.parameters[param.name]}
                                onChange={(e) => updateIndicatorParameter(index, param.name, parseFloat(e.target.value))}
                                className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all duration-200"
                              />
                            </div>
                          ))}
                        </div>
                      </div>
                    )
                  })}
                </div>
                
                <button
                  onClick={normalizeWeights}
                  className="mt-4 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white text-sm rounded-lg transition-colors duration-200"
                >
                  Normalize Weights
                </button>
              </div>
            )}

            {/* ML Weight Slider - Only show for hybrid strategy */}
            {config.strategyType === 'hybrid' && (
              <div className="backdrop-blur-xl bg-white/10 rounded-2xl border border-white/20 shadow-2xl p-6">
                <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
                  <span className="mr-3">🤖</span>
                  ML Signal Weight
                </h2>
                <div className="mb-3">
                  <label className="block text-sm font-medium text-blue-200 mb-2">
                    ML Model
                  </label>
                  <select
                    value={config.mlModel}
                    onChange={e => setConfig(prev => ({ ...prev, mlModel: e.target.value }))}
                    className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all duration-200 mb-2"
                  >
                    {ML_MODELS.map(model => (
                      <option key={model.value} value={model.value}>{model.label}</option>
                    ))}
                  </select>
                </div>
                <div className="mb-3">
                  <label className="block text-sm font-medium text-blue-200 mb-2">
                    ML Weight: {config.mlWeight?.toFixed(2)}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={config.mlWeight}
                    onChange={(e) => setConfig(prev => ({ ...prev, mlWeight: parseFloat(e.target.value) }))}
                    className="w-full h-2 bg-white/20 rounded-lg appearance-none cursor-pointer slider"
                  />
                </div>
                <button
                  onClick={normalizeWeights}
                  className="mt-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white text-sm rounded-lg transition-colors duration-200"
                >
                  Normalize All Weights
                </button>
              </div>
            )}

            {/* ML Strategy Info - Only show for ML strategy */}
            {config.strategyType === 'ml' && (
              <div className="backdrop-blur-xl bg-white/10 rounded-2xl border border-white/20 shadow-2xl p-6">
                <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
                  <span className="mr-3">🤖</span>
                  Machine Learning Strategy
                </h2>
                <div className="mb-3">
                  <label className="block text-sm font-medium text-blue-200 mb-2">
                    ML Model
                  </label>
                  <select
                    value={config.mlModel}
                    onChange={e => setConfig(prev => ({ ...prev, mlModel: e.target.value }))}
                    className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all duration-200 mb-2"
                  >
                    {ML_MODELS.map(model => (
                      <option key={model.value} value={model.value}>{model.label}</option>
                    ))}
                  </select>
                </div>
                <div className="bg-gradient-to-r from-purple-500/20 to-blue-500/20 rounded-lg p-4 border border-purple-400/30">
                  <div className="text-blue-200 text-sm mb-3">
                    <strong>Model: {ML_MODELS.find(m => m.value === config.mlModel)?.label || 'Logistic Regression'}</strong>
                  </div>
                  <ul className="text-blue-300/80 text-sm space-y-2">
                    <li>• Uses price returns as features</li>
                    <li>• Predicts buy/sell signals based on historical patterns</li>
                    <li>• Automatically trained on your selected date range</li>
                    <li>• No manual parameter configuration required</li>
                    <li>• Time series split preserves temporal order</li>
                  </ul>
                </div>
              </div>
            )}

            {/* Run Backtest Button */}
            <button
              onClick={handleBacktest}
              disabled={loading || !config.ticker.trim() || (config.strategyType === 'indicators' && config.indicators.length === 0)}
              className="w-full px-6 py-4 bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 disabled:from-gray-500 disabled:to-gray-600 text-white font-semibold rounded-xl transition-all duration-200 transform hover:scale-105 disabled:transform-none disabled:cursor-not-allowed shadow-lg"
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

          {/* Results Panel */}
          <div className="backdrop-blur-xl bg-white/10 rounded-2xl border border-white/20 shadow-2xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
              <span className="mr-3">📈</span>
              Performance Results
            </h2>
            
            {result ? (
              <div className="space-y-4">
                {/* Header Info */}
                <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-blue-200 text-sm">Ticker</span>
                      <span className="text-white font-bold">{result.ticker}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-blue-200 text-sm">Strategy</span>
                      <span className="text-white font-semibold">{result.strategy}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-blue-200 text-sm">Period</span>
                      <span className="text-white text-sm">
                        {new Date(result.dateRange.start).toLocaleDateString()} - {new Date(result.dateRange.end).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Performance Metrics */}
                <div className="space-y-3">
                  {/* Key Metrics */}
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-white/5 rounded-lg p-3 border border-white/10">
                      <div className="text-blue-200 text-xs font-medium mb-1">Total Return</div>
                      <div className={`font-bold ${(result.performance.total_return || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {formatMetric(result.performance.total_return || 0, 'percentage')}
                      </div>
                    </div>
                    <div className="bg-white/5 rounded-lg p-3 border border-white/10">
                      <div className="text-blue-200 text-xs font-medium mb-1">Win Rate</div>
                      <div className="text-white font-bold">
                        {formatMetric(result.performance.win_rate, 'percentage')}
                      </div>
                    </div>
                  </div>
                  {/* ML Model Metrics Card */}
                  {result.ml_metrics && (
                    <div className="bg-gradient-to-r from-purple-800/40 to-blue-800/40 rounded-xl border border-purple-400/30 shadow-lg p-5 mt-2">
                      <div className="mb-2">
                        <h2 className="text-xl font-bold text-purple-200 flex items-center mb-1">
                          <span className="mr-2">🤖</span> ML Model Metrics
                        </h2>
                        <div className="text-blue-200 text-sm">Logistic Regression Performance</div>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-blue-100 text-sm mb-2">
                        <div>Train Accuracy: <span className="font-semibold text-white">{formatMetric(result.ml_metrics.train_accuracy, 'percentage')}</span></div>
                        <div>Test Accuracy: <span className="font-semibold text-white">{formatMetric(result.ml_metrics.test_accuracy, 'percentage')}</span></div>
                        <div>Precision: <span className="font-semibold text-white">{formatMetric(result.ml_metrics.precision, 'percentage')}</span></div>
                        <div>Recall: <span className="font-semibold text-white">{formatMetric(result.ml_metrics.recall, 'percentage')}</span></div>
                      </div>
                      <div className="text-blue-200 text-xs font-medium mb-1 mt-2">Confusion Matrix</div>
                      <div className="grid grid-cols-2 gap-2 text-blue-100 text-xs">
                        <div>TP: <span className="font-semibold text-white">{result.ml_metrics.confusion_matrix?.[0]?.[0]}</span></div>
                        <div>FP: <span className="font-semibold text-white">{result.ml_metrics.confusion_matrix?.[0]?.[1]}</span></div>
                        <div>FN: <span className="font-semibold text-white">{result.ml_metrics.confusion_matrix?.[1]?.[0]}</span></div>
                        <div>TN: <span className="font-semibold text-white">{result.ml_metrics.confusion_matrix?.[1]?.[1]}</span></div>
                      </div>
                    </div>
                  )}
                  
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-white/5 rounded-lg p-3 border border-white/10">
                      <div className="text-blue-200 text-xs font-medium mb-1">Sharpe Ratio</div>
                      <div className="text-white font-bold">
                        {formatMetric(result.performance.sharpe_ratio, 'ratio')}
                      </div>
                    </div>
                    <div className="bg-white/5 rounded-lg p-3 border border-white/10">
                      <div className="text-blue-200 text-xs font-medium mb-1">Max Drawdown</div>
                      <div className="text-red-400 font-bold">
                        {formatMetric(result.performance.max_drawdown, 'percentage')}
                      </div>
                    </div>
                  </div>
                  
                  {/* Portfolio Metrics */}
                  <div className="bg-gradient-to-r from-green-500/20 to-blue-500/20 rounded-lg p-3 border border-green-400/30">
                    <div className="text-blue-200 text-xs font-medium mb-1">Portfolio Performance</div>
                    <div className="space-y-1">
                      <div className="flex justify-between">
                        <span className="text-blue-200 text-sm">Initial Capital:</span>
                        <span className="text-white font-semibold">${result.performance.initial_capital?.toLocaleString() || 'N/A'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-blue-200 text-sm">Final Value:</span>
                        <span className="text-white font-semibold">${result.performance.final_portfolio_value?.toLocaleString() || 'N/A'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-blue-200 text-sm">Profit/Loss:</span>
                        <span className={`font-semibold ${result.performance.total_profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          ${result.performance.total_profit_loss?.toLocaleString() || 'N/A'}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Trade Summary */}
                  <div className="bg-white/5 rounded-lg p-3 border border-white/10">
                    <div className="text-blue-200 text-xs font-medium mb-2">Trade Summary</div>
                    <div className="grid grid-cols-3 gap-2 text-center">
                      <div>
                        <div className="text-white font-bold">{result.performance.total_trades || 0}</div>
                        <div className="text-blue-200 text-xs">Total</div>
                      </div>
                      <div>
                        <div className="text-green-400 font-bold">{result.performance.buy_trades || 0}</div>
                        <div className="text-blue-200 text-xs">Buy</div>
                      </div>
                      <div>
                        <div className="text-red-400 font-bold">{result.performance.sell_trades || 0}</div>
                        <div className="text-blue-200 text-xs">Sell</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Trades Summary */}
                {result.trades && result.trades.length > 0 && (
                  <details className="bg-white/5 rounded-lg border border-white/10">
                    <summary className="p-3 text-blue-200 font-medium cursor-pointer hover:text-white transition-colors">
                      📋 Recent Trades ({result.trades.length})
                    </summary>
                    <div className="p-3 border-t border-white/10 max-h-40 overflow-y-auto">
                      {result.trades.slice(-5).map((trade, index) => (
                        <div key={index} className="flex justify-between items-center py-1 text-sm">
                          <span className={`font-medium ${trade.action === 'BUY' ? 'text-green-400' : 'text-red-400'}`}>
                            {trade.action}
                          </span>
                          <span className="text-blue-200">
                            {new Date(trade.date).toLocaleDateString()}
                          </span>
                          <span className="text-white">
                            ${trade.price.toFixed(2)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </details>
                )}

                {/* Raw Data Toggle */}
                <details className="bg-white/5 rounded-lg border border-white/10">
                  <summary className="p-3 text-blue-200 font-medium cursor-pointer hover:text-white transition-colors">
                    📋 View Raw Data
                  </summary>
                  <div className="p-3 border-t border-white/10">
                    <pre className="text-xs text-blue-100 bg-black/20 rounded-lg p-3 overflow-x-auto max-h-40 overflow-y-auto">
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
                  Configure your strategy and run a backtest to see performance metrics
                </p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 py-8 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <p className="text-blue-300/60 text-sm">
              Built with ❤️ by <span className="text-blue-400 font-semibold">ALGONEX</span>
            </p>
            <p className="text-blue-300/40 text-xs mt-1">
              Advanced Algorithmic Trading Platform with 20+ Technical Indicators
            </p>
          </div>
        </div>
      </footer>

      {/* Custom CSS for slider */}
      <style jsx>{`
        .slider::-webkit-slider-thumb {
          appearance: none;
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: #3b82f6;
          cursor: pointer;
        }
        .slider::-moz-range-thumb {
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: #3b82f6;
          cursor: pointer;
          border: none;
        }
      `}</style>
    </div>
  )
}
