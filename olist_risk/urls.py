from django.urls import path
from . import views

urlpatterns = [
    # Vistas HTML
    path('',            views.simulator,   name='simulator'),
    path('modelo/',     views.model_info,  name='model_info'),

    # API REST (compatible con el HTML original)
    path('api/',             views.api_root,       name='api_root'),
    path('api/health/',      views.api_health,     name='api_health'),
    path('api/predict/',     views.api_predict,    name='api_predict'),
    path('api/model-info/',  views.api_model_info, name='api_model_info'),
]
