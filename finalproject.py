from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import flash
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, StudioItem, User
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
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog"

# connect to the database
engine = create_engine('sqlite:///collectioncatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# set the secret key.
app.secret_key = "CGKDkh8xrtOhLrHdpyVwPMpA"


# Declare my login decorator.
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
# return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


# facebook
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_' \
          'exchange_token&client_id=%s&client_secret' \
          '=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]


# Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange
        we have to split the token first on commas and select the first index
         which gives us the key : value for the server access token then we
         split it on colons to pull out the actual token value and replace
         the remaining quotes with nothing so that it can be used directly
         in the graph api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,' \
          'id,email' % token
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
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token' \
          '=%s&redirect=0&height=200&width=200' % token
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


def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?' \
          'access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
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
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already '
                                            'connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['user_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists, if it doesn't make a new one
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
    output += ' " style = "width: 300px;' \
                         'height: 300px;' \
                         'border-radius: 150px;' \
                         '-webkit-border-radius: 150px;' \
                         '-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
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


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not '
                                            'connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % \
          login_session
    ['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given'
                                            ' user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# json API
@app.route('/category/JSON')
def categoryJSON():
    categories = session.query(categories).all()
    return jsonify(categories=[c.serialize for c in categories])


@app.route('/category/<int:category_id>/studio/JSON')
def StudioJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(studio).filter_by(
        category_id=category_id).all()
    return jsonify(studio=[i.serialize for i in items])


@app.route('/category/<int:category_id>/items/<int:item_id>/JSON')
def categoryItemJSON(category_id, item_id):
    Studio = session.query(Item).filter_by(id=item_id).one()
    return jsonify(studio=Studio.serialize)


# Show all category
@app.route('/')
@app.route('/category/')
def showCategories():
    categories = session.query(Category)
    if 'username' not in login_session:
        return render_template('publicstudio.html', categories=categories)
    else:
        return render_template('categories.html', categories=categories)


# Create a new category
@app.route('/category/new/', methods=['GET', 'POST'])
@login_required
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCategory = Category(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newCategory)
        flash('New Category %s Successfully Created' % newCategory.name)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('newCategory.html')
    # return "This page will be for making a new category"


# Edit a category
@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
@login_required
def editCategory(category_id):
    editedCategory = session.query(
        Category).filter_by(id=category_id).one()
    if editedCategory.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized" \
               " to edit this category. Please create your own category in " \
               "order to edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
            flash('Category Successfully Edited %s' % editedCategory.name)
            return redirect(url_for('showCategory'))
    else:
        return render_template('editCategory.html',
                                category=editedCategory)
# return 'This page will be for editing category %s' % category_id


# Delete a Category
@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
@login_required
def deleteCategory(category_id):
    (Category).filter_by(id=category_id).one()
    if deleteCategory.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized" \
               "to delete this category. Please create your own category in" \
               " order to delete.');}</script><body onload='myFunction()''>"
        if request.method == 'POST':
            session.delete(categoryToDelete)
            session.commit()
        return redirect(
            url_for('showCategories', category_id=category_id))
    else:
        return render_template(
            'deleteCategory.html', category=categoryToDelete)
    # return 'This page will be for deleting category %s' % category_id


# Show a studio
@app.route('/category/<int:category_id>/')
@app.route('/category/<int:category_id>/studio/')
def showStudios(category_id):
    category = session.query(Category).filter_by(id=category_id).first()
    creator = getUserInfo(category.user_id)
    items = session.query(StudioItem).filter_by(
        category_id=category_id).all()
    if 'username' not in login_session or creator.id != \
            login_session['user_id']:
        return render_template('publiccategory.html', items=items,
                               category=category, creator=creator)
    else:
        return render_template('studio.html', items=items, category=category)
    # return 'This page is the studio for category %s' % category_id


# Create a new studio item
@app.route(
    '/category/<int:category_id>/studio/new/', methods=['GET', 'POST'])
def newStudio(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    if login_session['user_id'] != category.user_id:
        return "<script>function myFunction() {alert('unfortunally, you are " \
               "not authorized to add menu items to this category at this " \
               "time, Please create your own category in order to add your " \
               "new favorite studio in the area.');}</script><body " \
               "onload='myFunction()''>"
    if request.method == 'POST':
        newstudio = StudioItem(name=request.form['name'],
                               category=request.form[description],
                               Price=request.form['price'],
                               Address=request.form['course'],
                               category_id=category_id)
        session.add(newstudio)
        session.commit()

        return redirect(url_for('showStudio', category_id=category_id))
    else:
        return render_template('newstudioitem.html', category_id=category_id)

    # return render_template('newStudioItem.html', category=category)
    # return 'This page is for making a new menu item for category %s'
    # %category_id


# Edit a menu item
@app.route('/category/<int:category_id>/studio/<int:studio_id>/edit',
           methods=['GET', 'POST'])
def editStudio(category_id, studio_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedstudio = session.query(StudioItem).filter_by(id=studio_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedstudio.name = request.form['name']
        if request.form['description']:
            editedstudio.description = request.form['name']
        if request.form['price']:
            editedstudio.price = request.form['price']
        if request.form['Address']:
            editedstudio.course = request.form['Address']
        session.add(editedstudio)
        session.commit()
        return redirect(url_for('showStudio', category_id=category_id))
    else:

        return render_template(
            'editstudioitem.html', category_id=category_id,
            studio_id=studio_id, item=editedstudio)

    # return 'This page is for editing menu item %s' % menu_id


# Delete a menu item
@app.route('/category/<int:category_id>/studio/<int:studio_id>/delete',
           methods=['GET', 'POST'])
def deleteStudioItem(category_id, studio_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    itemToDelete = session.query(StudioItem).filter_by(id=studio_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('category Item Successfully Deleted')
        return redirect(url_for('showStudio', category_id=category_id))
    else:
        return render_template('deletestudioitem.html', item=deleteStudioItem)
    # return "This page is for deleting menu item %s" % menu_id


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategories'))

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
