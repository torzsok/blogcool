# -*- coding: utf-8 -*-
"""

"""

from flask import Flask, session, g, redirect, url_for, render_template, flash
from flask_restful import Resource, Api, request, reqparse

from peewee import *
from werkzeug import check_password_hash, generate_password_hash

from flask_jsonpify import jsonify
import json

db = SqliteDatabase('blogcool.db')

class BaseModel(Model):
    class Meta:
        database = db

class Author(BaseModel):
    user_id = PrimaryKeyField()
    username = CharField(unique=True)
    email = CharField()
    pw_hash = CharField()

class Entry(BaseModel):
    id = PrimaryKeyField()
    title = CharField()
    published = TimestampField()
    text = CharField()
    category = CharField()
    author = ForeignKeyField(Author)

db.connect()

db.create_tables([Author, Entry], safe = True)

app = Flask(__name__)
app.config.from_object(__name__)

app.secret_key = '5H\x89g|\x91`!\xf1\xdf\xbe\x8cM +a\xf8?B\xb0@9}\xe4'

def auth_user(user):
    session['logged_in'] = True
    session['user_id'] = user.id
    session['username'] = user.username
    flash('You are logged in as %s' % (user.username))

@app.before_request
def before_request():
    g.db = db
    g.db.connect()

@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route('/')
def show_entries():
    entries = Entry.select().join(Author)
    return render_template('index.html', entries=entries)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logs the user in."""
    if request.method == 'POST' and request.form['username']:
        try:
            user = Author.get(
                username=request.form['username'])
        except Author.DoesNotExist:
            flash('The username entered is incorrect')
        else:
            if not check_password_hash(user.pw_hash,
                    request.form['password']):
                flash('The password entered is incorrect')
            else:
                auth_user(user)
                return redirect(url_for('add_entry'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST' and request.form['username']:
        try:
            with db.transaction():
                user = Author.create(
                    username = request.form['username'],
                    email = request.form['email'],
                    pw_hash = generate_password_hash(request.form['password']))
            auth_user(user)
            return redirect(url_for('add_entry'))

        except IntegrityError:
            flash('That username is already taken')

    return render_template('register.html')


@app.route('/', methods=['POST', 'GET'])
def add_entry():
    if not session['logged_in']:
        return redirect(url_for('login'))

    entry = Entry.create(title = request.form['title'],
                         text = request.form['text'],
                         category = request.form['category'],
                         author = Author.get(username=session['username']))
    flash('New entry was successfully posted')

    return redirect(url_for('show_entries'))


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

"""The REST api part"""

api = Api(app)


class Blogposts(Resource):

    def get(self, **kwargs):

        def getentries(keywords):
            rv = []
            if 'author' in keywords:
                if 'category' in keywords:
                    entries = Entry.select().join(Author) \
                        .where(Author.username == keywords['author']
                               & Entry.category == keywords['category'])
                else:
                    entries = Entry.select().join(Author) \
                        .where(Author.username == keywords['author'])
            else:
                if 'category' in keywords:
                    entries = Entry.select().where(Entry.category == keywords['category'])
                else:
                    entries = Entry.select()

            for entry in entries:
                rv.append({'author': entry.author.username,
                           'category': entry.category,
                           'text': entry.text})

            return jsonify(rv)

        if 'author' in kwargs or 'category' in kwargs:
            return getentries(kwargs)
        else:
            parser = reqparse.RequestParser()
            parser.add_argument('author', store_missing=False, location='args',)
            parser.add_argument('category', store_missing=False, location='args')
            args = parser.parse_args()

            return getentries(args)


api.add_resource(Blogposts, '/category/<string:category>',
                            '/author/<string:author>',
                            '/all')


if __name__ == '__main__':
    app.run(debug=True)

