from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.db.models import F, Count
from django.contrib import messages

from .models import (
    Customer, Seller, Product, Category,
    Order, OrderItem, Payment, RiskPrediction,
)
from .forms import (
    CustomerForm, SellerForm, ProductForm, CategoryForm,
    OrderCreateForm, OrderStatusForm, OrderItemFormSet, PaymentForm,
)


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
def dashboard(request):
    total_orders    = Order.objects.count()
    total_products  = Product.objects.count()
    total_customers = Customer.objects.count()
    orders_at_risk  = RiskPrediction.objects.filter(risk_label=True).count()
    recent_orders   = Order.objects.select_related("customer").order_by("-purchase_timestamp")[:8]
    recent_risk     = (
        RiskPrediction.objects.filter(risk_label=True)
        .select_related("order__customer")
        .order_by("-predicted_at")[:5]
    )
    return render(request, "marketplace/dashboard.html", {
        "total_orders":    total_orders,
        "total_products":  total_products,
        "total_customers": total_customers,
        "orders_at_risk":  orders_at_risk,
        "recent_orders":   recent_orders,
        "recent_risk":     recent_risk,
    })


# ─────────────────────────────────────────────────────────────────────────────
# CUSTOMERS
# ─────────────────────────────────────────────────────────────────────────────
def customer_list(request):
    customers = Customer.objects.annotate(total_orders=Count("orders")).order_by("name")
    return render(request, "marketplace/customer_list.html", {"customers": customers})

def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    orders   = customer.orders.order_by("-purchase_timestamp")
    return render(request, "marketplace/customer_detail.html", {"customer": customer, "orders": orders})

def customer_create(request):
    form = CustomerForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Cliente creado correctamente.")
        return redirect("marketplace:customer_list")
    return render(request, "marketplace/form.html", {"form": form, "title": "Nuevo Cliente"})

def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST or None, instance=customer)
    if form.is_valid():
        form.save()
        messages.success(request, "Cliente actualizado.")
        return redirect("marketplace:customer_detail", pk=pk)
    return render(request, "marketplace/form.html", {"form": form, "title": "Editar Cliente"})

def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        customer.delete()
        messages.success(request, "Cliente eliminado.")
        return redirect("marketplace:customer_list")
    return render(request, "marketplace/confirm_delete.html", {"object": customer, "title": "Eliminar Cliente"})


# ─────────────────────────────────────────────────────────────────────────────
# SELLERS
# ─────────────────────────────────────────────────────────────────────────────
def seller_list(request):
    sellers = Seller.objects.annotate(total_products=Count("products")).order_by("name")
    return render(request, "marketplace/seller_list.html", {"sellers": sellers})

def seller_detail(request, pk):
    seller   = get_object_or_404(Seller, pk=pk)
    products = seller.products.all()
    return render(request, "marketplace/seller_detail.html", {"seller": seller, "products": products})

def seller_create(request):
    form = SellerForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Vendedor creado correctamente.")
        return redirect("marketplace:seller_list")
    return render(request, "marketplace/form.html", {"form": form, "title": "Nuevo Vendedor"})

def seller_edit(request, pk):
    seller = get_object_or_404(Seller, pk=pk)
    form   = SellerForm(request.POST or None, instance=seller)
    if form.is_valid():
        form.save()
        messages.success(request, "Vendedor actualizado.")
        return redirect("marketplace:seller_detail", pk=pk)
    return render(request, "marketplace/form.html", {"form": form, "title": "Editar Vendedor"})

def seller_delete(request, pk):
    seller = get_object_or_404(Seller, pk=pk)
    if request.method == "POST":
        seller.delete()
        messages.success(request, "Vendedor eliminado.")
        return redirect("marketplace:seller_list")
    return render(request, "marketplace/confirm_delete.html", {"object": seller, "title": "Eliminar Vendedor"})


# ─────────────────────────────────────────────────────────────────────────────
# CATEGORIES
# ─────────────────────────────────────────────────────────────────────────────
def category_list(request):
    categories = Category.objects.annotate(total_products=Count("products")).order_by("name")
    return render(request, "marketplace/category_list.html", {"categories": categories})

def category_create(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Categoría creada correctamente.")
        # Si viene de la página de producto, volver allí
        next_url = request.GET.get("next", "")
        if next_url:
            return redirect(next_url)
        return redirect("marketplace:category_list")
    return render(request, "marketplace/form.html", {"form": form, "title": "Nueva Categoría"})

def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form     = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        messages.success(request, "Categoría actualizada.")
        return redirect("marketplace:category_list")
    return render(request, "marketplace/form.html", {"form": form, "title": "Editar Categoría"})

def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Categoría eliminada.")
        return redirect("marketplace:category_list")
    return render(request, "marketplace/confirm_delete.html", {"object": category, "title": "Eliminar Categoría"})


# ─────────────────────────────────────────────────────────────────────────────
# PRODUCTS
# ─────────────────────────────────────────────────────────────────────────────
def product_list(request):
    products = Product.objects.select_related("seller", "category").order_by("name")
    return render(request, "marketplace/product_list.html", {"products": products})

def product_detail(request, pk):
    product = get_object_or_404(Product.objects.select_related("seller", "category"), pk=pk)
    return render(request, "marketplace/product_detail.html", {"product": product})

def product_create(request):
    form       = ProductForm(request.POST or None)
    categories = Category.objects.order_by("name")
    if form.is_valid():
        form.save()
        messages.success(request, "Producto creado correctamente.")
        return redirect("marketplace:product_list")
    return render(request, "marketplace/product_form.html", {
        "form": form, "title": "Nuevo Producto", "categories": categories,
    })

def product_edit(request, pk):
    product    = get_object_or_404(Product, pk=pk)
    form       = ProductForm(request.POST or None, instance=product)
    categories = Category.objects.order_by("name")
    if form.is_valid():
        form.save()
        messages.success(request, "Producto actualizado.")
        return redirect("marketplace:product_detail", pk=pk)
    return render(request, "marketplace/product_form.html", {
        "form": form, "title": "Editar Producto", "categories": categories,
    })

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        messages.success(request, "Producto eliminado.")
        return redirect("marketplace:product_list")
    return render(request, "marketplace/confirm_delete.html", {"object": product, "title": "Eliminar Producto"})


# ─────────────────────────────────────────────────────────────────────────────
# ORDERS
# ─────────────────────────────────────────────────────────────────────────────
def order_list(request):
    orders = (
        Order.objects
        .select_related("customer")
        .prefetch_related("risk_prediction")
        .order_by("-purchase_timestamp")
    )
    return render(request, "marketplace/order_list.html", {"orders": orders})

def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects
        .select_related("customer")
        .prefetch_related("items__product__seller", "items__product__category", "payments"),
        pk=pk,
    )
    risk = getattr(order, "risk_prediction", None)
    return render(request, "marketplace/order_detail.html", {"order": order, "risk": risk})

@transaction.atomic
def order_create(request):
    order_form = OrderCreateForm(request.POST or None)
    formset    = OrderItemFormSet(request.POST or None)
    pay_form   = PaymentForm(request.POST or None)

    if request.method == "POST":
        if order_form.is_valid() and formset.is_valid() and pay_form.is_valid():
            order = order_form.save()
            formset.instance = order
            items = formset.save(commit=False)
            for item in items:
                item.price         = item.product.price
                item.freight_value = item.product.freight_value
                item.save()
                Product.objects.filter(pk=item.product.pk).update(stock=F("stock") - item.quantity)
            formset.save_m2m()
            Payment.objects.create(order=order, **pay_form.cleaned_data)
            order.recalculate_summary()
            messages.success(request, f"Orden #{order.pk} creada correctamente.")
            return redirect("marketplace:order_detail", pk=order.pk)

    return render(request, "marketplace/order_create.html", {
        "order_form": order_form,
        "formset":    formset,
        "pay_form":   pay_form,
    })

def order_status_update(request, pk):
    order = get_object_or_404(Order, pk=pk)
    form  = OrderStatusForm(request.POST or None, instance=order)
    if form.is_valid():
        form.save()
        messages.success(request, f"Estado actualizado a: {order.get_status_display()}")
        return redirect("marketplace:order_detail", pk=pk)
    return render(request, "marketplace/form.html", {"form": form, "title": f"Cambiar estado — Orden #{pk}"})


# ─────────────────────────────────────────────────────────────────────────────
# RISK
# ─────────────────────────────────────────────────────────────────────────────
def risk_dashboard(request):
    predictions = (
        RiskPrediction.objects
        .select_related("order__customer")
        .order_by("-predicted_at")
    )
    total   = predictions.count()
    at_risk = predictions.filter(risk_label=True).count()
    pct     = round(at_risk / total * 100, 1) if total else 0
    return render(request, "marketplace/risk_dashboard.html", {
        "predictions": predictions[:50],
        "total":       total,
        "at_risk":     at_risk,
        "pct":         pct,
    })
