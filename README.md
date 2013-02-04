# The Hot Spot

This is a sample application that I developed as part of a presentation on building apps using MongoDB. The app is a checkin application. The data was pulled from the [Factual places API](http://www.factual.com/data-apis/places) and I generated checkins for 50 sample users over the span of 1 month.

There are three versions of the app, each with increasingly more functionality:

* v1: browse users and places, and create new checkins
* v2: v1 plus each place now has browseable categories
* v3: v2 plus geospatial support (for nearby places) and some simple aggregate stats per place

## Setup

* Get yourself a working [MongoDB](http://www.mongodb.org) setup (I used [MongoHQ](http://www.mongohq.com))
* Use `sampledata/data.py` to pull data from Factual and create places, users, and checkins
* Note: Each version is an independent application in case you want to deploy them individually
* Run `pip install -r requirements.txt` and run the app with `python app.py`
