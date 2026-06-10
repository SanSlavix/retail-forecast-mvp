import joblib
import pandas as pd
import numpy as np

model = joblib.load('model.pkl')
scaler = joblib.load('scaler.pkl')
feature_cols = joblib.load('feature_cols.pkl')
le_store = joblib.load('le_store.pkl')
le_sku = joblib.load('le_sku.pkl')

def predict(data_dict):
    # Преобразование входных данных в признаки
    store_enc = le_store.transform([data_dict['store_id']])[0]
    sku_enc = le_sku.transform([data_dict['sku_id']])[0]
    date = pd.to_datetime(data_dict['date'])
    
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
    }
    
    # Собираем в правильном порядке
    X = np.array([[features[col] for col in feature_cols]])
    X_scaled = scaler.transform(X)
    pred = model.predict(X_scaled)[0]
    return float(pred)
