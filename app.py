from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'webgis_secret_key'  # کلید رمزنگاری کوکی‌ها

# ساخت دیتابیس ساده برای ذخیره کاربران
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, email TEXT)''')
    conn.commit()
    conn.close()

init_db() # اجرا هنگام شروع برنامه

# صفحه اصلی (همان لاگین)
@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('map_page'))
    return redirect(url_for('login'))

# صفحه ورود
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['username'] = username # ساخت کوکی ورود
            return redirect(url_for('map_page'))
        else:
            error = 'نام کاربری یا رمز عبور اشتباه است'
            
    return render_template('login.html', error=error)

# صفحه ثبت نام
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            error = 'رمز عبور و تکرار آن مطابقت ندارند'
        else:
            try:
                conn = sqlite3.connect('users.db')
                c = conn.cursor()
                c.execute("INSERT INTO users VALUES (?, ?, ?)", (username, password, email))
                conn.commit()
                conn.close()
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                error = 'این نام کاربری قبلا گرفته شده است'
                
    return render_template('register.html', error=error)

# صفحه نقشه (محافظت شده)
@app.route('/map')
def map_page():
    if 'username' not in session:
        return redirect(url_for('login')) # اگر لاگین نبود، برتش گردان
    return render_template('map.html', username=session['username'])

# خروج
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)