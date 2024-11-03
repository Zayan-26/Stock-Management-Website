from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from flask_login import login_user, login_required, logout_user, current_user, UserMixin, LoginManager


auth = Blueprint('auth', __name__)
conn = sqlite3.connect('database.db')

def query(statement, *args):
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute(statement, *args)
        return cursor.fetchall()

def insert_user(conn, data):
      sql = """INSERT INTO userinfo(email, password, forename, surname) VALUES (?, ?, ?, ?)"""
      cursor = conn.cursor()
      cursor.execute(sql, data)
      conn.commit()
      return 

class User(UserMixin):
    def __init__(self, id, email, password):
         self.id = id
         self.email = email
         self.password = password

login_manager = LoginManager()
@login_manager.user_loader
def load_user(userID):
          conn = sqlite3.connect("database.db")
          curs = conn.cursor()
          c = curs.execute("SELECT * from userinfo where userID = (?)", (userID,))
          lu = curs.fetchone()
          if lu is None:
              return None
          else:
              return User(int(lu[0]), lu[1], lu[2])


@auth.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    email = request.form.get('email')
    password = request.form.get('password')

    # Check is email exists in database
    retrieve_user = query('''SELECT * FROM userinfo where email=?''', (email,))

    if len(retrieve_user) > 0:
      # creates user object
      user = User(retrieve_user[0][0], email, password)
      p_check = retrieve_user[0][2]
      if check_password_hash(p_check, password):
        flash('Logged in Successfully', category='Success')
        login_user(user, remember=True)
        if retrieve_user[0][5] == "Employee":
           return redirect(url_for('views.employee_view'))
        else:
          return redirect(url_for('views.home'))
      else:
        flash('Incorrect password. Try Again', category='Error')
    else:
      flash('User does not exist!', category='Error')

  return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect(url_for('auth.login'))

@auth.route('/signup', methods=['GET', 'POST'])
def sign_up():
  if request.method == 'POST':
    # getting info from user via form
    email = request.form.get('email')
    firstName = request.form.get('firstName')
    lastName = request.form.get('lastName')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    password_hash = generate_password_hash(password1, method='pbkdf2:sha256')
    
    user_data = (email, password_hash, firstName, lastName)

    #checking data requirements
    if len(email) < 4:
      flash('Email must be greater than 3 characters', category='Error')
    elif len(firstName) < 2:
      flash('First Name must be greater than  1 character', category='Error') 
    elif len(lastName) < 2:
      flash('Last Name must be greater than  1 character', category='Error')  
    elif password1 != password2:
      flash('Passwords do not match. Please retry', category='Error')
    elif len(password1) < 7:
      flash('Password must be at least 7 characters', category='Error')
    else:
      # checking if user already exists
      check = query('''SELECT email FROM userinfo where email=?''', (email,))
      if len(check) > 0:
        flash('User already exists', category='Error')   
      else:
        # inserting new user data into database
        conn = sqlite3.connect('database.db')
        insert_user(conn, user_data)
        retrieve_user = query('''SELECT * FROM userinfo where email=?''', (email,))
        user = User(retrieve_user[0][0], email, password1)
        login_user(user, remember=True)
        flash('Account created!', category='Success')
        if retrieve_user[0][5] == "Employee":
           return redirect(url_for('views.employee_view'))
        else:
          return redirect(url_for('views.home'))

  return render_template("signup.html", user=current_user)