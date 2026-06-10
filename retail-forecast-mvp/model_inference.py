import joblib
import pandas as pd
import numpy as np

# Загрузка моделей и scaler
model = joblib.load('model.pkl')
scaler = joblib.load('scaler.pkl')
le_store = joblib.load('le_store.pkl')
le_sku = joblib.load('le_sku.pkl')

def preprocess_input(data_dict):
    """Преобразование входного словаря в вектор признаков в том же порядке, что и при обучении"""
    store_enc = le_store.transform([data_dict['store_id']])[0]
    sku_enc = le_sku.transform([data_dict['sku_id']])[0]
    date = pd.to_datetime(data_dict['date'])
    
    # Словарь признаков (в том же порядке, как в train_model.py)
    # Порядок признаков, который использовался при обучении (см. feature_cols в train_model.py)
    # Мы воссоздадим признаки вручную
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
        # Лаги (заглушки — в реальной системе нужна история)
        'lag_1': 0,
        'lag_7': 0,
        'lag_14': 0,
        'lag_28': 0,
        'rolling_mean_7': 0,
        'rolling_mean_30': 0,
        'promo_previous_day': 0,
        'price_per_unit': 1.0,
    }
    
    # Порядок должен точно совпадать с feature_cols из train_model.py
    # Убедитесь, что порядок такой же, как при обучении. Возьмём из train_model.py:
    order = [
        'store_encoded', 'sku_encoded', 'price', 'on_promotion', 'discount_percent',
        'temperature', 'day_of_week', 'month', 'quarter', 'year',
        'lag_1', 'lag_7', 'lag_14', 'lag_28',
        'rolling_mean_7', 'rolling_mean_30', 'promo_previous_day', 'price_per_unit'
    ]
    
    X = np.array([[features[col] for col in order]])
    # Масштабируем
    X_scaled = scaler.transform(X)
    return X_scaled

def predict(data_dict):
    X = preprocess_input(data_dict)
    pred = model.predict(X)[0]
    return float(pred)
