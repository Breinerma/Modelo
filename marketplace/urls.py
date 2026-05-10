from django.urls import path
from . import views

app_name = "marketplace"

urlpatterns = [
    # Dashboard
    path("",                              views.dashboard,           name="dashboard"),

    # Categories
    path("categorias/",                   views.category_list,       name="category_list"),
    path("categorias/nueva/",             views.category_create,     name="category_create"),
    path("categorias/<int:pk>/editar/",   views.category_edit,       name="category_edit"),
    path("categorias/<int:pk>/borrar/",   views.category_delete,     name="category_delete"),

    # Customers
    path("clientes/",                     views.customer_list,       name="customer_list"),
    path("clientes/nuevo/",               views.customer_create,     name="customer_create"),
    path("clientes/<int:pk>/",            views.customer_detail,     name="customer_detail"),
    path("clientes/<int:pk>/editar/",     views.customer_edit,       name="customer_edit"),
    path("clientes/<int:pk>/borrar/",     views.customer_delete,     name="customer_delete"),

    # Sellers
    path("vendedores/",                   views.seller_list,         name="seller_list"),
    path("vendedores/nuevo/",             views.seller_create,       name="seller_create"),
    path("vendedores/<int:pk>/",          views.seller_detail,       name="seller_detail"),
    path("vendedores/<int:pk>/editar/",   views.seller_edit,         name="seller_edit"),
    path("vendedores/<int:pk>/borrar/",   views.seller_delete,       name="seller_delete"),

    # Products
    path("productos/",                    views.product_list,        name="product_list"),
    path("productos/nuevo/",              views.product_create,      name="product_create"),
    path("productos/<int:pk>/",           views.product_detail,      name="product_detail"),
    path("productos/<int:pk>/editar/",    views.product_edit,        name="product_edit"),
    path("productos/<int:pk>/borrar/",    views.product_delete,      name="product_delete"),

    # Orders
    path("ordenes/",                      views.order_list,          name="order_list"),
    path("ordenes/nueva/",                views.order_create,        name="order_create"),
    path("ordenes/<int:pk>/",             views.order_detail,        name="order_detail"),
    path("ordenes/<int:pk>/estado/",      views.order_status_update, name="order_status_update"),

    # Risk
    path("riesgo/",                       views.risk_dashboard,      name="risk_dashboard"),
]
