from flask import Blueprint, render_template
import pandas as pd
import requests
from bs4 import BeautifulSoup

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/contact')
def contact():
    return render_template('contact.html')

@main.route('/rankings')
def rankings():
    # URL of the webpage
    url = 'https://www.footballguys.com/adp'
    # Fetch the HTML content from the URL
    response = requests.get(url)
    player_data = []
    if response.status_code == 200:
        html_content = response.text
        # Create a BeautifulSoup object
        soup = BeautifulSoup(html_content, 'html.parser')
        # Extract player data
        rows = soup.find_all('tr')
        for row in rows:
            name_td = row.find('td', class_='name sticky-col text-start')
            if name_td:
                name_a = name_td.find('a')
                if name_a:
                    player_name = name_a.get_text().strip()
                    tds = row.find_all('td')
                    if len(tds) >= 9:
                        espn_value = tds[8].get_text().strip()
                        player_data.append((player_name, espn_value))
        # Sort and create DataFrame
        player_data_sorted = sorted(player_data, key=lambda x: int(x[1]) if x[1].isdigit() else float('inf'))
        df = pd.DataFrame(player_data_sorted, columns=['Player Name', 'ESPN Ranking'])
        html_data = df.to_html(index=False, classes="table table-striped")
    else:
        html_data = "<p>Failed to retrieve data.</p>"

    return render_template('rankings.html', table=html_data)