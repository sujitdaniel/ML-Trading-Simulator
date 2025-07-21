import pandas as pd
import numpy as np
try:
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense
    from tensorflow.keras.optimizers import Adam
except ImportError:
    Sequential = None
    LSTM = None
    Dense = None
    Adam = None
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, confusion_matrix

def create_lstm_sequences(X, y, window=10):
    Xs, ys = [], []
    for i in range(len(X) - window):
        Xs.append(X[i:i+window])
        ys.append(y[i+window])
    return np.array(Xs), np.array(ys)

def train_lstm_model(X_train, y_train, window=10):
    if Sequential is None:
        raise ImportError("TensorFlow/Keras is not installed. Please install tensorflow to use LSTM.")
    model = Sequential()
    model.add(LSTM(16, input_shape=(window, 1)))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])
    model.fit(X_train, y_train, epochs=10, batch_size=16, verbose=0)
    return model

def generate_ml_signals_lstm(df: pd.DataFrame, window=10):
    """
    Generate trading signals using LSTM.
    Returns (signals_df, metrics_dict)
    """
    if Sequential is None:
        raise ImportError("TensorFlow/Keras is not installed. Please install tensorflow to use LSTM.")
    df_ml = df.copy()
    df_ml["return"] = df_ml["Close"].pct_change()
    df_ml["direction"] = (df_ml["return"].shift(-1) > 0).astype(int)
    df_ml = df_ml.dropna()
    X = df_ml[["return"]].values
    y = df_ml["direction"].values
    X_seq, y_seq = create_lstm_sequences(X, y, window=window)
    X_train, X_test, y_train, y_test = train_test_split(
        X_seq, y_seq, shuffle=False, test_size=0.2, random_state=42
    )
    model = train_lstm_model(X_train, y_train, window=window)
    y_pred_prob = model.predict(X_seq)
    y_pred = (y_pred_prob > 0.5).astype(int).flatten()
    ml_signal = np.where(y_pred == 1, 1, -1)
    # Pad the beginning to match index length
    ml_signal_full = np.zeros(len(df_ml))
    ml_signal_full[:window] = 0
    ml_signal_full[window:] = ml_signal
    df_ml["ml_signal"] = ml_signal_full
    # Metrics
    y_pred_test = (model.predict(X_test) > 0.5).astype(int).flatten()
    train_score = model.evaluate(X_train, y_train, verbose=0)[1]
    test_score = model.evaluate(X_test, y_test, verbose=0)[1]
    precision = precision_score(y_test, y_pred_test, zero_division=0)
    recall = recall_score(y_test, y_pred_test, zero_division=0)
    cm = confusion_matrix(y_test, y_pred_test).tolist()
    metrics = {
        "train_accuracy": train_score,
        "test_accuracy": test_score,
        "precision": precision,
        "recall": recall,
        "confusion_matrix": cm
    }
    return df_ml, metrics 