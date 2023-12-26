from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import redis

app = Flask(__name__)
app.secret_key = 'G&:<2/_xLKR9v|0&Em/9m(>P,z&Q;~'

KEYS_FOLDER = 'keys'
DATABASE_KEY = 'user_database'
licenses_in_use = {}

# Redis Configuration
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# Load data from the file into Redis
with open('TUTAJ PATH DO DB', 'r') as file:
    for line in file:
        nickname, ip_address = line.strip().split(':')
        redis_client.hset(DATABASE_KEY, nickname, f'{nickname}:{ip_address}')

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

def query_database(nickname):
    user_data = redis_client.hget(DATABASE_KEY, nickname)
    return user_data

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    license_key = request.form['license_key']
    user_ip = request.remote_addr

    if check_license(license_key, user_ip):
        session['logged_in'] = True
        return redirect(url_for('search'))
    flash('Invalid license key or already in use.')
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

@app.route('/search')
def search():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('home'))

    nickname = request.args.get('nickname', None)
    ip_address = None
    
    if nickname:
        result_data = query_database(nickname)
        if result_data:
            # Extract the IP address from the result data
            ip_address = result_data.decode('utf-8').split(':')[1]

    return render_template('search.html', nickname=nickname, results=[{'ip': ip_address}])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
