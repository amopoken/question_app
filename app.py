from flask import Flask, render_template, g, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

def get_current_user():
    user = None
    if 'user' in session:
        user = session['user']
        db = get_db()
        user_cur = db.execute('select id, name, password, expert, admin from users where name=?', [user])
        user = user_cur.fetchone()
    return user


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite3_db'):
        g.sqlite3_db.close()


@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        db = get_db()
        existing_user_cur = db.execute('select id from users where name = ?', [request.form['name']])
        exist_user = existing_user_cur.fetchone()
        if exist_user:
            return render_template('register.html', error = 'User already exists. Pick another name')
        db.execute('insert into users(name, password, expert, admin) values (?, ?, ?, ?)', [request.form['name'], \
            generate_password_hash(request.form['password'], method='sha256'), False, False])
        db.commit()
        session['user'] = request.form['name']
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    error = None
    user = get_current_user()
    if request.method == 'POST':
        db = get_db()
        name = request.form['name']
        password = request.form['password']
        user_cur = db.execute('select id, name, password from users where name=?', [name])
        user = user_cur.fetchone()
        if check_password_hash(user['password'], password):
            session['user'] = user['name']
            return redirect(url_for('index'))
        else:
            error = "Password is incorrect or user does not exists"
    return render_template('login.html', error = error)

@app.route('/question/<question_id>')
def question(question_id):
    user = get_current_user()
    db = get_db()
    ques_cur = db.execute('select q.answer_text as answer, q.question_text as text, u.name as author, us.name as expert from questions as q join users as u on u.id = q.asked_by_id join users as us on us.id = q.expert_id where q.id = ?', [question_id])
    question = ques_cur.fetchone()
    return render_template('question.html', user=user, question = question)

@app.route('/answer/<question_id>', methods=['GET', 'POST'])
def answer(question_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    db = get_db()
    if request.method == 'POST':
        db.execute('update questions set answer_text = ? where id = ?', [request.form['answer'], question_id])
        db.commit()
        return redirect(url_for('unanswered'))
    question_cur = db.execute('select id, question_text from questions where id = ?', [question_id])
    question = question_cur.fetchone()
    return render_template('answer.html', user=user, question = question)

@app.route('/ask', methods = ['GET', 'POST'])
def ask():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    db = get_db()
    if request.method == 'POST':
        db.execute('insert into questions(question_text, expert_id, asked_by_id) values (?, ?, ?)', [request.form['text_question'], request.form['to_expert'], user['id']])
        db.commit()
        return redirect(url_for('index'))
    expert_cur = db.execute('select id, name from users where expert = 1')
    expert_result = expert_cur.fetchall()

    return render_template('ask.html', user=user, experts = expert_result)

@app.route('/')
def index():
    user = get_current_user()
    db = get_db()
    ques_cur = db.execute('select q.id as id, q.question_text as text, u.name as author, us.name as expert from questions as q join users as u on u.id = q.asked_by_id join users as us on us.id = q.expert_id where q.answer_text is not null')
    questions = ques_cur.fetchall()
    return render_template('home.html', user=user, questions = questions)

@app.route('/unanswered')
def unanswered():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    db = get_db()
    question_cur = db.execute('select questions.id as id, questions.question_text as question, users.name as author from questions join users on users.id = questions.asked_by_id where questions.answer_text is null and questions.expert_id = ?', [user['id']])
    ques_results = question_cur.fetchall()    
    return render_template('unanswered.html', user=user, questions = ques_results)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/users')
def users():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    if user['admin'] == 0:
        return redirect(url_for('index'))
    db = get_db()
    users_cur = db.execute('select id, name, expert, admin from users')
    users_result = users_cur.fetchall()
    return render_template('users.html', user=user, users = users_result)

@app.route('/promote/<int:user_id>')
def promote(user_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    if user['admin'] == 0:
        return redirect(url_for('index'))
    db = get_db()
    db.execute('update users set expert = 1 where id = ?', [user_id])
    db.commit()
    return redirect(url_for('users'))

if __name__ == '__main__':
    app.run()
