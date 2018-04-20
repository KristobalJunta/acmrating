#!env/bin/python

import requests
from bs4 import BeautifulSoup
from flask import Flask
from flask import make_response, render_template, render_template_string, request, abort
from io import StringIO
import csv
from config import config
import sqlite3
import random
import string


conn = sqlite3.connect(config.get('db'))
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


app = Flask(__name__)


@app.route('/', methods=['GET'])
def show_form():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def save_url():
    link = request.form['url']
    uuid = get_short_code()

    cur.execute("INSERT INTO urls(uuid,link) VALUES(?,?)", (uuid, link))
    conn.commit()

    url = "http://{}/{}".format(request.host, uuid)
    response = "<a href='{}'>{}</a>".format(url, url)
    return render_template_string(response)


@app.route('/<uuid>', methods=['GET'])
def show_table(uuid):
    cur.execute("SELECT link FROM urls WHERE uuid='{}';".format(uuid))
    links = cur.fetchall()
    if len(links) > 0:
        page_url = links[0][0]
    else:
        page_url = ''
        abort(404)

    content = requests.get(page_url).content

    soup = BeautifulSoup(content, 'html.parser')

    table = soup.find_all('table')
    if table:
        table = table[0]
    else:
        return make_response('No table found.')

    rows = table.find_all('tr')[1:]
    data_rows = []

    # fields
    # 'Place', 'User', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'Region', 'Total', 'Penalty'

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

    out = StringIO()
    wr = csv.writer(out)
    for row in data_rows:
        wr.writerow(row)

    response = make_response(out.getvalue())
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0')
