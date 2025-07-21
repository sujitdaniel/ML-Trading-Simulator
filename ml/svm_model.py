import pandas as pd
import numpy as np
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, confusion_matrix

def train_svm_model(X_train, y_train):
    model = SVC(kernel='rbf', probability=True, random_state=42)
    model.fit(X_train, y_train)
    return model

def generate_ml_signals_svm(df: pd.DataFrame):
    """
    Generate trading signals using SVM.
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
    model = train_svm_model(X_train, y_train)
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