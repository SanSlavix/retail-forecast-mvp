import streamlit as st
import requests
import pandas as pd
import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="Прогноз продаж", layout="wide")
st.title("📊 Прогнозирование продаж товаров")

left_col, right_col = st.columns([1, 2], gap="large")

with left_col:
    st.subheader("Параметры прогноза")
    store_id = st.selectbox("Магазин", options=[1, 2, 3, 4, 5])
    sku_id = st.selectbox("Товар (SKU)", options=list(range(1, 101)))
    date = st.date_input("Дата прогноза", value=datetime.date.today() + datetime.timedelta(days=7))
    price = st.number_input("Цена (руб)", min_value=10.0, value=99.9, step=5.0)
    on_promo = st.checkbox("Акция?")
    discount = st.slider("Скидка (%)", 0, 50, 0, disabled=not on_promo)
    temperature = st.number_input("Температура (°C)", value=20.0, step=1.0)
    submitted = st.button("Рассчитать прогноз", type="primary", use_container_width=True)

with right_col:
    st.subheader("Результат прогноза")
    if submitted:
        payload = {
            "store_id": store_id,
            "sku_id": sku_id,
            "date": date.strftime("%Y-%m-%d"),
            "price": price,
            "on_promotion": on_promo,
            "discount_percent": discount,
            "temperature": temperature
        }
        try:
            response = requests.post("http://localhost:8000/predict", json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                forecast = result['forecast_qty']
                
                st.success(f"📅 На {date.strftime('%d.%m.%Y')} прогноз продаж: **{forecast:.1f} шт.**")
                
                # Среднее значение (заглушка)
                try:
                    df_avg = pd.read_csv('avg_sales.csv')
                    avg_key = f"{store_id}_{sku_id}"
                    avg_val = df_avg[df_avg['key'] == avg_key]['avg_qty'].values[0]
                except:
                    avg_val = 40.0
                
                # Рекомендация
                if forecast > avg_val * 1.2:
                    st.info("📈 Ожидается повышенный спрос! Рекомендуется увеличить заказ.")
                elif forecast < avg_val * 0.8:
                    st.warning("📉 Ожидается снижение спроса. Возможно, заказ стоит уменьшить.")
                
                # ---------- КОМПАКТНЫЙ ГРАФИК (фиксированный размер) ----------
                fig, ax = plt.subplots(figsize=(4, 2.5))   # маленький размер
                bars = ax.bar(["Прогноз", "Среднее"], [forecast, avg_val],
                              color=['#2ecc71', '#95a5a6'])
                ax.set_ylabel("Количество, шт", fontsize=8)
                ax.set_title("Сравнение", fontsize=9)
                ax.tick_params(axis='both', labelsize=7)
                
                # Подписи значений
                for bar in bars:
                    height = bar.get_height()
                    if height < 5:
                        y_pos = height + 0.5
                        va = 'bottom'
                    else:
                        y_pos = height - 1.5
                        va = 'top'
                    ax.annotate(f'{height:.1f}', xy=(bar.get_x() + bar.get_width()/2, y_pos),
                                ha='center', va=va, fontsize=7, color='white' if height > 5 else 'black')
                
                ax.set_ylim(0, max(forecast, avg_val) * 1.1)
                
                # Отображаем график, НЕ растягивая по ширине контейнера
                st.pyplot(fig, use_container_width=False)
                # Можно также добавить отступы:
                plt.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.2)
                # но это необязательно
                
            else:
                st.error(f"Ошибка API: {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Не удалось соединиться с API. Убедитесь, что сервер запущен (uvicorn).")
        except Exception as e:
            st.error(f"Произошла ошибка: {e}")
    else:
        st.info("Заполните параметры слева и нажмите «Рассчитать прогноз».")
