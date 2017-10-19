import os
from django.shortcuts import render, render_to_response, get_object_or_404
from django.views import generic
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.html import strip_tags
import requests
from bs4 import BeautifulSoup
import csv
from io import StringIO
from acmratingapp.helpers import get_short_code
import json
from acmratingapp.models import Urls
# from django.core.context_processors import csrf


# Create your views here.


class CsvView(generic.View):
    # page_url = 'http://olymp.sumdu.edu.ua:8080/tren.php'
    # page_url = 'http://ejudge.sumdu.edu.ua/cgi-bin/new-client?SID=003d5702c5891776&action=94'

    def get(self, request, *args, **kwargs):
        short_id = request.GET.get('sid', '')
        if short_id == '':
            # here we show the form

            # c = {}
            # c.update(csrf(request))
            # return render_to_response('acmratingapp/index.html', c)
            return render_to_response('acmratingapp/index.html')
        else:
            # here we show the csv

            page_url = get_object_or_404(Urls, pk=short_id)
            content = requests.get(page_url).content

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
                    data_row.append(' '.join(list(map(lambda x: strip_tags(str(x)), cell.contents))).strip())
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

    def post(self, request, *args, **kwargs):
        url = request.POST.get('url', '')
        if not (url == ''):
            short_id = get_short_code()
            b = Urls(httpurl=url, short_id=short_id)
            b.save()

            response_data = dict()
            response_data['url'] = 'http://{}/?sid={}'.format(request.get_host(), short_id)
            # return HttpResponse(json.dumps(response_data), content_type="application/json")
            return HttpResponseRedirect(response_data['url'])
        return HttpResponse(json.dumps({"error": "error occurs"}), content_type="application/json")
