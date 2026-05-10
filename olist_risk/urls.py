from django.urls import path
from . import views

# Rutas HTML del simulador (se montan bajo /modelo/)
simulator_urls = [
    path('',       views.simulator,  name='simulator'),
    path('info/',  views.model_info, name='model_info'),
]

# Rutas de la API REST (se montan bajo /api/)
api_urls = [
    path('',          views.api_root,       name='api_root'),
    path('health/',   views.api_health,     name='api_health'),
    path('predict/',  views.api_predict,    name='api_predict'),
    path('model-info/', views.api_model_info, name='api_model_info'),
]
