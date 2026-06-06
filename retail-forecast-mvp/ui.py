import streamlit as st
import requests
import pandas as pd
import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="Прогноз продаж", layout="centered")
st.title("📊 Прогнозирование продаж товаров")

with st.form("prediction_form"):
    store_id = st.selectbox("Магазин", options=[1,2,3,4,5])
    sku_id = st.selectbox("Товар (SKU)", options=range(1,101))
    date = st.date_input("Дата прогноза", value=datetime.date.today() + datetime.timedelta(days=7))
    price = st.number_input("Цена (руб)", min_value=10.0, value=99.9)
    on_promo = st.checkbox("Акция?")
    discount = st.slider("Скидка (%)", 0, 50, 0, disabled=not on_promo)
    temperature = st.number_input("Температура (°C)", value=20.0)
    submitted = st.form_submit_button("Рассчитать прогноз")

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
        response = requests.post("http://localhost:8000/predict", json=payload)
        if response.status_code == 200:
            result = response.json()
            st.success(f"Прогноз продаж: **{result['forecast_qty']} шт.**")
            # Простой график: сравнение с средним
            fig, ax = plt.subplots()
            ax.bar(["Прогноз", "Среднее (история)"], [result['forecast_qty'], 40], color=['green', 'gray'])
            ax.set_ylabel("Количество")
            st.pyplot(fig)
        else:
            st.error(f"Ошибка API: {response.text}")
    except Exception as e:
        st.error(f"Не удалось соединиться с API: {e}")