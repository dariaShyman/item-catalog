#! /usr/bin/env python

# Flask and SQLalchemy
from flask import Flask, render_template, request
from flask import redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from database_setup import Base, Item, Category, User

# Third party authentication & authorization
from flask import session as login_session

# Generation of the unique session identifier
import random
import string

# Generation of the item slug
import re

# Authorization for /gconnect
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from oauth2client import client
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# Create database & session
engine = create_engine(
    'sqlite:///appdata.db',
    connect_args={'check_same_thread': False},
    echo=True
)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Application credentials
CLIENT_ID = json.loads(
    open(
        'client_secrets.json', 'r').read()
    )['web']['client_id']
APPLICATION_NAME = "NeverBoringBerlin"


# ---------------------------------------------------------
# Login handling
# ---------------------------------------------------------


@app.route('/login')
def showLogin():
    """Create anti-forgery state token and generate login template"""
    state = ''.join(random.choices(
        string.ascii_uppercase + string.digits, k=32)
    )

    login_session['state'] = state
    return render_template('pages/login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """Facebook connect validation"""
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Get authorization token
    access_token = request.data

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open(
            'fb_client_secrets.json', 'r').read()
        )['web']['app_secret']

    url = (
        'https://graph.facebook.com/oauth/access_token?grant_type='
        'fb_exchange_token&client_id=%s&client_secret=%s&'
        'fb_exchange_token=%s' % (app_id, app_secret, access_token)
    )

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    # Transform the formatting of the server response
    # so token can be used in the graph api calls
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = (
        'https://graph.facebook.com/v2.8/me?access_token=%s'
        '&fields=name,id,email' % token
    )

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Set session data
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # Store the token in the login_session for logout
    login_session['access_token'] = token

    # Get user picture
    url = (
        'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect'
        '=0&height=200&width=200' % token
    )

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    # Set user picture
    login_session['picture'] = data["data"]["url"]

    # Check if user exists
    # if not create a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    # Display successful login message
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src = "'
    output += login_session['picture']
    output += (
        ' " style="width: 150px; '
        'height: 150px;border-radius: 75px;'
        '-webkit-border-radius: 75px;'
        '-moz-border-radius: 75px;"> '
    )

    flash("Logged in as %s" % login_session['username'])
    return output


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Google connect validation"""
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Get authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(
            'client_secrets.json',
            scope=''
        )
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
    # Abort if there was an error in the access token info
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
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'
            ), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    # Set session data
    data = answer.json()
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # Check if user exists
    # if not create a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    # Display successful login message
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src = "'
    output += login_session['picture']
    output += (
        ' " style="width: 150px; '
        'height: 150px;border-radius: 75px;'
        '-webkit-border-radius: 75px;'
        '-moz-border-radius: 75px;"> '
    )

    flash("Logged in as %s" % login_session['username'])
    return output


def createUser(login_session):
    """Create user from the Google or Facebook connect"""
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """Get session user data"""
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """Get session user id"""
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/fbdisconnect')
def fbdisconnect():
    """Facebook disconnect"""
    facebook_id = login_session['facebook_id']
    # Included the session access token to successfully logout
    access_token = login_session['access_token']
    url = (
        'https://graph.facebook.com/%s/permissions?access_token=%s'
        % (facebook_id, access_token)
    )
    h = httplib2.Http()
    h.request(url, 'DELETE')[1]
    return "You have been logged out"


@app.route('/gdisconnect')
def gdisconnect():
    """Google disconnect"""
    access_token = login_session.get('access_token')
    # Only disconnect a connected user.
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = (
        'https://accounts.google.com/o/oauth2/revoke?token=%s'
        % access_token
    )
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(
            json.dumps('Successfully disconnected.'), 200
        )
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400)
        )
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/disconnect')
def disconnect():
    """Disconnect based on provider"""
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

        flash("You have successfully been logged out")
        return redirect(url_for('showCategoryList'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showLogin'))


# ---------------------------------------------------------
# Url slug rendering
# ---------------------------------------------------------


def getSlug(name):
    # Remove uppercase
    noUppercase = re.sub('([A-Z]{1})', r'-\1', name).lower()
    # Remove special characters
    noSpecialChars = re.sub(r'\W+', ' ', noUppercase)
    # Replace spaces with dashes
    noSpaces = noSpecialChars.replace(' ', '-')
    # Remove dashes form the beginning and end of the string
    return noSpaces.strip('-')

# ---------------------------------------------------------
# Template rendering
# ---------------------------------------------------------


@app.route('/')
@app.route('/locations')
def showCategoryList():
    """Display all categories and 6 latest items"""
    categories = session.query(Category).all()
    latestItems = session.query(Item).order_by(
        Item.id.desc()).limit(6)

    if 'username' not in login_session:
        return render_template(
            'pages/public-category-list.html',
            categories=categories,
            latestItems=latestItems)
    else:
        return render_template(
            'pages/category-list.html',
            categories=categories,
            latestItems=latestItems)


@app.route('/locations/<string:category_slug>/')
def showCategory(category_slug):
    """Display all items in a specific category"""
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(slug=category_slug).one()
    items = session.query(Item).filter_by(category_id=category.id)
    count = items.count()

    if 'username' not in login_session:
        return render_template(
            'pages/public-category.html',
            items=items,
            category=category,
            categories=categories,
            count=count)
    else:
        return render_template(
            'pages/category.html',
            category=category,
            categories=categories,
            items=items,
            count=count)


@app.route('/locations/<string:category_slug>/<string:item_slug>/')
def showItem(category_slug, item_slug):
    """Display one item"""
    categories = session.query(Category).all()
    item = session.query(Item).filter_by(slug=item_slug).one()
    creator = getUserInfo(item.user_id)

    if (
        'username' not in login_session or
        creator.id != login_session['user_id']
    ):
        return render_template(
            'pages/public-item.html',
            item=item,
            categories=categories)
    else:
        return render_template(
            'pages/item.html',
            item=item,
            categories=categories)


@app.route('/locations/new/', methods=['GET', 'POST'])
def createNewItem():
    """Create a new item"""
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))

    categories = session.query(Category).all()

    if request.method == 'POST':
        newItem = Item(
            name=request.form['name'],
            slug=getSlug(request.form['name']),
            description=request.form['description'],
            address=request.form['address'],
            category_id=request.form['category'],
            user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()

        flash("New art space %s created successfully" % newItem.name)

        return redirect(url_for('showCategoryList'))
    else:
        return render_template('pages/new-item.html', categories=categories)


@app.route('/locations/<string:item_slug>/edit', methods=['GET', 'POST'])
def editItem(item_slug):
    """Edit item"""
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))

    item = session.query(Item).filter_by(slug=item_slug).one()
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=item.category_id).one()

    if item.user_id != login_session['user_id']:
        flash("You are not authorized to edit this art space")

        return redirect(url_for('showCategoryList'))

    if request.method == 'POST':
        if request.form['name']:
            item.name = request.form['name']
            item.slug = getSlug(request.form['name'])
        if request.form['description']:
            item.description = request.form['description']
        if request.form['address']:
            item.address = request.form['address']
        if request.form['category']:
            item.category_id = request.form['category']
        item.user_id = login_session['user_id']

        session.add(item)
        session.commit()

        flash("Art space %s edited successfuly" % item.name)

        return redirect(url_for('showCategoryList'))
    else:
        return render_template(
            'pages/edit-item.html',
            categories=categories,
            item=item,
            category=category)


@app.route('/locations/<string:item_slug>/delete', methods=['GET', 'POST'])
def deleteItem(item_slug):
    """Delete item"""
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))

    item = session.query(Item).filter_by(slug=item_slug).one()
    category = session.query(Category).filter_by(id=item.category_id).one()

    if item.user_id != login_session['user_id']:
        flash("You are not authorized to delete this art space")

        return redirect(url_for('showCategoryList'))
    if request.method == 'POST':
        session.delete(item)
        session.commit()

        flash("Art space %s deleted successfuly" % item.name)

        return redirect(url_for('showCategoryList'))
    else:
        return render_template(
            'pages/delete-item.html',
            item=item,
            category=category
        )

# --------------------------------------
# JSON APIs for application data
# --------------------------------------


@app.route('/locations-grouped/json')
def ItemsGroupedJSON():
    """Returns JSON of all items grouped by categories"""
    categories = session.query(Category).options(
        joinedload(Category.items)).all()
    return jsonify(
        Category=[
            dict(
                c.serialize,
                items=[
                    i.serialize for i in c.items]) for c in categories])


@app.route('/location-types/json')
def CategoriesJSON():
    """Returns JSON of all categories in the application"""
    categories = session.query(Category).all()
    return jsonify(Categories=[c.serialize for c in categories])


@app.route('/location-types/<int:category_id>/json')
def CategoryJSON(category_id):
    """Returns JSON for selected category"""
    category = session.query(Category).filter_by(id=category_id).one()
    return jsonify(Category=category.serialize)


@app.route('/locations/json')
def ItemsJSON():
    """Returns JSON of all items in the application"""
    items = session.query(Item).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/locations/<int:item_id>/json')
def ItemJSON(item_id):
    """Returns JSON for selected item"""
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(Item=item.serialize)


@app.route('/users/json')
def UsersJSON():
    """Returns JSON of all users in the application"""
    users = session.query(User).all()
    return jsonify(User=[u.serialize for u in users])


@app.route('/users/<int:user_id>/json')
def UserJSON(user_id):
    """Returns JSON for selected user"""
    user = session.query(User).filter_by(id=user_id).one()
    return jsonify(User=user.serialize)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
