import pandas as pd
from flask import Flask, render_template, request, jsonify
from collections import OrderedDict

app = Flask(__name__)

def excel_column_to_index(column):
    index = 0
    for char in column:
        index = index * 26 + (ord(char.upper()) - ord('A') + 1)
    return index - 1

def clean_item(item):
    if isinstance(item, (int, float)):
        return str(int(item))
    return str(item).strip()

def read_excel_columns(file_path, sheet_name, columns):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    col_indices = [excel_column_to_index(col) for col in columns]
    
    selected_columns = df.iloc[:, col_indices]
    
    custom_names = ['QB', 'RB', 'WR', 'TE']
    
    result = OrderedDict((name, [clean_item(item) for item in selected_columns.iloc[:, i].tolist() 
                   if pd.notna(item) and len(clean_item(item)) > 2 and clean_item(item) != 'Player']) 
            for i, name in enumerate(custom_names))
    
    # Add DST rankings
    dst_rankings = [
        "Dallas Cowboys", "Baltimore Ravens", "New York Jets", "Philadelphia Eagles",
        "Cleveland Browns", "Buffalo Bills", "Indianapolis Colts", "Pittsburgh Steelers",
        "Kansas City Chiefs", "Houston Texans", "Miami Dolphins", "Cincinnati Bengals",
        "San Francisco 49ers", "New York Giants", "Los Angeles Chargers", "Tampa Bay Buccaneers",
        "Washington Commanders", "Green Bay Packers", "Seattle Seahawks", "Minnesota Vikings",
        "Jacksonville Jaguars", "New Orleans Saints", "Detroit Lions", "Denver Broncos",
        "Las Vegas Raiders", "Atlanta Falcons", "New England Patriots", "Los Angeles Rams",
        "Chicago Bears", "Tennessee Titans", "Arizona Cardinals", "Carolina Panthers"
    ]
    result['DST'] = dst_rankings
    
    return result

file_path = 'rankings.xlsx'
sheet_name = "Ranks"
columns = ['B', 'Q', 'AE', 'AR']

data = read_excel_columns(file_path, sheet_name, columns)
removed_items = []

@app.route('/')
def index():
    return render_template('index.html', data=data)

@app.route('/remove_item', methods=['POST'])
def remove_item():
    column = request.json['column']
    item = request.json['item']
    if column in data and item in data[column]:
        index = data[column].index(item)
        data[column].remove(item)
        removed_items.append((column, item, index))
    return jsonify(data=data)  # Return updated data

@app.route('/undo', methods=['POST'])
def undo():
    if removed_items:
        column, item, index = removed_items.pop()
        if index < len(data[column]):
            data[column].insert(index, item)
        else:
            data[column].append(item)
    return jsonify(data=data)  # Return updated data

@app.route('/get_data', methods=['GET'])
def get_data():
    return jsonify(data=data)

if __name__ == '__main__':
    app.run(debug=True)