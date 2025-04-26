import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session
import pickle
import numpy as np
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Nécessaire pour utiliser flash et session

# Charger le modèle de prédiction
model = pickle.load(open('scaler.pkl', 'rb'))

# Initialisation de la base de données SQLite
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Créer la table users pour stocker les identifiants
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT)''')
    # Créer la table predictions pour stocker les prédictions
    c.execute('''CREATE TABLE IF NOT EXISTS predictions
                 (username TEXT, input_data TEXT, prediction TEXT, timestamp TEXT)''')
    # Insérer un utilisateur par défaut (admin/password123) s'il n'existe pas
    c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ('Fabrice', '1234'))
    conn.commit()
    conn.close()

# Appeler init_db() au démarrage de l'application
init_db()

# Vérifier les identifiants dans la base de données
def check_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

# Enregistrer une prédiction dans la base de données
def save_prediction(username, input_data, prediction):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute("INSERT INTO predictions (username, input_data, prediction, timestamp) VALUES (?, ?, ?, ?)",
              (username, str(input_data), prediction, timestamp))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        username = request.form['username']
        password = request.form['password']
       
        # Vérifier les identifiants dans la base de données
        user = check_user(username, password)
       
        if user:
            session['username'] = username
            flash('Connection successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Nom d’utilisateur ou mot de passe incorrect.', 'danger')
            return redirect(url_for('login'))
   
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Vous êtes déconnecté.', 'info')
    return redirect(url_for('login'))

@app.route('/predict', methods=['POST'])
def predict():
    if 'username' not in session:
        return redirect(url_for('login'))

    input_data = [
        float(request.form['pregnancies']),
        float(request.form['glucose']),
        float(request.form['blood_pressure']),
        float(request.form['skin_thickness']),
        float(request.form['insulin']),
        float(request.form['bmi']),
        float(request.form['dpf']),
        float(request.form['age'])
    ]

    prediction = model.predict([input_data])[0]
    prediction_text = 'Diabétique' if prediction == 1 else 'Non diabétique'
   
    # Enregistrer la prédiction dans la base de données
    save_prediction(session['username'], input_data, prediction_text)

    return render_template('result.html', prediction=prediction_text)

if __name__ == '__main__':
    app.run(debug=True)