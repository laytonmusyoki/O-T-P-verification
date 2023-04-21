from flask import Flask, render_template, redirect, url_for, request,flash
from flask_mail import Mail, Message
from flask_mysqldb import MySQL
import re
from random import *

app = Flask(__name__)

app.config['MYSQL_HOST']="localhost"
app.config['MYSQL_USER']="root"
app.config['MYSQL_PASSWORD']=""
app.config['MYSQL_DB']="flask_db"
mysql=MySQL(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = #email
app.config['MAIL_PASSWORD'] = #passwoed
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
otp = randint(0000, 9999)


app.secret_key="layton"

#landing page
@app.route('/')
def home():
    return render_template("home.html")

# obtaining user inputs
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT username FROM users ")
        result = cur.fetchall()
        existing_usernames = [row[0] for row in result]
        if username in existing_usernames:
            flash("Username is already taken try another one !!")
            return render_template('register.html', name=name, username=username, email=email,password=password)
        elif len(password) < 8:
            flash("password must be more than 8 characters!")
            return render_template('register.html', name=name, username=username, email=email,password=password)
        elif not re.search("[a-z]", password):
            flash("password must have small letters!")
            return render_template('register.html', name=name, username=username, email=email,password=password)
        elif not re.search("[A-Z]", password):
            flash("password must have capital letters!")
            return render_template('register.html', name=name, username=username, email=email,password=password)
        elif not re.search("[_@$]+", password):
          flash("Password must contain special characters!")
          return render_template('register.html', name=name, username=username, email=email, password=password)
        else:
            cur.execute("INSERT INTO users(name, username, email, password) VALUES(%s, %s, %s, %s)",(name, username, email, password))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('send_otp'))
    else:
        return render_template('register.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='POST':
       name=request.form['nm']
       password=request.form['password']

       cur=mysql.connection.cursor()
       cur.execute("SELECT *FROM users WHERE username=%s AND password=%s",(name,password))
       result=cur.fetchone()

       if result is not None:
          session['username']=name[0]
          flash("log in successfully !")
          return redirect(url_for('welcome'))

       else:
           flash("Invalid username or password !!",'danger')
           
    return render_template('login.html')

@app.route('/welcome')
def welcome():
    if "username" in session:
        name=session['username']
        return render_template('welcome.html')
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    if "username" in session:
       session.pop('name',None)
       flash("You have been logged out !",'error')
       return redirect(url_for('login'))


@app.route('/send_otp')
def send_otp():
     return render_template('otp.html')  



@app.route('/verify', methods=['POST', 'GET'])
def verify():
     if request.method == 'POST':
        email = request.form['email']
        msg = Message(subject='OTP', sender='laytonmatheka@gmail.com', recipients=[email])
        msg.body = str(otp)
        mail.send(msg)
     return render_template('verify.html')


@app.route('/validate', methods=['POST', 'GET'])
def validate():
     user_otp = request.form['otp']
     if otp == int(user_otp):
          flash("Account verified successfully")
          return redirect(url_for('login'))
     else:
         flash("Invalid OTP please try again...",'success')
         return redirect(url_for('send_otp'))
   
if __name__ == '__main__':
     app.run(debug=True)
