from pathlib import Path
from flask import Flask, render_template, flash, request, url_for, redirect
from flask_login import login_required, fresh_login_required, login_user, logout_user, current_user
from datetime import datetime
from dateutil.relativedelta import relativedelta
from modules import db, login_manager, bcrypt
import models

app = Flask(__name__)
app.config.from_pyfile('config.py')
db.init_app(app)
login_manager.init_app(app)
bcrypt.init_app(app)
if not Path('test.db').exists():
    with app.app_context():
        db.create_all()


@login_manager.user_loader
def get_user(id):
    return models.User.query.get(id)


@app.route('/')
@app.route('/home/')
def homepage():
    return render_template("home.html", name=current_user.username)


@app.route('/login/<fresh_register>', methods=['GET', 'POST'])
@app.route('/login/', methods=['GET', 'POST'])
def login(fresh_register=None):
    error = None
    if request.method == "POST":
        attempted_username = request.form['username'].strip()
        attempted_password = request.form['password'].strip()
        user = models.User.query.filter_by(username=attempted_username).first()
        db.session.commit()
        if user is not None:
            if bcrypt.check_password_hash(user.password, attempted_password):
                login_user(user, remember=True)
                return redirect(url_for("homepage"))
        error = "Invalid credentials. Please try again."

    return render_template("login.html", title="Login", error=error, fresh_register=fresh_register)


@app.route('/logout/')
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.commit()
    logout_user()
    return render_template('logout.html')


@app.route('/register/', methods=['GET', 'POST'])
def register():
    errors = []
    if request.method == "POST":
        given_username = request.form['username']
        given_password = request.form['password']
        name = f"{request.form['first_name'].strip()} {request.form['last_name'].strip()}"
        birthday = request.form['birthday']
        #   Username checks
        if models.User.query.filter_by(username=given_username).first() is not None:
            errors.append(f"Username '{given_username}' already taken!")

        #   Password checks
        if len(given_password) < app.config['MINIMUM_PASSWORD_LENGTH']:
            errors.append(f"Your password is too short! "
                          f"(minimum length of {app.config['MINIMUM_PASSWORD_LENGTH']} characters)")
        elif len(given_password) > app.config['MAXIMUM_PASSWORD_LENGTH']:
            errors.append(f"Your password is too long! (maximum length of "
                          f"{app.config['MAXIMUM_PASSWORD_LENGTH']} characters)")

        #   Birthday (check if 18+)
        if datetime.strptime(birthday, "%Y-%m-%d") > datetime.now() - relativedelta(years=18):
            errors.append(f"You must be 18+ to have an account! Anyone younger is perfect and has no flaws...")
        print(errors)
        if len(errors) == 0:
            #   Everything looks good, let's register da user
            db.session.add(models.User(given_username, given_password, name, birthday))
            db.session.commit()
            print('redirecting')
            return redirect(url_for('login', fresh_register=True))

    return render_template("register.html", title="Register", errors=errors)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


@app.errorhandler(405)
def method_not_found(e):
    return render_template("405.html")


if __name__ == "__main__":
    app.run()
