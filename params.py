#!/usr/bin/env python3

# Things used to establish a connection with the RMQ Server

rmq_params = {'vhost': 'my_vhost',
              'username': 'user',
              'password': 'pass',
              'exchange': 'my_exchange',
              'order_queue': 'my_order_queue'}
socket_params = {'size': 1024,
                 'port': 8080}
