from flask import Flask, render_template, request, redirect, url_for, session
import os
import requests


app = Flask(__name__)
app.secret_key = 'G&:<2/_xLKR9v|0&Em/9m(>P,z&Q;~'  # Replace with a random key for security

# Folder where the license keys are stored
KEYS_FOLDER = 'keys'

# Dictionary to track used license keys and their associated IPs
licenses_in_use = {}

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    license_key = request.form['license_key']
    user_ip = request.remote_addr  # Get user's IP address

    if check_license(license_key, user_ip):
        session['logged_in'] = True  # Set session for logged-in user
        return redirect(url_for('search'))
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)  # Remove 'logged_in' from session
    return redirect(url_for('home'))

@app.route('/search')
def search():
    nickname = request.args.get('nickname', None)
    results = []
    if nickname:
        # Perform the search and populate the results
        response_data = query_api(nickname)
        if response_data['status'] == 'ok':
            results = response_data['results']

    return render_template('search.html', nickname=nickname, results=results)


def check_license(key, user_ip):
    global licenses_in_use

    # Check if the license key is already in use and associated with the same or another IP
    if key in licenses_in_use and len(licenses_in_use[key]) < 2:
        if user_ip not in licenses_in_use[key]:
            licenses_in_use[key].append(user_ip)
        return True

    # If the key is not in use or already associated with two IPs, check if it's valid
    if is_valid_license(key):
        licenses_in_use[key] = [user_ip]  # Associate the key with the user's IP
        return True

    return False

def is_valid_license(key):
    keys_path = os.path.join(KEYS_FOLDER)

    # Read all license keys from files in the keys folder
    for filename in os.listdir(keys_path):
        with open(os.path.join(keys_path, filename), 'r') as file:
            stored_key = file.read().strip()
            if key == stored_key:
                return True

    return False

def query_api(nickname):
    if not session.get('logged_in'):  # Sprawdź, czy użytkownik jest zalogowany
        return "Unauthorized access to the API."

    url = "http://duny.demolishmc.net/api/search"
    headers = {
        'key': '381O-23VT-NR7R-I6AT',  # Klucz API
        'user': nickname
    }
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()  # Sprawdź, czy odpowiedź jest sukcesem
        return response.json()  # Zwróć odpowiedź w formacie JSON
    except requests.RequestException as e:
        return f"API Error: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
