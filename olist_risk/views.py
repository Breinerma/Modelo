import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from . import ml_engine


def simulator(request):
    """Vista principal — simulador interactivo."""
    model, features, config = ml_engine.load_model()
    context = {
        'model_name': config.get('model_name', 'LightGBM'),
        'version':    config.get('version', '1.0.0'),
        'threshold':  config.get('threshold', 0.45),
        'metrics':    config.get('metrics', {}),
        'features':   features,
    }
    return render(request, 'olist_risk/simulator.html', context)


def model_info(request):
    """Vista de información del modelo."""
    _, features, config = ml_engine.load_model()
    return render(request, 'olist_risk/model_info.html', {
        'config': config,
        'features': features,
    })


# ── API Endpoints ─────────────────────────────────────────────────────────────

@require_http_methods(['GET'])
def api_health(request):
    return JsonResponse({'status': 'ok'})


@require_http_methods(['GET'])
def api_root(request):
    _, features, config = ml_engine.load_model()
    return JsonResponse({
        'status': 'online',
        'model':    config.get('model_name', 'LightGBM'),
        'version':  config.get('version', '1.0.0'),
        'threshold': config.get('threshold', 0.45),
        'features': len(features),
        'metrics':  config.get('metrics', {}),
    })


@require_http_methods(['GET'])
def api_model_info(request):
    _, features, config = ml_engine.load_model()
    return JsonResponse({
        'features':  features,
        'threshold': config.get('threshold', 0.45),
        'config':    config,
    })


@csrf_exempt
@require_http_methods(['POST'])
def api_predict(request):
    """
    POST /api/predict/
    Body JSON con los campos del pedido.
    """
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    try:
        result = ml_engine.predict(data)
        return JsonResponse(result)
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=500)
