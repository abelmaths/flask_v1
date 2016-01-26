#################### IMPORTS ####################

import pymongo, os
from bson.objectid import ObjectId
import random, string, time, pprint, datetime
pp = pprint.PrettyPrinter(indent=4)

#################### DATABASE SETUP ####################

mongo_username = os.environ['MONGO_USERNAME']
mongo_password = os.environ['MONGO_PASSWORD']

MONGODB_URI = 'mongodb://{mongo_username}:{mongo_password}@ds035985.mongolab.com:35985/adaptive_maths'.format(
	mongo_username=mongo_username,
	mongo_password=mongo_password
	)
client = pymongo.MongoClient(MONGODB_URI)
print "Settting up the Mongo database"
db = client.get_default_database()
print "Completed set up of the Mongo database"

