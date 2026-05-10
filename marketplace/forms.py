from django import forms
from .models import Customer, Seller, Product, Category, Order, OrderItem, Payment


class CustomerForm(forms.ModelForm):
    class Meta:
        model  = Customer
        fields = ["name", "email", "customer_state", "phone"]
        widgets = {
            "name":           forms.TextInput(attrs={"class": "form-control"}),
            "email":          forms.EmailInput(attrs={"class": "form-control"}),
            "customer_state": forms.Select(attrs={"class": "form-select"}),
            "phone":          forms.TextInput(attrs={"class": "form-control"}),
        }


class SellerForm(forms.ModelForm):
    class Meta:
        model  = Seller
        fields = ["name", "email", "seller_state", "phone"]
        widgets = {
            "name":         forms.TextInput(attrs={"class": "form-control"}),
            "email":        forms.EmailInput(attrs={"class": "form-control"}),
            "seller_state": forms.Select(attrs={"class": "form-select"}),
            "phone":        forms.TextInput(attrs={"class": "form-control"}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model  = Category
        fields = ["name", "risk_rate", "is_high_risk"]
        widgets = {
            "name":      forms.TextInput(attrs={"class": "form-control"}),
            "risk_rate": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0", "max": "1"}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model  = Product
        fields = ["name", "description", "seller", "category", "price", "freight_value", "stock"]
        widgets = {
            "name":          forms.TextInput(attrs={"class": "form-control"}),
            "description":   forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "seller":        forms.Select(attrs={"class": "form-select"}),
            "category":      forms.Select(attrs={"class": "form-select"}),
            "price":         forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "freight_value": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "stock":         forms.NumberInput(attrs={"class": "form-control"}),
        }


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model  = Order
        fields = ["customer", "estimated_delivery"]
        widgets = {
            "customer":           forms.Select(attrs={"class": "form-select"}),
            "estimated_delivery": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model  = Order
        fields = ["status"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
        }


class OrderItemForm(forms.ModelForm):
    """
    Formulario de ítem con filtro de categoría.
    El campo 'category_filter' no es un campo del modelo — solo sirve
    para filtrar el select de productos vía JS en el template.
    """
    category_filter = forms.ModelChoiceField(
        queryset=Category.objects.all().order_by("name"),
        required=False,
        empty_label="— Todas las categorías —",
        label="Filtrar por categoría",
        widget=forms.Select(attrs={"class": "form-select category-filter"}),
    )

    class Meta:
        model  = OrderItem
        fields = ["product", "quantity"]
        widgets = {
            "product":  forms.Select(attrs={"class": "form-select product-select"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Incluir categoría en el label del producto para poder filtrar por JS
        self.fields["product"].queryset = (
            Product.objects.select_related("category", "seller")
            .filter(stock__gt=0)
            .order_by("name")
        )
        self.fields["product"].label_from_instance = lambda p: (
            f"{p.name} — ${p.price} "
            f"[{p.category.name if p.category else 'Sin categoría'}] "
            f"(Stock: {p.stock})"
        )


OrderItemFormSet = forms.inlineformset_factory(
    Order, OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class PaymentForm(forms.ModelForm):
    class Meta:
        model  = Payment
        fields = ["payment_type", "installments", "amount"]
        widgets = {
            "payment_type": forms.Select(attrs={"class": "form-select"}),
            "installments": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
            "amount":       forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }
