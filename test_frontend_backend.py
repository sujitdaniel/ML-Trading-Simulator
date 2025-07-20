#!/usr/bin/env python3
"""Test script to verify frontend-backend integration."""

import requests
import json
from datetime import datetime, timedelta

def test_api_endpoints():
    """Test all API endpoints."""
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing Algonex API Endpoints\n")
    
    # Test 1: Health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("   ✅ Health check passed")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: Get indicators
    print("\n2. Testing indicators endpoint...")
    try:
        response = requests.get(f"{base_url}/indicators")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {data['total_count']} indicators")
            print(f"   ✅ Categories: {', '.join(data['categories'])}")
        else:
            print(f"   ❌ Indicators endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Indicators endpoint error: {e}")
    
    # Test 3: Get available tickers
    print("\n3. Testing available tickers...")
    try:
        response = requests.get(f"{base_url}/available-tickers")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {data['count']} tickers")
            print(f"   ✅ Tickers: {', '.join(data['tickers'][:5])}...")
        else:
            print(f"   ❌ Tickers endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Tickers endpoint error: {e}")
    
    # Test 4: Test backtest with single indicator
    print("\n4. Testing backtest with RSI...")
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        backtest_request = {
            "ticker": "AAPL",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "indicators": [
                {
                    "id": "rsi",
                    "name": "Relative Strength Index",
                    "weight": 1.0,
                    "parameters": {
                        "period": 14,
                        "overbought": 70,
                        "oversold": 30
                    }
                }
            ]
        }
        
        response = requests.post(
            f"{base_url}/backtest",
            json=backtest_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Backtest completed successfully")
            print(f"   ✅ Strategy: {data['strategy']}")
            print(f"   ✅ Total trades: {data['performance']['total_trades']}")
            print(f"   ✅ Buy trades: {data['performance']['buy_trades']}")
            print(f"   ✅ Sell trades: {data['performance']['sell_trades']}")
        else:
            print(f"   ❌ Backtest failed: {response.status_code}")
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Backtest error: {e}")
    
    # Test 5: Test backtest with dual indicators
    print("\n5. Testing backtest with RSI + MACD...")
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        backtest_request = {
            "ticker": "AAPL",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "indicators": [
                {
                    "id": "rsi",
                    "name": "Relative Strength Index",
                    "weight": 0.5,
                    "parameters": {
                        "period": 14,
                        "overbought": 70,
                        "oversold": 30
                    }
                },
                {
                    "id": "macd",
                    "name": "MACD",
                    "weight": 0.5,
                    "parameters": {
                        "fast_period": 12,
                        "slow_period": 26,
                        "signal_period": 9
                    }
                }
            ]
        }
        
        response = requests.post(
            f"{base_url}/backtest",
            json=backtest_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Dual indicator backtest completed")
            print(f"   ✅ Strategy: {data['strategy']}")
            print(f"   ✅ Total trades: {data['performance']['total_trades']}")
        else:
            print(f"   ❌ Dual indicator backtest failed: {response.status_code}")
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Dual indicator backtest error: {e}")
    
    # Test 6: Test error handling
    print("\n6. Testing error handling...")
    try:
        # Test with invalid ticker
        backtest_request = {
            "ticker": "INVALID_TICKER",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "indicators": [
                {
                    "id": "rsi",
                    "name": "Relative Strength Index",
                    "weight": 1.0,
                    "parameters": {"period": 14}
                }
            ]
        }
        
        response = requests.post(
            f"{base_url}/backtest",
            json=backtest_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 404:
            print("   ✅ Invalid ticker error handled correctly")
        else:
            print(f"   ⚠️ Unexpected response for invalid ticker: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error handling test failed: {e}")

def test_frontend_config():
    """Test frontend configuration format."""
    print("\n🧪 Testing Frontend Configuration\n")
    
    # Sample frontend configuration
    frontend_config = {
        "ticker": "AAPL",
        "startDate": "2023-01-01",
        "endDate": "2023-12-31",
        "indicators": [
            {
                "id": "rsi",
                "name": "Relative Strength Index",
                "weight": 0.6,
                "parameters": {
                    "period": 14,
                    "overbought": 70,
                    "oversold": 30
                }
            },
            {
                "id": "macd",
                "name": "MACD",
                "weight": 0.4,
                "parameters": {
                    "fast_period": 12,
                    "slow_period": 26,
                    "signal_period": 9
                }
            }
        ]
    }
    
    print("✅ Frontend configuration format:")
    print(json.dumps(frontend_config, indent=2))
    
    # Test conversion to backend format
    backend_request = {
        "ticker": frontend_config["ticker"],
        "start_date": frontend_config["startDate"],
        "end_date": frontend_config["endDate"],
        "indicators": frontend_config["indicators"]
    }
    
    print("\n✅ Backend request format:")
    print(json.dumps(backend_request, indent=2))

if __name__ == "__main__":
    print("🚀 Algonex Frontend-Backend Integration Test\n")
    print("=" * 50)
    
    # Test API endpoints
    test_api_endpoints()
    
    # Test frontend configuration
    test_frontend_config()
    
    print("\n" + "=" * 50)
    print("✅ Integration test completed!")
    print("\n📋 Next steps:")
    print("1. Start the backend: python api/main.py")
    print("2. Start the frontend: cd frontend && npm run dev")
    print("3. Open http://localhost:3000 in your browser")
    print("4. Test the indicator selection and backtesting features") 