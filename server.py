#!/usr/bin/env python3

from datetime import datetime
import math
from time import sleep

import pymongo


def checkpoint(message):
    """Prints [CHeckpoint] <message>
    """
    print("[Checkpoint] {}".format(message))

def get_info(id):
    """Looks up all data for an id
    """
    checkpoint("Looking up data for id \'{}\'".format(id))

    # Connect to mongodb & return user
    collection = pymongo.MongoClient().group23.bac_monitoring
    return collection.find({'id': 123456})[0]

def add_drink(id):
    """Adds 1 drink to the user
    """
    checkpoint("Adding 1 drink for id \'{}\'".format(id))

    ## Connect to mongodb & add drink
    collection = pymongo.MongoClient().group23.bac_monitoring
    
    curr_time = int(datetime.today().timestamp())
    collection.update({'id': id}, {'$push': {'drinks': curr_time}})

def remove_drinks(id=None, finished_drinks=None):
    """Remove finished drinks. Removes all drinks from all ids
    if id==None, all drinks from specific if if finished_drinks==None, otherwise
    removes drinks in finished_drinks
    """
    # Connecto to mongodb
    collection = pymongo.MongoClient().group23.bac_monitoring

    # Remove all drinks from all users
    if id == None:
        checkpoint('Removing all drinks for all users')
        collection.update({}, {'$set': {'drinks': []}}, multi=True)
    # Remove all drinks for specific user
    elif finished_drinks == None:
        checkpoint("Removing all drinks for user \'{}\'".format(id))
        collection.update({'id': id}, {'$set': {'drinks': []}})
    # Remove only specified drinks
    else:
        checkpoint("Removing drinks: \'{}\' for user \'{}\'"
            .format(finished_drinks, id))
        for drink in finished_drinks:
            collection.update({'id': id}, {'$pull': {'drinks': drink}})     

def allowed_drinks(id):
    """Gets the amount of drinks someone is allowed to have, taking into account
    their body weight & gender
    """
    ## Calculate current BAC
    # Lookup BAC for 1 drink
    user_info = get_info(id)
    bac_lookup = {'M': {'100': .06, '120': .05, '140': .045, '160': .04,
                        '180': .035, '200': .03, '220': .033, '240': .025},
                  'F': {'100': .07, '120': .06, '140': .05,  '160': .04,
                        '180': .04,  '200': .035, '220': .03, '240': .03}}
    # Lookup gender & rounded weight
    weight = int(20 * round(float(user_info['weight']) / 20))
    one_drink = bac_lookup[user_info['gender']][str(weight)]

    # Add up BAC for each drink
    bac = 0
    finished_drinks = []
    # According the the BAC chart, for ever 40 minutes .01% is subtracted from BAC
    #  and there are 2400 seconds on 40 minutes
    curr_time = int(datetime.today().timestamp()) / 2400
    for drink in user_info['drinks']:
        # Calculate drinking time and bac
        drink_time = drink / 2400
        drinking_time = curr_time - drink_time
        # Calculate BAC from specific drink, or remove it 
        drink_bac = one_drink - (drinking_time * .01)
        if drink_bac == 0:
            finished_drinks.append[drink]
        else:
            bac += drink_bac

    # Debugging
    checkpoint("BAC for \'{}\': {}".format(id, bac))

    # Remove all drinks not contributing to current BAC
    remove_drinks(id, finished_drinks)
    
    # Calculate drinks left
    drinks_left = int(math.ceil((.06 - bac) / one_drink))
    checkpoint("Allowed drinks for id \'{}\': {}".format(id, drinks_left))
   
    return drinks_left

def main():
    """Create & start 'drinks' queue for submitting drinks
    """

    # Create order queue
    # TODO

    # Start consuming drink queue
    # TODO

    # Arguments
    id = 123456
    remove_drinks(id)
    print()
    allowed_drinks(id)
    print()
    add_drink(id)
    allowed_drinks(id)
    print()
    sleep(2)
    add_drink(id)
    allowed_drinks(id)
    print()
    add_drink(id)
    allowed_drinks(id)

main()
