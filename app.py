from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = 'G&:<2/_x£KR9v|0&Em/9m(>P,z&Q;~'  # Replace with a random key for security

def check_login(username, password):
    return username == "123" and password == "123"

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if check_login(username, password):
        session['logged_in'] = True  # Set session for logged in user
        return redirect(url_for('search'))
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)  # Remove 'logged_in' from session
    return redirect(url_for('home'))

@app.route('/search')
def search():
    if not session.get('logged_in'):  # Check if user is logged in
        return redirect(url_for('home'))

    nickname = request.args.get('nickname', '')
    results = query_api(nickname) if nickname else ""
    return render_template('search.html', results=results)

def query_api(nickname):
    url = "http://duny.demolishmc.net/api/search"
    headers = {
        'key': '1PSG-D9WP-U47V-6QFL',
        'user': nickname
    }
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data['status'] == 'ok':
            return data['results']
        else:
            return f"Error in response: {data.get('status')}"
    except requests.RequestException as e:
        return f"API Error: {e}"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
