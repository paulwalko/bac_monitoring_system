#!/usr/bin/env python3

import argparse
import socket
from socket import SOL_SOCKET, SO_REUSEADDR

import pickle
import pika

from params import rmq_params, socket_params

def checkpoint(message):
    """Prints [Checkpoint] <message>
    """
    print("[Checkpoint] {}".format(message))

# Get pi's IP
# From https://stackoverflow.com/questions/166506/
#  finding-local-ip-addresses-using-pythons-stdlib?page=1&tab=votes#tab-top
def my_ip():
    return str((([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]
        if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)),
        s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET,
        socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0])

def process_response(response):
    """Process response from serve & update GUI
    """
    # Update GUI with color
    # TODO
    color = 'red'
    checkpoint("Update GUI with color \'{}\'".format(color))

    # Wait a few seconds for a possible reject
    # TODO
    reject = False
    checkpoint("Drink rejected? \'{}\'".format(reject))

    return

def main():
    """Processes rfid scans
    """
    parser = argparse.ArgumentParser(description='Processses arguments')
    parser.add_argument('-s', help='Set RMQ server', required=True)
    parser.add_argument('-p', help='Set port for socket to listen on',
                       default=socket_params['port'])
    parser.add_argument('-z', help='Set size for socket to recive messages',
                       default=socket_params['size'])
    parser.add_argument('-b', help='Set socket backlog size',
                       default=socket_params['backlog'])

    # Process args
    args = parser.parse_args()
    rmq_host = args.s
    socket_port = int(args.p)
    socket_size = int(args.z)
    socket_backlog = int(args.b)

    # Setup RabbitMQ
    credentials = pika.PlainCredentials(rmq_params['username'],
                                        rmq_params['password'])
    parameters = pika.ConnectionParameters(host=rmq_host,
                                           virtual_host=rmq_params['vhost'],
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
        socket_host = my_ip()
        order_data = {'id': rfid_id, 'ip': socket_host, 'port': socket_port,
                      'size': socket_size}

        checkpoint("Received id \'{}\'".format(rfid_id))

        # Submit new drink order to queue
        channel.basic_publish(exchange=rmq_params['exchange'],
                              routing_key=rmq_params['order_queue'],
                              body=str(order_data))
        checkpoint("Getting status for id \'{}\'".format(rfid_id))


        ## Wait for response from server for drink order
        # Setup socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        s.bind((socket_host, socket_port))
        s.listen(socket_backlog)
        checkpoint("Created socket at {} on port {}"
            .format(socket_host, socket_port))

        # Listen for reply from server
        server, address = s.accept()
        svr_addr = server.getpeername()[0]
        svr_port = server.getpeername()[1]
        checkpoint("Accepted server connection from {} on {}"
            .format(svr_addr, svr_port))

        # Receive data from server
        recv_data = server.recv(socket_size)
        recv_data = pickle.loads(recv_data)
        checkpoint("Received data: {}".format(recv_data))
        s.close()

        # Update GUI based on response
        process_response(recv_data)
        break

main()
