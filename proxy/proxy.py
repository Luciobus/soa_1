import json
import logging
import socket
import socketserver
import sys
import struct
import time

CONVERTERS_TO_PORTS = {
    'NATIVE': 3001,
    'JSON': 3002,
    'XML': 3003,
    'GOOGLE_BUFFER': 3004,
    'APACHE': 3005,
    'YAML': 3006,
    'MESSAGEPACK': 3007,
}

class ConvertersUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        logging.info("Incoming message from {}".format(self.client_address[0]))

        msg = json.loads(self.request[0].strip().decode())
        requested = self.request[1]

        if msg['type'] == 'get_result':
            format_type = msg['format']
            host = format_type
            if host not in CONVERTERS_TO_PORTS:
                logging.error("Can not use {} format type: Unknown".format(format_type))
                requested.sendto(bytes("Unknown format type", "utf-8"), self.client_address)
                return
            port = CONVERTERS_TO_PORTS[host]
            print(host, port, file=sys.stderr)

            converter = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            converter.sendto(bytes("", "utf-8"), (host, port))
            result = converter.recv(1024)

            logging.info("Received result from ({}, {}): result = {}".format(host, port, result.decode()))

            requested.sendto(result, self.client_address)
            converter.close()
        elif msg['type'] == 'get_result_all':
            multicast_group = ('224.0.0.1', 10000)
            group_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            group_socket.settimeout(20)
            ttl = struct.pack('b', 5)
            group_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

            answers = []

            requested.sendto(b'Hello\n', self.client_address)

            group_socket.sendto(bytes("", "utf-8"), multicast_group)
            while len(answers) < len(CONVERTERS_TO_PORTS):
                ans, _ = group_socket.recvfrom(1024)
                print("Received {}".format(ans), file=sys.stderr)
                requested.sendto(ans, self.client_address)
                answers.append(ans)
            requested.sendto(b'Hello\n', self.client_address)

            print("Received result from all converters: result = {}".format(answers), file=sys.stderr)
            # requested.sendto(ans, self.client_address)
            
            group_socket.close()

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 2000
    with socketserver.UDPServer((HOST, PORT), ConvertersUDPHandler) as proxy:
        proxy.serve_forever()