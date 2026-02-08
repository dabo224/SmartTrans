import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from django.conf import settings

def train_model():
    data_path = settings.DATA_ROOT / 'traffic_data.csv'
    if not data_path.exists():
        return {"error": "Data file not found."}

    df = pd.read_csv(data_path)
    
    X = df[['hour', 'day_of_week', 'is_weekend', 'avg_speed']]
    y = df['traffic_level']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, target_names=['Low', 'Medium', 'High'], output_dict=True)
    
    model_path = settings.MODELS_ROOT / 'traffic_model.pkl'
    joblib.dump(model, model_path)
    
    features_path = settings.MODELS_ROOT / 'features.joblib'
    joblib.dump(list(X.columns), features_path)
    
    return report
