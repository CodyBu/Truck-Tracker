from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from hashlib import sha256
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
    #clear any existing data in session
    session.clear()
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
            session['UserType'] = account['UserType']
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)

@app.route('/home')
def home():
    if 'loggedin' in session:
        if session['UserType'] == "Admin":
            return redirect(url_for('admin'))
        elif session['UserType'] == "Driver":
            return redirect(url_for('driver'))
        elif session['UserType'] == "Mechanic":
            return redirect(url_for('mechanic'))
    return render_template('index.html')

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.clear()
   # Redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/admin - this will be the admin home page, only accessible for logged in admins
@app.route('/admin')
def admin():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('admin.html', username=session['UserName'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/driver - this will be the driver home page, only accessible for logged in drivers
@app.route('/driver')
def driver():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('driver.html', username=session['UserName'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/mechanic - this will be the mechanic home page, only accessible for logged in mechanics
@app.route('/mechanic')
def mechanic():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('mechanic.html', username=session['UserName'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/profile')
def viewProfile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM USER WHERE UserName = \"%s\"" % session['UserName'])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('employee-profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/profile/update-profile', methods=['POST', 'GET'])
def updateProfile():
    msg = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #check if post method exists
    if request.method == 'POST' and ('first' and 'last') in request.form:
        firstName = request.form['first']
        lastName = request.form['last']
        cursor.execute('UPDATE User SET FirstName = \"%s\", LastName = \"%s\" WHERE UserName = \"%s\"' % (firstName, lastName, session['UserName']))
        mysql.connection.commit()
        msg='Profile Updated!'
    cursor.execute('SELECT FirstName, LastName FROM USER WHERE UserName = \"%s\"' % session['UserName'])
    names = cursor.fetchone()
    return render_template('update-profile.html', names=names, msg=msg)

@app.route('/profile/update-password', methods=['POST', 'GET'])
def updatePassword():
    msg=''
    if request.method == 'POST' and ('old' and 'new' and 'confirm') in request.form:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT HashPwd FROM User WHERE UserName = \"%s\"' % session['UserName'])
        actualPassword = cursor.fetchone()['HashPwd']
        oldHashPassword = sha256(request.form['old'].encode()).hexdigest()
        if oldHashPassword != actualPassword:
            msg = 'Your entered the wrong password'
            return render_template('update-password.html', msg=msg)
        newPassword = request.form['new']
        confirmPassword = request.form['confirm']
        if newPassword != confirmPassword:
            msg = 'Passwords do not match'
            return render_template('update-password.html', msg=msg)
        newHashPassword = sha256(newPassword.encode()).hexdigest()
        cursor.execute('UPDATE USER SET HashPwd = \"%s\" WHERE UserName = \"%s\"' % (newHashPassword, session['UserName']))
        mysql.connection.commit()
        msg = "Password updated successfully!"
    return render_template('update-password.html', msg=msg)


#Employee Section
# http://localhost:5000/Falsk/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/employees/add-employee', methods=['GET', 'POST'])
def addEmployee():
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
        else:
        # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO USER (UserName, FirstName, LastName, HashPwd, UserType) VALUES ( \"%s\", \"%s\", \"%s\", \"%s\", \"%s\")' % (username, firstname, lastname, hashPassword, usertype))
            mysql.connection.commit()
            msg = 'Employee Added!'
    # Show registration form with message (if any)
    return render_template('add-employee.html', msg=msg)

@app.route('/employees/delete-employee', methods=['GET', 'POST'])
def deleteEmployee():
    if request.method == 'POST' and 'selected' in request.form:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        user = request.form['selected']
        if session['UserType'] == 'Admin':
            cursor.execute('DELETE FROM USER WHERE UserName = \"%s\"' % user)
            mysql.connection.commit()
    return redirect(url_for('viewEmployees'))

@app.route('/employees')
def viewEmployees():
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT UserName, FirstName, LastName, UserType FROM USER WHERE UserType != \"%s\"" % "Admin")
        employeeList = cursor.fetchall()
        # Show the profile page with account info
        return render_template('employees.html', employeeList=employeeList)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

#Vehicle Section
@app.route('/vehicles/add-vehicle', methods=['GET', 'POST'])
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
    return render_template('add-vehicle.html', msg=msg)

@app.route('/vehicles/delete')
def deleteVehicle():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM VEHICLE WHERE VehicleID = \"%s\"' % session['VehicleID'])
    mysql.connection.commit()
    return redirect(url_for('viewVehicles'))

@app.route('/vehicles')
def viewVehicles():
    if 'loggedin' in session:
        # We need all the vehicle info to display
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM VEHICLE")
        vehicleList = cursor.fetchall()
        # Show list of vehicles
        return render_template('vehicles.html', vehicleList=vehicleList)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/vehicles/vehicle-profile', methods=['GET', 'POST'])
def vehicleProfile():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST' and 'selected' in request.form:
        vehicleID = request.form['selected']
        session['VehicleID'] = vehicleID
        cursor.execute('SELECT * FROM VEHICLE WHERE VehicleID = \"%s\"' % vehicleID)
        vehicle = cursor.fetchone()
        cursor.execute('SELECT * FROM MAINTENANCE_ENTRY WHERE Vehicle = \"%s\" ORDER BY EntryDate' % vehicleID)
        entries = cursor.fetchall()        
        cursor.execute('SELECT * FROM SERVICE_JUNCTION WHERE Entry IN (SELECT EntryID FROM MAINTENANCE_ENTRY WHERE Vehicle = \"%s\")' % vehicleID)
        serviceList = cursor.fetchall()
        cursor.execute('SELECT * FROM NOTE WHERE Entry IN (SELECT EntryID FROM MAINTENANCE_ENTRY WHERE Vehicle = \"%s\")' % vehicleID)
        noteList = cursor.fetchall()
        return render_template('vehicle-profile.html', vehicle=vehicle, entries=entries, type=session['UserType'], serviceList=serviceList, noteList=noteList)
    elif 'VehicleID' in session:
        cursor.execute('SELECT * FROM VEHICLE WHERE VehicleID = \"%s\"' % session['VehicleID'])
        vehicle = cursor.fetchone()
        cursor.execute('SELECT * FROM MAINTENANCE_ENTRY WHERE Vehicle = \"%s\" ORDER BY EntryDate' % session['VehicleID'])
        entries = cursor.fetchall()
        cursor.execute(
            'SELECT * FROM SERVICE_JUNCTION WHERE Entry IN (SELECT EntryID FROM MAINTENANCE_ENTRY WHERE Vehicle = \"%s\")' % session['VehicleID'])
        serviceList = cursor.fetchall()
        cursor.execute(
            'SELECT * FROM NOTE WHERE Entry IN (SELECT EntryID FROM MAINTENANCE_ENTRY WHERE Vehicle = \"%s\")' % session['VehicleID'])
        noteList = cursor.fetchall()
        return render_template('vehicle-profile.html', vehicle=vehicle, entries=entries, type=session['UserType'], serviceList=serviceList, noteList=noteList)
    else:
        return redirect(url_for('viewVehicles'))

#Entry Section
@app.route('/vehicles/add-entry', methods=['GET', 'POST'])
def addEntry():
    # Output message if something goes wrong...
    msg = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST' and 'mileage' in request.form:
        # Create variables for easy access
        mileage = int(request.form['mileage'])
        selected = request.form.getlist('services')
        cursor.execute('SELECT Mileage FROM VEHICLE WHERE VehicleID = \"%s\"' % session['VehicleID'])
        currentMileage = cursor.fetchone()['Mileage']
        if mileage < currentMileage:
            msg = "Invalid Mileage Value! New Mileage Must Be Larger Than Current Mileage!"
            cursor.execute('SELECT ServiceName FROM Service')
            serviceList = cursor.fetchall()
            return render_template('add-entry.html', msg=msg, serviceList=serviceList)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO MAINTENANCE_ENTRY (Vehicle, EntryDate, MileageAtTime, Requester) VALUES ( \"%s\", \"%s\", %d, \"%s\")' % (session['VehicleID'], date.today(), mileage, session['UserName']))
        cursor.execute('UPDATE VEHICLE SET Mileage = %d WHERE VehicleID = \"%s\"' % (mileage, session['VehicleID']))
        mysql.connection.commit()
        cursor.execute('SELECT LAST_INSERT_ID()')
        entryID = cursor.fetchone()['LAST_INSERT_ID()']

        for service in selected:
            cursor.execute('INSERT INTO SERVICE_JUNCTION (Entry, Service) VALUES ( %d, \"%s\")' % (entryID, service))
            mysql.connection.commit()

        if 'note' in request.form:
            # Create variables for easy access
            noteText = request.form['note']
            cursor.execute(
                'INSERT INTO NOTE (NoteText, NoteDate, Entry, User) VALUES ( \"%s\", \"%s\", %d, \"%s\")' % (
                noteText, date.today(), entryID, session['UserName']))
            mysql.connection.commit()
        msg = 'Entry Added!'
    cursor.execute('SELECT ServiceName FROM Service')
    serviceList = cursor.fetchall()
    return render_template('add-entry.html', msg=msg, serviceList=serviceList)

#Note Section
@app.route('/notes/add-note', methods=['GET', 'POST'])
def addNote():
    msg=''
    if request.method == 'POST' and 'note' in request.form:
        noteText = request.form['note']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO NOTE (NoteText, NoteDate, User) VALUES ( \"%s\", \"%s\", \"%s\")' % (
                    noteText, date.today(), session['UserName']))
        mysql.connection.commit()
        msg = 'Note Added!'
    return render_template('add-note.html', msg=msg)

@app.route('/notes/delete', methods=['GET', 'POST'])
def deleteNote():
    msg=''
    if request.method == 'POST' and 'selected' in request.form:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        noteID = int(request.form['selected'])
        cursor.execute('SELECT * FROM NOTE WHERE NoteID = %d' % noteID)
        note = cursor.fetchone()
        user = note['User']
        if session['UserType'] == 'Admin' or user == session['UserName']:
            cursor.execute('DELETE FROM Note WHERE NoteID = %d' % noteID)
            mysql.connection.commit()
        else:
            msg="You are not permitted to delete this note"
    return redirect(url_for('viewNotes', msg=msg))

@app.route('/notes')
def viewNotes():
    msg = request.args.get('msg')
    if msg is None:
        msg=''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM NOTE WHERE Entry IS NULL ORDER BY NoteDate DESC')
    noteList = cursor.fetchall()
    return render_template('notes.html', noteList=noteList, msg=msg)

#Service Section
@app.route('/services/add-service', methods=['GET', 'POST'])
def addService():
    msg=''
    if request.method == 'POST' and 'name' in request.form:
        serviceName = request.form['name']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM SERVICE WHERE ServiceName = \"%s\"' % serviceName)
        service = cursor.fetchone()
        if service:
            msg = 'Service already exists'
        elif 'description' in request.form:
            description = request.form['description']
            cursor.execute('INSERT INTO SERVICE (ServiceName, ServiceDescription) VALUES ( \"%s\", \"%s\")' % (serviceName, description))
            mysql.connection.commit()
            msg = 'Service Added!'
        else:
            cursor.execute('INSERT INTO SERVICE (ServiceName) VALUES ( \"%s\")' % serviceName)
            mysql.connection.commit()
            msg = 'Service Added!'
    return render_template('add-service.html', msg=msg)

@app.route('/services')
def viewServices():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM SERVICE')
    serviceList = cursor.fetchall()
    return render_template('services.html', serviceList=serviceList)

# Manual
@app.route('/manual')
def viewManual():
    return render_template('manual.html')

if __name__ == '__main__':
    app.run(debug=True)
