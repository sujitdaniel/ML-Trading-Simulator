#!/usr/bin/env python3
"""Data fetching service for dynamic date ranges."""

import yfinance as yf
import pandas as pd
from pathlib import Path
import os
from datetime import datetime, date
import tempfile
import shutil

class DataFetcher:
    """Service to fetch and manage stock data for specific date ranges."""
    
    def __init__(self, data_dir: str = "./data/temp"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.temp_files = []
    
    def fetch_data_for_date_range(self, ticker: str, start_date: str, end_date: str) -> str:
        """
        Fetch data for a specific ticker and date range.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Path to the temporary CSV file
        """
        try:
            print(f"📥 Fetching data for {ticker} from {start_date} to {end_date}")
            
            # Convert dates
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            # Add buffer days to ensure we get enough data for indicators
            buffer_days = 100  # Extra days for indicator calculations
            fetch_start = start_dt.replace(day=max(1, start_dt.day - buffer_days))
            
            # Fetch data using yfinance
            stock = yf.Ticker(ticker)
            data = stock.history(start=fetch_start, end=end_dt, interval="1d")
            
            if data.empty:
                raise ValueError(f"No data available for {ticker} in the specified date range")
            
            # Convert timezone-aware index to timezone-naive for comparison
            data.index = data.index.tz_localize(None)
            
            # Filter to exact date range
            data = data[(data.index >= start_dt) & (data.index <= end_dt)]
            
            if data.empty:
                raise ValueError(f"No data available for {ticker} between {start_date} and {end_date}")
            
            # Create temporary file
            temp_file = self.data_dir / f"{ticker}_{start_date}_{end_date}.csv"
            
            # Save data in the expected format (matching the old format)
            with open(temp_file, 'w') as f:
                # Write header rows to match existing format
                f.write("Price,Close,High,Low,Open,Volume\n")
                f.write(f"Ticker,{ticker},{ticker},{ticker},{ticker},{ticker}\n")
                f.write("Date,,,,,\n")
                
                # Write the data
                data.to_csv(f, header=False)
            
            # Track the file for cleanup
            self.temp_files.append(temp_file)
            
            print(f"✅ Downloaded {len(data)} data points for {ticker}")
            print(f"📁 Saved to: {temp_file}")
            
            return str(temp_file)
            
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            raise
    
    def cleanup_temp_files(self):
        """Clean up all temporary data files."""
        for temp_file in self.temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
                    print(f"🗑️ Deleted temporary file: {temp_file}")
            except Exception as e:
                print(f"⚠️ Error deleting {temp_file}: {e}")
        
        self.temp_files.clear()
    
    def get_available_tickers(self) -> list:
        """Get list of popular tickers for testing."""
        return ["AAPL", "MSFT", "GOOGL", "TSLA", "META", "AMZN", "NVDA", "NFLX", "AMD", "INTC"]

# Global instance
data_fetcher = DataFetcher()
