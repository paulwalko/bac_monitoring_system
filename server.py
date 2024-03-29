#!/usr/bin/env python3

import ast
from datetime import datetime
import math
import socket
from time import sleep

import pickle
import pymongo
import pika

from params import rmq_params, socket_params

def checkpoint(message):
    """Prints [Checkpoint] <message>
    """
    print("[Checkpoint] {}".format(message))

def error(message):
    """Prints [ERROR] <message>
    """
    print("[ERROR] {}".format(message))

def get_info(id):
    """Looks up all data for an id
    """
    checkpoint("Looking up data for id \'{}\'".format(id))

    # Connect to mongodb & return user
    collection = pymongo.MongoClient().group23.bac_monitoring
    return collection.find({'id': id})[0]

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

    # Account for database errors
    try:
        user_info = get_info(id)
    except Exception as ex:
        error('User not found in database')
        return 0, 0

    bac_lookup = {'M': {'80':  .07,  '100': .06,  '120': .05,  '140': .045,
                        '160': .04,  '180': .035, '200': .03,  '220': .033,
                        '240': .025, '260': .02,  '280': .015, '300': .01,
                        '320': .005, '340': .003, '360': .002, '380': .001},
                  'F': {'80':  .08,  '100': .07,  '120': .06,  '140': .05,
                        '160': .04,  '180': .04,  '200': .035, '220': .03,
                        '240': .03, '260': .025,  '280': .02,  '300': .015,
                        '320': .01, '340': .003,  '360': .002, '380': .001}}
    # Round weight to the nearest increment of 20
    weight = int(20 * round(float(user_info['weight']) / 20))

    # Lookup gender & rounded weight
    if weight < 80:
        checkpoint('Weight too low')
        return 0, 9999
    elif weight > 380:
        checkpoint('ERROR: Weight too high. Using .001 for one drink.')
        one_drink = .001
    else:
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
    
    # Round to 2 places
    bac = round(bac, 2)

    # Debugging
    checkpoint("BAC for \'{}\': {}".format(id, bac))

    # Remove all drinks not contributing to current BAC
    remove_drinks(id, finished_drinks)
    
    # Calculate drinks left
    drinks_left = int(math.ceil((.06 - bac) / one_drink))
    checkpoint("Allowed drinks for id \'{}\': {}".format(id, drinks_left))
  
    # Calculate time left till they can drink again
    time_left = 0
    if bac > .06:
        time_left = ((bac - .06) / .01) * (2 / 3)

    return drinks_left, time_left

def order_callback(ch, method, properties, body):
    """Process 1 drink being ordered
    """

    # Decode body
    body = body.decode('utf-8')
    client_params = ast.literal_eval(body)

    # Try to get host & port
    try:
        host = client_params.get('ip')
        port = int(client_params.get('port'))
    except Exception as ex:
        error(ex)
        return

    # Try to get id
    try:
        id = int(client_params.get('id'))
        # Add drink for user
        add_drink(id)
        drinks, time = allowed_drinks(id)
    except Exception as ex:
        error(ex)
        drinks, time = 0, 0

    # Try to send response to client
    try:
        # Connect to client socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        checkpoint("Created socket at {} on port {}".format(host, port))

        # Send num drinks to client
        s.send(pickle.dumps((drinks, time)))
        s.close()
    except Exception as ex:
        error(ex)

def reject_callback(ch, method, properties, body):
    """Remove most recent drink for user
    """

    # Decode body
    id = int(body.decode('utf-8'))

    # Remove most recent drink
    remove_drink = get_info(id)['drinks'][-1]
    remove_drinks(id, [remove_drink])

def main():
    """Create & start 'drinks' queue for submitting drinks
    """
    # Remove drinks before we start
    remove_drinks()

    # Connect to RMQ
    credentials = pika.PlainCredentials(rmq_params['username'], rmq_params['password'])
    parameters = pika.ConnectionParameters(host='localhost',
                                           virtual_host=rmq_params['vhost'],
                                           credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    checkpoint('Connect to RMQ server')

    # Create order queue
    checkpoint('Setting up exchanges and queue...')
    channel.exchange_declare(exchange=rmq_params['exchange'],
                             exchange_type='direct',
                             auto_delete=True)
    channel.queue_declare(queue=rmq_params['order_queue'], auto_delete=True)
    channel.queue_bind(exchange=rmq_params['exchange'], queue=rmq_params['order_queue'])
    channel.queue_declare(queue=rmq_params['reject_queue'], auto_delete=True)
    channel.queue_bind(exchange=rmq_params['exchange'], queue=rmq_params['reject_queue'])

    # Start consuming drink queue
    channel.basic_consume(lambda ch, method, properties,
                          body: order_callback(ch, method, properties, body),
                          queue=rmq_params['order_queue'], no_ack=True)
    channel.basic_consume(lambda ch, method, properties,
                          body: reject_callback(ch, method, properties, body),
                          queue=rmq_params['reject_queue'], no_ack=True)

    checkpoint("Consuming RMQ queues: \'{}\' and \'{}\'"
        .format(rmq_params['order_queue'], rmq_params['reject_queue']))
    channel.start_consuming()

main()
