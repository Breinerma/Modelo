"""
Cargador del modelo LightGBM — patrón Singleton para no recargar en cada request.
"""
import joblib
import json
import numpy as np
from pathlib import Path
from django.conf import settings

_model = None
_features = None
_config = None


def load_model():
    """Carga el modelo una sola vez al inicio."""
    global _model, _features, _config

    if _model is not None:
        return _model, _features, _config

    model_dir = Path(settings.MODEL_DIR)

    _model    = joblib.load(model_dir / 'lightgbm_model.pkl')
    _features = joblib.load(model_dir / 'feature_names.pkl')

    with open(model_dir / 'config.json', encoding='utf-8') as f:
        _config = json.load(f)

    return _model, _features, _config


def predict(order_data: dict) -> dict:
    """
    Recibe un dict con los campos del pedido y devuelve la predicción.

    Parámetros de entrada esperados
    --------------------------------
    total_items, total_price, total_freight, unique_sellers,
    approval_delay_hours, estimated_delivery_days,
    purchase_month, purchase_weekday,
    seller_historic_risk_rate, seller_historic_order_count,
    category_risk_rate, is_high_risk_category,
    payment_installments, same_state, customer_is_sp
    """
    model, features, config = load_model()
    threshold = config['threshold']

    # ── Transformaciones (igual que en el notebook) ──────────────────────────
    approval_delay_hours     = float(order_data.get('approval_delay_hours', 0))
    estimated_delivery_days  = float(order_data.get('estimated_delivery_days', 0))
    purchase_month           = int(order_data.get('purchase_month', 1))
    purchase_weekday         = int(order_data.get('purchase_weekday', 0))

    approval_delay_log      = float(np.log1p(max(approval_delay_hours, 0)))
    estimated_delivery_log  = float(np.log1p(max(estimated_delivery_days, 0)))
    month_sin  = float(np.sin(2 * np.pi * purchase_month / 12))
    month_cos  = float(np.cos(2 * np.pi * purchase_month / 12))
    weekday_sin = float(np.sin(2 * np.pi * purchase_weekday / 7))
    weekday_cos = float(np.cos(2 * np.pi * purchase_weekday / 7))

    row = {
        'total_items':                  float(order_data.get('total_items', 1)),
        'unique_sellers':               float(order_data.get('unique_sellers', 1)),
        'seller_historic_risk_rate':    float(order_data.get('seller_historic_risk_rate', 0.15)),
        'total_freight':                float(order_data.get('total_freight', 0)),
        'category_risk_rate':           float(order_data.get('category_risk_rate', 0.15)),
        'month_cos':                    month_cos,
        'is_high_risk_category':        float(order_data.get('is_high_risk_category', 0)),
        'month_sin':                    month_sin,
        'customer_is_sp':               float(order_data.get('customer_is_sp', 0)),
        'same_state':                   float(order_data.get('same_state', 0)),
        'estimated_delivery_log':       estimated_delivery_log,
        'total_price':                  float(order_data.get('total_price', 0)),
        'payment_installments':         float(order_data.get('payment_installments', 1)),
        'seller_historic_order_count':  float(order_data.get('seller_historic_order_count', 0)),
        'approval_delay_log':           approval_delay_log,
        'weekday_sin':                  weekday_sin,
        'weekday_cos':                  weekday_cos,
    }

    X = np.array([[row[f] for f in features]])
    prob  = float(model.predict_proba(X)[0, 1])
    label = int(prob >= threshold)

    # Top features por importancia
    try:
        importances = model.feature_importances_
        total = max(sum(importances), 1)
        feat_imp = {
            features[i]: round(float(importances[i]) / total, 4)
            for i in range(len(features))
        }
        top_features = dict(sorted(feat_imp.items(), key=lambda x: -x[1])[:8])
    except Exception:
        top_features = {}

    return {
        'risk_probability':  round(prob, 4),
        'risk_label':        label,
        'risk_label_text':   'RIESGO' if label == 1 else 'NO RIESGO',
        'threshold':         threshold,
        'top_features':      top_features,
        'model_version':     config.get('version', '1.0.0'),
        'metrics':           config.get('metrics', {}),
    }
