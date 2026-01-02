from flask import Flask, render_template_string, request, jsonify, send_file
import sqlite3
import os
import csv
import io

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
    <title>🗄️ SQLite Database Manager</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1400px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); }
        
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 8px; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 32px; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }
        .header-info { opacity: 0.9; font-size: 14px; }
        
        .db-selector { margin: 20px 0; padding: 20px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 8px; display: flex; align-items: center; gap: 15px; }
        .db-selector strong { color: #333; font-size: 16px; }
        .db-selector select { padding: 10px 15px; font-size: 16px; border-radius: 6px; border: 2px solid #667eea; background: white; cursor: pointer; min-width: 200px; transition: all 0.3s; }
        .db-selector select:hover { border-color: #764ba2; }
        .db-selector select:focus { outline: none; border-color: #764ba2; box-shadow: 0 0 0 3px rgba(118, 75, 162, 0.1); }
        .db-path { color: #666; font-size: 14px; margin-left: auto; }
        
        .nav { display: flex; gap: 10px; margin: 20px 0; flex-wrap: wrap; }
        .nav a, .btn { padding: 12px 24px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; 
                 text-decoration: none; border-radius: 6px; display: inline-block; font-weight: 500; transition: all 0.3s; 
                 box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4); border: none; cursor: pointer; font-size: 14px; }
        .nav a:hover, .btn:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(102, 126, 234, 0.6); }
        
        h2 { color: #333; margin: 30px 0 15px 0; font-size: 24px; }
        h3 { color: #555; margin: 20px 0 10px 0; padding-bottom: 8px; border-bottom: 3px solid #667eea; font-size: 18px; display: flex; align-items: center; justify-content: space-between; }
        
        .table-card { background: #f8f9fa; padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #667eea; }
        .table-name { font-size: 18px; font-weight: 600; color: #333; margin-bottom: 5px; }
        .table-info { color: #666; font-size: 14px; margin-bottom: 10px; }
        .table-actions a { font-size: 14px; }
        
        table { border-collapse: collapse; width: 100%; background: white; margin: 20px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; }
        th, td { border: 1px solid #e0e0e0; padding: 12px 16px; text-align: left; }
        th { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; font-weight: 600; position: sticky; top: 0; z-index: 10; }
        tr:nth-child(even) { background-color: #f8f9fa; }
        tr:hover { background-color: #e8eaf6; transition: background-color 0.2s; }
        
        .sql-form { margin: 20px 0; }
        textarea { width: 100%; min-height: 150px; padding: 15px; font-family: 'Courier New', monospace; font-size: 14px; 
                   border: 2px solid #e0e0e0; border-radius: 8px; resize: vertical; }
        textarea:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1); }
        
        button { padding: 12px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; 
                 border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: 500; transition: all 0.3s; 
                 box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4); margin-top: 10px; }
        button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(102, 126, 234, 0.6); }
        
        .badge { padding: 4px 12px; background: #667eea; color: white; border-radius: 12px; font-size: 12px; font-weight: 600; }
        .error { color: #dc3545; background: #f8d7da; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #dc3545; }
        .success { color: #155724; background: #d4edda; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #28a745; }
        
        .result-info { margin: 15px 0; padding: 12px; background: #e8eaf6; border-radius: 6px; color: #333; }
        .export-btn { background: linear-gradient(135deg, #28a745 0%, #20c997 100%); margin-left: 10px; }
        
        @media (max-width: 768px) {
            .container { padding: 15px; }
            .db-selector { flex-direction: column; align-items: flex-start; }
            .nav { flex-direction: column; }
            table { font-size: 12px; }
            th, td { padding: 8px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗄️ SQLite Database Manager</h1>
            <div class="header-info">Professional SQLite Database Viewer & Query Tool</div>
        </div>
        
        <div class="db-selector">
            <strong>📂 Select Database:</strong>
            <select onchange="window.location.href='/?db=' + this.value">
                <option value="test.db" {% if current_db == 'test.db' %}selected{% endif %}>🔵 test.db (Production)</option>
                <option value="utility.db" {% if current_db == 'utility.db' %}selected{% endif %}>🟢 utility.db (Utility)</option>
            </select>
            <span class="db-path">{{ db_path }}</span>
        </div>
        
        <div class="nav">
            <a href="/?db={{ current_db }}">📋 Tables</a>
            <a href="/query?db={{ current_db }}">🔍 SQL Query</a>
        </div>
        
        {% if page == 'tables' %}
            <h2>📊 Database Tables</h2>
            {% if tables %}
                {% for table in tables %}
                    <div class="table-card">
                        <div class="table-name">📋 {{ table[0] }}</div>
                        <div class="table-info"><span class="badge">{{ table[1] }} rows</span></div>
                        <div class="table-actions">
                            <a href="/table/{{ table[0] }}?db={{ current_db }}" class="btn">View Data →</a>
                        </div>
                    </div>
                {% endfor %}
            {% else %}
                <p style="color: #999; text-align: center; padding: 40px;">No tables found in this database</p>
            {% endif %}
            
        {% elif page == 'table' %}
            <h2>📋 Table: {{ table_name }}</h2>
            <div class="result-info">
                <strong>Total rows:</strong> {{ total_rows }} | 
                <strong>Showing:</strong> {{ rows|length }} rows (max 100)
                <a href="/?db={{ current_db }}" class="btn" style="float: right;">← Back to Tables</a>
            </div>
            
            {% if rows %}
                <div style="overflow-x: auto;">
                    <table>
                        <thead>
                            <tr>
                                {% for col in columns %}
                                    <th>{{ col }}</th>
                                {% endfor %}
                            </tr>
                        </thead>
                        <tbody>
                            {% for row in rows %}
                                <tr>
                                    {% for cell in row %}
                                        <td>{{ cell if cell is not none else '<i>NULL</i>' }}</td>
                                    {% endfor %}
                                </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            {% else %}
                <p style="color: #999; text-align: center; padding: 40px;">No data in this table</p>
            {% endif %}
            
        {% elif page == 'query' %}
            <h2>🔍 Run SQL Query</h2>
            <form method="POST" class="sql-form">
                <textarea name="sql" placeholder="Enter your SQL query here...
Example: SELECT * FROM users LIMIT 10;">{{ sql }}</textarea>
                <br>
                <button type="submit">▶️ Execute Query</button>
            </form>
            
            {% if error %}
                <div class="error"><strong>❌ Error:</strong> {{ error }}</div>
            {% endif %}
            
            {% if result %}
                <div class="success">
                    <strong>✅ Query executed successfully!</strong> 
                    {{ result.count }} row(s) returned
                </div>
                
                {% if result.rows %}
                    <div style="overflow-x: auto;">
                        <table>
                            <thead>
                                <tr>
                                    {% for col in result.columns %}
                                        <th>{{ col }}</th>
                                    {% endfor %}
                                </tr>
                            </thead>
                            <tbody>
                                {% for row in result.rows %}
                                    <tr>
                                        {% for cell in row %}
                                            <td>{{ cell if cell is not none else '<i>NULL</i>' }}</td>
                                        {% endfor %}
                                    </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                {% endif %}
            {% endif %}
        {% endif %}
        
        <div style="margin-top: 40px; padding-top: 20px; border-top: 2px solid #e0e0e0; text-align: center; color: #999; font-size: 14px;">
            <p>🗄️ SQLite Database Manager | Powered by Flask & Python</p>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    db_path, current_db = get_db_path()
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        table_names = cursor.fetchall()
        
        tables = []
        for (name,) in table_names:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {name}")
                count = cursor.fetchone()[0]
                tables.append((name, count))
            except:
                tables.append((name, 0))
        
        conn.close()
        
        return render_template_string(HTML_TEMPLATE, page='tables', tables=tables, 
                                     db_path=db_path, current_db=current_db)
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/table/<table_name>')
def view_table(table_name):
    db_path, current_db = get_db_path()
    try:
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
    except Exception as e:
        return f"Error: {str(e)}", 500

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
            
            conn.commit()
            conn.close()
        except Exception as e:
            error = str(e)
    
    return render_template_string(HTML_TEMPLATE, page='query', result=result, error=error, 
                                 sql=sql, db_path=db_path, current_db=current_db)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
