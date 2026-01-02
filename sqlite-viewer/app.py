from flask import Flask, render_template_string, request
import sqlite3
import os

app = Flask(__name__)

DATABASES = {
    'test.db': '/data/test.db',
    'utility.db': '/data/utility.db'
}

def get_db_path():
    db_name = request.args.get('db', 'test.db')
    return DATABASES.get(db_name, '/data/test.db'), db_name

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>SQLite Viewer</title>
    <style>
        body { font-family: Arial; margin: 20px; background: #f5f5f5; }
        h1 { color: #333; }
        table { border-collapse: collapse; width: 100%; background: white; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        .nav { margin: 20px 0; }
        .nav a { margin-right: 15px; padding: 10px 20px; background: #4CAF50; color: white; 
                 text-decoration: none; border-radius: 4px; display: inline-block; }
        .nav a:hover { background: #45a049; }
        .db-selector { margin: 20px 0; padding: 15px; background: #e8f5e9; border-radius: 4px; }
        .db-selector select { padding: 8px; font-size: 16px; border-radius: 4px; border: 1px solid #4CAF50; }
        .sql-form { margin: 20px 0; }
        textarea { width: 100%; height: 100px; padding: 10px; font-family: monospace; }
        button { padding: 10px 20px; background: #4CAF50; color: white; border: none; 
                 border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background: #45a049; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🗄️ SQLite Database Viewer</h1>
        
        <div class="db-selector">
            <strong>Select Database:</strong>
            <select onchange="window.location.href='/?db=' + this.value">
                <option value="test.db" {% if current_db == 'test.db' %}selected{% endif %}>test.db</option>
                <option value="utility.db" {% if current_db == 'utility.db' %}selected{% endif %}>utility.db</option>
            </select>
            <span style="margin-left: 20px; color: #666;">Current: {{ db_path }}</span>
        </div>
        
        <div class="nav">
            <a href="/?db={{ current_db }}">Tables</a>
            <a href="/query?db={{ current_db }}">SQL Query</a>
        </div>
        
        {% if page == 'tables' %}
            <h2>Tables</h2>
            {% for table in tables %}
                <h3>📋 {{ table[0] }} ({{ table[1] }} rows)</h3>
                <a href="/table/{{ table[0] }}?db={{ current_db }}">View Data</a>
            {% endfor %}
        {% elif page == 'table' %}
            <h2>Table: {{ table_name }}</h2>
            <p>Total rows: {{ total_rows }}</p>
            <a href="/?db={{ current_db }}">← Back to Tables</a>
            <table>
                <tr>
                    {% for col in columns %}
                        <th>{{ col }}</th>
                    {% endfor %}
                </tr>
                {% for row in rows %}
                    <tr>
                        {% for cell in row %}
                            <td>{{ cell }}</td>
                        {% endfor %}
                    </tr>
                {% endfor %}
            </table>
        {% elif page == 'query' %}
            <h2>Run SQL Query</h2>
            <form method="POST" class="sql-form">
                <textarea name="sql" placeholder="SELECT * FROM users LIMIT 10;">{{ sql }}</textarea>
                <br><br>
                <button type="submit">Execute</button>
            </form>
            
            {% if result %}
                <h3>Results:</h3>
                <table>
                    {% if result.columns %}
                        <tr>
                            {% for col in result.columns %}
                                <th>{{ col }}</th>
                            {% endfor %}
                        </tr>
                    {% endif %}
                    {% for row in result.rows %}
                        <tr>
                            {% for cell in row %}
                                <td>{{ cell }}</td>
                            {% endfor %}
                        </tr>
                    {% endfor %}
                </table>
                <p>{{ result.count }} rows returned</p>
            {% endif %}
            
            {% if error %}
                <p style="color: red;">Error: {{ error }}</p>
            {% endif %}
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    db_path, current_db = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    table_names = cursor.fetchall()
    
    tables = []
    for (name,) in table_names:
        cursor.execute(f"SELECT COUNT(*) FROM {name}")
        count = cursor.fetchone()[0]
        tables.append((name, count))
    
    conn.close()
    
    return render_template_string(HTML_TEMPLATE, page='tables', tables=tables, 
                                 db_path=db_path, current_db=current_db)

@app.route('/table/<table_name>')
def view_table(table_name):
    db_path, current_db = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    total_rows = cursor.fetchone()[0]
    
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 100")
    rows = cursor.fetchall()
    
    conn.close()
    
    return render_template_string(HTML_TEMPLATE, page='table', table_name=table_name,
                                 columns=columns, rows=rows, total_rows=total_rows, 
                                 db_path=db_path, current_db=current_db)

@app.route('/query', methods=['GET', 'POST'])
def query():
    db_path, current_db = get_db_path()
    result = None
    error = None
    sql = ''
    
    if request.method == 'POST':
        sql = request.form.get('sql', '')
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(sql)
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            
            result = {
                'rows': rows,
                'columns': columns,
                'count': len(rows)
            }
            
            conn.close()
        except Exception as e:
            error = str(e)
    
    return render_template_string(HTML_TEMPLATE, page='query', result=result, error=error, 
                                 sql=sql, db_path=db_path, current_db=current_db)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
