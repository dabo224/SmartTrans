import pandas as pd
import numpy as np
import os
from django.conf import settings

def generate_traffic_data(n_samples=3000):
    """
    Generates realistic traffic data with location-based hotspots.
    Features: lat, lng, hour, day_of_week, avg_speed, is_weekend
    """
    np.random.seed(42)
    
    # Simulate Abidjan area roughly [5.3, -4.0]
    lat = np.random.uniform(5.30, 5.40, n_samples)
    lng = np.random.uniform(-4.05, -3.95, n_samples)
    hour = np.random.randint(0, 24, n_samples)
    day_of_week = np.random.randint(0, 7, n_samples)
    is_weekend = (day_of_week >= 5).astype(int)
    
    # Define Hotspots (City centers/Main bridges)
    hotspots = [
        {'lat': 5.33, 'lng': -4.02}, # Plateau
        {'lat': 5.37, 'lng': -3.99}  # Cocody/Hervé
    ]
    
    traffic_level = []
    
    for i in range(n_samples):
        h = hour[i]
        d_w = day_of_week[i]
        l1, l2 = lat[i], lng[i]
        
        # Distance to nearest hotspot
        min_dist = min([np.sqrt((l1-hs['lat'])**2 + (l2-hs['lng'])**2) for hs in hotspots])
        is_near_hotspot = min_dist < 0.015
        
        # Base logic with higher variance
        if (7 <= h <= 9 or 17 <= h <= 19) and d_w < 5:
            # Peak hours: mostly high, some medium
            level = np.random.choice([0, 1, 2], p=[0.05, 0.25, 0.7]) if is_near_hotspot else np.random.choice([0, 1, 2], p=[0.2, 0.4, 0.4])
        elif is_near_hotspot and (8 <= h <= 20):
            # Busy areas stay dense during the day
            level = np.random.choice([1, 2], p=[0.4, 0.6])
        elif (10 <= h <= 16 or 20 <= h <= 22) or (d_w >= 5 and 10 <= h <= 18):
            # Normal hours: mostly low or medium
            level = np.random.choice([0, 1, 2], p=[0.5, 0.4, 0.1])
        else:
            # Night/Early morning: mostly low
            level = np.random.choice([0, 1], p=[0.9, 0.1])
            
        traffic_level.append(level)
        
    df = pd.DataFrame({
        'lat': lat,
        'lng': lng,
        'hour': hour,
        'day_of_week': day_of_week,
        'is_weekend': is_weekend,
        'traffic_level': traffic_level
    })
    
    data_path = settings.DATA_ROOT / 'traffic_data.csv'
    df.to_csv(data_path, index=False)
    return df
