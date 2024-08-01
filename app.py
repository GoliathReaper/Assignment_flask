from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import json

app = Flask(__name__)
app.secret_key = "your_secret_key"


def get_table_data(database, table):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {table}')
    data = cursor.fetchall()
    conn.close()
    return data


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Updating table1 data based on form submission
        try:
            conn = sqlite3.connect('database1.db')
            cursor = conn.cursor()
            cursor.execute('DELETE FROM table1')  # Clear existing data
            updated_data = []
            for key in request.form:
                if key.startswith('row_'):
                    index, column = map(int, key[4:].split('_'))
                    while len(updated_data) <= index:
                        updated_data.append([None] * 6)
                    updated_data[index][column] = request.form[key]
            for row in updated_data:
                cursor.execute('INSERT INTO table1 VALUES (?, ?, ?, ?, ?, ?)', row)
            conn.commit()
            conn.close()
            flash("Table 1 data updated successfully!", "success")
        except Exception as e:
            flash(f"Error updating Table 1 data: {e}", "danger")

    table1_data = get_table_data('database1.db', 'table1')
    table2_data = get_table_data('database2.db', 'table2')

    with open('mapping_config.json', 'r') as f:
        mapping = json.load(f)

    return render_template('index.html', table1_data=table1_data, table2_data=table2_data, mapping=mapping, enumerate=enumerate)


@app.route('/sync', methods=['POST'])
def sync_databases():
    try:
        with open('mapping_config.json', 'r') as f:
            mapping = json.load(f)

        conn1 = sqlite3.connect('database1.db')
        cursor1 = conn1.cursor()
        cursor1.execute('SELECT * FROM table1')
        table1_data = cursor1.fetchall()

        conn2 = sqlite3.connect('database2.db')
        cursor2 = conn2.cursor()
        cursor2.execute('DELETE FROM table2')

        for row in table1_data:
            mapped_row = [None] * 6
            for col1, col2 in mapping.items():
                source_index = int(col1[6:]) - 1
                target_index = int(col2[6:]) - 21
                mapped_row[target_index] = row[source_index]
            cursor2.execute(
                'INSERT INTO table2 (column21, column22, column23, column24, column25, column26) VALUES (?, ?, ?, ?, ?, ?)',
                tuple(mapped_row))
        conn2.commit()
        conn2.close()
        conn1.close()
        flash("Databases synchronized successfully!", "success")
    except Exception as e:
        flash(f"Error during synchronization: {e}", "danger")

    return redirect(url_for('index'))


@app.route('/save_mapping', methods=['POST'])
def save_mapping():
    try:
        mapping = request.form.to_dict()
        with open('mapping_config.json', 'w') as f:
            json.dump(mapping, f)
        flash("Mapping configuration saved successfully!", "success")
    except Exception as e:
        flash(f"Error saving mapping: {e}", "danger")

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
