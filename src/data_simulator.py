import pandas as pd
import numpy as np
import os

def generate_traffic_data(n_samples=2000):
    """
    Generates synthetic traffic data for SmartTransport.
    Features: hour, day_of_week, average_speed, is_weekend
    Target: traffic_level (0: Low, 1: Medium, 2: High)
    """
    np.random.seed(42)
    
    # Hour of the day (0-23)
    hour = np.random.randint(0, 24, n_samples)
    
    # Day of the week (0: Monday, 6: Sunday)
    day_of_week = np.random.randint(0, 7, n_samples)
    
    # Is weekend
    is_weekend = (day_of_week >= 5).astype(int)
    
    # Base traffic level based on hour (peak hours: 7-9 and 17-19)
    traffic_level = []
    avg_speed = []
    
    for h, d_w in zip(hour, day_of_week):
        # Heuristic for traffic level
        if (7 <= h <= 9 or 17 <= h <= 19) and d_w < 5:
            # Peak hours on weekdays
            level = np.random.choice([1, 2], p=[0.3, 0.7])
            speed = np.random.uniform(5, 20)
        elif (10 <= h <= 16 or 20 <= h <= 22) or (d_w >= 5 and 10 <= h <= 20):
            # Normal hours or weekends
            level = np.random.choice([0, 1], p=[0.4, 0.6])
            speed = np.random.uniform(20, 50)
        else:
            # Night or early morning
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
    
    return df

if __name__ == "__main__":
    print("Generating synthetic traffic data...")
    data = generate_traffic_data()
    
    os.makedirs('data', exist_ok=True)
    data_path = os.path.join('data', 'traffic_data.csv')
    data.to_csv(data_path, index=False)
    print(f"Data saved to {data_path}")
    print(data.head())
    print("\nTraffic Level Distribution:")
    print(data['traffic_level'].value_counts(normalize=True))
