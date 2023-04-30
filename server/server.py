import os
import socket
import logging
import struct
import threading
import sys

import converters

def get_data():
    ser_time, deser_time, size = 0, 0, 0
    format_type = os.getenv('FORMAT_TYPE')
    if format_type not in converters.NAME_TO_CONVERTER.keys():
        return ""
    converter = converters.NAME_TO_CONVERTER[format_type]
    ser_time, deser_time, size = converter()
    data_to_send = '-'.join([format_type, str(size), str(int(ser_time*1000)) + 'ms', str(int(deser_time*1000)) + 'ms\n'])
    return data_to_send

def multicast_socket():
    server_address = ('', 10000)

    # Create the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind to the server address
    sock.bind(server_address)

    # Tell the operating system to add the socket to the multicast group
    # on all interfaces.
    group = socket.inet_aton('224.0.0.1')
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    # Receive/respond loop
    while True:
        logging.info('waiting to receive message\n')
        _, address = sock.recvfrom(1024)
        
        logging.info('received request from {}'.format(address))
        data = get_data()

        logging.info('sending result to {}\n'.format(address))
        sock.sendto(bytes(data, "utf-8"), address)


def udp_socket(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host = os.getenv('FORMAT_TYPE')
    logging.info('listening on {} {}'.format(host, port))
    listening_address = (host, port)
    sock.bind(listening_address)

    while True:
        logging.info('waiting to receive message\n')
        _, address = sock.recvfrom(1024)
        
        logging.info('received request from {}'.format(address))
        data = get_data()

        logging.info('sending result to {}\n'.format(address))
        sock.sendto(bytes(data, "utf-8"), address)


if __name__ == '__main__':
    port = int(sys.argv[1])
    t1 = threading.Thread(target=multicast_socket)
    t2 = threading.Thread(target=udp_socket, args=(port,))
    for t in [t1, t2]: t.start()
    for t in [t1, t2]: t.join()