#!env/bin/python

import requests
from bs4 import BeautifulSoup
from flask import Flask
from flask import request, abort, make_response, jsonify
from io import StringIO
import csv
from config import config


app = Flask(__name__)


@app.route('/')
def index():
    page_url = config.get('url')
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
            data_row.append(' '.join(list(map(lambda x: BeautifulSoup(str(x)).get_text(), cell.contents))).strip())
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
