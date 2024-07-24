from flask import Blueprint, render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
import pandas as pd
import requests
from bs4 import BeautifulSoup
from webapp.forms import LoginForm, RegistrationForm, ListItemForm
from webapp import db, User, UserList, ListItem
import logging

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

@main.route('/rankings', methods=['GET', 'POST'])
@login_required
def rankings():
    form = ListItemForm()
    user_list = UserList.query.filter_by(user_id=current_user.id).first()
    if not user_list:
        user_list = UserList(user_id=current_user.id, name="My List")
        db.session.add(user_list)
        db.session.commit()

    if form.validate_on_submit():
        return redirect(url_for('main.save_list'))

    items = ListItem.query.filter_by(list_id=user_list.id).all()
    return render_template('rankings.html', form=form, items=items)

@main.route('/save_list', methods=['GET', 'POST'])
@login_required
def save_list():
    data = request.get_json()
    list_data = data.get('list', [])

    user_list = UserList.query.filter_by(user_id=current_user.id).first()
    if not user_list:
        user_list = UserList(user_id=current_user.id, name="My List")
        db.session.add(user_list)
        db.session.commit()

    # Clear existing items
    ListItem.query.filter_by(list_id=user_list.id).delete()

    # Add new items
    for idx, item_id in enumerate(list_data):
        new_item = ListItem(content=item_id, list_id=user_list.id)
        db.session.add(new_item)

    db.session.commit()
    return jsonify({'message': 'List saved successfully!'})

@main.route('/delete_list/<int:list_id>', methods=['POST'])
@login_required
def delete_list(list_id):
    user_list = UserList.query.filter_by(id=list_id, user_id=current_user.id).first_or_404()
    ListItem.query.filter_by(list_id=user_list.id).delete()
    db.session.delete(user_list)
    db.session.commit()
    return jsonify({'message': 'List deleted successfully!'})

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

def convert_nan_to_na(df):
    return df.where(pd.notnull(df), "NA")

@main.route('/api/ppr', methods=['GET'])
def get_ppr_data():
    df = pd.read_csv('Final Rankings/Full PPR Rankings with Weighted VBD.csv', usecols=['Rank', 'Name', 'Team', 'Position', 'Bye Week', 'ESPN ADP'])
    df = convert_nan_to_na(df)
    data = df.to_dict(orient='records')
    return jsonify(data)

@main.route('/api/half_ppr', methods=['GET'])
def get_half_ppr_data():
    df = pd.read_csv('Final Rankings/Half PPR Rankings with Weighted VBD.csv', usecols=['Rank', 'Name', 'Team', 'Position', 'Bye Week', 'ESPN ADP'])
    df = convert_nan_to_na(df)
    data = df.to_dict(orient='records')
    return jsonify(data)

@main.route('/api/standard', methods=['GET'])
def get_standard_data():
    df = pd.read_csv('Final Rankings/Non PPR Rankings with Weighted VBD.csv', usecols=['Rank', 'Name', 'Team', 'Position', 'Bye Week', 'ESPN ADP'])
    df = convert_nan_to_na(df)
    data = df.to_dict(orient='records')
    return jsonify(data)
