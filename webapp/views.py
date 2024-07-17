from flask import Blueprint, render_template, url_for, flash, redirect, request, send_from_directory
from flask_login import login_user, current_user, logout_user, login_required, LoginManager, UserMixin
import pandas as pd
import requests
from bs4 import BeautifulSoup
from webapp.forms import LoginForm, RegistrationForm
from webapp import db, User


main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(id=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('main.home'))
        else:
            flash('Invalid username or password')
    return render_template('login.html', form=form)

@main.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.login'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(id=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering! Please log in.')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/home')
@login_required
def home():
    return render_template('home.html')


@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/contact')
def contact():
    return render_template('contact.html')

def get_csv_data(filename):
    # Read CSV file and select specific columns
    df = pd.read_csv(filename, usecols=['Name', 'Team', 'Position', 'ESPN ADP'])
    # Convert to HTML table
    html_table = df.to_html(classes='table table-striped', index=False)
    return html_table

@main.route('/rankings')
@login_required
def rankings():
    ppr_table = get_csv_data('/Users/kmaran3/Dropbox/Darkhorse/Final Rankings/Full PPR Rankings with Weighted VBD.csv')
    half_ppr_table = get_csv_data('/Users/kmaran3/Dropbox/Darkhorse/Final Rankings/Half PPR Rankings with Weighted VBD.csv')
    standard_table = get_csv_data('/Users/kmaran3/Dropbox/Darkhorse/Final Rankings/Non PPR Rankings with Weighted VBD.csv')
    return render_template('rankings.html', ppr_table=ppr_table, half_ppr_table=half_ppr_table, standard_table=standard_table)

@main.route('/Users/kmaran3/Dropbox/Darkhorse/Final Rankings/Half PPR Rankings with Weighted VBD.csv')
def get_csv(filename):
    return send_from_directory('/Users/kmaran3/Dropbox/Darkhorse/Final Rankings', filename)

@main.route('/mockdraft', methods=['GET', 'POST'])
@login_required
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
