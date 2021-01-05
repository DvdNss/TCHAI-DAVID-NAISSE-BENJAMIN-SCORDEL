import hashlib
from datetime import date

from flask import *
from flask import g

import config as cfg
from tchai import database as db

app = Flask(__name__)


@app.teardown_appcontext
def close_database_connection(exception):
    """Closes database connection."""

    database = getattr(g, '_database', None)
    if database is not None:
        database.close()


@app.route(cfg.LIST_USERS, methods=[cfg.LIST_USERS_METHOD])
def list_users():
    """Lists all users."""

    cursor = db.get_database().cursor()
    cursor.execute('SELECT * FROM user')
    names = cursor.fetchall()
    html = '<h1>Registered users : </h1>'
    for name in names:
        html += '<li>    ' + name[1] + ' - ' + str(name[2]) + '€ ; </li>'
    html += '</ul>\n'
    return html


@app.route(cfg.DISPLAY_USER, methods=[cfg.DISPLAY_USER_METHOD])
def get_user(uname):
    """Displays <user> information."""

    connection = db.get_database()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM user \
                        WHERE name=?", (uname,))
    connection.commit()
    result = cursor.fetchall()

    if len(result) == 0:
        return 'Error -> User doesn\'t exist', 400

    html = '<h1>User Data : </h1>'
    html += '<li>  Num: ' + str(result[0][0]) + '</li>'
    html += '<li>  Name: ' + str(result[0][1]) + '</li>'
    html += '<li>  Pay: ' + str(result[0][2]) + '€ </li>'

    return html


@app.route(cfg.ADD_USER, methods=[cfg.ADD_USER_METHOD])
def add_user(uname, pay):
    """Adds user given a name and a pay."""

    connection = db.get_database()
    cursor = connection.cursor()
    cursor.execute('INSERT INTO user (name, pay) \
                        VALUES (?, ?)', (uname, int(pay)))
    connection.commit()
    resp = list_users()

    return resp


@app.route(cfg.RMV_USER, methods=[cfg.RMV_USER_METHOD])
def remove_user(uname):
    connection = db.get_database()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM user \
                            WHERE name=?', (uname,))
    user = cursor.fetchall()
    cursor.execute('DELETE FROM trans \
                                WHERE p1=? OR p2=?', (user[0][0], user[0][0],))
    cursor.execute('DELETE FROM user \
                        WHERE name=?', (uname,))
    connection.commit()

    resp = list_users()

    return resp


@app.route(cfg.LIST_TRANSACTIONS, methods=[cfg.LIST_TRANSACTIONS_METHOD])
def list_transactions():
    """Displays all transactions."""

    connection = db.get_database()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM trans \
                        ORDER BY date')
    result = cursor.fetchall()

    html = '<h1>Registered transactions : </h1>'
    for i in range(len(result)):
        cursor.execute('SELECT * FROM user \
                            WHERE id=?', (result[i][1],))
        source = cursor.fetchall()
        cursor.execute('SELECT * FROM user \
                                    WHERE id=?', (result[i][2],))
        rec = cursor.fetchall()
        html += '<li> Transaction N°' + str(
            result[i][0]) + ' --> FROM   ' + source[0][1] + '   TO   ' + rec[0][1] + '   AMOUNT   ' + str(
            result[i][3]) + '€   ON   ' + str(result[i][4]) + ' </li>'
    html += '</ul>\n'

    return html


@app.route(cfg.USER_TRANSACTIONS, methods=[cfg.USER_TRANSACTIONS_METHOD])
def list_transaction_of(user):
    """Lists transactions of a defined user."""

    connection = db.get_database()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM user \
                        WHERE name=?', (user,))
    result = cursor.fetchall()
    user_id = result[0][0]
    cursor.execute('SELECT * FROM trans \
                        WHERE p1=? OR p2=? \
                        ORDER BY date', (user_id, user_id))
    result = cursor.fetchall()

    html = '<h1>Registered transactions for ' + user + ': </h1>'
    for i in range(len(result)):
        cursor.execute('SELECT * FROM user \
                                WHERE id=?', (result[i][1],))
        source = cursor.fetchall()
        cursor.execute('SELECT * FROM user \
                                        WHERE id=?', (result[i][2],))
        rec = cursor.fetchall()
        html += '<li> Transaction N°' + str(
            result[i][0]) + ' --> FROM   ' + source[0][1] + '   TO   ' + rec[0][1] + '   AMOUNT   ' + str(
            result[i][3]) + '€   ON   ' + str(result[i][4]) + ' </li>'
    html += '</ul>\n'

    return html


@app.route(cfg.ADD_TRANSACTIONS, methods=[cfg.ADD_TRANSACTIONS_METHOD])
def add_transaction(source, recipient, amount):
    """Adds a transaction given a <source>, a <recipient> and an <amount>."""

    connection = db.get_database()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM user \
                        WHERE name=?', (source,))
    data = cursor.fetchall()
    source_id = data[0][0]
    source_amount = data[0][2]
    cursor.execute('SELECT id FROM user \
                        WHERE name=?', (recipient,))
    data = cursor.fetchall()
    recipient_id = data[0][0]

    if source_id == "":
        return "Error -> <From> user doesn\'t exist.\n", 400

    if recipient_id == "":
        return "Error -> <To> user doesn\'t exist.\n", 400

    if source_amount < int(amount):
        return "Error -> Transaction amount exceeds pay.\n", 400

    hash = hashlib.sha256((str(source_id) + "|"
                           + str(recipient_id) + "|"
                           + str(amount) + "|"
                           + str(date.today())).encode()).hexdigest()

    cursor.execute('INSERT INTO trans (p1, p2, amount, date, hash) \
                        VALUES (?,?,?,?,?)', (source_id, recipient_id, amount, date.today(), hash))

    cursor.execute('UPDATE user \
                        SET pay = pay + (?) \
                        WHERE id = (?)', (amount, recipient_id))

    cursor.execute('UPDATE user \
                        SET pay = pay - (?) \
                        WHERE id = (?)', (amount, source_id))

    connection.commit()
    resp = list_transactions()
    resp += list_users()

    return resp


@app.route(cfg.HASH_CHECK, methods=[cfg.HASH_CHECK_METHOD])
def hash_check():
    """Checks if the hash of the transaction n°<id> is correct. """

    connection = db.get_database()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM trans')
    trans = cursor.fetchall()

    html = '<h1>Transactions hash check : </h1>'

    for t in trans:
        id = t[0]
        p1 = t[1]
        p2 = t[2]
        amount = t[3]
        date = t[4]
        hash = t[5]

        checked_hash = hashlib.sha256((str(p1) + "|" +
                                       str(p2) + "|" +
                                       str(amount) + "|" +
                                       str(date)).encode()).hexdigest()

        if checked_hash == hash:
            html += '<li>  Transaction n°' + str(id) + ' has correct hash. </li>'
        else:
            html += '<li>  Transaction n°' + str(id) + ' has incorrect hash. </li>'
            #cursor.execute('UPDATE trans SET hash=? WHERE id=?', (checked_hash, id))

    return html


@app.route(cfg.CREATE_DATABASE, methods=[cfg.CREATE_DATABASE_METHOD])
def create_database():
    db.initialize_database()
    return "Database has been successfully initialized. \n", 201


app.run(host='0.0.0.0', debug=True)
