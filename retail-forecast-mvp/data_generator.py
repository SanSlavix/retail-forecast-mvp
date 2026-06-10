import pandas as pd
import numpy as np

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
    
    # Базовый средний спрос для каждого SKU (от 10 до 150)
    base_demand = np.random.uniform(10, 150, n_skus)
    # Базовая цена (от 50 до 300)
    base_price = np.random.uniform(50, 300, n_skus)
    
    for store_id in range(1, n_stores+1):
        for sku_id in range(1, n_skus+1):
            for date in dates:
                # День недели
                dow = date.dayofweek
                weekday_factor = 1.0
                if dow == 4:   # пятница
                    weekday_factor = 1.4
                elif dow == 5: # суббота
                    weekday_factor = 1.2
                elif dow == 6: # воскресенье
                    weekday_factor = 0.8
                
                # Сезонность
                month = date.month
                seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * (month - 0.5) / 12)
                
                # Акция (10% дней)
                on_promo = np.random.rand() < 0.1
                discount = np.random.choice([10, 20, 30, 40, 50]) if on_promo else 0
                promo_factor = 1 + (discount / 100) * 2.5 if on_promo else 1
                
                # Праздники
                is_holiday = 0
                if (date.month == 1 and date.day == 1) or (date.month == 3 and date.day == 8) or (date.month == 2 and date.day == 23):
                    is_holiday = 1
                    holiday_factor = 1.5
                else:
                    holiday_factor = 1.0
                
                # Цена со случайным отклонением и скидкой
                price_variation = np.random.uniform(0.8, 1.2)
                price = base_price[sku_id-1] * price_variation * (1 - discount/100)
                # Сильная эластичность: чем выше цена, тем ниже спрос (степень 1.5)
                avg_price = base_price[sku_id-1]
                price_effect = (avg_price / price) ** 1.5
                # Ограничим эффект цены: не более 3 и не менее 0.2
                price_effect = np.clip(price_effect, 0.2, 3.0)
                
                # Температура (влияние)
                temperature = np.random.normal(10, 15)
                # При низкой температуре спрос падает, при высокой растёт
                if temperature < -10:
                    temp_effect = 0.3
                elif temperature < 0:
                    temp_effect = 0.6
                elif temperature < 10:
                    temp_effect = 0.8
                elif temperature < 20:
                    temp_effect = 1.0
                elif temperature < 30:
                    temp_effect = 1.3
                else:
                    temp_effect = 1.6
                
                # Итоговый спрос
                demand = base_demand[sku_id-1] * weekday_factor * seasonal_factor * promo_factor * holiday_factor * price_effect * temp_effect
                demand += np.random.normal(0, 0.15 * demand)
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
    print(f"✅ Сгенерировано {len(df)} строк. Сохранено в sales_train.csv")
    print(f"📊 Диапазон продаж: {df['sales_qty'].min()} - {df['sales_qty'].max()} шт.")
    print(f"📈 Средние продажи: {df['sales_qty'].mean():.1f} шт.")
    return df

if __name__ == '__main__':
    generate_sales_data()
