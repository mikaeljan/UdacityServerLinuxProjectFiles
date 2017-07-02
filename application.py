from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   jsonify,
                   url_for,
                   flash)

from sqlalchemy import create_engine, asc, func
from sqlalchemy.orm import sessionmaker
from db_setup import Base, User, Item, Category
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('/var/www/catalog/catalog/client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Web Application"

# check the localhost par.
engine = create_engine('postgresql://catalog:catalog@localhost/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# JSON APIs to view Catalog Information
@app.route('/catalog.json')
def categoryJSON():
    categories = session.query(Category).all()
    return jsonify(Category=[c.serialize for c in categories])


@app.route('/catalog/<category_name>/<book_title>.json')
def itemJSON(category_name, book_title):
    item = session.query(Item).filter_by(book_title=book_title).one()
    return jsonify(Book=item.serialize)


@app.route('/catalog/<category_name>/items.json')
def itemsJSON(category_name):
    items = session.query(Item).filter_by(category_name=category_name).all()
    return jsonify(Books=[i.serialize for i in items])


# =================== Connecting/Disconnecting - Routing =====================
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    # Exchange client token for long-lived server-side token
    app_id = json.loads(
        open('/var/www/catalog/catalog/fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(
        open('/var/www/catalog/catalog/fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/v2.9/oauth/access_token?'
           'grant_type=fb_exchange_token&client_id=%s&client_secret=%s'
           '&fb_exchange_token=%s') % (app_id, app_secret, access_token)
    http = httplib2.Http()
    result = http.request(url, 'GET')[1]
    data = json.loads(result)

    # Extract the access token from response
    token = 'access_token=' + data['access_token']

    # Use token to get user info from API.
    url = 'https://graph.facebook.com/v2.9/me?%s&fields=name,id,email' % token
    http = httplib2.Http()
    result = http.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session
    # in order to properly logout, let's strip out
    # the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = ('https://graph.facebook.com/v2.9/me/'
           'picture?%s&redirect=0&height=200&width=200' % token)
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
    output += (' " style = "width: 300px; height: 300px;border-radius:'
               ' 150px;-webkit-border-radius:'
               '150px;-moz-border-radius: 150px;"> ')

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = ('https://graph.facebook.com/'
           '%s/permissions?access_token=%s') % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "You have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps(('Invalid state '
                                             'parameter.')), 401)
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
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('This user is already logged.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    login_session['provider'] = 'google'

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists otherwise create user
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
    output += (' " style = "width: 150px; height: 150px;border-radius: '
               '150px;-webkit-border-radius: '
               '150px;-moz-border-radius: 150px;"> ')
    flash("You are now logged in as %s" % login_session['username'])
    print "done!"
    return output

    # DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('This user is not logged'), 401)
    	response.headers['Content-Type'] = 'application/json'
        return response
    url = ('https://accounts.google.com/'
           'o/oauth2/revoke?token=%s') % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        response = make_response(json.dumps('Successfully disconnected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(('Failed to revoke '
                                             'token for given user.'), 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('show_catalog'))
    else:
        flash("You were not logged in")
        return redirect(url_for('show_catalog'))
# ==================================================================


@app.route('/')
@app.route('/catalog')
def show_catalog():
    """ This shows main menu and lists all categories and last 10 items"""
    categories = session.query(Category).order_by(Category.name).all()
    items = session.query(Item).order_by(Item.created_on).limit(10).all()
    item_sum = session.query(func.count(Item.category_name),
                             Item.category_name).group_by(
                             Item.category_name).all()

    if 'username' not in login_session:
        return render_template('public_catalog.html',
                               item_sum=item_sum,
                               categories=categories,
                               items=items)
    else:
        return render_template('show_catalog.html',
                               item_sum=item_sum,
                               categories=categories,
                               items=items)


@app.route('/catalog/<category_name>/items')
def show_items(category_name):
    """This shows the specified category and all the list items"""
    categories = session.query(Category).order_by(Category.name).all()
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_name=category.name).all()
    item_sum = session.query(func.count(Item.category_name),
                             Item.category_name).group_by(
                             Item.category_name).all()
    return render_template('show_items.html',
                           categories=categories,
                           item_sum=item_sum,
                           category=category,
                           items=items)


@app.route('/catalog/<category_name>/<book_title>')
def show_item(category_name, book_title):
    """This shows the specified item and its description"""
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(book_title=book_title).one()
    return render_template('show_item.html', item=item, category=category)


@app.route('/catalog/<book_title>/edit',  methods=['POST', 'GET'])
def edit_item(book_title):
    """This enables editing of an item"""
    # Checks whether visitor is logged in, if not gets redirected
    #  and alerted to log in
    if 'username' not in login_session:
        flash('Please login to access this section.')
        return redirect(url_for('show_catalog'))
    categories = session.query(Category).all()
    itemToEdit = session.query(Item).filter_by(book_title=book_title).one()
    if itemToEdit.creator_id != login_session['user_id']:
        return ("<script>function myFunction() {alert('You are not "
                "authorized to edit this item. Please create your "
                "own in order to edit it.');"
                "window.location.href='/catalog';}</script>"
                "<body onload='myFunction()'>")

    if request.method == 'POST':
        if request.form['edit_item_name']:
            itemToEdit.book_title = request.form['edit_item_name']
        if request.form['edit_item_author']:
            itemToEdit.author = request.form['edit_item_author']
        if request.form['edit_item_year']:
            itemToEdit.year_published = request.form['edit_item_year']
        if request.form['edit_item_des']:
            itemToEdit.description = request.form['edit_item_des']
        if request.form['edit_item_cat']:
            itemToEdit.category_name = request.form['edit_item_cat']
        if request.form['edit_item_price']:
            itemToEdit.price = request.form['edit_item_price']

        session.add(itemToEdit)
        session.commit()
        flash('Item Successfully Edited')
        return redirect(url_for('show_catalog'))
    else:
        return render_template('edit_item.html',
                               categories=categories,
                               item=itemToEdit,
                               book_title=book_title)


@app.route('/catalog/<book_title>/delete', methods=['POST', 'GET'])
def delete_item(book_title):
    """Enables deleting of an item"""
    # Checks whether visitor is logged in, if not gets redirected
    # and alerted to log in
    if 'username' not in login_session:
        flash('Please login to access this section.')
        return redirect(url_for('show_catalog'))
    itemToDelete = session.query(Item).filter_by(book_title=book_title).one()
    if itemToDelete.creator_id != login_session['user_id']:
        return ("<script>function myFunction() {alert('You are not authorized"
                " to remove this item."
                " Please create your own in order to remove it.');"
                "window.location.href='/catalog';}</script>"
                "<body onload='myFunction()'>")
    if request.method == 'POST':
        session.delete(itemToDelete)
        flash('Book Successfully Deleted')
        session.commit()
        return redirect(url_for('show_catalog'))
    else:
        return render_template('delete_item.html',
                               book_title=book_title,
                               item=itemToDelete)


@app.route('/catalog/new', methods=['POST', 'GET'])
def new_item():
    """Enables creating new item"""
    # Checks whether visitor is logged in,
    # if not gets redirected and alerted to log in
    if 'username' not in login_session:
        flash('Please login to access this section.')
        return redirect(url_for('show_catalog'))
    categories = session.query(Category).all()
    if request.method == 'POST':
        new_item = Item(book_title=request.form['new_item_name'],
                        description=request.form['new_item_des'],
                        price=request.form['new_item_price'],
                        author=request.form['new_item_author'],
                        year_published=request.form['new_item_year'],
                        category_name=request.form['new_item_cat'],
                        creator_id=login_session['user_id'])
        session.add(new_item)
        session.commit()
        flash('Book Successfully Added!')
        return redirect(url_for('show_catalog'))
    else:
        return render_template('new_item.html', categories=categories)


# User Helper Functions

def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
