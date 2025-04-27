from flask import Flask, render_template, request, redirect, url_for, session
import joblib
import numpy as np

import sqlite3
from datetime import datetime

def log_prediction(features, result, confidence):
    conn = sqlite3.connect('predictions.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS predictions
                 (timestamp TEXT, features TEXT, result TEXT, confidence REAL)''')
    c.execute("INSERT INTO predictions VALUES (?, ?, ?, ?)",
              (datetime.now(), str(features), result, confidence))
    conn.commit()
    conn.close()


app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Load the model and scaler
model = joblib.load('diabetes_model.pkl')
scaler = joblib.load('scaler.pkl')

# Simulate a user database
users = {'Fabrice': '1234'}

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('predict'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Utilisez .get() pour éviter KeyError si les champs sont absents
        username = request.form.get('username')
        password = request.form.get('password')

        # Vérifiez que les champs ne sont pas vides
        if not username or not password:
            return render_template('login.html', error="Username and password are required")

        # Vérifiez les identifiants
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('predict'))
        else:
            return render_template('login.html', error="Invalid credentials")

    # GET : Affiche la page de connexion
    return render_template('login.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
        # Get form data
            features = [
                float(request.form['pregnancies']),
                float(request.form['glucose']),
                float(request.form['bloodpressure']),
                float(request.form['skinthickness']),
                float(request.form['insulin']),
                float(request.form['bmi']),
                float(request.form['dpf']),
                float(request.form['age'])
             ]
        
            if features[1] <= 0:  # Check that Glucose > 0
                return render_template('index.html', error="Glucose level must be greater than 0.")
        # Other validations
        except ValueError:
             return render_template('index.html', error="Please enter valid numeric values.")
        # Standardize the data
        features_scaled = scaler.transform([features])
        
        # Make a prediction
        prediction = model.predict(features_scaled)[0]
        prediction_proba = model.predict_proba(features_scaled)[0]
        
        # Interpret the result
        result = "Diabetic" if prediction == 1 else "Non-diabetic"
        confidence = prediction_proba[prediction] * 100
        
        return render_template('result.html', result=result, confidence=confidence)
    
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)