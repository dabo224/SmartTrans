import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

def train_model():
    data_path = os.path.join('data', 'traffic_data.csv')
    if not os.path.exists(data_path):
        print("Data file not found. Run data_simulator.py first.")
        return

    df = pd.read_csv(data_path)
    
    # Features and Target
    X = df[['hour', 'day_of_week', 'is_weekend', 'avg_speed']]
    y = df['traffic_level']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Initialize and train model
    print("Training RandomForest model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    print("\nModel Evaluation:")
    print(classification_report(y_test, y_pred, target_names=['Low', 'Medium', 'High']))
    
    # Save model
    os.makedirs('models', exist_ok=True)
    model_path = os.path.join('models', 'traffic_model.pkl')
    joblib.dump(model, model_path)
    print(f"\nModel saved to {model_path}")
    
    # Save feature names to ensure consistency in the app
    features_path = os.path.join('models', 'features.joblib')
    joblib.dump(list(X.columns), features_path)

if __name__ == "__main__":
    train_model()
