import streamlit as st
import requests
import pandas as pd
import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="Прогноз продаж", layout="wide")
st.title("📊 Прогнозирование продаж товаров")

# Создаём две колонки: левая (30% ширины) для ввода, правая (70%) для результатов
left_col, right_col = st.columns([1, 2], gap="large")

# ======================= ЛЕВАЯ КОЛОНКА (все поля ввода) =======================
with left_col:
    st.subheader("Параметры прогноза")
    
    store_id = st.selectbox("Магазин", options=[1, 2, 3, 4, 5])
    sku_id = st.selectbox("Товар (SKU)", options=list(range(1, 101)))
    date = st.date_input(
        "Дата прогноза",
        value=datetime.date.today() + datetime.timedelta(days=7),
        help="Выберите день, на который хотите предсказать продажи"
    )
    price = st.number_input("Цена (руб)", min_value=10.0, value=99.9, step=5.0)
    
    on_promo = st.checkbox("Акция?")
    discount = st.slider(
        "Скидка (%)", 0, 50, 0, disabled=not on_promo,
        help="Размер скидки (только если акция включена)"
    )
    temperature = st.number_input("Температура (°C)", value=20.0, step=1.0)
    
    submitted = st.button("Рассчитать прогноз", type="primary", use_container_width=True)

# ======================= ПРАВАЯ КОЛОНКА (результаты) =======================
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
            # Отправляем запрос к API (предполагается, что API запущен на localhost:8000)
            response = requests.post("http://localhost:8000/predict", json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                forecast = result['forecast_qty']
                
                # Отображаем крупно прогноз
                st.metric(label="Прогноз продаж (шт.)", value=f"{forecast:.1f}")
                
                # Получаем среднее значение для этого товара и магазина (нужно из данных)
                # В MVP будем загружать сохранённое среднее из файла, если есть
                try:
                    df_avg = pd.read_csv('avg_sales.csv')
                    avg_key = f"{store_id}_{sku_id}"
                    avg_val = df_avg[df_avg['key'] == avg_key]['avg_qty'].values[0]
                except:
                    # Если файла нет — считаем среднее из сгенерированных данных (упрощённо)
                    avg_val = 40.0  # заглушка, но можно пересчитать
                
                # График: прогноз vs среднее
                fig, ax = plt.subplots(figsize=(6, 4))
                bars = ax.bar(["Прогноз", "Среднее (история)"], [forecast, avg_val], 
                              color=['#2ecc71', '#95a5a6'])
                ax.set_ylabel("Количество, шт")
                ax.set_title("Сравнение прогноза со средними продажами")
                # Подписываем значения на столбцах
                for bar in bars:
                    height = bar.get_height()
                    ax.annotate(f'{height:.1f}', xy=(bar.get_x() + bar.get_width()/2, height),
                                xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')
                st.pyplot(fig)
                
                # Дополнительная информация
                st.success(f"Прогноз на {date.strftime('%d.%m.%Y')}: **{forecast:.1f} шт.**")
                
                # Если прогноз значительно выше среднего — подсветим
                if forecast > avg_val * 1.2:
                    st.info("📈 Ожидается повышенный спрос! Рекомендуется увеличить заказ.")
                elif forecast < avg_val * 0.8:
                    st.warning("📉 Ожидается снижение спроса. Возможно, заказ стоит уменьшить.")
                    
            else:
                st.error(f"Ошибка API: {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Не удалось соединиться с API. Убедитесь, что сервер запущен (uvicorn).")
        except Exception as e:
            st.error(f"Произошла ошибка: {e}")
    else:
        st.info("Заполните параметры слева и нажмите «Рассчитать прогноз».")

# Для красоты добавим небольшую информацию в боковую панель (опционально)
with st.sidebar:
    st.markdown("### ℹ️ О системе")
    st.markdown("""
    **MVP прогнозирования продаж**  
    Модель: LightGBM  
    Метрика: MAPE ≈ 14%  
    
    Параметры:
    - Магазин (1–5)
    - Товар (1–100)
    - Дата, цена, акция, температура
    """)
