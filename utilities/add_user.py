#!/usr/bin/env python3

import pymongo


def checkpoint(message):
    """Prints [CHeckpoint] <message>
    """
    print("[Checkpoint] {}".format(message))

def main():
    """Adds new user to mongodb
    """
    id = 444444 
    weight = 240 
    gender = 'M'
    
    # Connect to mongodb & add user
    collection = pymongo.MongoClient().group23.bac_monitoring
    collection.update({'id': id}, {'$set': {'weight': weight, 'gender': gender}}, upsert=True)
    checkpoint("Added user \'{}\' with weight {} and gender {}"
        .format(id, weight, gender))

main()
