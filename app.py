import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email, Length
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ece_secret_key_12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models (Steps 5, 6, 13)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# WTForms Configuration (Steps 1, 2, 12, 14)
class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(), Length(max=50)], description="Your school email address")
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=80)])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit(): # Steps 18, 19
        print("Form submitted!")
        # Step 13: Prevent Duplicate Email Registration
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Email already registered.")
            return redirect(url_for('register'))
        
        new_user = User(email=form.email.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    elif request.method == 'POST':
        print("Validation failed.")
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('home'))
        flash("Invalid credentials.")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/students')
def students():
    # Step 6: Sort Students Alphabetically Before Displaying
    students = Student.query.order_by(Student.full_name).all()
    return render_template('view_students.html', students=students)

# Step 9: Add 404 Error Handler to app.py
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Auto-seed sample records for testing
def init_db():
    with app.app_context():
        db.create_all()
        if not Student.query.first():
            s1 = Student(full_name='Echapare, Precious Nedilyn B.', email='precious.echapare@tup.edu.ph')
            s2 = Student(full_name='John Doe', email='john.doe@tup.edu.ph')
            db.session.add_all([s1, s2])
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)