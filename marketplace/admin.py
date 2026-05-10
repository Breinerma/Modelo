from django.contrib import admin
from .models import Category, Seller, Customer, Product, Order, OrderItem, Payment, RiskPrediction, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ["name", "risk_rate", "is_high_risk", "updated_at"]
    list_filter   = ["is_high_risk"]
    search_fields = ["name"]


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display  = ["name", "email", "seller_state", "historic_risk_rate", "total_orders_count", "is_new"]
    list_filter   = ["seller_state", "is_new"]
    search_fields = ["name", "email"]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display  = ["name", "email", "customer_state", "created_at"]
    list_filter   = ["customer_state"]
    search_fields = ["name", "email"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ["name", "seller", "category", "price", "freight_value", "stock"]
    list_filter   = ["category", "seller"]
    search_fields = ["name"]


class OrderItemInline(admin.TabularInline):
    model  = OrderItem
    extra  = 0
    fields = ["product", "quantity", "price", "freight_value"]

class PaymentInline(admin.TabularInline):
    model  = Payment
    extra  = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ["pk", "customer", "status", "total_price", "purchase_timestamp"]
    list_filter   = ["status"]
    search_fields = ["customer__name"]
    inlines       = [OrderItemInline, PaymentInline]


@admin.register(RiskPrediction)
class RiskPredictionAdmin(admin.ModelAdmin):
    list_display  = ["order", "risk_probability", "risk_label", "model_version", "predicted_at"]
    list_filter   = ["risk_label"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["order", "score", "is_negative", "created_at"]
