import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
import lightgbm as lgb
import joblib
from preprocessing import preprocess_pipeline
from features import build_features

# Загрузка и подготовка данных
df = pd.read_csv('sales_train.csv')
df = preprocess_pipeline(df)
df = build_features(df)

# Целевая переменная
target = 'sales_qty'

# Явно задаём порядок признаков (строго 18 признаков)
feature_order = [
    'store_encoded', 'sku_encoded', 'price', 'on_promotion', 'discount_percent',
    'temperature', 'day_of_week', 'month', 'quarter', 'year',
    'lag_1', 'lag_7', 'lag_14', 'lag_28',
    'rolling_mean_7', 'rolling_mean_30', 'promo_previous_day', 'price_per_unit'
]

# Убедимся, что все признаки присутствуют в датафрейме
for col in feature_order:
    if col not in df.columns:
        raise ValueError(f"Column {col} not found in dataframe!")

X = df[feature_order].values
y = df[target].values

# Масштабирование
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Сохраняем scaler и порядок признаков
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(feature_order, 'feature_order.pkl')   # <--- сохраняем порядок

# Обучение модели
params = {
    'num_leaves': 64,
    'learning_rate': 0.05,
    'n_estimators': 1500,
    'subsample': 0.8,
    'colsample_bytree': 0.7,
    'reg_alpha': 0.1,
    'reg_lambda': 0.1,
    'objective': 'quantile',
    'alpha': 0.5,
    'verbose': -1
}

model = lgb.LGBMRegressor(**params)
model.fit(X_scaled, y, eval_metric='mape')

joblib.dump(model, 'model.pkl')
print("Model saved to model.pkl")

# Оценка на последних 3 месяцах (примерно)
split_date = '2025-10-01'
train_mask = df['date'] < split_date
test_mask = df['date'] >= split_date

X_train = X_scaled[train_mask]
y_train = y[train_mask]
X_test = X_scaled[test_mask]
y_test = y[test_mask]

model.fit(X_train, y_train)
y_pred = model.predict(X_test)

mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
print(f"Test MAPE: {mape:.2f}%")
