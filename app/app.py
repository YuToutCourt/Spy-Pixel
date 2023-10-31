import json
import datetime
import urllib.request
import mariadb
import os

from icecream import ic
from flask import Flask, send_file, request, jsonify

app = Flask(__name__)

# Database configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'caca'
app.config['MYSQL_PASSWORD'] = 'caca'
app.config['MYSQL_DB'] = 'mydb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

def establish_db_connection():
    return mariadb.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )

def fetch_data(ip):
    url = f"http://ipinfo.io/{ip}?token=95c708f8827e83"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    return data

def duplicate_check(ip):
    conn = establish_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM Informations WHERE IP=%s"
    cursor.execute(query, (ip,))
    result = cursor.fetchone()
    conn.close()
    return result

def insert_data(data, time_stamp, user_agent):
    conn = establish_db_connection()
    cursor = conn.cursor()

    if duplicate_check(data['ip']):
        query = "UPDATE Informations SET TimeStamp=%s WHERE IP=%s"
        values = (time_stamp, data['ip'])
    else:
        query = "INSERT INTO Informations(IP,City,Region,ZIP,Localisation,Organization,TimeZone,TimeStamp,User_Agent,Country) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (
            data['ip'],
            data['city'],
            data['region'].encode("ascii", 'ignore'),
            data['postal'],
            data['loc'],
            data['org'],
            data['timezone'],
            time_stamp,
            user_agent,
            data['country']
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
    client_ip = request.headers.get('X-Forwarded-For')
    user_agent = request.headers.get('User-Agent')
    ic(client_ip)
    current_time = datetime.datetime.now()
    sql_time = current_time.strftime('%Y-%m-%d %H:%M:%S')

    ip = request.remote_addr
    ic(ip)
    data = fetch_data(ip)
    ic(data)
    insert_data(data, sql_time, user_agent)

    return send_file(file_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port="8081")