from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import wikipedia
import pyttsx3
import os
from datetime import datetime
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import threading
import uuid
from functools import wraps
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Surya2003@@',
    'database': 'wikipedia_app'
}

os.makedirs(os.path.join(app.root_path, 'static', 'audio'), exist_ok=True)
os.makedirs(os.path.join(app.root_path, 'static', 'pdf'), exist_ok=True)
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            search_query VARCHAR(255) NOT NULL,
            wikipedia_title VARCHAR(255),
            search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    cursor.close()
    conn.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def clean_text_for_speech(text):
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\$\$.*?\$\$', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def generate_audio(text, filename):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.9)
        audio_path = os.path.join(app.root_path, 'static', 'audio', f'{filename}.wav')
        engine.save_to_file(text, audio_path)
        engine.runAndWait()
        if not os.path.exists(audio_path):
            print(f"pyttsx3 did not create the file: {audio_path}")
            return None
        return audio_path
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None

def generate_pdf(title, content, filename):
    try:
        pdf_path = os.path.join(app.root_path, 'static', 'pdf', f'{filename}.pdf')
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        story.append(Paragraph(title, styles['Title']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(content.replace('\n', '<br/>'), styles['Normal']))
        doc.build(story)
        return pdf_path
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None

def summarize_text(text, sentences=3):
    parts = text.split('. ')
    if len(parts) <= sentences:
        return text
    return '. '.join(parts[:sentences]) + '.'

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session.get('username'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        a = request.form['username']
        b = request.form['email']
        c = request.form['password']
        if not a or not b or not c:
            flash('All fields are required!')
            return render_template('register.html')
        conn = get_db_connection()
        d = conn.cursor()
        d.execute('SELECT id FROM users WHERE username = %s OR email = %s', (a, b))
        if d.fetchone():
            flash('Username or email already exists!')
            d.close()
            conn.close()
            return render_template('register.html')
        e = generate_password_hash(c)
        d.execute('INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)', (a, b, e))
        conn.commit()
        d.close()
        conn.close()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        a = request.form['username']
        b = request.form['password']
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT id, username, password_hash FROM users WHERE username = %s', (a,))
        d = c.fetchone()
        c.close()
        conn.close()
        if d and check_password_hash(d[2], b):
            session['user_id'] = d[0]
            session['username'] = d[1]
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/search', methods=['POST'])
@login_required
def search():
    a = request.form['search_term']
    try:
        wikipedia.set_lang("en")
        b = wikipedia.page(a)
        c = b.content
        d = b.summary
        e = b.title
        f = summarize_text(d, 2)
        g = str(uuid.uuid4())[:8]
        conn = get_db_connection()
        h = conn.cursor()
        h.execute('INSERT INTO search_history (user_id, search_query, wikipedia_title) VALUES (%s, %s, %s)', (session['user_id'], a, e))
        conn.commit()
        h.close()
        conn.close()
        i = clean_text_for_speech(d)
        generate_audio(i, f'summary_{g}')
        generate_pdf(e, c, f'content_{g}')
        return render_template('results.html', title=e, content=c, summary=d, ai_summary=f, file_id=g)
    except wikipedia.exceptions.DisambiguationError as x:
        return render_template('disambiguation.html', options=x.options[:10], search_term=a)
    except wikipedia.exceptions.PageError:
        flash(f'No Wikipedia page found for "{a}"', 'error')
        return redirect(url_for('index'))
    except Exception as y:
        flash(f'Error occurred: {str(y)}', 'error')
        return redirect(url_for('index'))

@app.route('/search_specific/<query>')
@login_required
def search_specific(query):
    return search_wikipedia_page(query)

def search_wikipedia_page(q):
    try:
        a = wikipedia.page(q)
        b = a.content
        c = a.summary
        d = a.title
        e = str(uuid.uuid4())[:8]
        conn = get_db_connection()
        f = conn.cursor()
        f.execute('INSERT INTO search_history (user_id, search_query, wikipedia_title) VALUES (%s, %s, %s)', (session['user_id'], q, d))
        conn.commit()
        f.close()
        conn.close()
        def g_files():
            g = clean_text_for_speech(c)
            generate_audio(g, f'summary_{e}')
            generate_pdf(d, b, f'content_{e}')
        t = threading.Thread(target=g_files)
        t.start()
        return render_template('result.html', title=d, content=b, summary=c, file_id=e)
    except Exception as x:
        flash(f'Error occurred: {str(x)}')
        return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    a = conn.cursor()
    a.execute('SELECT search_query, search_date FROM search_history WHERE user_id = %s ORDER BY search_date DESC LIMIT 50', (session['user_id'],))
    b = a.fetchall()
    a.close()
    conn.close()
    return render_template('dashboard.html', searches=b, username=session.get('username'))

@app.route('/check_audio/<file_id>')
@login_required
def check_audio(file_id):
    a = os.path.join(app.root_path, 'static', 'audio', f'summary_{file_id}.wav')
    return jsonify({'ready': os.path.exists(a)})

@app.route('/download_audio')
@login_required
def download_audio():
    a = request.args.get('title')
    b = request.args.get('content')
    if not a or not b:
        flash('Missing title or content for audio generation', 'error')
        return redirect(url_for('index'))
    c = str(uuid.uuid4())[:8]
    d = clean_text_for_speech(b[:1000])
    e = generate_audio(d, f'download_{c}')
    if e and os.path.exists(e):
        return send_file(e, as_attachment=True, download_name=f'{a}_audio.wav')
    else:
        print(f"Audio file was not created or found: {e}")
        flash('Error generating audio file. Please check your TTS engine setup or try again later.', 'error')
        return redirect(url_for('index'))
    
@app.route('/stream_audio/<file_id>')
@login_required
def stream_audio(file_id):
    audio_path = os.path.join(app.root_path, 'static', 'audio', f'summary_{file_id}.wav')
    if os.path.exists(audio_path):
        return send_file(audio_path, mimetype='audio/wav')
    else:
        return jsonify({'error': 'Audio file not found'}), 404

@app.route('/download_pdf')
@login_required
def download_pdf():
    a = request.args.get('title')
    b = request.args.get('content')
    if not a or not b:
        flash('Missing title or content for PDF generation', 'error')
        return redirect(url_for('index'))
    c = str(uuid.uuid4())[:8]
    d = generate_pdf(a, b, f'download_{c}')
    if d and os.path.exists(d):
        return send_file(d, as_attachment=True, download_name=f'{a}.pdf')
    else:
        flash('Error generating PDF file', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
