import pandas as pd
import numpy as np
import os
from django.conf import settings

def generate_traffic_data(n_samples=2000):
    """
    Generates synthetic traffic data for SmartTransport.
    Features: hour, day_of_week, average_speed, is_weekend
    Target: traffic_level (0: Low, 1: Medium, 2: High)
    """
    np.random.seed(42)
    
    hour = np.random.randint(0, 24, n_samples)
    day_of_week = np.random.randint(0, 7, n_samples)
    is_weekend = (day_of_week >= 5).astype(int)
    
    traffic_level = []
    avg_speed = []
    
    for h, d_w in zip(hour, day_of_week):
        if (7 <= h <= 9 or 17 <= h <= 19) and d_w < 5:
            level = np.random.choice([1, 2], p=[0.3, 0.7])
            speed = np.random.uniform(5, 20)
        elif (10 <= h <= 16 or 20 <= h <= 22) or (d_w >= 5 and 10 <= h <= 20):
            level = np.random.choice([0, 1], p=[0.4, 0.6])
            speed = np.random.uniform(20, 50)
        else:
            level = 0
            speed = np.random.uniform(50, 80)
            
        traffic_level.append(level)
        avg_speed.append(speed)
        
    df = pd.DataFrame({
        'hour': hour,
        'day_of_week': day_of_week,
        'is_weekend': is_weekend,
        'avg_speed': avg_speed,
        'traffic_level': traffic_level
    })
    
    data_path = settings.DATA_ROOT / 'traffic_data.csv'
    df.to_csv(data_path, index=False)
    return df
