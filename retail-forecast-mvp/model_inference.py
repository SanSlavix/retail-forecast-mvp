import joblib
import pandas as pd
import numpy as np

model = joblib.load('model.pkl')
scaler = joblib.load('scaler.pkl')
le_store = joblib.load('le_store.pkl')
le_sku = joblib.load('le_sku.pkl')

def preprocess_input(data_dict):
    """Преобразование входного словаря в вектор признаков"""
    # data_dict содержит: store_id, sku_id, date, price, on_promotion, discount_percent, temperature
    store_enc = le_store.transform([data_dict['store_id']])[0]
    sku_enc = le_sku.transform([data_dict['sku_id']])[0]
    date = pd.to_datetime(data_dict['date'])
    
    # Базовые признаки
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
    # Добавить заглушки для лагов и скользящих средних (в реальном использовании нужна история)
    # Для простоты MVP: заполняем нулями/средними.
    # В полноценной системе необходим feature store с историей.
    for lag in [1,7,14,28]:
        features[f'lag_{lag}'] = 0
    for win in [7,30]:
        features[f'rolling_mean_{win}'] = 0
    features['promo_previous_day'] = 0
    features['price_per_unit'] = 1.0
    
    # Создаем DataFrame с одним наблюдением в правильном порядке
    expected_cols = scaler.feature_names_in_  # если у scaler заданы имена, иначе придется вручную
    # Упростим: вернем список значений в том порядке, в котором обучали
    # Для демонстрации используем фиксированный порядок (это не production-решение)
    order = ['store_encoded','sku_encoded','price','on_promotion','discount_percent','temperature',
             'day_of_week','month','quarter','year','lag_1','lag_7','lag_14','lag_28',
             'rolling_mean_7','rolling_mean_30','promo_previous_day','price_per_unit']
    X = np.array([[features[col] for col in order]])
    X_scaled = scaler.transform(X)
    return X_scaled

def predict(data_dict):
    X = preprocess_input(data_dict)
    pred = model.predict(X)[0]
    return float(pred)