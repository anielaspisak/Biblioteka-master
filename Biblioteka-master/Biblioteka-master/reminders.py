import sqlite3
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

DATABASE = 'database.db'

# Konfiguracja SMTP
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_USER = 'sidzinska.menelownia4@gmail.com'       # Twój email do logowania na SMTP
EMAIL_PASS = 'tulg rgci doph auvw'            # Hasło aplikacji SMTP

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def send_email(to_email, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = to_email

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        print(f"Wysłano e-mail do {to_email}")
    except Exception as e:
        print(f"Błąd przy wysyłaniu do {to_email}: {e}")

def send_reminders():
    conn = get_db()
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    print(f"Sprawdzam datę: {tomorrow}")
    # Pobieranie wypożyczenia, które mają termin zwrotu jutro z danymi użytkownika
    loans = conn.execute('''
        SELECT users.email, users.username, books.title, loans.due_date
        FROM loans
        JOIN users ON loans.user_id = users.id
        JOIN books ON loans.book_id = books.id
        WHERE loans.due_date = ?
    ''', (tomorrow,)).fetchall()
    print(f"Pobrano {len(loans)} rekordów z wypożyczeniami do zwrotu jutro")
    # wypożyczenia po użytkowniku, żeby wysłać 1 mail z listą książek
    reminders = {}
    for loan in loans:
        email = loan['email']
        print(f"DEBUG: Wysyłam przypomnienie na adres: {loan['email']}")
        if email not in reminders:
            print("Znaleziono maila do wyslania")
            reminders[email] = {
                'username': loan['username'],
                'books': []
            }
        reminders[email]['books'].append((loan['title'], loan['due_date']))

    # wysłanie maila do każdego użytkownika
    for email, data in reminders.items():
        username = data['username']
        books_list = "\n".join([f"- {title} do {due_date}" for title, due_date in data['books']])
        subject = "Przypomnienie o terminie zwrotu książek"
        body = f"Cześć {username},\n\nPrzypominamy, że musisz zwrócić następujące książki:\n{books_list}\n\nPozdrawiamy, Moja Biblioteka"
        send_email(email, subject, body)

    conn.close()

if __name__ == '__main__':
    send_reminders()
