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
from .models import SearchHistory, Favorite
import json
from django.views.decorators.http import require_POST

def home(request):
    """
    Landing page view.
    """
    return render(request, 'traffic/home.html')

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
            
            # Save history if user is authenticated
            if request.user.is_authenticated:
                try:
                    # Get source and destination from request if available (we need to update frontend to send them)
                    # For now, we'll store the coordinates as source
                    source = coords_str
                    destination = "Destination prédite" # Placeholder until we get real names
                    
                    # Check if we have source_name and dest_name in POST
                    source_name = request.POST.get('source_name')
                    dest_name = request.POST.get('dest_name')
                    
                    if source_name and dest_name:
                        SearchHistory.objects.create(
                            user=request.user,
                            source=source_name,
                            destination=dest_name
                        )
                except Exception as e:
                    print(f"Error saving history: {e}")

            return JsonResponse({'prediction': levels[int(prediction)]})
        except Exception as e:
            return JsonResponse({'error': f'Erreur de traitement : {str(e)}'}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def predict_trend(request):
    """
    Get 24h traffic trend prediction for a specific location.
    """
    try:
        lat = float(request.GET.get('lat'))
        lng = float(request.GET.get('lng'))
        day_of_week = int(request.GET.get('day_of_week', 4)) # Default to Friday
        
        model_path = settings.MODELS_ROOT / 'traffic_model.pkl'
        if not model_path.exists():
            return JsonResponse({'error': 'Model not trained'}, status=400)
            
        model = joblib.load(model_path)
        is_weekend = 1 if day_of_week >= 5 else 0
        
        trend_data = []
        for hour in range(24):
            features = [lat, lng, hour, day_of_week, is_weekend]
            # Probabilities if available, or just the class
            # Many classifiers don't support predict_proba by default depending on training
            # We'll use the class and add some noise for a smoother visualization if it's class-only
            pred_class = int(model.predict([features])[0])
            # Map classes to intensity scores (0-100)
            # Low=20, Moyen=50, High=80
            intensity = 20 if pred_class == 0 else (50 if pred_class == 1 else 80)
            
            # Add a bit of peak hour bias manually if the model is too simple
            # (In a real system, the model should learn this, but here it helps stability)
            if (hour >= 7 and hour <= 9) or (hour >= 17 and hour <= 19):
                intensity = max(intensity, 70)
                
            trend_data.append(intensity)
            
        return JsonResponse({'trend': trend_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

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
            
        if User.objects.filter(email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'Cet email est déjà utilisé.'}, status=400)
            
        user = User.objects.create_user(username=username, email=email, password=password)
        return JsonResponse({'status': 'success', 'message': 'Compte créé avec succès !'})
        
    return render(request, 'traffic/register.html')

@login_required
@require_POST
def add_favorite(request):
    try:
        data = json.loads(request.body)
        name = data.get('name')
        source = data.get('source')
        destination = data.get('destination')
        
        if not all([name, source, destination]):
            return JsonResponse({'status': 'error', 'message': 'Données incomplètes'}, status=400)
            
        Favorite.objects.create(
            user=request.user,
            name=name,
            source=source,
            destination=destination
        )
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def get_user_data(request):
    try:
        favorites = Favorite.objects.filter(user=request.user).order_by('-created_at').values('id', 'name', 'source', 'destination')
        history = SearchHistory.objects.filter(user=request.user).order_by('-timestamp')[:10].values('id', 'source', 'destination', 'timestamp')
        
        return JsonResponse({
            'status': 'success',
            'favorites': list(favorites),
            'history': list(history)
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
@require_POST
def delete_favorite(request, fav_id):
    try:
        favorite = Favorite.objects.get(id=fav_id, user=request.user)
        favorite.delete()
        return JsonResponse({'status': 'success'})
    except Favorite.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Favori non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return render(request, 'traffic/register.html')
