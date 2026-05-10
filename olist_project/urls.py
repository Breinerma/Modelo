from django.contrib import admin
from django.urls import path, include
from olist_risk.urls import simulator_urls, api_urls

urlpatterns = [
    path('admin/',   admin.site.urls),
    path('',         include('marketplace.urls')),
    path('modelo/',  include(simulator_urls)),
    path('api/',     include(api_urls)),
]
