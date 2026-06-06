import pandas as pd
import numpy as np

def clean_data(df):
    """Удаление пропусков, дубликатов, обработка выбросов"""
    # Пропуски
    df = df.dropna()
    
    # Дубликаты
    df = df.drop_duplicates(subset=['date', 'store_id', 'sku_id'])
    
    # Выбросы по продажам (каппинг на уровне 99.9 перцентиля)
    upper = df['sales_qty'].quantile(0.999)
    df['sales_qty'] = df['sales_qty'].clip(upper=upper)
    
    return df

def add_date_features(df):
    """Извлечение признаков из даты"""
    df['date'] = pd.to_datetime(df['date'])
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    df['year'] = df['date'].dt.year
    return df

def encode_categorical(df):
    """Кодирование store_id и sku_id через LabelEncoder"""
    from sklearn.preprocessing import LabelEncoder
    le_store = LabelEncoder()
    le_sku = LabelEncoder()
    df['store_encoded'] = le_store.fit_transform(df['store_id'])
    df['sku_encoded'] = le_sku.fit_transform(df['sku_id'])
    # Сохраняем энкодеры для последующего использования
    import joblib
    joblib.dump(le_store, 'le_store.pkl')
    joblib.dump(le_sku, 'le_sku.pkl')
    return df

def preprocess_pipeline(df):
    df = clean_data(df)
    df = add_date_features(df)
    df = encode_categorical(df)
    return df