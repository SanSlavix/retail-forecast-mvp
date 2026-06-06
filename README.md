# retail-forecast-mvp
MVP системы прогнозирования продаж для ритейла

## Запуск проекта

1. Установите зависимости:
pip install -r requirements.txt

2. Сгенерируйте данные и обучите модель:
python data_generator.py
python train_model.py

3. Запустите API:
uvicorn api:app --reload --port 8000

4. В другом терминале запустите UI:
streamlit run ui.py

5. Откройте браузер http://localhost:8501

## Использование

- Выберите магазин, товар, дату, цену, параметры акции.
- Нажмите "Рассчитать прогноз".
- Получите прогнозное количество продаж.

## Документация API

После запуска API откройте http://localhost:8000/docs

## Тестирование
pytest tests/
