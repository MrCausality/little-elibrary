from flask import Flask, render_template, request, \
    redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Books, User_Books, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from functools import wraps

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Little e-Library"


# Connect to Database and create database session
engine = create_engine('sqlite:///littleelibrary.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def login_required(f):
    """Decorator function to login protect other pages"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@app.route('/login')
def showLogin():
    """Creates anti-forgery state token"""
    if 'username' in login_session:
        id = getUserID(login_session['email'])
        return redirect('/user/' + str(id))
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """Logs user in via Facebook"""
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print("access token received %s " % access_token)

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type' \
          '=fb_exchange_token&client_id=%s&client_secret=%s' \
          '&fb_exchange_token=%s' % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange
        we have to split the token first on commas and select the first index
        which gives us the key : valuefor the server access token then we
        split it on colons to pull out the actual token value and replace
        the remaining quotes with nothing so that it can be used directly
        in the graph api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?' \
          'access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?' \
          'access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;' \
              '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    """Disconnects user from facebook login"""
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' \
          % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Logs user in via Google account"""
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;' \
              '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


# User Helper Functions
def createUser(login_session):
    """Creates user in database"""
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """Takes a user id and returns the user object from User table"""
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """Takes a users email and returns the user object from User table"""
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/gdisconnect')
def gdisconnect():
    """Disconnects a google login session, evoke a current user's token and
    reset their login_session"""
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    parms = ['access_token', 'gplus_id', 'username', 'email', 'picture']
    if result['status'] == '200':
        for parm in parms:
            if parm in login_session:
                del login_session[parm]
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/books/JSON')
@login_required
def bookInfoAllJSON():
    """Returns all books info as JSON"""
    books = session.query(Books).all()
    return jsonify(Books=[b.serialize for b in books])


@app.route('/books/<int:book_id>/JSON')
@login_required
def bookInfoJSON(book_id):
    """Takes a book id and returns its info as JSON"""
    book = session.query(Books).filter_by(id=book_id).one()

    return jsonify(BookInfo=book.serialize)


@app.route('/users/<int:user_id>/JSON')
@login_required
def userJSON(user_id):
    """Takes a user id and returns user's info including all books owned"""
    user = session.query(User).filter_by(id=user_id).one()
    books = session.query(User_Books).filter_by(user_id=user_id).all()
    return jsonify(User=user.serialize,
                   BooksOwned=[i.serialize for i in books])


@app.route('/users/')
@login_required
def showUsers():
    """Shows all users in database"""
    users = session.query(User).order_by(asc(User.name))
    return render_template('users.html', users=users)


@app.route('/books/<int:book_id>/', methods=['GET', 'POST'])
@login_required
def showBook(book_id):
    """Renders page for a single book in database.
    If POST, adds that book to users collection."""

    book = session.query(Books).filter_by(id=book_id).one()
    try:
        book_owned = session.query(User_Books).filter_by(
            user_id=login_session['user_id'], book_id=book_id).one()
        owned = True
    except:
        owned = False
    if request.method == 'POST':
        if not owned:
            add_book = User_Books(user_id=login_session['user_id'],
                                  book_id=book.id, status='Unread')
            session.add(add_book)
            flash('%s Successfully Added to Collection' % book.title)
            session.commit()
            return redirect(url_for('showUser',
                                    user_id=login_session['user_id']))
        else:
            flash('%s is already in your collection!' % book.title)
            return redirect(url_for('showUser',
                                    user_id=login_session['user_id']))
    else:
        return render_template('book.html', book=book, owned=owned,
                               user_id=login_session['user_id'])


@app.route('/books/')
@login_required
def showBooks():
    """Renders page for all books in database"""
    books = session.query(Books).order_by(asc(Books.title))
    owned = session.query(User_Books).filter_by(
        user_id=login_session['user_id'])
    return render_template('books.html', owned=owned, books=books)


@app.route('/book/new/', methods=['GET', 'POST'])
@login_required
def newBook():
    """Creates a new book"""
    if request.method == 'POST':
        new_book = Books(
            title=request.form['title'],
            description=request.form['description'],
            author=request.form['author'])
        session.add(new_book)
        flash('New Book %s Successfully Created' % new_book.title)
        session.commit()
        return redirect(url_for('showBooks'))
    else:
        return render_template('newBook.html')


@app.route('/user/')
@app.route('/user/<int:user_id>/')
@app.route('/user/<int:user_id>/books/')
@login_required
def showUser(user_id):
    """Renders page showing a users entire collection"""
    if not user_id:
        user_id = login_session['user_id']
    user = session.query(User).filter_by(id=user_id).one()
    user_books = session.query(User_Books).filter_by(user_id=user_id).all()
    ids = []
    for book in user_books:
        ids.append(book.book_id)
    books = session.query(Books).filter(Books.id.in_(ids)).all()
    for book in books:
        for b in user_books:
            if b.book_id == book.id:
                book.status = b.status
                book.notes = b.notes
    if login_session['user_id'] != user_id:
        return render_template('publicUser.html', user_id=user_id,
                               user=user, books=books)
    else:
        return render_template('user.html', user_id=user_id, user=user,
                               books=books, user_books=user_books)


@app.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def editUser(user_id):
    """Takes a user id and renders page allowing
    user to edit their own details."""
    edited_user = session.query(User).filter_by(id=user_id).one()
    if login_session['user_id'] != user_id:
        return "<script>function myFunction() {alert('You are not " \
               "authorized to edit this user');}" \
               "</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['submit'] == "cancel":
            return redirect(url_for('showUser', user_id=user_id))
        if request.form['name']:
            edited_user.name = request.form['name']
        session.add(edited_user)
        session.commit()
        flash('User Successfully Edited')
        return redirect(url_for('showUser', user_id=user_id))
    else:
        return render_template('editUser.html', user_id=user_id,
                               user=edited_user)


@app.route('/user/<int:user_id>/delete/', methods=['GET', 'POST'])
@login_required
def deleteUser(user_id):
    """Takes a user id and deletes that user from the database"""
    user_to_delete = session.query(User).filter_by(id=user_id).one()
    user_books_to_delete = session.query(User_Books).filter_by(
        user_id=user_id).all()
    if user_to_delete.id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not " \
               "authorized to delete this user.');}" \
               "</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(user_to_delete)
        session.delete(user_books_to_delete)
        flash('%s Successfully Removed User ' % user_to_delete.name)
        session.commit()
        return redirect(url_for('disconnect'))
    else:
        return render_template('deleteUser.html', user_id=user_id)


@app.route('/user/<int:user_id>/book/<int:book_id>/edit',
           methods=['GET', 'POST'])
@login_required
def editUserBook(user_id, book_id):
    """Edits the status and notes of a users book in collection"""
    if login_session['user_id'] != user_id:
        return "<script>function myFunction() {alert('You are not " \
               "authorized to edit this users library.');}" \
               "</script><body onload='myFunction()''>"
    edited_book = session.query(User_Books).filter_by(
        user_id=user_id, book_id=book_id).one()
    book_info = session.query(Books).filter_by(id=book_id).one()
    if request.method == 'POST':
        if request.form['submit'] == "cancel":
            return redirect(url_for('showUser', user_id=user_id))
        if request.form['status']:
            edited_book.status = request.form['status']
        if request.form['notes']:
            edited_book.notes = request.form['notes']
        session.add(edited_book)
        session.commit()
        flash('%s Successfully Edited' % book_info.title)
        return redirect(url_for('showUser', user_id=user_id))
    else:
        return render_template('editUserBook.html', user_id=user_id,
                               book_id=book_id, book=book_info,
                               user_book=edited_book)


@app.route('/<int:user_id>/<int:book_id>/delete/', methods=['GET', 'POST'])
@login_required
def deleteUserBook(user_id, book_id):
    """Removes book from users collection"""
    book_to_delete = session.query(User_Books).filter_by(
        book_id=book_id, user_id=user_id).one()
    book_info = session.query(Books).filter_by(id=book_id).one()
    if book_to_delete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not " \
               "authorized to delete books for this user.');}" \
               "</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(book_to_delete)
        flash('%s Successfully Removed From Collection' % book_info.title)
        session.commit()
        return redirect(url_for('showUser', user_id=user_id))
    else:
        return render_template('deleteUserBook.html', user_id=user_id,
                               book_id=book_id, book=book_info)


@app.route('/disconnect')
def disconnect():
    """Disconnects the user from FB or Google account"""
    if 'provider' in login_session:
        parms = ['username', 'email', 'picture', 'user_id', 'provider']
        if login_session['provider'] == 'google':
            gdisconnect()
            parms.extend(['gplus_id', 'credentials'])
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            parms.append('facebook_id')
        for parm in parms:
            if parm in login_session:
                del login_session[parm]
        flash("You have successfully been logged out.")
        return redirect(url_for('showLogin'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showLogin'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
