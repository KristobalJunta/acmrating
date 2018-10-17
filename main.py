#!env/bin/python

import requests
from bs4 import BeautifulSoup
from flask import Flask
from flask import make_response, render_template, request, abort
from io import StringIO
import csv
from config import config
import sqlite3
import random
import string


conn = sqlite3.connect(config.get('db'), check_same_thread=False)
cur = conn.cursor()


def get_short_code(length=6):
    char = string.ascii_uppercase + string.digits + string.ascii_lowercase

    cur.execute('SELECT uuid from urls;')
    uuids = cur.fetchall()
    uuids = [x[0] for x in uuids]

    # if the randomly generated short_id is used then generate next
    while True:
        short_id = ''.join(random.choice(char) for x in range(length))
        if short_id not in uuids:
            return short_id


def get_rating_data(page_url):
    content = requests.get(page_url).content

    soup = BeautifulSoup(content, 'html.parser')

    table = soup.find_all('table')
    if table:
        table = table[0]
    else:
        return make_response('No table found.')

    rows = table.find_all('tr')[1:]
    data_rows = []

    for row in rows:
        data_row = []
        for cell in row.find_all('td'):
            data_row.append(' '.join(list(map(
                lambda x: BeautifulSoup(str(x), 'html.parser').get_text(),
                cell.contents))).strip()
                            )
        if len(data_row[0]) == 0:
            continue
        for i in range(0, len(data_row)):
            if len(data_row[i]) == 0:
                data_row[i] = '-'
        data_rows.append(data_row)

    return data_rows


def filter_rating(rating_data, region=''):
    rating_data = [row for row in rating_data if region != '' and row[2] == region]
    for place in range(0, len(rating_data)):
        rating_data[place][0] = place + 1
    return rating_data


def get_header(rating_data):
    columns = [
        'Place',
        'User',
        'Region',
        'Total',
        'Penalty',
    ]

    letters = []
    for letter_num in range(0, len(rating_data[0]) - len(columns)):
        letters.append(chr(letter_num + ord('A')))
    columns = columns[:3] + letters + columns[3:]
    return columns


app = Flask(__name__)


@app.route('/', methods=['GET'])
def show_form():
    cur.execute("SELECT * FROM urls;")
    links = cur.fetchall()
    return render_template('index.html', links=links)


@app.route('/', methods=['POST'])
def save_url():
    link = request.form['url']
    uuid = get_short_code()

    cur.execute("INSERT INTO urls(uuid,link) VALUES(?,?)", (uuid, link))
    conn.commit()

    csv_url = "http://{}/{}".format(request.host, uuid)
    html_url = "http://{}/{}.html".format(request.host, uuid)
    return render_template('urls.html', csv_url=csv_url, html_url=html_url)


@app.route('/<uuid>', methods=['GET'])
def show_csv(uuid):
    cur.execute("SELECT link FROM urls WHERE uuid='{}';".format(uuid))
    links = cur.fetchall()
    if len(links) > 0:
        page_url = links[0][0]
    else:
        page_url = ''
        abort(404)

    rating_data = get_rating_data(page_url)
    header = get_header(rating_data)
    region = request.args.get('region')
    if region:
        rating_data = filter_rating(rating_data, region)

    out = StringIO()
    wr = csv.writer(out)

    wr.writerow(header)
    for row in rating_data:
        wr.writerow(row)

    response = make_response(out.getvalue())
    response.mimetype = 'text/csv'
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Content-disposition', 'attachment; filename={}.csv'.format(uuid))
    return response


@app.route('/<uuid>.html', methods=['GET'])
def show_table(uuid):
    cur.execute("SELECT link FROM urls WHERE uuid='{}';".format(uuid))
    links = cur.fetchall()
    if len(links) > 0:
        page_url = links[0][0]
    else:
        page_url = ''
        abort(404)

    rating_data = get_rating_data(page_url)
    columns = get_header(rating_data)

    region = request.args.get('region')
    if region:
        rating_data = filter_rating(rating_data, region)

    return render_template('table.html', data=rating_data, columns=columns)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
