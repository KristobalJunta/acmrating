acmrating

# ACM Rating table filter

A simple Flask app to parse, display and export data from ACM ICPC rating tables.

## Features

- Export table data to CSV
- Display custom html table with standings
- Filter by region (using `?region=<desired region here>`

## Dependencies

- Python 3
- beautifulsoup4
- Flask
- Jinja2
- Werkzeug

## Installation & Launch

- Create virtual env
- `pip install -r requirements.txt`
- `./serve.sh` or `FLASK_APP=main.py flask run --host=0.0.0.0` (development purposes only)
- use uWSGI to run it on a real server

## Contribution

Feel free to do so :)
