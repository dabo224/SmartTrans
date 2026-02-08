from django.shortcuts import render
from django.http import JsonResponse
from .utils.data_simulator import generate_traffic_data
from .utils.model_trainer import train_model
import joblib
import os
from django.conf import settings
import pandas as pd

def index(request):
    """
    Dashboard view.
    """
    model_path = settings.MODELS_ROOT / 'traffic_model.pkl'
    model_exists = model_path.exists()
    
    context = {
        'model_exists': model_exists,
    }
    return render(request, 'traffic/index.html', context)

def simulate(request):
    """
    Trigger data simulation and model training.
    """
    generate_traffic_data()
    report = train_model()
    return JsonResponse({'status': 'success', 'report': report})

def predict(request):
    """
    Get traffic prediction.
    """
    if request.method == 'POST':
        hour = int(request.POST.get('hour'))
        day_of_week = int(request.POST.get('day_of_week'))
        is_weekend = 1 if day_of_week >= 5 else 0
        avg_speed = float(request.POST.get('avg_speed'))
        
        model_path = settings.MODELS_ROOT / 'traffic_model.pkl'
        if not model_path.exists():
            return JsonResponse({'error': 'Model not trained yet.'}, status=400)
            
        model = joblib.load(model_path)
        prediction = model.predict([[hour, day_of_week, is_weekend, avg_speed]])[0]
        
        levels = {0: 'Low', 1: 'Medium', 2: 'High'}
        return JsonResponse({'prediction': levels[int(prediction)]})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
