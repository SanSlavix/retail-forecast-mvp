import pytest
import pandas as pd
from preprocessing import clean_data, add_date_features

def test_clean_data():
    df = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-01'],
        'store_id': [1,1],
        'sku_id': [101,101],
        'sales_qty': [10, 1000000]
    })
    cleaned = clean_data(df)
    assert cleaned['sales_qty'].max() < 1000000  # выброс обрезан
    assert len(cleaned) == 2

def test_add_date_features():
    df = pd.DataFrame({'date': ['2024-01-01']})
    df = add_date_features(df)
    assert 'day_of_week' in df.columns
    assert df['day_of_week'].iloc[0] == 0  # понедельник