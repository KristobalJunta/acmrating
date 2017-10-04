import os
from django.shortcuts import render
from django.views import generic
from django.conf import settings
from django.http import HttpResponse
from django.utils.html import strip_tags
import requests
from bs4 import BeautifulSoup
import csv
from io import StringIO

# Create your views here.


class CsvView(generic.View):
    def get(self, request, *args, **kwargs):

        page = 'http://olymp.sumdu.edu.ua:8080/tren.php'
        content = requests.get(page).content

        soup = BeautifulSoup(content, 'html.parser')

        table = soup.find_all('table')
        if table:
            table = table[0]
        else:
            raise Exception('No table found')

        rows = table.find_all('tr')[1:]
        data_rows = []

        fields = [
            'Place', 'User',
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
            'Region', 'Total', 'Penalty'
        ]

        for row in rows:
            data_row = []
            for cell in row.find_all('td'):
                data_row.append(' '.join(list(map(lambda x: strip_tags(str(x)), cell.contents))))
            data_rows.append(data_row)

        # print(data_rows)
        out = StringIO()
        wr = csv.writer(out)
        for row in data_rows:
            wr.writerow(row)

        return HttpResponse(out.getvalue())
