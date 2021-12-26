import socket
import threading
import sys
import random


class Client:

    def __init__(self, server_ip, buffer_size=1024):
        self.server_ip = server_ip
        self.server = (str(self.server_ip), 5000)
        self.buffer_size = buffer_size
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = random.randint(6000, 10000)

    def run_client(self):
        print('Client IP->' + str(self.host) + ' Port->' + str(self.port))

        udp_client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        udp_client_socket.bind((self.host, self.port))

        name = 'make connection to the server'
        udp_client_socket.sendto(name.encode('utf-8'), self.server)

        threading.Thread(
            target=self.client_rcv_data,
            args=(udp_client_socket,)
        ).start()

        print("Connected successfully")

        while True:
            m = input()
            udp_client_socket.sendto(m.encode("utf-8"), self.server)

    def client_rcv_data(self, sock):
        while True:
            try:
                data, addr = sock.recvfrom(self.buffer_size)
                print(data.decode('utf-8'))
            except Exception as e:
                pass


if __name__ == '__main__':
    server_ip = sys.argv[1]
    client = Client(server_ip)
    client.run_client()
