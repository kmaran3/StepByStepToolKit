from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required, LoginManager, UserMixin
import pandas as pd
import requests
from bs4 import BeautifulSoup
from .forms import LoginForm


main = Blueprint('main', __name__)

class User(UserMixin):
    def __init__(self, username):
        self.id = username

users = {'admin': {'password': 'secret'}}

@main.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('main.home'))
        else:
            flash('Invalid username or password')
    return render_template('login.html', form=form)

@main.route('/home')
#@login_required
def home():
    return render_template('home.html')

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))

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

@main.route('/mockdraft', methods=['GET', 'POST'])
def mock_draft():
    if request.method == 'POST':
        draft_position = request.form['position']
        player_data = fetch_player_data()  # Call function to fetch data
        return render_template('mockdraft.html', player_data=player_data, draft_position=draft_position)
    else:
        return render_template('mockdraft.html')

def fetch_player_data():
    url = 'https://www.footballguys.com/adp'
    response = requests.get(url)
    player_data = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
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
        player_data_sorted = sorted(player_data, key=lambda x: int(x[1]) if x[1].isdigit() else float('inf'))
        return player_data_sorted
    else:
        return []
