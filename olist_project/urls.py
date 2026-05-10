from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/',    admin.site.urls),
    path('',          include('marketplace.urls')),
    path('modelo/',   include('olist_risk.urls')),
]
