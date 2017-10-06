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

    page_url = 'http://olymp.sumdu.edu.ua:8080/tren.php'

    def get(self, request, *args, **kwargs):
        content = requests.get(self.page_url).content

        soup = BeautifulSoup(content, 'html.parser')

        table = soup.find_all('table')
        if table:
            table = table[0]
        else:
            raise Exception('No table found')

        rows = table.find_all('tr')[1:]
        data_rows = []

        # fields
        # 'Place', 'User', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'Region', 'Total', 'Penalty'

        for row in rows:
            data_row = []
            for cell in row.find_all('td'):
                data_row.append(' '.join(list(map(lambda x: strip_tags(str(x)), cell.contents))).replace(u"\u00A0", ''))
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

        return HttpResponse(out.getvalue())
