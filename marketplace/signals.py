from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
import logging

from .models import Order, OrderItem, Payment, RiskPrediction

logger = logging.getLogger(__name__)


@receiver(post_save, sender=OrderItem)
def update_order_on_item(sender, instance, **kwargs):
    instance.order.recalculate_summary()


@receiver(post_save, sender=Order)
def trigger_risk_prediction(sender, instance, **kwargs):
    if kwargs.get("update_fields"):
        return

    should_predict = (
        instance.status in (Order.Status.APPROVED, Order.Status.PROCESSING)
        and not RiskPrediction.objects.filter(order=instance).exists()
        and instance.items.exists()
        and instance.payments.exists()
    )

    if not should_predict:
        return

    try:
        from olist_risk import ml_engine
        feature_dict = instance.build_feature_dict()
        result = ml_engine.predict(feature_dict)

        RiskPrediction.objects.create(
            order=instance,
            risk_probability=result["risk_probability"],
            risk_label=bool(result["risk_label"]),
            threshold_used=result["threshold"],
            model_version=result["model_version"],
            features_snapshot=feature_dict,
        )

        nivel = "⚠️  RIESGO" if result["risk_label"] else "✓ Sin riesgo"
        logger.info("%s — Orden #%s prob=%.2f%%", nivel, instance.pk, result["risk_probability"] * 100)

    except Exception as exc:
        logger.error("Error al predecir riesgo para Orden #%s: %s", instance.pk, exc)
