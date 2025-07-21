from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, confusion_matrix
import pandas as pd
import numpy as np

def train_logistic_regression_model(X_train, y_train):
    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X_train, y_train)
    return model

def generate_ml_signals_logistic(df: pd.DataFrame):
    """
    Generate trading signals using logistic regression.
    Returns (signals_df, metrics_dict)
    """
    df_ml = df.copy()
    df_ml["return"] = df_ml["Close"].pct_change()
    df_ml["direction"] = (df_ml["return"].shift(-1) > 0).astype(int)
    df_ml = df_ml.dropna()
    X = df_ml[["return"]]
    y = df_ml["direction"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, shuffle=False, test_size=0.2, random_state=42
    )
    model = train_logistic_regression_model(X_train, y_train)
    df_ml["ml_signal"] = model.predict(X)
    df_ml["ml_signal"] = np.where(df_ml["ml_signal"] == 1, 1, -1)
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    y_pred = model.predict(X_test)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    cm = confusion_matrix(y_test, y_pred).tolist()
    metrics = {
        "train_accuracy": train_score,
        "test_accuracy": test_score,
        "precision": precision,
        "recall": recall,
        "confusion_matrix": cm
    }
    return df_ml, metrics

# Keep the original function for backward compatibility

def generate_ml_signals(df: pd.DataFrame):
    return generate_ml_signals_logistic(df)

def generate_ml_signals_advanced(df: pd.DataFrame, features: list = None) -> pd.DataFrame:
    """
    Advanced ML strategy with multiple features.
    
    Args:
        df (pd.DataFrame): OHLCV DataFrame
        features (list): List of feature names to use
        
    Returns:
        pd.DataFrame: DataFrame with ml_signal column
    """
    if features is None:
        features = ["return", "volume_ratio", "volatility"]
    
    df_ml = df.copy()
    
    # Calculate features
    df_ml["return"] = df_ml["Close"].pct_change()
    df_ml["volume_ratio"] = df_ml["Volume"] / df_ml["Volume"].rolling(20).mean()
    df_ml["volatility"] = df_ml["return"].rolling(20).std()
    
    # Create labels
    df_ml["direction"] = (df_ml["return"].shift(-1) > 0).astype(int)
    df_ml = df_ml.dropna()
    
    # Prepare features and target
    X = df_ml[features]
    y = df_ml["direction"]
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, shuffle=False, test_size=0.2, random_state=42
    )
    
    # Train model
    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X_train, y_train)
    
    # Generate signals
    df_ml["ml_signal"] = model.predict(X)
    df_ml["ml_signal"] = np.where(df_ml["ml_signal"] == 1, 1, -1)
    
    # Print performance
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"Advanced ML Model Performance:")
    print(f"  Features: {features}")
    print(f"  Training Accuracy: {train_score:.3f}")
    print(f"  Test Accuracy: {test_score:.3f}")
    
    return df_ml

# Example usage and testing
if __name__ == "__main__":
    # Test with sample data
    import yfinance as yf
    
    # Download sample data
    df = yf.download("MSFT", start="2022-01-01", end="2023-01-01")
    
    # Generate ML signals
    df_with_signals, metrics = generate_ml_signals(df)
    
    print(f"\nSample of results:")
    print(df_with_signals[["Close", "return", "ml_signal"]].tail(10)) 