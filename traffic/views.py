from django.shortcuts import render
from django.http import JsonResponse
from .utils.data_simulator import generate_traffic_data
from .utils.model_trainer import train_model
import joblib
import os
from django.conf import settings
import pandas as pd
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views

@login_required(login_url='login')
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
        try:
            coords_str = request.POST.get('coords-display')
            hour_str = request.POST.get('hour')
            day_of_week_str = request.POST.get('day_of_week')
            avg_speed_str = request.POST.get('avg_speed')
            
            if not all([coords_str, hour_str, day_of_week_str]):
                return JsonResponse({'error': 'Veuillez remplir tous les champs (Localisation, Heure, Jour).'}, status=400)

            lat, lng = map(float, coords_str.split(','))
            hour = int(hour_str)
            day_of_week = int(day_of_week_str)
            is_weekend = 1 if day_of_week >= 5 else 0
            
            features = [lat, lng, hour, day_of_week, is_weekend]
            print(f"DEBUG: Predicting with features (len={len(features)}): {features}")
            
            model_path = settings.MODELS_ROOT / 'traffic_model.pkl'
            if not model_path.exists():
                return JsonResponse({'error': 'Model not trained yet. Please click "Train Model".'}, status=400)
                
            model = joblib.load(model_path)
            prediction = model.predict([features])[0]
            
            levels = {0: 'Faible', 1: 'Moyen', 2: 'Elevé'}
            return JsonResponse({'prediction': levels[int(prediction)]})
        except Exception as e:
            return JsonResponse({'error': f'Erreur de traitement : {str(e)}'}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def login_view(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Identifiants invalides'}, status=400)
    return render(request, 'traffic/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({'status': 'error', 'message': 'Ce nom d\'utilisateur est déjà pris.'}, status=400)
            
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return JsonResponse({'status': 'success'})
    return render(request, 'traffic/register.html')
