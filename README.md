# Olist Risk Engine — Django

Predictor de riesgo transaccional con LightGBM integrado en Django.

## Estructura del proyecto

```
Modelo/
├── manage.py
├── requirements.txt
├── model_deploy/               ← archivos del modelo ML
│   ├── lightgbm_model.pkl
│   ├── feature_names.pkl
│   └── config.json
├── olist_project/              ← configuración Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── olist_risk/                 ← app Django
    ├── ml_engine.py            ← carga y predicción del modelo
    ├── views.py                ← vistas HTML + API REST
    ├── urls.py
    ├── templates/olist_risk/
    │   ├── simulator.html
    │   └── model_info.html
    └── static/olist_risk/
        ├── css/styles.css
        └── js/simulator.js
```

## Instalación

```bash
# 1. Crear entorno virtual
cd C:\Users\ASUS\Proyectos\Modelo
python -m venv venv
venv\Scripts\activate          # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Aplicar migraciones
python manage.py migrate

# 4. Correr el servidor
python manage.py runserver
```

## Acceso

| URL | Descripción |
|-----|-------------|
| http://localhost:8000/ | Simulador interactivo |
| http://localhost:8000/modelo/ | Info del modelo |
| http://localhost:8000/api/ | Estado de la API (JSON) |
| http://localhost:8000/api/health/ | Health check |
| http://localhost:8000/api/predict/ | POST predicción |
| http://localhost:8000/api/model-info/ | Config completa |

## Ejemplo API

```bash
curl -X POST http://localhost:8000/api/predict/ \
  -H "Content-Type: application/json" \
  -d '{
    "total_items": 1,
    "total_price": 95,
    "total_freight": 12,
    "unique_sellers": 1,
    "approval_delay_hours": 0.5,
    "estimated_delivery_days": 7,
    "purchase_month": 4,
    "purchase_weekday": 1,
    "seller_historic_risk_rate": 0.05,
    "seller_historic_order_count": 120,
    "category_risk_rate": 0.07,
    "is_high_risk_category": 0,
    "payment_installments": 1,
    "same_state": 1,
    "customer_is_sp": 1
  }'
```
