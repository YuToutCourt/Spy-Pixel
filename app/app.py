import os
import json
import datetime
import urllib.request
import mariadb  # Import the mariadb module

from flask import Flask, send_file, request, jsonify

app = Flask(__name__)

# Modify the database connection configuration for MariaDB
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'caca'
app.config['MYSQL_PASSWORD'] = 'caca'
app.config['MYSQL_DB'] = 'caca'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # Use a dictionary cursor for easier data access

def fetch_data(ip):
    url = f"http://ipinfo.io/{ip}/json"
    response = urllib.request.urlopen(url)
    data = response.read()
    data = json.loads(data)
    return data

def insert_data(data, time_stamp, user_agent):
    conn = mariadb.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )
    cursor = conn.cursor()

    query = """
INSERT INTO Informations(
    ip,
    city,
    region,
    country,
    postal,
    loc,
    org,
    timezone,
    timestamp,
    user_agent
)
values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
    values = ( 
        data['ip'],
        data['city'],
        data['region'],
        data['country'],
        data['postal'],
        data['loc'],
        data['org'],
        data['timezone'],
        time_stamp,
        user_agent
    )

    cursor.execute(query, values)
    conn.commit()
    conn.close()

@app.route('/')
def index():
    response = jsonify({'error': 'Page not found'})
    response.status_code = 404
    return response

@app.route('/image')
def spy_pixel():
    file_path = os.path.join(os.path.dirname(__file__), 'static', 'spy_pixel.png')

    user_agent = request.headers.get('User-Agent')

    current_time = datetime.datetime.now()
    sql_time = current_time.strftime('%Y-%m-%d %H:%M:%S')

    ip = request.remote_addr

    data = fetch_data(ip)

    insert_data(data, sql_time, user_agent)

    return send_file(file_path, mimetype='image/png')

if __name__ == '__main__':
    app.run()
