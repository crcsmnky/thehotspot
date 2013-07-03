import os
from flask import Flask
from flask import request, render_template, redirect, url_for, flash
from flask.ext.pymongo import PyMongo
import pymongo
from datetime import datetime

app = Flask(__name__)

app.config['MONGO_HOST'] = '[HOST]'
app.config['MONGO_PORT'] = 0
app.config['MONGO_DBNAME'] = 'thehotspot'
app.config['MONGO_USERNAME'] = '[USERNAME]'
app.config['MONGO_PASSWORD'] = '[PASSWORD]'

app.secret_key="1062511ff23a05a8a5eec866c84fc4cd" # $ md5 -s thehotspot

mongo = PyMongo(app)


@app.route('/', methods=['GET'])
def tops():
    topusers = mongo.db.users.find({}).sort('checkins', pymongo.DESCENDING).limit(5)
    topplaces = mongo.db.places1.find({}).sort('checkins', pymongo.DESCENDING).limit(5)
    return render_template('top.html', topusers=topusers, topplaces=topplaces)


@app.route('/users/<int:userid>', methods=['GET'])
def user(userid):
    user = mongo.db.users.find_one_or_404({'_id': userid})
    checkins_skip = int(request.args.get('skip', 0))
    checkins = mongo.db.checkins.find({'user_id': userid}).sort(
        'datetime', pymongo.DESCENDING).skip(checkins_skip).limit(10)
    place_ids = [c['place_id'] for c in checkins.clone()]
    places = {place['_id']: place for place in mongo.db.places1.find({'_id':{'$in':place_ids}})}

    return render_template('user.html', user=user, places=places, checkins=checkins)


@app.route('/places/<int:placeid>', methods=['GET'])
def place(placeid):
    place = mongo.db.places1.find_one_or_404({'_id': placeid})
    checkins_skip = int(request.args.get('skip', 0))
    checkins = mongo.db.checkins.find({'place_id': placeid}).sort(
        'datetime', pymongo.DESCENDING).skip(checkins_skip).limit(10)
    user_ids = [c['user_id'] for c in checkins.clone()]
    users = {user['_id']: user for user in mongo.db.users.find({'_id':{'$in':user_ids}})}

    return render_template('place.html', place=place, users=users, checkins=checkins)


@app.route('/places/all', methods=['GET'])
def allplaces():
    checkins_skip = int(request.args.get('skip', 0))
    places = mongo.db.places1.find({}).sort(
        'checkins', pymongo.DESCENDING).skip(checkins_skip).limit(10)
    count = mongo.db.places1.count()

    return render_template('places.html', places=places, count=count, skip=checkins_skip)


@app.route('/users/all', methods=['GET'])
def allusers():
    checkins_skip = int(request.args.get('skip', 0))
    users = mongo.db.users.find({}).sort(
        'checkins', pymongo.DESCENDING).skip(checkins_skip).limit(10)
    count = mongo.db.users.count()

    return render_template('users.html', users=users, count=count, skip=checkins_skip)

@app.route('/checkins/all', methods=['GET'])
def allcheckins():
    checkins_skip = int(request.args.get('skip', 0))
    checkins = mongo.db.checkins.find().sort(
        'datetime', pymongo.DESCENDING).skip(checkins_skip).limit(10)
    count = mongo.db.checkins.count()
    user_ids = [c['user_id'] for c in checkins.clone()]
    place_ids = [c['place_id'] for c in checkins.clone()]
    users = {user['_id']: user for user in mongo.db.users.find({'_id':{'$in':user_ids}})}
    places = {place['_id']: place for place in mongo.db.places1.find({'_id':{'$in':place_ids}})}

    return render_template('checkins.html', checkins=checkins, users=users, places=places, skip=checkins_skip, count=count)

@app.route('/checkins/new', methods=['GET', 'POST'])
def newcheckin():
    if request.method == 'POST':
        user_id = int(request.form['user_id'])
        place_id = int(request.form['place_id'])
        checkin = {'user_id': user_id, 'place_id': place_id, 'datetime': datetime.now()}
        mongo.db.checkins.save(checkin)
        mongo.db.places1.update({'_id': place_id}, {'$inc':{'checkins': 1}})
        mongo.db.users.update({'_id': user_id}, {'$inc':{'checkins': 1}})
        flash('Success! Added new checkin.')

    users = mongo.db.users.find().sort('firstname', pymongo.ASCENDING)
    places = mongo.db.places1.find({},{'_id':1,'name':1}).sort('name', pymongo.ASCENDING)
    return render_template('newcheckin.html', users=users, places=places)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)