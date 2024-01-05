from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Database setup moved inside the app context
def get_db():
    db = sqlite3.connect('invoice_processing_db.sqlite')
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor_name TEXT,
                amount REAL,
                status TEXT
            )
        ''')
        db.commit()

@app.route('/')
def display_invoices():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM invoices')
    invoices = cursor.fetchall()
    db.close()
    return render_template('invoices.html', invoices=invoices)

@app.route('/process_invoice/<int:invoice_id>')
def process_invoice(invoice_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE invoices SET status = ? WHERE id = ?', ('Approved', invoice_id))
    db.commit()
    db.close()
    return redirect(url_for('display_invoices'))

@app.route('/capture_invoice', methods=['GET', 'POST'])
def capture_invoice():
    if request.method == 'POST':
        vendor_name = request.form['vendor_name']
        amount = float(request.form['amount'])
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO invoices (vendor_name, amount, status) VALUES (?, ?, ?)',
                       (vendor_name, amount, 'Pending'))
        db.commit()
        db.close()
        return redirect(url_for('display_invoices'))

    return render_template('capture_invoice.html')

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)
