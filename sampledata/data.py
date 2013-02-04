from factual import Factual
from factual.api import APIException
from pymongo import Connection, ASCENDING, DESCENDING, GEO2D
from time import sleep
from sanetime import time
from random import randint, choice

KEY = "[FACTUAL KEY GOES HERE]"
SECRET = "[FACTUAL SECRET GOES HERE]"
MONGOURL = 'mongodb://[USERNAME]:[PASSWORD]@[MONGOHQ HOST]/thehotspot'

def get_data():
    factual = Factual(KEY,SECRET)
    cn = Connection(MONGOURL)
    db = cn['factual']
    fields = "name,address,locality,region,postcode,country,category_labels,latitude,longitude"
    query = factual.table('places-v3').filters({"locality":"San Francisco"}).limit(50)
    try:
        for offset in xrange(0,10000,50):
            data = query.select(fields).offset(offset).data()
            inserted = db.places.insert(data)
            print "offset", offset, "inserted", len(inserted), "documents, sleeping for 60s"
            sleep(60)
    except APIException as e:
        print e


def make_places():
    cn = Connection(MONGOURL)
    db = cn['thehotspot']
    factualdb = cn['factual']

    query = factualdb.places.find()
    i = 1
    categories = dict()
    for doc in query:
        doc['_id'] = i
        i += 1
        category_labels = doc.pop('category_labels')
        doc['categories'] = category_labels[0]
        lat = doc.pop('latitude')
        lon = doc.pop('longitude')
        doc['location'] = [lat,lon]
        db.places3.insert(doc)

        del doc['location']
        db.places2.insert(doc)

        del doc['categories']
        db.places1.insert(doc)

        for c in category_labels[0]:
            categories[c] = categories.get(c, 0) + 1

    i = 1
    for cat,count in categories.iteritems():
        db.categories.insert({"_id": i, "name": cat, "count": count})
        i += 1


def add_users():
    cn = Connection(MONGOURL)
    db = cn['thehotspot']
    users = open('users.txt')
    i = 1
    for line in users:
        name = line.split()
        db.users.save({'_id':i, 'firstname': name[0], 'lastname': name[1]})
        i += 1


def generate_checkins():
    # let's make 10000 checkins with 50 users and 500 places
    # ranging from 9am-9pm between 2012-9-1 and 2012-9-30
    cn = Connection(MONGOURL)
    db = cn['thehotspot']
    count_users = db.users.count()
    count_places = db.places1.count()
    for i in xrange(10000):
        dt = time(2012,9, randint(1,30), randint(9,21)).datetime
        ruser = randint(1,count_users)
        rplace = randint(1,count_places)
        db.checkins.save({
            'user_id': ruser,
            'place_id': rplace,
            'datetime': dt
        })
        db.users.update({"_id":ruser}, {"$inc": {"checkins":1}})
        db.places1.update({"_id":rplace}, {"$inc": {"checkins":1}})
        db.places2.update({"_id":rplace}, {"$inc": {"checkins":1}})
        db.places3.update({"_id":rplace}, {"$inc": {"checkins":1}})

def make_indexes():
    cn = Connection(MONGOURL)
    db = cn['thehotspot']

    db.checkins.create_index([("user_id", ASCENDING), ("place_id", ASCENDING)])

    db.places1.create_index([("checkins", ASCENDING)])

    db.places2.create_index([("categories", ASCENDING)])
    db.places2.create_index([("checkins", ASCENDING)])

    db.places3.create_index([("categories", ASCENDING)])
    db.places3.create_index([("checkins", ASCENDING)])
    db.places3.create_index([("location", GEO2D)])

def main():
    get_data()
    add_users()
    make_places()
    generate_checkins()
    make_indexes()

if __name__ == '__main__':
    main()