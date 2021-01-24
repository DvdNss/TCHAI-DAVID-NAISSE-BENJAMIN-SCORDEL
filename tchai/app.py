import hashlib
from datetime import date

from flask import *
from flask import g
import configparser
import crypto
from tchai import database as db

config = configparser.ConfigParser()
config.read('../config.ini')

app = Flask(__name__)


def verify_signature(id):
    """Verifies signature of a transaction given a transaction id.

        - id -> int

    """

    cursor = db.get_database().cursor()  # Gets database
    cursor.execute('SELECT * FROM trans WHERE id=(?)',
                   (id,))  # Pull the transaction
    data = cursor.fetchall()  # Gets the result of the request

    p1 = data[0][1]  # Fetches id of source
    hash = data[0][5]  # Fetches hash of transaction
    signature = data[0][6]  # Fetches signature of transaction

    cursor.execute('SELECT name FROM user WHERE id=?',
                   (p1,))  # Pulls name of user
    data = cursor.fetchall()  # Fetches result
    name = data[0][0]  # Fetches name of the source

    return crypto.verification(name, signature, hash)  # Returns true if verification of signature is good


@app.teardown_appcontext
def close_database_connection(exception):
    """Closes database connection."""

    database = getattr(g, '_database', None)  # Gets the database
    if database is not None:  # If database is running
        database.close()  # Shuts it down


@app.route(config['COMMAND']['LIST_USERS'], methods=[config['METHOD']['LIST_USERS']])
def list_users():
    """Lists all users."""

    cursor = db.get_database().cursor()  # Gets database
    cursor.execute('SELECT * FROM user')  # Pulls all users
    names = cursor.fetchall()  # Fetches the name of the user

    html = '<h1>Registered users : </h1>'  # HTML syntax for browser display
    for name in names:
        html += '<li>    ' + name[1] + ' - ' + str(name[2]) + '€ ; </li>'
    html += '</ul>\n'

    return html


@app.route(config['COMMAND']['DISPLAY_USER'], methods=[config['METHOD']['DISPLAY_USER']])
def get_user(uname):
    """Displays <user> information."""

    connection = db.get_database()  # Gets database
    cursor = connection.cursor()  # Places the cursor
    cursor.execute("SELECT * FROM user WHERE name=?",
                   (uname,))  # Pull the user with the given name
    result = cursor.fetchall()  # Fetches the result

    if len(result) == 0:
        return 'Error -> User doesn\'t exist', 400
    else:
        html = '<h1>User Data : </h1>'  # HTML syntax for browser display
        html += '<li>  Num: ' + str(result[0][0]) + '</li>'
        html += '<li>  Name: ' + str(result[0][1]) + '</li>'
        html += '<li>  Pay: ' + str(result[0][2]) + '€ </li>'

    connection.commit()  # Closes connection

    return html


@app.route(config['COMMAND']['ADD_USER'], methods=[config['METHOD']['ADD_USER']])
def add_user(uname, pay):
    """Adds user given a name and a pay."""

    crypto.generate_key(uname)  # Generates public and private keys for user
    connection = db.get_database()  # Gets database
    cursor = connection.cursor()
    cursor.execute('INSERT INTO user (name, pay) VALUES (?, ?)',
                   (uname, int(pay)))  # Inserts user values
    connection.commit()  # Closes connection
    resp = list_users()  # HTML display all users

    return resp


@app.route(config['COMMAND']['RMV_USER'], methods=[config['METHOD']['RMV_USER']])
def remove_user(uname):
    """Removes an user given its name. """

    connection = db.get_database()  # Gets the database
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM user WHERE name=?',
                   (uname,))  # Selects user from database
    user = cursor.fetchall()

    cursor.execute('DELETE FROM trans WHERE p1=? OR p2=?',
                   (user[0][0], user[0][0],))  # Deletes all rel. transactions
    cursor.execute('DELETE FROM user WHERE name=?',
                   (uname,))  # Deletes the user

    connection.commit()  # Closes connection
    resp = list_users()  # Display users

    return resp


@app.route(config['COMMAND']['LIST_TRANSACTIONS'], methods=[config['METHOD']['LIST_TRANSACTIONS']])
def list_transactions():
    """Displays all transactions."""

    connection = db.get_database()  # Gets database
    cursor = connection.cursor()  # Places cursor
    cursor.execute('SELECT * FROM trans ORDER BY date')  # Pulls transactions of user ordered by date
    result = cursor.fetchall()  # Fetches the result

    html = '<h1>Registered transactions : </h1>'  # HTML syntax to display

    for i in range(len(result)):  # Gathers information of user given its id
        cursor.execute('SELECT * FROM user WHERE id=?', (result[i][1],))
        source = cursor.fetchall()
        cursor.execute('SELECT * FROM user WHERE id=?', (result[i][2],))
        rec = cursor.fetchall()
        html += '<li> Transaction N°' + str(
            result[i][0]) + ' --> SOURCE: [ ' + source[0][1] + ' ] || RECIPIENT[ ' + rec[0][1] + ' ] || AMOUNT[ ' + str(
            result[i][3]) + '€ ] || DATE [ ' + str(result[i][4]) + ' ] </li>'
    html += '</ul>\n'

    html += check_transactions()

    return html


@app.route(config['COMMAND']['USER_TRANSACTIONS'], methods=[config['METHOD']['USER_TRANSACTIONS']])
def list_transaction_of(user):
    """Lists transactions of a defined user."""

    connection = db.get_database()  # Gets the database
    cursor = connection.cursor()  # Places the cursor
    cursor.execute('SELECT * FROM user WHERE name=?', (user,))  # Gathers informations of user given its name
    result = cursor.fetchall()  # Fetches result
    user_id = result[0][0]  # Pulls its id
    cursor.execute('SELECT * FROM trans WHERE p1=? OR p2=? ORDER BY date', (user_id, user_id))  # Selects transactions
    result = cursor.fetchall()  # Fetches result

    html = '<h1>Registered transactions for ' + user + ': </h1>'  # HTML Syntax to display

    for i in range(len(result)):
        cursor.execute('SELECT * FROM user WHERE id=?', (result[i][1],))
        source = cursor.fetchall()
        cursor.execute('SELECT * FROM user WHERE id=?', (result[i][2],))
        rec = cursor.fetchall()
        html += '<li> Transaction N°' + str(
            result[i][0]) + ' --> SOURCE: [ ' + source[0][1] + ' ] || RECIPIENT[ ' + rec[0][1] + ' ] || AMOUNT[ ' + str(
            result[i][3]) + '€ ] || DATE [ ' + str(result[i][4]) + ' ] </li>'
    html += '</ul>\n'

    html += check_transactions()

    return html


@app.route(config['COMMAND']['ADD_TRANSACTION'], methods=[config['METHOD']['ADD_TRANSACTION']])
def add_transaction(source, recipient, amount):
    """Adds a transaction given a <source>, a <recipient> and an <amount>."""

    connection = db.get_database()  # Gets the database
    cursor = connection.cursor()  # Places the cursor
    cursor.execute('SELECT * FROM user WHERE name=?', (source,))  # Selects informations of "from" user given its name
    data = cursor.fetchall()  # Fetches result
    sourceId = data[0][0]  # Pulls user's id
    sourceAmount = data[0][2]  # Pull user's amount

    cursor.execute('SELECT id FROM user WHERE name=?', (recipient,))  # Selects id of "to" user given its name
    data = cursor.fetchall()  # Fetches result
    recipientId = data[0][0]  # Pulls "to" user's id

    if sourceId == "":
        return "Error -> <From> user doesn\'t exist.\n", 400
    elif recipientId == "":
        return "Error -> <To> user doesn\'t exist.\n", 400
    elif sourceAmount < int(amount):
        return "Error -> Transaction amount exceeds pay.\n", 400
    else:
        cursor.execute('SELECT * FROM trans ORDER by id')  # Selects all transactions
        last_trans = cursor.fetchall()

        if len(last_trans) != 0:  # Builds the hash
            last_hash = last_trans[len(last_trans) - 1][5]

            hash = hashlib.sha256((str(sourceId) + "|"
                                   + str(recipientId) + "|"
                                   + str(amount) + "|"
                                   + str(date.today()) + "|"
                                   + str(last_hash)).encode()).hexdigest()
        else:
            hash = hashlib.sha256((str(sourceId) + "|"
                                   + str(recipientId) + "|"
                                   + str(amount) + "|"
                                   + str(date.today())).encode()).hexdigest()

        signature = crypto.sign(source, hash)  # Builds the signature

        cursor.execute('INSERT INTO trans (p1, p2, amount, date, hash, signature) VALUES (?,?,?,?,?,?)',
                       (sourceId, recipientId, amount, date.today(), hash, signature))  # Inserts transaction values

        cursor.execute('UPDATE user SET pay = pay + (?) WHERE id = (?)',
                       (amount, recipientId))  # Updates "from" user's sold

        cursor.execute('UPDATE user SET pay = pay - (?) WHERE id = (?)',
                       (amount, sourceId))  # Updates "to" user's sold

        connection.commit()
        resp = list_transactions()
        resp += list_users()

    return resp


@app.route(config['COMMAND']['CHECK'], methods=[config['METHOD']['CHECK']])
def check_transactions():
    """Checks if the hashes of the transactions are correct. """

    connection = db.get_database()  # Gets the database
    cursor = connection.cursor()  # Places the cursor
    cursor.execute('SELECT * FROM trans ORDER by id')  # Selects trans by id
    trans = cursor.fetchall()

    html = '<h1>Transactions check : </h1>'  # HTML Syntax to display
    last_hash = ''  # Previous hash

    for i, t in enumerate(trans):
        id = t[0]  # id of trans
        p1 = t[1]  # p1 of trans
        p2 = t[2]  # p2 of trans
        amount = t[3]  # amount of trans
        date = t[4]  # date of trans
        hash = t[5]  # hash of trans

        if i == 0:  # If it's the first transaction, no previous hash
            checked_hash = hashlib.sha256((str(p1) + "|" +
                                           str(p2) + "|" +
                                           str(amount) + "|" +
                                           str(date)).encode()).hexdigest()
        else:  # else take previous hash in account
            checked_hash = hashlib.sha256((str(p1) + "|" +
                                           str(p2) + "|" +
                                           str(amount) + "|" +
                                           str(date) + "|" +
                                           str(last_hash)).encode()).hexdigest()

        last_hash = hash  # Privous hash update
        goodSign = verify_signature(id=id)  # Verifies signature

        if checked_hash == hash and goodSign:  # HTML Display
            html += '<li>  Transaction n°' + str(id) + ' has correct hash and signature. No changes noticed. </li>'
        elif not goodSign:
            html += '<li>  Transaction n°' + str(id) + ' has incorrect signature. It probably has been modified from the outside. </li>'
        elif not checked_hash == hash:
            html += '<li>  Transaction n°' + str(id) + ' has incorrect hash. It probably has been modified from the outside. </li>'

    return html


@app.route(config['COMMAND']['CREATE_DATABASE'], methods=[config['METHOD']['CREATE_DATABASE']])
def create_database():
    """Creates the database. To do before first request."""

    db.initialize_database()
    return "Database has been successfully initialized. \n", 201


app.run(host='0.0.0.0', debug=True)  # Launch the API
