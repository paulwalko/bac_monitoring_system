#!/usr/bin/env python3

import argparse
import socket
from socket import SOL_SOCKET, SO_REUSEADDR

import pickle
import pika

from params import rmq_params, socket_params

import sys
import os
import tkinter
from tkinter import *

root=Tk()
root.geometry("500x400")

textBox=Text(root, height=2, width=30)
textBox.grid(row=0, column=1)
buttonCommit=Button(root, height=1, width=10, text="Enter",
                    command=lambda: retrieve_input())
buttonCommit.grid(row=0, column=2)
Label(root, text="# of Allowed Drinks: ").grid(row=5, column=1)
v = StringVar()
v.set("--")
Label(root, textvariable=v).grid(row=5, column=2)
Label(root, text="Time Until Another Drink (Hours): ").grid(row=6, column=1)
v1 = StringVar()
v1.set("--")
Label(root, textvariable=v1).grid(row=6, column=2)

def retrieve_input():
    rfid_id=textBox.get("1.0","end-1c")
    order_data = {'id': rfid_id, 'ip': socket_host, 'port': socket_port,
                  'size': socket_size}

    checkpoint("Received id \'{}\'".format(rfid_id))

    # Submit new drink order to queue
    channel.basic_publish(exchange=rmq_params['exchange'],
                          routing_key=rmq_params['order_queue'],
                          body=str(order_data))
    checkpoint("Getting status for id \'{}\'".format(rfid_id))

    ## Wait for response from server for drink order
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

    # Update GUI based on response
    process_response(recv_data)


def update_gui(numDrinks, timeLeft):
    if numDrinks <= 0:
        change_red()
    elif numDrinks == 1:
        change_yellow()
    else:
        change_green()
    v.set(numDrinks)
    v1.set(timeLeft)

def change_red():
    root.configure(background="red")
def change_yellow():
    root.configure(background="yellow")
def change_green():
    root.configure(background="green")

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

    drinks = response[0]
    time = round(response[1], 2)
    update_gui(str(drinks), str(time))

    # Update GUI with color
    # TODO
    color = 'red'
    checkpoint("Update GUI with color \'{}\'".format(color))

    # Wait a few seconds for a possible reject
    # TODO
    reject = False
    checkpoint("Drink rejected? \'{}\'".format(reject))
    if reject:
        channel.basic_publish(exchange=rmq_params['exchange'],
                              routing_key=rmq_params['order_queue'],
                              body=str(id))
    return

if __name__ == "__main__":
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

    # Process args & contants
    args = parser.parse_args()
    rmq_host = args.s
    socket_port = int(args.p)
    socket_size = int(args.z)
    socket_backlog = int(args.b)
    socket_host = my_ip()

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

    # Setup socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((socket_host, socket_port))
    s.listen(socket_backlog)
    checkpoint("Created socket at {} on port {}"
        .format(socket_host, socket_port))

    # Continuously listen for RFID ids
    mainloop()
