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
    
    # Базовые параметры для каждого SKU
    base_demand = np.random.lognormal(mean=3, sigma=0.8, size=n_skus)  # средние продажи ~20
    price_base = np.random.uniform(50, 500, n_skus)
    
    for store_id in range(1, n_stores+1):
        for sku_id in range(1, n_skus+1):
            for date in dates:
                # Сезонность: недельная (пятница, суббота выше)
                dow = date.dayofweek  # 0=пн, 4=пт, 5=сб, 6=вс
                weekday_factor = 1.0
                if dow == 4:  # пятница
                    weekday_factor = 1.4
                elif dow == 5:  # суббота
                    weekday_factor = 1.3
                elif dow == 6:  # воскресенье
                    weekday_factor = 0.8
                
                # Годовая сезонность (пик в декабре)
                month = date.month
                seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * (month - 0.5) / 12)
                
                # Акция: случайная с вероятностью 5% в день
                on_promo = np.random.rand() < 0.05
                discount = np.random.choice([10, 20, 30]) if on_promo else 0
                promo_factor = 1 + discount/100 * np.random.uniform(0.8, 1.5) if on_promo else 1
                
                # Праздники: новый год, 8 марта, 23 февраля
                is_holiday = 0
                if (date.month == 1 and date.day == 1) or (date.month == 3 and date.day == 8) or (date.month == 2 and date.day == 23):
                    is_holiday = 1
                    holiday_factor = 1.3
                else:
                    holiday_factor = 1.0
                
                # Тренд (рост на 5% в год)
                days_since_start = (date - pd.Timestamp(start_date)).days
                trend_factor = 1 + 0.05 * (days_since_start / 365)
                
                # Итоговый спрос
                demand = base_demand[sku_id-1] * weekday_factor * seasonal_factor * promo_factor * holiday_factor * trend_factor
                demand += np.random.normal(0, 0.1 * demand)  # шум
                demand = max(0, int(round(demand)))
                
                # Цена со скидкой
                price = price_base[sku_id-1] * (1 - discount/100)
                
                # Температура (просто случайная для демонстрации)
                temperature = np.random.normal(10, 15)
                
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
    return df

if __name__ == '__main__':
    generate_sales_data()