# API Documentation

## POST /predict
Тело запроса (JSON):
- store_id (int, 1-5)
- sku_id (int, 1-100)
- date (YYYY-MM-DD)
- price (float >0)
- on_promotion (bool)
- discount_percent (0-50)
- temperature (float)

Ответ:
- forecast_qty (float)
- model_version (string)