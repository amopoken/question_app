from flask import Flask, render_template, g, request
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db

app = Flask(__name__)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite3_db'):
        g.sqlite3_db.close()


@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        db = get_db()
        db.execute('insert into users(name, password, expert, admin) values (?, ?, ?, ?)', [request.form['name'], \
            generate_password_hash(request.form['password'], method='sha256'), False, False])
        db.commit()
        return 'User created'
    
    return render_template('register.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        db = get_db()
        name = request.form['name']
        password = request.form['password']
        user_cur = db.execute('select id, name, password from users where name=?', [name])
        user = user_cur.fetchone()
        if check_password_hash(user['password'], password):
            return 'password is correct'
        else:
            return 'password is wrong'
    return render_template('login.html')

@app.route('/question')
def question():
    return render_template('question.html')

@app.route('/answer')
def answer():
    return render_template('answer.html')

@app.route('/ask')
def ask():
    return render_template('ask.html')

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/unanswered')
def unanswered():
    return render_template('unanswered.html')

@app.route('/users')
def users():
    return render_template('users.html')

if __name__ == '__main__':
    app.run()
