from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
import csv
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"
login_manager = LoginManager(app)

# Set the directory where uploaded files will be stored
UPLOAD_FOLDER = 'uploads'
if not os.path.isdir(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the file if it doesn't exist
file_path = 'uploads/messages.csv'
if not os.path.exists(file_path):
    with open(file_path, 'w') as file:
        #file.write('message,time_sent,ip\n')
        file.close()
if not os.path.isfile('database.db'):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE users
                 (username text, password text)''')
    # Add a new 'id' column to the messages table
    #c.execute('''ALTER TABLE messages ADD COLUMN id INTEGER PRIMARY KEY AUTOINCREMENT''')

    conn.commit()
    conn.close()
    
    
# Define user model
class User(UserMixin):
    def __init__(self, username, password):
        self.id = username
        self.password = password

    @staticmethod
    def get(user_id):
        return None

# Dictionary to store user information
users = {
    'user': User('user', 'password')
}

# Define the login view
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        fetch = SignIn(username,password)
        if(fetch == None):
            return render_template('login.html')
        session['username'] = fetch
        return redirect(url_for('index'))
        #if user and user.password == password:
        #    login_user(user)
        #    return redirect(url_for('index'))
        #else:
        #flash('Invalid username or password')

    return render_template('login.html')
    
def SignIn(username, password):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Check if user exists and password is correct
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    row = c.fetchone()
    if row is None:
        return None
    else:
        return row[0] # Return the username

# Define the sign up view
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get the username and password from the form data
        username = request.form['username']
        password = request.form['password']
        
        # Open a connection to the database
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # Check if the username already exists in the database
        c.execute('SELECT username FROM users WHERE username = ?', [username])
        result = c.fetchone()
        if result:
            # If the username already exists, show an error message
            flash('Username already taken')
        else:
            # If the username is not already taken, add the new user to the database
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', [username, password])
            conn.commit()
            flash('Account created successfully')
            return redirect(url_for('index'))
        
        # Close the database connection
        conn.close()
        
    return render_template('signup.html')

# Define the logout view
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('password', None)
    logout_user()
    return redirect(url_for('login'))

# Define the index view
@app.route('/')
def index():
    messages = []
    username = session.get('username')
    filename = os.path.join(app.config['UPLOAD_FOLDER'], 'messages.csv')

    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reversed(list(reader)):
            messages.append({
                'username': row[0],
                'time': row[1],
                'ip': row[2],
                'text': row[3]
            })
    return render_template('index.html', messages=messages, username=username)

# Define the post message view
@app.route('/post-message', methods=['POST'])
def post_message():
    text = request.form['text']
    ip = request.remote_addr
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    username = session.get('username')
    with open('uploads/messages.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([username, time, ip, text])
    return redirect(url_for('index'))
    
@app.route('/get-messages', methods=['GET'])
def get_messages():
    messages = []
    username = session.get('username')
    filename = os.path.join(app.config['UPLOAD_FOLDER'], 'messages.csv')

    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reversed(list(reader)):
            messages.append({
                'username': row[0],
                'time': row[1],
                'ip': row[2],
                'text': row[3]
            })
    return render_template('index.html', messages=messages, username=username)

# Define the user loader function
@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

if __name__ == '__main__':
    app.run(debug=True)


