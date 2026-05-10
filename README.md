# Olist Risk Engine — Django Marketplace

Sistema de marketplace con predicción de riesgo transaccional integrada. Combina una tienda funcional (gestión de órdenes, productos, clientes y vendedores) con un modelo LightGBM que evalúa automáticamente el riesgo de cada orden en el momento de su aprobación.

---

## Estructura del proyecto

```
Modelo/
├── manage.py
├── requirements.txt
├── db.sqlite3
│
├── model_deploy/               ← Archivos del modelo ML (no editar)
│   ├── lightgbm_model.pkl      ← Modelo entrenado
│   ├── feature_names.pkl       ← Features
│   └── config.json             
│
├── olist_project/              ← Configuración Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── olist_risk/                 ← App del motor ML (simulador original)
│   ├── ml_engine.py            ← Singleton que carga y ejecuta el modelo
│   ├── views.py                ← Simulador interactivo + API REST
│   ├── urls.py
│   ├── templates/olist_risk/
│   └── static/olist_risk/
│
└── marketplace/                ← App del marketplace
    ├── models.py               ← Modelos
    ├── signals.py              ← Señal de predicción al aprobar orden
    ├── views.py
    ├── forms.py 
    ├── urls.py  
    ├── admin.py 
    └── templates/marketplace/ 
```

---

## Instalación

### 1. Clonar o ubicarse en la carpeta del proyecto

```bash
cd C:\Users\ASUS\Proyectos\Modelo
```

### 2. Crear y activar el entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
pip install djangorestframework  # para la API REST de olist_risk
```

### 4. Crear las migraciones e inicializar la base de datos

```bash
# Generar migraciones de la app marketplace (solo la primera vez
# o cuando se modifican los modelos)
python manage.py makemigrations marketplace

# Aplicar todas las migraciones pendientes
python manage.py migrate
```

### 5. Crear superusuario (opcional, para acceder al admin)

```bash
python manage.py createsuperuser
```

### 6. Correr el servidor

```bash
python manage.py runserver
```

---

## Orden recomendado para cargar datos por primera vez

El modelo necesita ciertos datos para generar predicciones correctas. Se recomienda crearlos en este orden:

1. **Categorías** → `/categorias/nueva/`
   Asignar `risk_rate` entre 0 y 1 según el riesgo histórico de la categoría. Marcar `is_high_risk` si supera el percentil 75.

2. **Vendedores** → `/vendedores/nuevo/`
   El campo `historic_risk_rate` es una de las features más importantes del modelo. Iniciar en `0.0` para vendedores nuevos.

3. **Clientes** → `/clientes/nuevo/`

4. **Productos** → `/productos/nuevo/`
   Requiere vendedor y categoría previamente creados.

5. **Órdenes** → `/ordenes/nueva/`
   Al crear una orden se elige cliente, productos y método de pago. La predicción de riesgo **se dispara automáticamente** cuando el estado cambia a `Aprobada`.

---

## URLs disponibles

| URL | Descripción |
|-----|-------------|
| `http://localhost:8000/` | Dashboard principal |
| `http://localhost:8000/ordenes/` | Gestión de órdenes |
| `http://localhost:8000/productos/` | Catálogo de productos |
| `http://localhost:8000/clientes/` | Gestión de clientes |
| `http://localhost:8000/vendedores/` | Gestión de vendedores |
| `http://localhost:8000/categorias/` | Gestión de categorías |
| `http://localhost:8000/riesgo/` | Panel de predicciones de riesgo |
| `http://localhost:8000/modelo/` | Simulador interactivo del modelo |
| `http://localhost:8000/admin/` | Panel de administración Django |
| `http://localhost:8000/api/` | Estado de la API REST |
| `http://localhost:8000/api/predict/` | POST — predicción directa |
| `http://localhost:8000/api/model-info/` | Configuración del modelo |

---

## Cómo funciona la predicción de riesgo

Cuando una orden pasa al estado **Aprobada** (`approved`), Django dispara automáticamente una señal (`post_save`) que:

1. Verifica que la orden tenga ítems y pagos registrados.
2. Construye un diccionario con las **17 features** que espera el modelo.
3. Llama a `risk_engine.predict()` en `olist_risk/ml_engine.py`.
4. Guarda el resultado en el modelo `RiskPrediction` asociado a la orden.

El resultado incluye:
- `risk_probability` — probabilidad de reseña negativa (≤ 3 estrellas), entre 0 y 1.
- `risk_label` — `True` si la probabilidad supera el umbral (0.45 por defecto).
- `risk_level` — clasificación en `bajo` / `medio` / `alto`.

### Features del modelo

| Feature | Fuente |
|---|---|
| `total_items` | Cantidad de ítems en la orden |
| `unique_sellers` | Número de vendedores distintos |
| `seller_historic_risk_rate` | Campo del vendedor principal |
| `seller_historic_order_count` | Total órdenes del vendedor |
| `total_freight` | Suma de fletes de todos los ítems |
| `total_price` | Suma de precios de todos los ítems |
| `category_risk_rate` | Campo de la categoría del primer ítem |
| `is_high_risk_category` | Flag de la categoría |
| `payment_installments` | Máximo de cuotas entre los pagos |
| `same_state` | Cliente y vendedor en el mismo departamento |
| `estimated_delivery_log` | log1p(días hasta entrega estimada) |
| `approval_delay_log` | log1p(horas entre compra y aprobación) |
| `month_sin` / `month_cos` | Codificación cíclica del mes |
| `weekday_sin` / `weekday_cos` | Codificación cíclica del día de la semana |
| `customer_is_sp` | Reservado (legado del dataset Olist Brasil) |

### Métricas del modelo (v1.0.0)

| Métrica | Valor |
|---|---|
| AUC-ROC | 0.6146 |
| Recall | 0.4064 |
| Precision | 0.1509 |
| F1 | 0.2201 |
| Accuracy | 0.7234 |

El modelo está optimizado para **recall** (detectar el mayor número posible de órdenes riesgosas), a costa de precisión. Umbral por defecto: **0.45**.

---

## API REST — Ejemplo de uso directo

```bash
curl -X POST http://localhost:8000/api/predict/ \
  -H "Content-Type: application/json" \
  -d '{
    "total_items": 2,
    "total_price": 180.50,
    "total_freight": 25.00,
    "unique_sellers": 1,
    "approval_delay_hours": 1.5,
    "estimated_delivery_days": 10,
    "purchase_month": 6,
    "purchase_weekday": 2,
    "seller_historic_risk_rate": 0.12,
    "seller_historic_order_count": 85,
    "category_risk_rate": 0.09,
    "is_high_risk_category": 0,
    "payment_installments": 3,
    "same_state": 0,
    "customer_is_sp": 0
  }'
```

---

## Comandos útiles

```bash
# Reiniciar la base de datos desde cero
del db.sqlite3
python manage.py migrate

# Crear migraciones nuevas tras modificar modelos
python manage.py makemigrations marketplace
python manage.py migrate

# Ver todas las migraciones y su estado
python manage.py showmigrations

# Abrir shell de Django para pruebas
python manage.py shell

# Colectar archivos estáticos (para producción)
python manage.py collectstatic
```

---

## Dependencias principales

| Paquete | Uso |
|---|---|
| `django >= 4.2` | Framework web |
| `lightgbm >= 4.0` | Modelo de predicción |
| `joblib >= 1.3` | Carga del modelo `.pkl` |
| `numpy >= 1.24` | Operaciones numéricas |
| `scikit-learn >= 1.3` | Preprocesamiento |
| `djangorestframework` | API REST del simulador |

---

## Notas de desarrollo

- El modelo fue entrenado con datos del dataset público **Olist** (e-commerce brasileño, corte julio 2018). El target es `review_score <= 3`.
- La feature `customer_is_sp` (cliente del estado de São Paulo) se conserva por compatibilidad con el modelo entrenado; en el contexto colombiano siempre vale `0`.
- Para reentrenar el modelo con datos reales del marketplace, los scripts de entrenamiento se pueden agregar en una carpeta `notebooks/` o `scripts/`.
- La base de datos por defecto es SQLite (`db.sqlite3`). Para producción se recomienda migrar a PostgreSQL actualizando `DATABASES` en `settings.py`.
