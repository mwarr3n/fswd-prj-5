#!usr/bin/env python

from flask import Flask, flash, render_template
from flask import request, redirect, jsonify, url_for
from flask import session as login_session

from sqlalchemy import create_engine
from sqlalchemy import desc, func

from sqlalchemy.orm import sessionmaker
from database_setup import Base, Categories, Items, Users

from sqlalchemy.sql import label
from sqlalchemy.sql import select

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import httplib2
import requests
from flask import make_response
import json
import random
import string

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

app.secret_key = CLIENT_ID

engine = create_engine('sqlite:///catalog.db',connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Main view that includes all categories and latest items
@app.route('/')
def show_latest():
    """  Main view that includes all categories and latest items. """

    categories = session.query(
            Categories.id,
            Categories.name,
            func.count(Items.id).label('item_count')).\
        outerjoin(Items, Categories.id == Items.category_id).\
        group_by(Categories.name,Categories.id).order_by(Categories.name).\
        order_by(desc('name')).all()

    qry_items = select([Items, Categories.name.label('category_name')]).\
        where(Items.category_id == Categories.id).\
        order_by(desc(Items.id)).limit(5)

    items = session.query(qry_items)

    return render_template('index.html', categories=categories, items=items)


# Show items in the selected category.
@app.route('/catalog/<int:category_id>/items', methods=['GET'])
def show_items_in_category(category_id):
    """ Show items in the selected category. """

    categories = session.\
        query(
            Categories.id,
            Categories.name,
            func.count(Items.id).label('item_count')).\
        outerjoin(Items, Categories.id == Items.category_id).\
        group_by(Categories.name,Categories.id).order_by(Categories.name).\
        order_by(desc('name')).all()

    category = session.query(Categories).filter_by(id=category_id).first()
    items = session.query(Items).filter_by(category_id=category_id).all()

    return render_template(
        'items.html',
        category=category,
        categories=categories,
        items=items)


# View selected item
@app.route('/item/<item_id>/view', methods=['GET'])
def show_item(item_id):
    """ View selected item """

    item_to_view = session.query(Items).filter_by(id=item_id).first()

    if not item_to_view:
        flash('We are unable to process your request right now.', 'info')
        return redirect(url_for('show_latest'))

    # get a list of categories
    categories = session.query(Categories).all()

    return render_template(
        'item-view.html',
        item=item_to_view,
        categories=categories)


# Edit selected item
@app.route('/item/<item_id>/edit', methods=['GET', 'POST'])
def edit_item(item_id):
    """ Edit selected item """

    if 'username' not in login_session:
        flash('You must login for this functionality.', 'danger')
        return redirect('/login')

    item_to_edit = session.query(Items).filter_by(id=item_id)\
        .filter_by(user_id=login_session['user_id']).first()

    if not item_to_edit:
        flash('We are unable to process your request right now.', 'info')
        return redirect(url_for('show_latest'))

    # get a list of categories
    categories = session.query(Categories).all()

    if request.method == 'POST':
        if request.form['name']:
            item_to_edit.name = request.form['name']
        if request.form['description']:
            item_to_edit.description = request.form['description']
        if request.form['category']:
            item_to_edit.category_id = request.form['category']

        session.add(item_to_edit)
        session.commit()

        flash('Item successfully updated!', 'success')

        return render_template(
            'item-edit.html',
            item=item_to_edit,
            categories=categories)
    else:
        return render_template(
            'item-edit.html',
            item=item_to_edit,
            categories=categories)


# Delete selected item
@app.route('/item/<int:item_id>/delete/', methods=['GET', 'POST'])
def delete_item(item_id):
    """ Delete selected item """

    if 'username' not in login_session:
        flash(' You must login for this functionality.', 'danger')
        return redirect('/login')

    item_to_delete = session.query(Items).filter_by(id=item_id)\
        .filter_by(user_id=login_session['user_id']).first()

    if not item_to_delete:
        flash("Sorry, You can only delete items you own.", 'info')
        return redirect(url_for('show_latest'))

    if request.method == 'POST':
        session.delete(item_to_delete)
        session.commit()
        flash(
            'Item "' + item_to_delete.name + '" has been deleted!',
            'success')

        return redirect(url_for('show_latest'))
    else:
        categories = session.query(Categories).all()

        return render_template(
            'item-delete.html',
            item=item_to_delete,
            categories=categories)


# Create a new item
@app.route("/catalog/item/new/", methods=['GET', 'POST'])
def new_item():
    """ Create a new item. """

    if 'username' not in login_session:
        flash('You must login for this functionality.', 'danger')
        return redirect('/login')

    # get categories
    categories = session.query(Categories).all()

    if request.method == 'POST':
        # get item
        item = session.query(Items).filter_by(name=request.form['name'])\
            .filter_by(user_id=login_session['user_id']).first()

        # does the item exist
        if item:
            flash('The item already exists in the database!', 'info')
            return redirect(url_for("new_item"))
        else:
            new_item = Items(
                name=request.form['name'],
                category_id=request.form['category'],
                description=request.form['description'],
                user_id=login_session['user_id'])

        session.add(new_item)
        session.commit()

        flash('New item successfully created!', 'success')

        return redirect(url_for('new_item'))

    return render_template('item-new.html', categories=categories)


# API: All items in the catalog.
@app.route('/catalog.json')
@app.route('/api/v1/catalog')
def api_catalog():
    """ Return JSON of all the Categories/items in the catalog. """

    categories = [c.serialize for c in session.query(Categories).all()]
    for c in range(len(categories)):
        items = [
            i.serialize for i in session.query(Items).filter_by(
                category_id=categories[c]["id"]).all()]
        if items:
            categories[c]["Item"] = items
    return jsonify(Category=categories)


# API: All categories.
@app.route('/api/v1/categories')
def api_all_categories():
    """ Return JSON of all categories. """

    categories = session.query(Categories).all()

    return jsonify(categories=[i.serialize for i in categories])


# API: All items in a specific category
@app.route("/api/v1/category/<path:category_id>", methods=["GET"])
def api_get_category(category_id):
    """ Return JSON for a specific category with its items. """

    category = session.query(Categories).\
        filter_by(id=category_id).one_or_none()

    if category:
        category = category.serialize
        items = [
            i.serialize for i in session.query(Items).filter_by(
                category_id=category["id"]).all()]
        if items:
            category["Item"] = items
    return jsonify(Category=category)


# API: A specific item
@app.route("/api/v1/item/<path:item_id>", methods=["GET"])
def api_get_item(item_id):
    """ Return JSON for a specific item. """

    item = session.query(Items).\
        filter_by(id=item_id).one_or_none()

    if item:
        item = item.serialize
        category = [
            i.serialize for i in session.query(Categories).
            filter_by(id=item["category_id"]).all()]
        if category:
            item["Category"] = category
    return jsonify(Item=item)


# Create anti-forgery state token
@app.route('/login/')
def login():
    """ Route to the login page and create anti-forgery state token. """

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template("login.html", STATE=state)


# Is the user registered
def is_user_registered(email):
    """ Has the user registered """
    try:
        user = session.query(Users).filter_by(email=email).one()
        return user.id
    except Exception:
        return None


# Register the user
def register_user(login_session):
    """ Register new user. """

    new_user = Users(
        name=login_session['username'],
        email=login_session['email']
    )

    session.add(new_user)
    session.commit()
    user = session.query(Users).filter_by(email=login_session['email']).one()

    return user.id


# Google authentication
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

    # is this a user registered, if not register.
    registered_user = is_user_registered(data['email'])
    if not registered_user:
        registered_user = register_user(login_session)

    login_session['user_id'] = registered_user

    output = ''
    output += '<h4>Welcome, '
    output += login_session['username']
    output += '!</h4>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 75px; height: 75px;border-radius: '
    output += '75px;-webkit-border-radius: 75px;-moz-border-radius: 75px;"> '

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
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s'\
        % login_session['access_token']

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
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))

        response.headers['Content-Type'] = 'application/json'
        return response


# logout the current user
@app.route('/logout')
def logout():
    """ Log out the currently connected user. """

    if 'username' in login_session:
        gdisconnect()

        flash('You have been successfully logged out!', 'info')

        return redirect(url_for('show_latest'))
    else:
        flash('You were not logged in!', 'danger')

        return redirect(url_for('show_latest'))


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
