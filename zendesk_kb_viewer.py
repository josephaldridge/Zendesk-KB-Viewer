from flask import Flask, render_template, request, send_file
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, date
import json
import io

app = Flask(__name__)

# Your Zendesk credentials
ZENDESK_EMAIL = 'joseph.aldridge@libtax.com'
ZENDESK_TOKEN = 'AedBgugdObrAKXm1iCjGIM8JlPvQFDCGGk9DZ4k3'

BRANDS = [
    {'name': 'USA', 'url': 'https://libertytax.zendesk.com/api/v2/help_center/articles.json'},
    {'name': 'Canada', 'url': 'https://supportcentralcanada.libertytax.net/api/v2/help_center/articles.json'}
]

def fetch_articles(from_date=None, to_date=None, selected_country=None):
    all_articles = []
    auth = HTTPBasicAuth(f'{ZENDESK_EMAIL}/token', ZENDESK_TOKEN)

    for brand in BRANDS:
        if selected_country and brand['name'] != selected_country:
            continue

        url = brand['url']
        while url:
            response = requests.get(url, auth=auth)
            if response.status_code != 200:
                break

            data = response.json()
            for article in data.get('articles', []):
                created_at = datetime.fromisoformat(article['created_at'][:-1])

                if from_date and created_at < from_date:
                    continue
                if to_date and created_at > to_date:
                    continue

                article['Country'] = brand['name']
                all_articles.append(article)

            url = data.get('next_page')

    return all_articles

@app.route('/', methods=['GET', 'POST'])
def index():
    articles = []
    from_date_str = request.form.get('from_date')
    to_date_str = request.form.get('to_date') or date.today().isoformat()
    selected_country = request.form.get('country')

    from_date = datetime.fromisoformat(from_date_str) if from_date_str else None
    to_date = datetime.fromisoformat(to_date_str) if to_date_str else None

    if request.method == 'POST':
        articles = fetch_articles(from_date, to_date, selected_country)

    return render_template('index.html', articles=articles, from_date=from_date_str, to_date=to_date_str, selected_country=selected_country)

@app.route('/export', methods=['POST'])
def export():
    from_date_str = request.form.get('from_date')
    to_date_str = request.form.get('to_date') or date.today().isoformat()
    selected_country = request.form.get('country')

    try:
        from_date = datetime.fromisoformat(from_date_str) if from_date_str else None
    except ValueError:
        from_date = None

    try:
        to_date = datetime.fromisoformat(to_date_str) if to_date_str else None
    except ValueError:
        to_date = None

    articles = fetch_articles(from_date, to_date, selected_country)
    json_data = json.dumps(articles, indent=2)
    buffer = io.BytesIO()
    buffer.write(json_data.encode('utf-8'))
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name='zendesk_articles.json', mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

app = Flask(__name__)

# Your Zendesk credentials
ZENDESK_EMAIL = 'joseph.aldridge@libtax.com'
ZENDESK_TOKEN = 'AedBgugdObrAKXm1iCjGIM8JlPvQFDCGGk9DZ4k3'
ZENDESK_SUBDOMAIN = 'libertytax'

ZENDESK_URL = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/help_center/articles.json"

def fetch_articles(from_date=None, to_date=None):
    all_articles = []
    url = ZENDESK_URL
    auth = HTTPBasicAuth(f'{ZENDESK_EMAIL}/token', ZENDESK_TOKEN)

    while url:
        response = requests.get(url, auth=auth)
        if response.status_code != 200:
            break

        data = response.json()
        for article in data.get('articles', []):
            created_at = datetime.fromisoformat(article['created_at'][:-1])

            if from_date and created_at < from_date:
                continue
            if to_date and created_at > to_date:
                continue

            all_articles.append(article)

        url = data.get('next_page')

    return all_articles

@app.route('/', methods=['GET', 'POST'])
def index():
    articles = []
    from_date_str = request.form.get('from_date')
    to_date_str = request.form.get('to_date')

    from_date = datetime.fromisoformat(from_date_str) if from_date_str else None
    to_date = datetime.fromisoformat(to_date_str) if to_date_str else None

    if request.method == 'POST':
        articles = fetch_articles(from_date, to_date)

    return render_template('index.html', articles=articles, from_date=from_date_str, to_date=to_date_str)

if __name__ == '__main__':
    app.run(debug=True)
