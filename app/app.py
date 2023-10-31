import os
import json
import datetime
import urllib.request

from flask import Flask, send_file, request, jsonify
from flask_mysqldb import MySQL


app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'caca'
app.config['MYSQL_PASSWORD'] = 'caca'
app.config['MYSQL_DB'] = 'caca'

mysql = MySQL(app)


def fetch_data(ip):
    url = f"http://ipinfo.io/{ip}/json"
    response = urllib.request.urlopen(url)
    data = response.read()
    data = json.loads(data)
    return data

def insert_data(data, time_stamp, user_agent):
    cursor = mysql.connection.cursor()

    query = """
INSERT INTO IP(
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
    mysql.connection.commit()
    cursor.close()


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
    time_stamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    ip = request.remote_addr

    data = fetch_data(ip)

    insert_data(data, time_stamp, user_agent)


    return send_file(file_path, mimetype='image/png')


if __name__ == '__main__':
    app.run()