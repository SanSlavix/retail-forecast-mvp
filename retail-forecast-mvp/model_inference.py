import joblib
import pandas as pd
import numpy as np

model = joblib.load('model.pkl')
scaler = joblib.load('scaler.pkl')
feature_order = joblib.load('feature_order.pkl')   # загружаем порядок признаков
le_store = joblib.load('le_store.pkl')
le_sku = joblib.load('le_sku.pkl')

def preprocess_input(data_dict):
    store_enc = le_store.transform([data_dict['store_id']])[0]
    sku_enc = le_sku.transform([data_dict['sku_id']])[0]
    date = pd.to_datetime(data_dict['date'])

    # Словарь признаков точно в том же порядке
    features = {
        'store_encoded': store_enc,
        'sku_encoded': sku_enc,
        'price': data_dict['price'],
        'on_promotion': data_dict.get('on_promotion', 0),
        'discount_percent': data_dict.get('discount_percent', 0),
        'temperature': data_dict.get('temperature', 15.0),
        'day_of_week': date.dayofweek,
        'month': date.month,
        'quarter': date.quarter,
        'year': date.year,
        'lag_1': 0,
        'lag_7': 0,
        'lag_14': 0,
        'lag_28': 0,
        'rolling_mean_7': 0,
        'rolling_mean_30': 0,
        'promo_previous_day': 0,
        'price_per_unit': 1.0,
    }

    # Используем точно тот же порядок, что и при обучении
    X = np.array([[features[col] for col in feature_order]])
    X_scaled = scaler.transform(X)
    return X_scaled

def predict(data_dict):
    X = preprocess_input(data_dict)
    pred = model.predict(X)[0]
    return float(pred)
