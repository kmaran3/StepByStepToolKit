from flask import Blueprint, render_template
import pandas as pd

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
    return render_template('rankings.html', players=df.to_dict('records'))

# Sample data for player rankings
data = {'Player': ['Player 1', 'Player 2', 'Player 3'], 'Rank': [1, 2, 3]}
df = pd.DataFrame(data)

# Endpoint to handle move up and move down
@main.route('/move', methods=['POST'])
def move_player():
    player_name = request.json['player']
    direction = request.json['direction']

    # Find the index of the player
    index = df.index[df['Player'] == player_name].tolist()[0]

    if direction == 'up' and index > 0:
        df.loc[index-1], df.loc[index] = df.loc[index], df.loc[index-1]
    elif direction == 'down' and index < len(df) - 1:
        df.loc[index+1], df.loc[index] = df.loc[index], df.loc[index+1]

    return jsonify(success=True, players=df.to_dict('records'))
