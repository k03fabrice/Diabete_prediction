from flask import Flask, render_template, request, redirect, url_for, flash
import joblib
import numpy as np

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Clé pour les messages flash

# Charger le modèle et le scaler
model = joblib.load('diabetes_model.pkl')
scaler = joblib.load('scaler.pkl')

# Simulation d'une base de données d'utilisateurs
users = {'Fabrice': '1234'}  # Nom d'utilisateur: mot de passe

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            return redirect(url_for('index'))
        else:
            flash('Nom d’utilisateur ou mot de passe incorrect.')
    return render_template('login.html')

@app.route('/predict', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        try:
            pregnancies = float(request.form['pregnancies'])
            glucose = float(request.form['glucose'])
            blood_pressure = float(request.form['blood_pressure'])
            skin_thickness = float(request.form['skin_thickness'])
            insulin = float(request.form['insulin'])
            bmi = float(request.form['bmi'])
            dpf = float(request.form['dpf'])
            age = float(request.form['age'])

            # Créer un tableau pour la prédiction
            input_data = np.array([[pregnancies, glucose, blood_pressure, skin_thickness,
                                   insulin, bmi, dpf, age]])
            input_data_scaled = scaler.transform(input_data)

            # Faire la prédiction
            prediction = model.predict(input_data_scaled)[0]
            result = 'Diabétique' if prediction == 1 else 'Non diabétique'

            return render_template('result.html', prediction=result)
        except ValueError:
            flash('Veuillez entrer des valeurs numériques valides.')
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)