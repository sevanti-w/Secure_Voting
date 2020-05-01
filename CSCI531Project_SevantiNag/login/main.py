#importing libraries to support login and registration of a voter
from flask import Flask, render_template, request, redirect, url_for, session
import re
import random 
import string
import passlib.hash
import sqlite3


#Creating Flask App interface
app = Flask(__name__)

#Salt for password encrypyion
salt="8sFt66rZ"

app.secret_key = 'your secret key'

# Database to store voter information
conn = sqlite3.connect('../voting.db', check_same_thread=False)
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS account (reg_index INTEGER PRIMARY KEY AUTOINCREMENT, license_num text, name text, username text, password text, generate_id text)')  


#Login page with GET and POST requests
@app.route('/login/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...    
    msg = ''
    
    # Check if "username" and "password" POST requests exist
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        
        # Check if account exists using SQL
        cur.execute('SELECT * FROM account WHERE (username=?)', (username,))
        # Fetch one record and return result
        accounts = cur.fetchone()
        
        # If account exists in accounts table in database
        if accounts:
            fetched_password = accounts[4]
            crypted_pw = passlib.hash.apr_md5_crypt.hash(password, salt=salt)
            if(crypted_pw == fetched_password):
                
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = accounts[0]
                session['username'] = accounts[3]
                
                # Redirect to profile page
                return redirect(url_for('profile'))
            else:
                #Entered password is incorrect, Show them error message
                msg = 'Incorrect username/password!'
        else:
            # Account doesnt exist or password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)

#Logout
@app.route('/login/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   # Redirect to login page
   return redirect(url_for('login'))



#Registration page with GET and POST requests
@app.route('/login/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "license_num", "name", "password" and "username" POST requests exist
    if request.method == 'POST' and 'license_num' in request.form and 'name' in request.form and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        license_num = request.form['license_num']
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        
        # Check if account exists using SQL using License number
        cur.execute('SELECT license_num FROM account WHERE (license_num=?)', (license_num,))
        account_license = cur.fetchone()
        
        #Check if account exists using Username if unique License ID is provided
        cur.execute('SELECT username FROM account WHERE (username=?)', (username,))
        account_username = cur.fetchone()
        
        # If account exists show error and validation checks
        if account_license:
            msg = 'Account already exists!'
        elif account_username:
            msg = 'Username already exists!'
        elif not re.match(r'^[0-9a-zA-Z]{4,9}$', license_num):
            msg = 'License has 8 characters with no spaces'
        elif bool(re.fullmatch('[A-Za-z]{2,25}( [A-Za-z]{2,25})?', name)) == False:
            msg = 'Invalid name'
        elif not re.match(r'^[a-zA-Z0-9]([._](?![._])|[a-zA-Z0-9]){4,18}[a-zA-Z0-9]$', username) or len(username)<4:
            msg = 'Username should have minimum 6 characters'
        elif not re.match(r'[A-Za-z0-9]+', password):
            msg = 'Invalid password'
        elif not license_num or not name or not username or not password or not username:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and form data is valid, Hash the Password
            hashed = passlib.hash.apr_md5_crypt.hash(password, salt=salt)

            #generate random ID for user to use this during Voting
            def generate_id_val(id_len):
                generate_id = ''.join(random.choices(string.ascii_letters + string.digits, k=id_len))
                return generate_id
            
            generate_id = generate_id_val(10)
            
            #Create a user entry using License Number, Name, Password, Username and Generated ID
            cur.execute('INSERT INTO account (license_num, name, username, password, generate_id) VALUES (?,?,?,?,?)', (license_num, name, username, hashed,generate_id,))
            conn.commit()
            
            msg = f'You have successfully registered!'

            #Redirect to Login page
            return redirect(url_for('login'))

    elif request.method == 'POST':
        # Form is empty 
        msg = 'Please fill out the form!'

    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


#Profile page logged in using username and password
@app.route('/login/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cur.execute('SELECT * FROM account WHERE (reg_index=?)', (session['id'],))
        accounts = cur.fetchone()

        # Show the profile page with account info
        return render_template('profile.html', account=accounts)
    
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
