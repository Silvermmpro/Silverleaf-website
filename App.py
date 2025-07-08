from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import qrcode
import os
import pandas as pd
from config import ADMIN_USERNAME, ADMIN_PASSWORD, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

# תיקייה לשמירת QR
QR_FOLDER = 'static/qr_codes'
os.makedirs(QR_FOLDER, exist_ok=True)

# קובץ נתונים
DATA_FILE = 'data/registrations.csv'
os.makedirs('data', exist_ok=True)
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=[
        'שם מלא', 'טלפון', 'מאיפה', 'ציוד', 'איך הגיע', 'זמינות',
        'רכב', 'מייל', 'תאריך לידה', 'מגדר'
    ]).to_csv(DATA_FILE, index=False)


@app.route('/')
def home():
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = {
            'שם מלא': request.form['full_name'],
            'טלפון': request.form['phone'],
            'מאיפה': request.form['origin'],
            'ציוד': request.form['equipment'],
            'איך הגיע': request.form['how_found'],
            'זמינות': request.form['availability'],
            'רכב': request.form['has_car'],
            'מייל': request.form['email'],
            'תאריך לידה': request.form['birthdate'],
            'מגדר': request.form['gender'],
        }
        df = pd.read_csv(DATA_FILE)
        df = df.append(data, ignore_index=True)
        df.to_csv(DATA_FILE, index=False)

        qr_path = os.path.join(QR_FOLDER, f"{data['שם מלא']}.png")
        qr = qrcode.make(f"רישום לאימפריית סילברליף:\n{data['שם מלא']}")
        qr.save(qr_path)

        return render_template("register.html", qr_image=qr_path)
    return render_template("register.html", qr_image=None)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return "גישה נדחתה"
    return render_template("admin_login.html")

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    df = pd.read_csv(DATA_FILE)
    return render_template("admin_dashboard.html", data=df.to_dict(orient='records'))

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
