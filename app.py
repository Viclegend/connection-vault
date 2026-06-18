from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'my_super_secret_key_for_si_system'

DB_FILE = 'data/system_v4.db'

# --- 透過 os.environ 從 .env 注入設定，如果沒讀到則給予預設值 ---
ADMIN_USER = os.environ.get('ADMIN_USER', 'admin')
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'admin123')

@app.before_request
def require_login():
    allowed_routes = ['login', 'static']
    if request.endpoint not in allowed_routes and 'logged_in' not in session:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USER and request.form['password'] == ADMIN_PASS:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = '帳號或密碼錯誤！'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

def init_db():
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS clients
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT UNIQUE NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS devices
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  client_id INTEGER,
                  device_name TEXT NOT NULL,
                  ip_address TEXT,
                  conn_method TEXT,
                  username TEXT,
                  password TEXT,
                  FOREIGN KEY(client_id) REFERENCES clients(id))''')
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row 
    return conn

@app.route('/')
def index():
    search_query = request.args.get('q', '').strip()
    conn = get_db_connection()
    clients = conn.execute("SELECT * FROM clients ORDER BY name").fetchall()
    
    if search_query:
        query = """SELECT d.*, c.name as client_name 
                   FROM devices d JOIN clients c ON d.client_id = c.id
                   WHERE d.device_name LIKE ? OR d.ip_address LIKE ? 
                      OR c.name LIKE ? OR d.username LIKE ?
                   ORDER BY c.name, d.id"""
        params = (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%', f'%{search_query}%')
        devices = conn.execute(query, params).fetchall()
    else:
        query = "SELECT d.*, c.name as client_name FROM devices d JOIN clients c ON d.client_id = c.id ORDER BY c.name, d.id"
        devices = conn.execute(query).fetchall()
    conn.close()

    # 優化資料結構，方便前端渲染與計算設備數量
    grouped_data = []
    for client in clients:
        client_devices = [d for d in devices if d['client_id'] == client['id']]
        grouped_data.append({
            'id': client['id'],
            'name': client['name'],
            'devices': client_devices
        })

    return render_template('index.html', clients=clients, grouped_data=grouped_data, search_query=search_query)

@app.route('/add_client', methods=['POST'])
def add_client():
    name = request.form['client_name'].strip()
    if name:
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO clients (name) VALUES (?)", (name,))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        conn.close()
    return redirect(url_for('index'))

# --- 新增：刪除客戶分類邏輯 ---
@app.route('/delete_client', methods=['POST'])
def delete_client():
    client_id = request.form['client_id']
    password_attempt = request.form.get('password', '')
    
    conn = get_db_connection()
    devices = conn.execute("SELECT id FROM devices WHERE client_id=?", (client_id,)).fetchall()
    
    # 判斷是否含有設備
    if len(devices) > 0:
        if password_attempt != ADMIN_PASS:
            flash('刪除失敗：驗證密碼錯誤！', 'danger')
            conn.close()
            return redirect(url_for('index'))
        else:
            # 密碼正確，先刪除旗下所有設備
            conn.execute("DELETE FROM devices WHERE client_id=?", (client_id,))
            
    # 刪除客戶分類本身
    conn.execute("DELETE FROM clients WHERE id=?", (client_id,))
    conn.commit()
    conn.close()
    flash('客戶分類及相關設備已成功刪除！', 'success')
    return redirect(url_for('index'))

@app.route('/add_device', methods=['POST'])
def add_device():
    client_id = request.form['client_id']
    device_name = request.form['device_name']
    ip_address = request.form['ip_address']
    conn_method = request.form['conn_method']
    username = request.form['username']
    password = request.form['password']
    conn = get_db_connection()
    conn.execute("""INSERT INTO devices (client_id, device_name, ip_address, conn_method, username, password) 
                    VALUES (?, ?, ?, ?, ?, ?)""",
                 (client_id, device_name, ip_address, conn_method, username, password))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM devices WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db_connection()
    if request.method == 'POST':
        client_id = request.form['client_id']
        device_name = request.form['device_name']
        ip_address = request.form['ip_address']
        conn_method = request.form['conn_method']
        username = request.form['username']
        password = request.form['password']
        conn.execute("""UPDATE devices SET client_id=?, device_name=?, ip_address=?, 
                        conn_method=?, username=?, password=? WHERE id=?""", 
                     (client_id, device_name, ip_address, conn_method, username, password, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    else:
        device = conn.execute("SELECT * FROM devices WHERE id=?", (id,)).fetchone()
        clients = conn.execute("SELECT * FROM clients ORDER BY name").fetchall()
        conn.close()
        return render_template('edit.html', device=device, clients=clients)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080)