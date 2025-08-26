#!/usr/bin/env python3
"""Test script to verify API connection from frontend perspective."""

import requests
import json
from datetime import datetime, timedelta

def test_frontend_backend_connection():
    """Test the exact endpoint the frontend is trying to connect to."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Frontend-Backend Connection\n")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check passed: {data}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: Test the exact backtest endpoint the frontend uses
    print("\n2. Testing backtest endpoint (exact frontend request)...")
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        # This is the exact request format the frontend sends
        backtest_request = {
            "ticker": "AAPL",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "initial_capital": 10000.0,
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
        
        # Test with strategy=indicators (what frontend uses)
        response = requests.post(
            f"{base_url}/backtest?strategy=indicators",
            json=backtest_request,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   📡 Request URL: {base_url}/backtest?strategy=indicators")
        print(f"   📤 Request body: {json.dumps(backtest_request, indent=2)}")
        print(f"   📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Backtest successful!")
            print(f"   ✅ Strategy: {data.get('strategy', 'N/A')}")
            print(f"   ✅ Performance: {data.get('performance', {}).get('total_trades', 'N/A')} trades")
        else:
            print(f"   ❌ Backtest failed: {response.status_code}")
            print(f"   ❌ Error response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Backtest error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Test CORS headers
    print("\n3. Testing CORS headers...")
    try:
        response = requests.options(f"{base_url}/backtest")
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        print(f"   📋 CORS Headers: {cors_headers}")
        
        if response.headers.get('Access-Control-Allow-Origin') == '*':
            print("   ✅ CORS is properly configured")
        else:
            print("   ⚠️ CORS might be restricted")
            
    except Exception as e:
        print(f"   ❌ CORS test error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Connection test completed!")
    
    if base_url == "http://localhost:8000":
        print("\n🔍 Frontend should be connecting to: http://localhost:8000")
        print("🌐 Frontend is running on: http://localhost:3000")
        print("📱 Backend is running on: http://localhost:8000")
        print("\n💡 If you're still getting 'Failed to fetch':")
        print("   1. Check browser console for CORS errors")
        print("   2. Verify the frontend is using the correct API URL")
        print("   3. Check if there are any network errors in browser dev tools")

if __name__ == "__main__":
    test_frontend_backend_connection() 