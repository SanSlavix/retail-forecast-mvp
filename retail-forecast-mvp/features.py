import pandas as pd
import numpy as np

def create_lag_features(df, sku_col='sku_encoded', store_col='store_encoded', date_col='date', target='sales_qty', lags=[1,7,14,28]):
    """Создание лагов продаж"""
    df = df.sort_values([store_col, sku_col, date_col])
    for lag in lags:
        df[f'lag_{lag}'] = df.groupby([store_col, sku_col])[target].shift(lag)
    return df

def create_rolling_features(df, sku_col='sku_encoded', store_col='store_encoded', date_col='date', target='sales_qty', windows=[7,30]):
    """Скользящие средние"""
    for win in windows:
        df[f'rolling_mean_{win}'] = df.groupby([store_col, sku_col])[target].transform(
            lambda x: x.rolling(win, min_periods=1).mean()
        )
    return df

def add_promo_features(df):
    """Признаки, связанные с акциями"""
    # Дней с последней акции (упрощённо: флаг, была ли акция вчера)
    df['promo_previous_day'] = df.groupby(['store_encoded', 'sku_encoded'])['on_promotion'].shift(1)
    df['promo_previous_day'] = df['promo_previous_day'].fillna(0)
    return df

def add_price_features(df):
    """Ценовая эластичность: цена относительно средней по SKU"""
    df['price_per_unit'] = df['price'] / df.groupby('sku_encoded')['price'].transform('mean')
    return df

def build_features(df):
    df = create_lag_features(df)
    df = create_rolling_features(df)
    df = add_promo_features(df)
    df = add_price_features(df)
    # Удаляем строки с NaN, образовавшимися после лагов
    df = df.dropna()
    return df