from flask import Flask, render_template, request, redirect, session, abort
from flask_login import LoginManager, login_user, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
import date
import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = b'};/,\x94C\xed3\x1e\xb8</'
login_manager.login_view = 'login'


class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    user_email = db.Column(db.String(80), nullable=False)
    authenticated = db.Column(db.Boolean, default=False)

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_active(self):
        """True, as all users are active."""
        return True

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.user_id


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    to_do = db.Column(db.String(200))
    date_to_do = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.Boolean, default=False)
    date_create = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey(User.user_id))
    task_number = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        if self.status is False:
            return 'Do zrobienia'
        else:
            return 'Gotowe'

    def start_time_format(self):
        return self.start_time.strftime('%H:%M')

    def stop_time_format(self):
        return self.end_time.strftime('%H:%M')


class LoginForm(FlaskForm):
    username = StringField('username')
    password = PasswordField('password')
    submit = SubmitField('Submit')


def valid_login(user_name, password):
    valid_name = db.session.query(User).filter(User.user_name == user_name).first()
    if valid_name is None:
        return False
    valid_password = valid_name.password
    if valid_password == password:
        return True
    else:
        return False


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)


@app.route("/", methods=["GET", "POST"])
def main():
    # print(request.headers)
    # print(request.cookies)
    print(request.date)
    today_date = date.today_date
    year = today_date.year
    month = today_date.month
    day = today_date.day
    day_name = date.days[today_date.today().weekday()]
    date_task = datetime.date(year=year, month=month, day=day)
    this_month = date.one_month(month, year)
    short_day_names = date.short_day_names

    if request.method == 'GET':
        user_task = ''
        if '_fresh' in session and '_user_id' in session:
            current_user = session['_fresh']
            user_id = session['_user_id']
            user_task = db.session.query(Todo).filter(Todo.date_to_do == date_task).filter(Todo.user_id == user_id).order_by(Todo.start_time).all()
        else:
            current_user = False
        return render_template('index.html', day_name=day_name, today_date=today_date,
                               months=this_month[0], le=this_month[1], year=this_month[2],
                               month_name=this_month[3], week=this_month[4], current_user=current_user,
                               tasks=user_task, short_day_names=short_day_names)

    if request.method == 'POST':
        if request.form.get('to_details'):
            task_number = request.form.get('to_details')
            return redirect(f'/update/{task_number}')
        if request.form.get('button'):
            if request.form.get('button') == 'login':
                return redirect('/login')
            elif request.form.get('button') == 'logout':
                return redirect('/logout')
            elif request.form.get('button') == 'day':
                return redirect(f'/{year}/{month}/{day}')
            elif request.form.get('button') == 'month':
                return redirect(f'/{year}/{month}')
            elif request.form.get('button') == 'index':
                return redirect('/')


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        if request.form["button"] == "index":
            return redirect('/')
        if request.form["button"] == 'login':
            username = request.form['username']
            password = request.form['password']
            if username == '':
                messages = 'Błędny login lub hasło'
                return render_template('login.html', messages=messages)
            if password == '':
                messages = 'Błędny login lub hasło'
                return render_template('login.html', messages=messages)

            if valid_login(username, password):
                user = db.session.query(User).filter(User.user_name == username).first()
                user.authenticated = True
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)
                return redirect("/")
            else:
                messages = 'Błędny login lub hasło'
                return render_template('login.html', messages=messages)
        if request.form.get('button') == 'register':
            return redirect("/register")
        return render_template("login.html")


@app.route('/logout')
@login_required
def logout():
    user_id = session['_user_id']
    current_user = db.session.query(User).filter(User.user_id == user_id).first()
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect('/')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    if request.method == 'POST':
        if request.form["button"] == "index":
            return redirect('/')

        elif request.form["button"] == "register":
            user_name = request.form["name"]
            user_email = request.form["email"]
            password = request.form["password"]
            repassword = request.form["repassword"]
            all_names = db.session.query(User).all()

            if user_name == '' or user_email == '' or password == '' or repassword == '':
                message = "Wypełnij wszystkie pola!"
                return render_template('register.html', message=message)

            for name in all_names:
                if user_name == name.user_name:
                    message = "Podany login już istnieje, wybierz inny"
                    return render_template('register.html', message=message)

            if password != repassword:
                message = "Hało i powtórzone hasło nie są takie same!"
                return render_template('register.html', message=message)

            try:
                new_user = User(user_name=user_name, password=password, user_email=user_email)
                db.session.add(new_user)
                db.session.commit()
            except:
                message = "Błąd zapisu, spróbuj jeszcze raz"
                return render_template('register.html', message=message)
        return redirect("/login")


@app.route("/<int:year>/<int:month>/<int:day>", methods=['GET', 'POST'])
@login_required
# @app.errorhandler(404)
def day_view(year, month, day):
    try:
        date_task = datetime.date(year=year, month=month, day=day)
    except:
        # return render_template('404.html'), 404
        abort(404)
    user_id = session['_user_id']
    tasks = db.session.query(Todo).filter(Todo.date_to_do == date_task).filter(Todo.user_id == user_id).order_by(
        Todo.start_time).all()
    if request.method == 'GET':
        return render_template('day.html',  value=date.day(year, month, day), tasks=tasks, month=month)
    if request.method == 'POST':
        site_day = datetime.date(year, month, day)
        next_day = (site_day + datetime.timedelta(days=1))
        previous_day = (site_day + datetime.timedelta(days=-1))
        if request.form.get("delete"):
            try:
                task_to_delete = Todo.query.get_or_404(request.form.get("delete"))
                db.session.delete(task_to_delete)
                db.session.commit()
                return redirect(f'/{year}/{month}/{day}')
            except:
                return 'Coś nie tak'

        if request.form.get("update"):
            return redirect(f"/update/{request.form.get('update')}")
        if request.form['button'] == "index":
            return redirect('/')
        elif request.form['button'] == 'yesterday':
            return redirect(f'/{int(previous_day.year)}/{int(previous_day.month)}/{int(previous_day.day)}')
        elif request.form['button'] == 'tomorrow':
            return redirect(f'/{int(next_day.year)}/{int(next_day.month)}/{int(next_day.day)}')
        elif request.form['button'] == 'Zapisz':
            task = db.session.query(Todo).filter(Todo.user_id == user_id).order_by(Todo.task_number).all()
            start_time = request.form.get('start_time')
            stop_time = request.form.get('stop_time')
            start_time = datetime.time(hour=int(start_time[0:2]), minute=int(start_time[3:]))
            stop_time = datetime.time(hour=int(stop_time[0:2]), minute=int(stop_time[3:]))
            value = request.form.get('text')
            title = request.form.get('title')
            if title == '':
                message = 'Nie wprowadziłeś danych'
                return render_template('day.html', title=title, value=date.day(year, month, day),
                                       tasks=tasks, month=month, message=message)
            if task == []:
                task_number = 1
            else:
                task_number = task[-1].task_number + 1

            if start_time >= stop_time:
                message = 'Godzina początkowa nie może być wcześniejsza niż końcowa'
                return render_template('day.html', title=title, value=date.day(year, month, day),
                                       tasks=tasks, month=month, message=message)
            try:
                new_task = Todo(title=title, to_do=value, start_time=start_time, end_time=stop_time,
                                date_to_do=date_task, user_id=user_id, task_number=task_number)
                db.session.add(new_task)
                db.session.commit()
                return redirect(f'/{year}/{month}/{day}')
            except:
                message = "Błąd zapisu, spróbuj jeszcze raz"
                return render_template('day.html',  value=date.day(year, month, day), tasks=tasks, month=month,
                                       message=message)

        elif request.form['button'] == 'logout':
            return redirect('/logout')


@app.route("/<int:year>/<int:month>", methods=['GET', 'POST'])
@login_required
def month_view(month, year):
    week = date.short_day_names
    if request.method == 'GET':
        this_month = date.one_month(month, year)
        if this_month is False:
            abort(404)
        months_name = date.months[1:]
        href = f'/{year}/{month}/'
        return render_template('month.html', months_name=months_name, months=this_month[0], le=this_month[1],
                               year=this_month[2], month_name=this_month[3], week=week, href=href)
    if request.method == 'POST':
        if request.form['button'] == "index":
            return redirect('/')
        if request.form['button'] == 'last_month':
            if month == 1:
                month = 12
                return redirect(f'/{year-1}/{month}')
            else:
                return redirect(f'/{year}/{month -1}')
        elif request.form['button'] == 'next_month':
            if month == 12:
                month = 1
                return redirect(f'/{year + 1}/{month}')
            else:
                return redirect(f'/{year}/{month +1}')

        elif request.form['button'] == 'logout':
            return redirect('/logout')


@app.route("/<int:year>", methods=['GET', 'POST'])
@login_required
def one_year_view(year):
    months_name_list = date.months
    week_day_name = date.short_day_names
    if request.method == 'GET':
        this_year = date.one_year(year)
        href = f'/{year}/'
        return render_template('year.html', href=href, year_calendar=this_year[0], len_calendar_months=this_year[1],
                               year=this_year[2], months_name_list=months_name_list, week_day_name=week_day_name)
    if request.method == 'POST':
        if request.form['button'] == "index":
            return redirect('/')
        elif request.form['button'] == 'last_year':
            return redirect(f'/{year-1}')
        elif request.form['button'] == 'next_year':
            return redirect(f'/{year+1}')
        elif request.form['button'] == 'logout':
            return redirect('/logout')


@app.route("/update/<int:task_number>", methods=['GET', 'POST'])
@login_required
def update(task_number):
    user_id = session['_user_id']
    task = db.session.query(Todo).filter(Todo.user_id == user_id).filter(Todo.task_number == task_number).first()
    try:
        day_date = task.date_to_do
    except:
        abort(404)
    year = day_date.year
    month = day_date.month
    day = day_date.day
    start = task.start_time
    stop = task.end_time
    task.start_time_format()
    week_day_name = date.days
    day_name = week_day_name[datetime.date(year, month, day).weekday()]

    if request.method == 'GET':
        return render_template('update.html', task=task, date=day_date, start=start, stop=stop, day_name=day_name)

    if request.method == 'POST':
        if request.form['button'] == "index":
            return redirect('/')

        elif request.form['button'] == 'register':
            return redirect("/register")

        elif request.form['button'] == 'update':
            task_to_update = request.form["update_value"]
            title_to_update = request.form["update_title"]
            start_time = request.form.get('start_time')
            stop_time = request.form.get('stop_time')
            start_time = datetime.time(hour=int(start_time[0:2]), minute=int(start_time[3:5]))
            stop_time = datetime.time(hour=int(stop_time[0:2]), minute=int(stop_time[3:5]))
            if request.form["status"] == 'To do':
                status = False
            else:
                status = True

            if start_time >= stop_time:
                message = 'Godzina początkowa nie może być wcześniejsza niż końcowa'
                return render_template('update.html', task=task, date=day_date, start=start, stop=stop,
                                       day_name=day_name, message=message)

            try:
                update_todo = Todo.query.filter_by(id=int(task.id)).first()
                update_todo.title = title_to_update
                update_todo.to_do = task_to_update
                update_todo.start_time = start_time
                update_todo.end_time = stop_time
                update_todo.status = status
                db.session.commit()
                return redirect(f'/{year}/{month}/{day}')
            except:
                return 'Coś nie tak'
    return redirect(f'/{year}/{month}/{day}')


if __name__ == "__main__":
    app.run(debug=True)

