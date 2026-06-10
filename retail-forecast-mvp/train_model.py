import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
import lightgbm as lgb
import joblib
from sklearn.model_selection import train_test_split

# Загрузка данных
df = pd.read_csv('sales_train.csv')
df['date'] = pd.to_datetime(df['date'])

# Создание признаков из даты
df['day_of_week'] = df['date'].dt.dayofweek
df['month'] = df['date'].dt.month
df['quarter'] = df['date'].dt.quarter
df['year'] = df['date'].dt.year

# Кодирование категорий
le_store = LabelEncoder()
le_sku = LabelEncoder()
df['store_encoded'] = le_store.fit_transform(df['store_id'])
df['sku_encoded'] = le_sku.fit_transform(df['sku_id'])

# Признаки (без лагов, только то, что есть во входных данных)
feature_cols = [
    'store_encoded', 'sku_encoded', 'price', 'on_promotion', 'discount_percent',
    'temperature', 'day_of_week', 'month', 'quarter', 'year'
]

X = df[feature_cols].values
y = df['sales_qty'].values

# Масштабирование
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Сохраняем всё для предсказаний
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(feature_cols, 'feature_cols.pkl')
joblib.dump(le_store, 'le_store.pkl')
joblib.dump(le_sku, 'le_sku.pkl')

# Обучение модели
params = {
    'num_leaves': 31,
    'learning_rate': 0.1,
    'n_estimators': 500,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'reg_alpha': 0.1,
    'reg_lambda': 0.1,
    'verbose': -1
}

model = lgb.LGBMRegressor(**params)
model.fit(X_scaled, y, eval_metric='mape')

joblib.dump(model, 'model.pkl')
print("Model saved to model.pkl")

# Простая оценка на отложенной выборке
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
print(f"Test MAPE: {mape:.2f}%")
print(f"Пример предсказаний: {y_pred[:5]}, факт: {y_test[:5]}")
