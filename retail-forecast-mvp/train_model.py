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
feature_cols = [c for c in df.columns if c not in ['date', 'sales_qty', 'store_id', 'sku_id', 'store_encoded', 'sku_encoded']]

X = df[feature_cols].values
y = df[target].values

# Масштабирование числовых признаков
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
joblib.dump(scaler, 'scaler.pkl')

# Временная кросс-валидация
tscv = TimeSeriesSplit(n_splits=3)
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

# Обучение финальной модели на всех данных
print("Training LightGBM model...")
model = lgb.LGBMRegressor(**params)
model.fit(X_scaled, y, eval_metric='mape')

# Сохранение модели
joblib.dump(model, 'model.pkl')
print("Model saved to model.pkl")

# Оценка на последних 3 месяцах (простой холд-аут)
split_date = '2025-10-01'
train_mask = df['date'] < split_date
test_mask = df['date'] >= split_date

X_train = X_scaled[train_mask]
y_train = y[train_mask]
X_test = X_scaled[test_mask]
y_test = y[test_mask]

model.fit(X_train, y_train)
y_pred = model.predict(X_test)

# MAPE
mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
print(f"Test MAPE: {mape:.2f}%")