#!/usr/bin/env python3

from datetime import datetime

import pymongo


def checkpoint(message):
    """Prints [CHeckpoint] <message>
    """
    print("[Checkpoint] {}".format(message))

def total_drinks(id):
    """Looks up the number of drinks a given user has consumed
    """
    # Lookup
    return 10

def remove_drinks(id=None, finished_drinks):
    """Remove finished drinks. Removes all drinks from all ids
    if id==None
    """

    # Remove all drinks from all users
    if id == None:
        # Iterate through all users
        # Remove set drink list to empty
    else:
        # Lookup specific user
        # Remove drinks < start_time

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
    one_drink = bac_lookup[user_info['gender']][user_info['weight']]

    # Add up BAC for each drink
    bac = 0
    finished_drinks = []
    # According the the BAC chart, for ever 40 minutes .01% is subtracted from BAC
    #  and there are 2400 seconds on 40 minutes
    curr_time = int(datetime.today().timestamp()) / 2400
    for drink in drinks
        # Calculate drinking time and bac
        drink_time = drink / 2400
        drinking_time = curr_time - drink_time
        # Calculate BAC from specific drink, or remove it 
        drink_bac = one_drink - (drinking_time * 01)
        if drink_bac == 0:
            finished_drinks.append[drink]
        else:
            bac += drink_bac

    # Remove all drinks not contributing to current BAC
    remove_drinks(id, finished_drinks)

    # Intoxicated, no drinks consumed, or some drinks consumed
    if bac >= .06:
        return 0
    elif bac == 0:
        return int(.06 / one_drink)
    else:
        return int(.06 / bac)

def main():

    # Arguments

    # Connect to to collection
    # Assumes 'bac_monitoring' collection already exists
    collection = pymongo.MongoClient().group23.bac_monitoring

    ## Add new drink
    # Current time in hours
    curr_time = int(datetime.today().timestamp())
    collection.update({'id': 123456}, {'$push': {'drinks': curr_time}})
    
    # Insert something
    drink_data = collection.find({'id': 123456})[0]
    print(drink_data)

main()
