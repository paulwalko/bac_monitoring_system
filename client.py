#!/usr/bin/env python

import argparse

import pika

from rmq_params import rmq_params

def checkpoint(message):
    """Prints [CHeckpoint] <message>
    """
    print("[Checkpoint] {}".format(message))

def process_response(response):
    """Process response from serve & update GUI
    """
    # Update GUI with color
    # TODO
    checkpoint("Update GUI with color \'{}\'".format(color))

    # Wait a few seconds for a possible reject
    # TODO
    checkpoint("Drink rejected? \'{}\'".format(reject))

    return

def main():
    """Processes rfid scans
    """
    parser = argparse.ArgumentParser(description='Processses arguments')
    parse.add_argument('-s', help='Set server IP or hostname', required=True)
    parse.add_argument('-p', help='Set server Port to receive messages on',
                       default=8080)
    parse.add_argument('-z', help='Set size for socket to recive messages',
                       default=1024)

    # Process args
    args = parser.parse_args()
    server_host = args.s
    server_port = args.p
    server_size = args.z

    # Setup RabbitMQ
    credentials = pika.PlainCredentials(rmq_params['username'],
                                        rmq_params['password'])
    parameters = pika.ConnectionParameters(host=rmq_host,
                                           virtual_host=rmq_paras['vhost'],
                                           credentials=credentials)

    # Connect to RabbitMQ
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # Bind to order queue
    channel.queue_bind(exchange=rmq_params['exchange'],
                       queue=rmq_params['order_queue'])

    # Continuously listen for RFID ids
    while True:
        # TODO
        print('Continuously listen for RFID ids')
        # TODO
        rfid_id = '123456'

        checkpoint("Received id \'{}\'".format(rfid_id))

        # Submit new drink order to queue
        channel.basic_publish(exchange=rmq_params['exchange'],
                              routing_key=rmq_params['order_queue'],
                              body=rfid_id)
        checkpoint("Getting status for id \'{}\'".format(rfid_id))

        # Wait for response from server for drink order
        try:
            s = socket.socket(AF_INET, socket.SOCK_STREAM)
            s.connect((server_host, server_port))
            recv_data = s.recv(server_size)
            s.close()
            process_response(recv_data)

        # Error receiving message
        except Exception as ex:
            print(ex)

main()
