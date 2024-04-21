import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import numpy as np

def train_and_select_best_model(df):
    # Filter entries based on classification and Attack Possibility columns
    filtered_df = df[(df['classification'] == 'result') & (~df['Attack Possibility'].fillna('').str.contains('Misconfiguration Attack'))]

    if filtered_df.empty:
        print("No valid entries found for training.")
        return None, None, None, {}

    tfidf = TfidfVectorizer(max_features=500)  # Reduced features for simplicity
    X = tfidf.fit_transform(filtered_df['Entry']).toarray()
    le = LabelEncoder()
    y = le.fit_transform(filtered_df['Attack Possibility'])

    # Preparing to use cross-validation
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)  # Using StratifiedKFold for better balance in splits

    classifiers = {
        'RandomForestClassifier': RandomForestClassifier(n_estimators=100, random_state=42),  
        'LogisticRegression': LogisticRegression(max_iter=1000, C=0.5, random_state=42),  
        'KNeighborsClassifier': KNeighborsClassifier(n_neighbors=5),  
        'SVC': SVC(kernel='linear', probability=True, random_state=42)  
    }
    
    best_model, best_model_name, highest_f1 = None, None, 0
    results = {}

    for name, model in classifiers.items():
        # Cross-validated F1 score
        f1_scores = cross_val_score(model, X, y, cv=skf, scoring='f1_weighted')
        mean_f1 = np.mean(f1_scores)
        results[name] = mean_f1

        print(f"{name}:")
        print(f" - Average F1 Score: {mean_f1:.4f}")

        if mean_f1 > highest_f1:
            highest_f1 = mean_f1
            best_model_name = name
            best_model = model

    # Fit the best model on the entire dataset
    best_model.fit(X, y)

    print(f"\nBest Model: {best_model_name} with Average F1 Score: {highest_f1:.4f}")
    return best_model, tfidf, le, results

if __name__ == '__main__':
    df = pd.read_csv('Data.csv')
    best_model, tfidf, le, model_results = train_and_select_best_model(df)

    if best_model:
        # Save the components and results
        joblib.dump(best_model, 'best_model.pkl')
        joblib.dump(tfidf, 'tfidf.pkl')
        joblib.dump(le, 'label-encoder.pkl')
        print("Model components saved successfully.")
        print("Model performance results:")
        for model_name, f1_score in model_results.items():
            print(f"{model_name}: F1 Score = {f1_score:.4f}")
