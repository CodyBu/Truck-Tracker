from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from hashlib import sha256
import re
from datetime import date

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'group4'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'TruckTracker'

# Intialize MySQL
mysql = MySQL(app)

# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests
@app.route('/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        hashPassword = sha256(request.form['password'].encode()).hexdigest()
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM USER WHERE UserName = \"%s\" AND HashPwd = \"%s\"' % (username, hashPassword))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['UserName'] = account['UserName']
            if account['UserType'] == "Admin":
                return redirect(url_for('admin'))
            elif account['UserType'] == "Driver":
                return redirect(url_for('driver'))
            elif account['UserType'] == "Mechanic":
                return redirect(url_for('mechanic'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('UserName', None)
   # Redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/Falsk/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" POST requests exist (user submitted form)
    if request.method == 'POST' and ('username' and 'firstname' and 'lastname' and 'password' and 'usertype') in request.form:
        # Create variables for easy access
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        hashPassword = sha256(request.form['password'].encode()).hexdigest()
        usertype = request.form['usertype']

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM USER WHERE UserName = \"%s\"' % username)
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not hashPassword:
            msg = 'Please fill out the form!'
        else:
        # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO USER (UserName, FirstName, LastName, HashPwd, UserType) VALUES ( \"%s\", \"%s\", \"%s\", \"%s\", \"%s\")' % (username, firstname, lastname, hashPassword, usertype))
            mysql.connection.commit()
            msg = 'Employee Added!'

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


# http://localhost:5000/pythinlogin/admin - this will be the admin home page, only accessible for logged in admins
@app.route('/trucktracker/admin')
def admin():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('admin.html', username=session['UserName'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/driver - this will be the driver home page, only accessible for logged in drivers
@app.route('/trucktracker/driver')
def driver():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('driver.html', username=session['UserName'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/mechanic - this will be the mechanic home page, only accessible for logged in mechanics
@app.route('/trucktracker/mechanic')
def mechanic():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('mechanic.html', username=session['UserName'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/trucktracker/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM USER WHERE UserName = \"%s\"" % session['UserName'])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/trucktracker/employees')
def employees():
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT UserName, FirstName, LastName, UserType FROM USER WHERE UserType != \"%s\"" % "Admin")
        employeeList = cursor.fetchall()
        # Show the profile page with account info
        return render_template('employees.html', employeeList=employeeList)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/trucktracker/vehicles')
def vehicles():
    if 'loggedin' in session:
        # We need all the vehicle info to display
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM VEHICLE")
        vehicleList = cursor.fetchall()
        # Show list of vehicles
        return render_template('vehicles.html', vehicleList=vehicleList)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/trucktracker/vehicle-registration', methods=['GET', 'POST'])
def addVehicle():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" POST requests exist (user submitted form)
    if request.method == 'POST' and ('vehicleid' and 'vin' and 'mileage' and 'plate' and 'type') in request.form:
        # Create variables for easy access
        vehicleid = request.form['vehicleid']
        vin = request.form['vin']
        mileage = int(request.form['mileage'])
        plate = request.form['plate']
        type = request.form['type']

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM VEHICLE WHERE VehicleID = \"%s\"' % vehicleid)
        vehicle = cursor.fetchone()
        # If account exists show error and validation checks
        if vehicle:
            msg = ' Vehicle already exists!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute(
                'INSERT INTO VEHICLE (VehicleID, VIN, Mileage, LicensePlate, VehicleType) VALUES ( \"%s\", \"%s\", %d, \"%s\", \"%s\")' % (vehicleid, vin, mileage, plate, type))
            mysql.connection.commit()
            msg = 'Vehicle Added!'

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('addvehicle.html', msg=msg)

@app.route('/trucktracker/vehicles/vehicle-profile', methods=['GET', 'POST'])
def vehicleProfile():
    if request.method == 'POST' and 'selected' in request.form:
        vehicleID = request.form['selected']
        session['VehicleID'] = vehicleID
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM VEHICLE WHERE VehicleID = \"%s\"' % vehicleID)
        vehicle = cursor.fetchone()
        cursor.execute('SELECT * FROM MAINTENANCE_ENTRY WHERE Vehicle = \"%s\"' % vehicleID)
        entries = cursor.fetchall()
        return render_template('vehicleprofile.html', vehicle=vehicle, entries=entries)
    else:
        return render_template('vehicles.html', msg="Please select a vehicle!")

@app.route('/trucktracker/add-entry', methods=['GET', 'POST'])
def addEntry():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" POST requests exist (user submitted form)
    if request.method == 'POST':
        if ('mileage' and 'entrydate') in request.form:
            # Create variables for easy access
            mileage = int(request.form['mileage'])
            entryDate = request.form['entrydate']

            # Check if account exists using MySQL
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO MAINTENANCE_ENTRY (Vehicle, EntryDate, MileageAtTime, Requester) VALUES ( \"%s\", \"%s\", %d, \"%s\")' % (session['VehicleID'], entryDate, mileage, session['UserName']))
            mysql.connection.commit()
            msg = 'Entry Added!'
        if 'note' in request.form:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT EntryID FROM MAINTENANCE_ENTRY')
            # Create variables for easy access
            noteText = request.form['note']
            entry = len(cursor.fetchall())

            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute(
                'INSERT INTO NOTE (NoteText, NoteDate, Entry, User) VALUES ( \"%s\", \"%s\", %d, \"%s\")' % (
                noteText, date.today(), entry, session['UserName']))
            mysql.connection.commit()
    return render_template('addentry.html', msg=msg)

@app.route('/trucktracker/vehicles/view-entry', methods=['GET', 'POST'])
def viewEntry():
    if request.method == 'POST' and 'selected' in request.form:
        entryID = int(request.form['selected'])
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM MAINTENANCE_ENTRY WHERE EntryID = %d' % entryID)
        entry = cursor.fetchone()
        return render_template('viewentry.html', entry=entry)
    else:
        return render_template('vehicleprofile.html', msg="Please select a vehicle!")

if __name__ == '__main__':
    app.run()
