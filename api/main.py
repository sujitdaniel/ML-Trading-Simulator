from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import os
import pandas as pd
from datetime import datetime, date
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.fetch_data import data_fetcher

# Add parent directory to path to import strategies module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.engine import TradingEngine, StrategyBuilder

app = FastAPI(
    title="Algonex API",
    description="Advanced Algorithmic Trading Platform API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class IndicatorParameter(BaseModel):
    name: str
    value: float

class SelectedIndicator(BaseModel):
    id: str
    name: str
    weight: float
    parameters: Dict[str, float]

class BacktestRequest(BaseModel):
    ticker: str
    start_date: str
    end_date: str
    initial_capital: float = 10000.0
    indicators: List[SelectedIndicator]
    ml_weight: Optional[float] = None  # For hybrid strategy
    ml_model: Optional[str] = 'logistic'  # For ML/hybrid strategy

class Trade(BaseModel):
    action: str
    date: str
    price: float

class BacktestResponse(BaseModel):
    ticker: str
    strategy: str
    dateRange: Dict[str, str]
    performance: Dict[str, Any]
    trades: Optional[List[Trade]] = None
    ml_metrics: Optional[Dict[str, Any]] = None

# Available indicators configuration
AVAILABLE_INDICATORS = {
    'ma': {
        'name': 'Moving Average Crossover',
        'category': 'Trend Following',
        'description': 'Simple moving average crossover strategy'
    },
    'rsi': {
        'name': 'Relative Strength Index',
        'category': 'Momentum',
        'description': 'Momentum oscillator measuring speed and magnitude of price changes'
    },
    'bollinger': {
        'name': 'Bollinger Bands',
        'category': 'Volatility',
        'description': 'Volatility indicator with upper and lower bands'
    },
    'mean_reversion': {
        'name': 'Mean Reversion',
        'category': 'Mean Reversion',
        'description': 'Statistical arbitrage based on mean reversion'
    },
    'mfi': {
        'name': 'Money Flow Index',
        'category': 'Volume',
        'description': 'Volume-based momentum oscillator'
    },
    'sar': {
        'name': 'Parabolic SAR',
        'category': 'Trend Following',
        'description': 'Trend-following stop and reverse indicator'
    },
    'cmo': {
        'name': 'Chande Momentum Oscillator',
        'category': 'Momentum',
        'description': 'Momentum oscillator measuring overbought/oversold conditions'
    },
    'stochastic': {
        'name': 'Stochastic Oscillator',
        'category': 'Momentum',
        'description': 'Momentum oscillator comparing closing price to price range'
    },
    'williams_r': {
        'name': 'Williams %R',
        'category': 'Momentum',
        'description': 'Momentum oscillator measuring overbought/oversold levels'
    },
    'macd': {
        'name': 'MACD',
        'category': 'Trend Following',
        'description': 'Moving Average Convergence Divergence'
    },
    'obv': {
        'name': 'On-Balance Volume',
        'category': 'Volume',
        'description': 'Volume-based indicator measuring buying/selling pressure'
    },
    'ema': {
        'name': 'Exponential Moving Average',
        'category': 'Trend Following',
        'description': 'Trend-following indicator using exponential moving averages'
    },
    'vwap': {
        'name': 'VWAP',
        'category': 'Volume',
        'description': 'Volume Weighted Average Price for fair value assessment'
    },
    'atr': {
        'name': 'Average True Range',
        'category': 'Volatility',
        'description': 'Volatility indicator for stop-loss and position sizing'
    },
    'ibs': {
        'name': 'Internal Bar Strength',
        'category': 'Support/Resistance',
        'description': 'Measures position of close within the bar\'s range'
    },
    'fibonacci': {
        'name': 'Fibonacci Retracement',
        'category': 'Support/Resistance',
        'description': 'Support/resistance levels based on Fibonacci ratios'
    },
    'ppo': {
        'name': 'Percentage Price Oscillator',
        'category': 'Trend Following',
        'description': 'MACD variant expressed as percentage'
    },
    'adx': {
        'name': 'Average Directional Index',
        'category': 'Trend Following',
        'description': 'Measures trend strength regardless of direction'
    },
    'std': {
        'name': 'Standard Deviation',
        'category': 'Volatility',
        'description': 'Volatility-based bands using standard deviation'
    },
    'rvi': {
        'name': 'Relative Volatility Index',
        'category': 'Volatility',
        'description': 'Volatility-based oscillator'
    }
}

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Algonex API",
        "version": "1.0.0",
        "description": "Advanced Algorithmic Trading Platform",
        "endpoints": {
            "/indicators": "Get all available indicators",
            "/backtest": "Run backtest with custom strategy",
            "/health": "Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/indicators")
async def get_indicators():
    """Get all available indicators with their configurations."""
    return {
        "indicators": AVAILABLE_INDICATORS,
        "total_count": len(AVAILABLE_INDICATORS),
        "categories": list(set(ind['category'] for ind in AVAILABLE_INDICATORS.values()))
    }

@app.post("/backtest", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest, strategy: str = "ma"):
    """
    Run a backtest with custom indicator configuration.
    
    Args:
        request: BacktestRequest containing ticker, date range, and indicators
        
    Returns:
        BacktestResponse with performance metrics and trade history
    """
    try:
        # ML model dispatch map
        from ml.logistic_model import generate_ml_signals_logistic
        from ml.random_forest_model import generate_ml_signals_random_forest
        from ml.xgboost_model import generate_ml_signals_xgboost
        from ml.gradient_boosting_model import generate_ml_signals_gradient_boosting
        from ml.svm_model import generate_ml_signals_svm
        from ml.knn_model import generate_ml_signals_knn
        from ml.lstm_model import generate_ml_signals_lstm
        ML_MODEL_MAP = {
            'logistic': generate_ml_signals_logistic,
            'random_forest': generate_ml_signals_random_forest,
            'xgboost': generate_ml_signals_xgboost,
            'gradient_boosting': generate_ml_signals_gradient_boosting,
            'svm': generate_ml_signals_svm,
            'knn': generate_ml_signals_knn,
            'lstm': generate_ml_signals_lstm,
        }
        ml_model = getattr(request, 'ml_model', 'logistic') or 'logistic'
        ml_func = ML_MODEL_MAP.get(ml_model, generate_ml_signals_logistic)
        # Validate request - Skip indicator validation for ML strategy
        if strategy not in ("ml", "hybrid"):
            if not request.indicators:
                raise HTTPException(status_code=400, detail="At least one indicator is required")
            
            if len(request.indicators) > 3:
                raise HTTPException(status_code=400, detail="Maximum 3 indicators allowed")
        if strategy == "hybrid":
            if not request.indicators:
                raise HTTPException(status_code=400, detail="At least one indicator is required for hybrid strategy")
            if len(request.indicators) > 3:
                raise HTTPException(status_code=400, detail="Maximum 3 indicators allowed for hybrid strategy")
            if not hasattr(request, 'ml_weight') and 'ml_weight' not in request.__dict__:
                raise HTTPException(status_code=400, detail="ml_weight is required for hybrid strategy")
        
        # Validate date range
        try:
            start_date = datetime.strptime(request.start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(request.end_date, "%Y-%m-%d").date()
            
            if start_date >= end_date:
                raise HTTPException(status_code=400, detail="Start date must be before end date")
                
            # Remove old date restrictions since we now fetch data dynamically
            # The data fetcher will handle date validation
                
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Validate ticker
        if not request.ticker or len(request.ticker) > 10:
            raise HTTPException(status_code=400, detail="Invalid ticker symbol")
        
        # Validate initial capital
        if request.initial_capital <= 0:
            raise HTTPException(status_code=400, detail="Initial capital must be greater than 0")
        
        # Handle ML and Hybrid strategies
        if strategy == "ml":
            # Pass the ML function to TradingEngine
            strategy_obj = None
        elif strategy == "hybrid":
            # Prepare indicator types, weights, and parameters
            indicator_types = [ind.id for ind in request.indicators]
            indicator_weights = [ind.weight for ind in request.indicators]
            ml_weight = getattr(request, 'ml_weight', None)
            if ml_weight is None:
                ml_weight = request.__dict__.get('ml_weight', 0.5)
            # Collect indicator parameters
            kwargs = {}
            for i, ind in enumerate(request.indicators):
                for key, value in ind.parameters.items():
                    prefix = f"ind{i+1}_"
                    if any(int_keyword in key.lower() for int_keyword in ['period', 'window', 'length', 'days', 'bars']):
                        kwargs[prefix + key] = int(value)
                    else:
                        kwargs[prefix + key] = float(value)
            strategy_obj = StrategyBuilder.create_hybrid_ml_indicator_strategy(
                indicator_types=indicator_types,
                indicator_weights=indicator_weights,
                ml_weight=ml_weight,
                signal_threshold=0.5,
                require_confirmation=True,
                ml_func=ml_func,
                **kwargs
            )
        else:
            # Create strategy based on number of indicators
            strategy_obj = None
            
            if len(request.indicators) == 1:
                indicator = request.indicators[0]
                
                # Convert parameters to proper types
                converted_params = {}
                for key, value in indicator.parameters.items():
                    # Convert to int if the parameter name suggests it should be an integer
                    if any(int_keyword in key.lower() for int_keyword in ['period', 'window', 'length', 'days', 'bars']):
                        converted_params[key] = int(value)
                    else:
                        converted_params[key] = float(value)
                
                strategy_obj = StrategyBuilder.create_single_indicator_strategy(
                    indicator.id, **converted_params
                )
            elif len(request.indicators) == 2:
                ind1, ind2 = request.indicators
                
                # Convert parameters to proper types
                ind1_params = {}
                ind2_params = {}
                
                for key, value in ind1.parameters.items():
                    if any(int_keyword in key.lower() for int_keyword in ['period', 'window', 'length', 'days', 'bars']):
                        ind1_params[f"ind1_{key}"] = int(value)
                    else:
                        ind1_params[f"ind1_{key}"] = float(value)
                
                for key, value in ind2.parameters.items():
                    if any(int_keyword in key.lower() for int_keyword in ['period', 'window', 'length', 'days', 'bars']):
                        ind2_params[f"ind2_{key}"] = int(value)
                    else:
                        ind2_params[f"ind2_{key}"] = float(value)
                
                strategy_obj = StrategyBuilder.create_dual_indicator_strategy(
                    ind1.id, ind2.id,
                    weight1=ind1.weight, weight2=ind2.weight,
                    **ind1_params,
                    **ind2_params
                )
            else:  # 3 indicators
                ind1, ind2, ind3 = request.indicators
                
                # Convert parameters to proper types
                ind1_params = {}
                ind2_params = {}
                ind3_params = {}
                
                for key, value in ind1.parameters.items():
                    if any(int_keyword in key.lower() for int_keyword in ['period', 'window', 'length', 'days', 'bars']):
                        ind1_params[f"ind1_{key}"] = int(value)
                    else:
                        ind1_params[f"ind1_{key}"] = float(value)
                
                for key, value in ind2.parameters.items():
                    if any(int_keyword in key.lower() for int_keyword in ['period', 'window', 'length', 'days', 'bars']):
                        ind2_params[f"ind2_{key}"] = int(value)
                    else:
                        ind2_params[f"ind2_{key}"] = float(value)
                
                for key, value in ind3.parameters.items():
                    if any(int_keyword in key.lower() for int_keyword in ['period', 'window', 'length', 'days', 'bars']):
                        ind3_params[f"ind3_{key}"] = int(value)
                    else:
                        ind3_params[f"ind3_{key}"] = float(value)
                
                strategy_obj = StrategyBuilder.create_triple_indicator_strategy(
                    ind1.id, ind2.id, ind3.id,
                    weight1=ind1.weight, weight2=ind2.weight, weight3=ind3.weight,
                    **ind1_params,
                    **ind2_params,
                    **ind3_params
                )
        
        # Fetch data for the requested date range
        try:
            data_file = data_fetcher.fetch_data_for_date_range(
                request.ticker, 
                request.start_date, 
                request.end_date
            )
        except Exception as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to fetch data for {request.ticker}: {str(e)}"
            )
        
        # Create trading engine with dynamic data and initial capital
        engine = TradingEngine(
            strategy_obj, 
            request.ticker, 
            data_file=data_file,
            initial_capital=request.initial_capital,
            ml_func=ml_func if strategy == 'ml' else None
        )
        
        trades = engine.run(strategy_type=strategy)
        summary = engine.get_trade_summary()
        signals = engine.get_signals()
        
        # Create strategy description
        if strategy == "ml":
            strategy_description = "Machine Learning (Logistic Regression)"
        elif strategy == "hybrid":
            indicator_names = [ind.name for ind in request.indicators]
            strategy_description = f"Hybrid: ML + ({' + '.join(indicator_names)})"
        else:
            indicator_names = [ind.name for ind in request.indicators]
            strategy_description = " + ".join(indicator_names)
        
        # Calculate real performance metrics
        performance_metrics = engine.calculate_performance_metrics()
        performance = {
            "total_trades": summary.get("total_trades", 0),
            "buy_trades": summary.get("buy_trades", 0),
            "sell_trades": summary.get("sell_trades", 0),
            "win_rate": performance_metrics.get("win_rate", 0.0),
            "total_return": performance_metrics.get("total_return", 0.0),
            "sharpe_ratio": performance_metrics.get("sharpe_ratio", 0.0),
            "max_drawdown": performance_metrics.get("max_drawdown", 0.0),
            "initial_capital": request.initial_capital,
            "final_portfolio_value": performance_metrics.get("final_portfolio_value", request.initial_capital),
            "total_profit_loss": performance_metrics.get("total_profit_loss", 0.0),
        }
        
        # Convert trades to response format
        trade_list = []
        for trade in trades:
            trade_list.append(Trade(
                action=trade[0],
                date=trade[1].isoformat(),
                price=trade[2]
            ))
        
        # Clean up temporary data files
        data_fetcher.cleanup_temp_files()
        
        return BacktestResponse(
            ticker=request.ticker.upper(),
            strategy=strategy_description,
            dateRange={
                "start": request.start_date,
                "end": request.end_date
            },
            performance=performance,
            trades=trade_list,
            ml_metrics=engine.get_ml_metrics() if strategy in ("ml", "hybrid") else None
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Data not found for ticker {request.ticker}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Backtest error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during backtest")

@app.get("/backtest/{ticker}")
async def run_simple_backtest(ticker: str, strategy: str = "ma"):
    """
    Simple backtest endpoint for testing ML strategy.
    
    Args:
        ticker: Stock ticker symbol
        strategy: Strategy type ("ma" for Moving Average, "ml" for Machine Learning)
        
    Returns:
        BacktestResponse with performance metrics
    """
    try:
        # Validate ticker
        if not ticker or len(ticker) > 10:
            raise HTTPException(status_code=400, detail="Invalid ticker symbol")
        
        # Use default date range for simple testing
        start_date = "2022-01-01"
        end_date = "2023-01-01"
        initial_capital = 10000.0
        
        # Fetch data
        try:
            data_file = data_fetcher.fetch_data_for_date_range(
                ticker, start_date, end_date
            )
        except Exception as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to fetch data for {ticker}: {str(e)}"
            )
        
        # Create strategy object (None for ML, default for MA)
        if strategy == "ml":
            strategy_obj = None
            strategy_description = "Machine Learning (Logistic Regression)"
        else:
            strategy_obj = StrategyBuilder.create_default_strategy()
            strategy_description = "Moving Average Crossover"
        
        # Create trading engine
        engine = TradingEngine(
            strategy_obj, 
            ticker, 
            data_file=data_file,
            initial_capital=initial_capital
        )
        
        trades = engine.run(strategy_type=strategy)
        summary = engine.get_trade_summary()
        performance_metrics = engine.calculate_performance_metrics()
        
        performance = {
            "total_trades": summary.get("total_trades", 0),
            "buy_trades": summary.get("buy_trades", 0),
            "sell_trades": summary.get("sell_trades", 0),
            "win_rate": performance_metrics.get("win_rate", 0.0),
            "total_return": performance_metrics.get("total_return", 0.0),
            "sharpe_ratio": performance_metrics.get("sharpe_ratio", 0.0),
            "max_drawdown": performance_metrics.get("max_drawdown", 0.0),
            "initial_capital": initial_capital,
            "final_portfolio_value": performance_metrics.get("final_portfolio_value", initial_capital),
            "total_profit_loss": performance_metrics.get("total_profit_loss", 0.0),
        }
        
        # Convert trades to response format
        trade_list = []
        for trade in trades:
            trade_list.append(Trade(
                action=trade[0],
                date=trade[1].isoformat(),
                price=trade[2]
            ))
        
        # Clean up temporary data files
        data_fetcher.cleanup_temp_files()
        
        return BacktestResponse(
            ticker=ticker.upper(),
            strategy=strategy_description,
            dateRange={
                "start": start_date,
                "end": end_date
            },
            performance=performance,
            trades=trade_list
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Data not found for ticker {ticker}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Backtest error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during backtest")

@app.get("/available-tickers")
async def get_available_tickers():
    """Get list of available tickers for backtesting."""
    try:
        tickers = data_fetcher.get_available_tickers()
        return {
            "tickers": tickers,
            "count": len(tickers)
        }
    except Exception as e:
        return {
            "tickers": ["AAPL", "MSFT", "GOOGL", "TSLA", "META"],  # Fallback
            "count": 5,
            "note": "Using fallback tickers due to data access error"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

