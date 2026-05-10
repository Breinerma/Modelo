from django.db import models
from django.utils import timezone
import math


ESTADOS_CO = [
    ("ANT", "Antioquia"), ("ATL", "Atlántico"), ("BOG", "Bogotá D.C."),
    ("BOL", "Bolívar"), ("BOY", "Boyacá"), ("CAL", "Caldas"),
    ("CAQ", "Caquetá"), ("CAU", "Cauca"), ("CES", "Cesar"),
    ("COR", "Córdoba"), ("CUN", "Cundinamarca"), ("CHO", "Chocó"),
    ("HUI", "Huila"), ("LAG", "La Guajira"), ("MAG", "Magdalena"),
    ("MET", "Meta"), ("NAR", "Nariño"), ("NSA", "Norte de Santander"),
    ("PUT", "Putumayo"), ("QUI", "Quindío"), ("RIS", "Risaralda"),
    ("SAP", "San Andrés y Providencia"), ("SAN", "Santander"),
    ("SUC", "Sucre"), ("TOL", "Tolima"), ("VAC", "Valle del Cauca"),
    ("VAU", "Vaupés"), ("VID", "Vichada"),
]


# ─────────────────────────────────────────────────────────────────────────────
# CATEGORY
# ─────────────────────────────────────────────────────────────────────────────
class Category(models.Model):
    name         = models.CharField(max_length=120, unique=True, verbose_name="Nombre")
    risk_rate    = models.FloatField(default=0.0, help_text="Tasa histórica de riesgo (0-1)")
    is_high_risk = models.BooleanField(default=False)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Categoría"
        verbose_name_plural = "Categorías"
        ordering            = ["name"]

    def __str__(self):
        flag = "⚠️" if self.is_high_risk else "✓"
        return f"{flag} {self.name}"


# ─────────────────────────────────────────────────────────────────────────────
# SELLER
# ─────────────────────────────────────────────────────────────────────────────
class Seller(models.Model):
    name                 = models.CharField(max_length=200, verbose_name="Nombre")
    email                = models.EmailField(unique=True)
    seller_state         = models.CharField(max_length=3, choices=ESTADOS_CO, blank=True, verbose_name="Departamento")
    phone                = models.CharField(max_length=20, blank=True)
    historic_risk_rate   = models.FloatField(default=0.0, help_text="Tasa histórica de riesgo del vendedor")
    total_orders_count   = models.PositiveIntegerField(default=0)
    is_new               = models.BooleanField(default=True)
    created_at           = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Vendedor"
        verbose_name_plural = "Vendedores"

    def __str__(self):
        return f"{self.name} ({self.get_seller_state_display()})"


# ─────────────────────────────────────────────────────────────────────────────
# CUSTOMER
# ─────────────────────────────────────────────────────────────────────────────
class Customer(models.Model):
    name             = models.CharField(max_length=200, verbose_name="Nombre")
    email            = models.EmailField(unique=True)
    customer_state   = models.CharField(max_length=3, choices=ESTADOS_CO, blank=True, verbose_name="Departamento")
    phone            = models.CharField(max_length=20, blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return f"{self.name} ({self.get_customer_state_display()})"


# ─────────────────────────────────────────────────────────────────────────────
# PRODUCT
# ─────────────────────────────────────────────────────────────────────────────
class Product(models.Model):
    seller        = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name="products", verbose_name="Vendedor")
    category      = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="products", verbose_name="Categoría")
    name          = models.CharField(max_length=300, verbose_name="Nombre")
    description   = models.TextField(blank=True)
    price         = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Precio")
    freight_value = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Flete")
    stock         = models.PositiveIntegerField(default=0)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return f"{self.name} — ${self.price}"


# ─────────────────────────────────────────────────────────────────────────────
# ORDER
# ─────────────────────────────────────────────────────────────────────────────
class Order(models.Model):
    class Status(models.TextChoices):
        PENDING    = "pending",    "Pendiente"
        APPROVED   = "approved",   "Aprobada"
        PROCESSING = "processing", "En proceso"
        SHIPPED    = "shipped",    "Enviada"
        DELIVERED  = "delivered",  "Entregada"
        CANCELLED  = "cancelled",  "Cancelada"

    customer           = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="orders", verbose_name="Cliente")
    status             = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    purchase_timestamp = models.DateTimeField(default=timezone.now)
    approved_at        = models.DateTimeField(null=True, blank=True)
    estimated_delivery = models.DateField(null=True, blank=True, verbose_name="Entrega estimada")
    delivered_at       = models.DateTimeField(null=True, blank=True)

    # Resumen (se recalcula automáticamente)
    total_items    = models.PositiveIntegerField(default=0)
    total_price    = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_freight  = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unique_sellers = models.PositiveIntegerField(default=0)
    same_state     = models.BooleanField(default=False)

    # Features cíclicas
    month_sin   = models.FloatField(default=0.0)
    month_cos   = models.FloatField(default=0.0)
    weekday_sin = models.FloatField(default=0.0)
    weekday_cos = models.FloatField(default=0.0)

    # Features logarítmicas
    approval_delay_log     = models.FloatField(default=0.0)
    estimated_delivery_log = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Orden"
        verbose_name_plural = "Órdenes"
        ordering            = ["-purchase_timestamp"]

    def _calc_cyclic_features(self):
        ts = self.purchase_timestamp
        self.month_sin   = math.sin(2 * math.pi * ts.month   / 12)
        self.month_cos   = math.cos(2 * math.pi * ts.month   / 12)
        self.weekday_sin = math.sin(2 * math.pi * ts.weekday() / 7)
        self.weekday_cos = math.cos(2 * math.pi * ts.weekday() / 7)

    def _calc_log_features(self):
        if self.approved_at:
            delay = max(0.0, (self.approved_at - self.purchase_timestamp).total_seconds() / 3600)
            self.approval_delay_log = math.log1p(delay)
        if self.estimated_delivery:
            from datetime import datetime, timezone as dt_tz
            est_dt = datetime.combine(self.estimated_delivery, datetime.min.time()).replace(tzinfo=dt_tz.utc)
            purchase = self.purchase_timestamp
            if timezone.is_naive(purchase):
                purchase = timezone.make_aware(purchase)
            days = max(0.0, (est_dt - purchase).total_seconds() / 86400)
            self.estimated_delivery_log = math.log1p(days)

    def recalculate_summary(self):
        items = self.items.select_related("product__seller")
        self.total_items   = items.count()
        self.total_price   = sum(i.price * i.quantity for i in items)
        self.total_freight = sum(i.freight_value for i in items)
        self.unique_sellers = items.values("product__seller").distinct().count()
        first = items.first()
        if first:
            self.same_state = (first.product.seller.seller_state == self.customer.customer_state
                               and bool(self.customer.customer_state))
        Order.objects.filter(pk=self.pk).update(
            total_items=self.total_items,
            total_price=self.total_price,
            total_freight=self.total_freight,
            unique_sellers=self.unique_sellers,
            same_state=self.same_state,
        )

    def build_feature_dict(self):
        """Construye el dict de features para el modelo de riesgo."""
        first = self.items.select_related("product__seller", "product__category").first()
        seller   = first.product.seller   if first else None
        category = first.product.category if first else None
        max_inst = self.payments.aggregate(models.Max("installments"))["installments__max"] or 1
        PRIOR = 0.11
        return {
            "total_items":               int(self.total_items),
            "unique_sellers":            int(self.unique_sellers),
            "seller_historic_risk_rate": seller.historic_risk_rate if seller else PRIOR,
            "total_freight":             float(self.total_freight),
            "category_risk_rate":        category.risk_rate if category else PRIOR,
            "month_cos":                 self.month_cos,
            "is_high_risk_category":     int(category.is_high_risk) if category else 0,
            "month_sin":                 self.month_sin,
            "customer_is_sp":            0,  # adaptado: no aplica SP en Colombia
            "same_state":                int(self.same_state),
            "estimated_delivery_log":    self.estimated_delivery_log,
            "total_price":               float(self.total_price),
            "payment_installments":      max_inst,
            "seller_historic_order_count": seller.total_orders_count if seller else 0,
            "approval_delay_log":        self.approval_delay_log,
            "weekday_sin":               self.weekday_sin,
            "weekday_cos":               self.weekday_cos,
        }

    def save(self, *args, **kwargs):
        self._calc_cyclic_features()
        self._calc_log_features()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Orden #{self.pk} — {self.customer} [{self.get_status_display()}]"


# ─────────────────────────────────────────────────────────────────────────────
# ORDER ITEM
# ─────────────────────────────────────────────────────────────────────────────
class OrderItem(models.Model):
    order         = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product       = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    quantity      = models.PositiveSmallIntegerField(default=1)
    price         = models.DecimalField(max_digits=12, decimal_places=2)
    freight_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name        = "Ítem"
        verbose_name_plural = "Ítems"

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"


# ─────────────────────────────────────────────────────────────────────────────
# PAYMENT
# ─────────────────────────────────────────────────────────────────────────────
class Payment(models.Model):
    class PaymentType(models.TextChoices):
        CREDIT_CARD = "credit_card", "Tarjeta de crédito"
        DEBIT_CARD  = "debit_card",  "Tarjeta débito"
        CASH        = "cash",        "Efectivo / PSE"
        VOUCHER     = "voucher",     "Voucher"

    order        = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    payment_type = models.CharField(max_length=20, choices=PaymentType.choices)
    installments = models.PositiveSmallIntegerField(default=1)
    amount       = models.DecimalField(max_digits=14, decimal_places=2)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Pago"
        verbose_name_plural = "Pagos"

    def __str__(self):
        return f"{self.get_payment_type_display()} — ${self.amount} ({self.installments}x)"


# ─────────────────────────────────────────────────────────────────────────────
# RISK PREDICTION
# ─────────────────────────────────────────────────────────────────────────────
class RiskPrediction(models.Model):
    order            = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="risk_prediction")
    risk_probability = models.FloatField()
    risk_label       = models.BooleanField()
    threshold_used   = models.FloatField(default=0.45)
    model_version    = models.CharField(max_length=20, default="1.0.0")
    features_snapshot = models.JSONField(default=dict, blank=True)
    predicted_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Predicción de Riesgo"
        verbose_name_plural = "Predicciones de Riesgo"

    @property
    def risk_level(self):
        if self.risk_probability >= 0.65:
            return "alto"
        if self.risk_probability >= 0.45:
            return "medio"
        return "bajo"

    def __str__(self):
        label = "⚠️ RIESGO" if self.risk_label else "✓ OK"
        return f"{label} — Orden #{self.order_id} ({self.risk_probability:.2%})"


# ─────────────────────────────────────────────────────────────────────────────
# REVIEW
# ─────────────────────────────────────────────────────────────────────────────
class Review(models.Model):
    order      = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="review")
    score      = models.PositiveSmallIntegerField(choices=[(i, f"{i} ⭐") for i in range(1, 6)])
    comment    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Reseña"
        verbose_name_plural = "Reseñas"

    @property
    def is_negative(self):
        return self.score <= 3

    def __str__(self):
        return f"{'😞' if self.is_negative else '😊'} {self.score}⭐ — Orden #{self.order_id}"
