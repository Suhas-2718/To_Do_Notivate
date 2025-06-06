from flask import Flask, render_template, redirect, url_for, request, session, flash 
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import jsonify, request

app = Flask(__name__)
app.secret_key = "hello"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notivate.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Notivate(db.Model):  
    __tablename__ = 'notivate'
    id = db.Column(db.Integer, primary_key=True)  
    name = db.Column(db.String(50), unique=True, nullable=False)  
    task = db.relationship('Task', backref='user', lazy=True)
    


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('notivate.id'), nullable=False)
    task_text = db.Column(db.String(200), nullable=False)
    datetimes = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, user_id, task_text, datetimes=None):
        self.user_id = user_id
        self.task_text = task_text
        self.datetimes = datetimes


@app.route("/")
def intro():
    return redirect(url_for("login"))


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        session["user"] = user

        found_user = Notivate.query.filter_by(name=user).first()  
        if not found_user:
            usr = Notivate(name=user)  
            db.session.add(usr)
            db.session.commit()
            found_user = usr 

        return redirect(url_for("user"))

    return render_template('login.html')


@app.route("/user", methods=["POST", "GET"])
def user():
    if "user" not in session:
        return redirect(url_for("login"))

    user = session["user"]
    found_user = Notivate.query.filter_by(name=user).first()

    task_text = None

    if request.method == 'POST':
        task_text = request.form.get('text')

        if found_user and task_text: 
            new_task = Task(user_id=found_user.id, task_text=task_text) 
            db.session.add(new_task)
            db.session.commit()

            flash("Task Added successfully", "info")

    
    alltodo = Task.query.filter_by(user_id=found_user.id).all()

    return render_template('user.html', content=user, alltodo=alltodo) 



@app.route('/delete/<int:id>')
def delete(id):  
    task = Task.query.get(id)  
    if task:  
        db.session.delete(task)
        db.session.commit()
        flash("Task deleted successfully", "info")
    else:
        flash("Task not found", "error")

    return redirect(url_for("user"))


@app.route('/logout')
def logout():
    if "user" in session:
        user = session["user"]
        flash(f"You have logged out successfully 👍🏻 Thank you, {user}😊", "info")

    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all() 
    app.run(debug=False)
