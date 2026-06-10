import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sales_data(
    start_date='2024-01-01',
    end_date='2025-12-31',
    n_stores=5,
    n_skus=100,
    seed=42
):
    np.random.seed(seed)
    dates = pd.date_range(start_date, end_date, freq='D')
    data = []
    
    # Базовый средний спрос для каждого SKU (от 20 до 180 штук)
    base_demand = np.random.uniform(20, 180, n_skus)
    # Базовая цена (от 50 до 500)
    base_price = np.random.uniform(50, 500, n_skus)
    
    for store_id in range(1, n_stores+1):
        for sku_id in range(1, n_skus+1):
            for date in dates:
                # День недели: 0=пн, 4=пт, 5=сб, 6=вс
                dow = date.dayofweek
                weekday_factor = 1.0
                if dow == 4:   # пятница
                    weekday_factor = 1.5
                elif dow == 5: # суббота
                    weekday_factor = 1.3
                elif dow == 6: # воскресенье
                    weekday_factor = 0.8
                
                # Сезонность: пик в декабре
                month = date.month
                seasonal_factor = 1 + 0.4 * np.sin(2 * np.pi * (month - 0.5) / 12)
                
                # Акция (случайно 10% дней)
                on_promo = np.random.rand() < 0.1
                discount = np.random.choice([10, 20, 30, 40, 50]) if on_promo else 0
                # Эффект акции: рост продаж от 1.5x до 3x в зависимости от скидки
                promo_factor = 1 + (discount / 100) * 2 if on_promo else 1
                
                # Праздники (НГ, 8 марта, 23 февраля)
                is_holiday = 0
                if (date.month == 1 and date.day == 1) or (date.month == 3 and date.day == 8) or (date.month == 2 and date.day == 23):
                    is_holiday = 1
                    holiday_factor = 1.4
                else:
                    holiday_factor = 1.0
                
                # Влияние цены: чем ниже цена, тем выше спрос (эластичность -0.7)
                # Цена может случайно отклоняться от базовой
                price_variation = np.random.uniform(0.8, 1.2)
                price = base_price[sku_id-1] * price_variation * (1 - discount/100)
                price_effect = (base_price[sku_id-1] / price) ** 0.7
                
                # Температура (влияет только для некоторых SKU, упростим: чем жарче, тем выше спрос для всех)
                temperature = np.random.normal(15, 10)
                temp_effect = 1 + max(0, (temperature - 20) / 20)  # при 20°C эффект 1, при 30°C = 1.5
                
                # Итоговый спрос
                demand = base_demand[sku_id-1] * weekday_factor * seasonal_factor * promo_factor * holiday_factor * price_effect * temp_effect
                demand += np.random.normal(0, 0.1 * demand)  # шум
                demand = max(0, int(round(demand)))
                
                data.append({
                    'date': date,
                    'store_id': store_id,
                    'sku_id': sku_id,
                    'sales_qty': demand,
                    'price': round(price, 2),
                    'on_promotion': 1 if on_promo else 0,
                    'discount_percent': discount,
                    'is_holiday': is_holiday,
                    'temperature': round(temperature, 1)
                })
    
    df = pd.DataFrame(data)
    df.to_csv('sales_train.csv', index=False)
    print(f"Generated {len(df)} rows. Saved to sales_train.csv")
    print(f"Example sales range: {df['sales_qty'].min()} - {df['sales_qty'].max()}")
    return df

if __name__ == '__main__':
    generate_sales_data()

if __name__ == '__main__':
    generate_sales_data()
