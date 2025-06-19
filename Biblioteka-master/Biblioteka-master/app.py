from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = 'supersecretkey'

DATABASE = 'database.db'

def add_sample_books():
    conn = get_db()
    conn = get_db()
    count = conn.execute('SELECT COUNT(*) FROM books').fetchone()[0]
    if count == 0:  # lista książek
        sample_books = [
            ('Harry Potter', 'J.K. Rowling', 1),
            ('Władca Pierścieni', 'J.R.R. Tolkien', 1),
            ('Python dla każdego', 'Autor Nieznany', 1),
            ('Pan Tadeusz', 'Henruk Sienkiewicz', 1),
            ('Lalka', 'Bolesław Prus', 1),
            ('Pożegnanie domu', 'Zofia Nałkowska', 1),
            ('Pogorzelisko', 'Wojciech Sumliński', 1),
        ]
        for title, author, available in sample_books:
            conn.execute('INSERT INTO books (title, author, available) VALUES (?, ?, ?)', (title, author, available))
        conn.commit()
        conn.close()


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# baza - tabele
def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            available INTEGER DEFAULT 1
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            book_id INTEGER,
            due_date TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(book_id) REFERENCES books(id)
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    # Główna strona - jeśli zalogowany to dashboard, jeśli nie to logowanie
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # W praktyce haszuj hasła
        email = request.form['email']
        conn = get_db()
        try:
            conn.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', (username, password, email))
            conn.commit()
            flash('Zarejestrowano pomyślnie, zaloguj się.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Nazwa użytkownika już istnieje.')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash('Błędne dane logowania.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = get_db()
    # Pobieranie wszystkich książek z dostępnością
    books = conn.execute('SELECT * FROM books').fetchall()
    # książki wypożyczone przez użytkownika z datą zwrotu
    loans = conn.execute('''
        SELECT books.title, loans.due_date FROM loans
        JOIN books ON loans.book_id = books.id
        WHERE loans.user_id = ?
    ''', (user_id,)).fetchall()
    conn.close()
    return render_template('dashboard.html', books=books, loans=loans)

@app.route('/borrow/<int:book_id>')
def borrow(book_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = get_db()
    book = conn.execute('SELECT * FROM books WHERE id = ? AND available = 1', (book_id,)).fetchone()
    if book:
        due_date = datetime.now() + timedelta(days=14)
        conn.execute('INSERT INTO loans (user_id, book_id, due_date) VALUES (?, ?, ?)', (user_id, book_id, due_date.strftime('%Y-%m-%d')))
        conn.execute('UPDATE books SET available = 0 WHERE id = ?', (book_id,))
        conn.commit()
        flash(f'Wypożyczono książkę "{book["title"]}" do {due_date.strftime("%Y-%m-%d")}.')
    else:
        flash('Książka niedostępna.')
    conn.close()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    init_db()
    add_sample_books()  # przykładowe książki
    app.run(debug=True)
