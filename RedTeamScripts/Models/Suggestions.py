import os
import subprocess
import pandas as pd
import re
import sys
import joblib
import nltk
import json
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from collections import Counter

# Ensure necessary NLTK resources are downloaded
nltk.download('punkt')
nltk.download('stopwords')

def run_docker_benchmark():
    # read from file
    with open("log/docker-bench-security.log", "r") as log_file:
        benchmark_output = log_file.read()

    return benchmark_output

def load_model(filepath):
    """
    Load a trained model from a file.
    """
    model = joblib.load(filepath)
    # print(f"Model loaded from {filepath}")
    return model

def load_vectorizer(filepath):
    """
    Load the TfidfVectorizer object from a file.
    """
    vectorizer = joblib.load(filepath)
    # print(f"TfidfVectorizer loaded from {filepath}")
    return vectorizer

def load_label_encoder(filepath):
    """
    Load the LabelEncoder object from a file.
    """
    le = joblib.load(filepath)
    # print(f"LabelEncoder loaded from {filepath}")
    return le

def classify_output(output):
    """
    Splits and classifies the output into entries.
    """
    lines = output.split('\n')
    df = pd.DataFrame({'Entry': lines})
    df['classification'] = df['Entry'].apply(lambda entry: 'result' if '*' in entry else 'check')
    return df

def clean_entry(entry):
    """
    Cleans the entry text by removing unnecessary patterns and numbers.
    """
    pattern = r'^.*?\*\s*(.*)'  # Updated pattern
    match = re.search(pattern, entry)
    if match:
        return match.group(1)
    return entry

def clean_output(df):
    """
    Applies cleaning to each entry classified as 'result'.
    """
    df_result = df[df['classification'] == 'result'].copy()
    df_result['Entry'] = df_result['Entry'].apply(clean_entry)
    return df_result

def preprocess_text(text):
    """
    Preprocesses text by tokenizing, removing punctuation and stopwords, and applying stemming.
    """
    tokens = word_tokenize(text)
    tokens = [token.lower() for token in tokens if token.isalnum()]
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if not token in stop_words]
    stemmer = PorterStemmer()
    tokens = [stemmer.stem(token) for token in tokens]
    return ' '.join(tokens)

def preprocess_dataframe(df, container_name, image_name, container_id):
    """
    Filters and preprocesses the DataFrame entries containing the container_name, image_name, or container_id.
    """
    df_filtered = df[(df['Entry'].str.contains(container_name) |
                      df['Entry'].str.contains(image_name) |
                      df['Entry'].str.contains(container_id))].copy()
    # print(df_filtered.head())
    # Use .loc to avoid SettingWithCopyWarning
    df_filtered.loc[:, 'Preprocessed_Entry'] = df_filtered['Entry'].apply(preprocess_text)
    return df_filtered


def predict_attack_possibility(best_model, tfidf, le, df, threshold=0.3):
    """
    Predicts the best attack possibility for the given DataFrame using a probability threshold.
    Returns only the name of the most likely attack above a specified confidence threshold.
    """
    if df.empty:
        # print("No valid data for predictions.")
        return "No valid data for predictions"

    X = tfidf.transform(df['Preprocessed_Entry']).toarray()
    probabilities = best_model.predict_proba(X)
    best_prob_indices = np.argmax(probabilities, axis=1)
    best_probs = probabilities[np.arange(len(best_prob_indices)), best_prob_indices]

    # Identify the highest probability
    max_index = np.argmax(best_probs)
    max_probability = best_probs[max_index]
    max_attack_index = best_prob_indices[max_index]

    # Check if the highest probability is above the threshold and return the corresponding attack name
    if max_probability > threshold:
        best_attack = le.inverse_transform([max_attack_index])[0]
        return best_attack
    else:
        return "Uncertain"

if __name__ == '__main__':
    if len(sys.argv) < 4:
        # print("Usage: python script.py <container_name> <image_name> <container_id>")
        sys.exit(1)

    container_name, image_name, container_id = sys.argv[1], sys.argv[2], sys.argv[3]
    # print(f"Selected container for analysis: {container_name}, Image: {image_name}, Container ID: {container_id}")

    # current working directory
    cwd = os.getcwd()
    model_file = os.path.join(cwd, "RedTeamScripts/Models/best_model.pkl")
    vectorizer_file = os.path.join(cwd, "RedTeamScripts/Models/tfidf.pkl")
    label_encoder_file = os.path.join(cwd, "RedTeamScripts/Models/label-encoder.pkl")

    best_model = load_model(model_file)
    tfidf = load_vectorizer(vectorizer_file)
    le = load_label_encoder(label_encoder_file)

    benchmark_output = run_docker_benchmark()
    df_classified = classify_output(benchmark_output)
    df_cleaned = clean_output(df_classified)
    preprocessed_df = preprocess_dataframe(df_cleaned, container_name, image_name, container_id)
    df_predictions = predict_attack_possibility(best_model, tfidf, le, preprocessed_df)

    output = {
        "suggestions": df_predictions,
    }

    print(json.dumps(output, indent=2))