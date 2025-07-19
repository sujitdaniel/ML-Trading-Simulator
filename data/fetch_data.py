import yfinance as yf
import pandas as pd
import os

def get_stock_data(ticker: str, start: str, end: str, interval: str = '1d') -> pd.DataFrame:
    """
    Download OHLCV price data using yfinance.
    Saves a local CSV in data/raw/ for reproducibility.
    Returns a DataFrame.
    """
    save_dir = 'data/raw'
    os.makedirs(save_dir, exist_ok=True)
    save_path = f'{save_dir}/{ticker}.csv'
    
    # Try to load from disk first for efficiency
    if os.path.exists(save_path):
        print(f'Loading cached data: {save_path}')
        return pd.read_csv(save_path, index_col=0, parse_dates=True)
    
    print(f'Downloading data for {ticker} from {start} to {end}...')
    df = yf.download(ticker, start=start, end=end, interval=interval)
    if df.empty:
        raise ValueError(f'No data returned for {ticker} in date range.')
    df.to_csv(save_path)
    print(f'Saved to {save_path}')
    return df

if __name__ == '__main__':
    # Example usage:
    df = get_stock_data('TSLA', '2022-01-01', '2023-01-01', '1d')
    print(df.head())
