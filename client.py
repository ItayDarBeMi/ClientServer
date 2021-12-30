import queue
import socket
import threading
import sys
import random
import getch


class Client:

    def __init__(self,server_ip,buffer_size=1024):
        self.server_ip = server_ip
        self.server = (self.server_ip, 13117)
        self.buffer_size = buffer_size
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = random.randint(6000, 10000)
        self.packets_q = queue.Queue()
        self.game_on = False
        self.question_on = False
        self.udp_client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.tcp_client = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

    def run_client(self):
        print('Client IP->' + str(self.host) + ' Port->' + str(self.port))

        self.udp_client_socket.bind((self.host, self.port))

        name = f"Client Hosted by {self.host}:{self.port} Request for connection"
        self.udp_client_socket.sendto(name.encode('utf-8'), self.server)

        threading.Thread(
            target=self.client_rcv_data
        ).start()

        print("Connected successfully")

        self.tcp_client.connect(self.server)

        threading.Thread(
            target=self.client_rcv_data_tcp
        ).start()

        while True:
            while not self.packets_q.empty():
                self.packets_q.get()
                # TODO uncoment the getch
                m = getch.getche()
                # m = input()
                # self.udp_client_socket.settimeout(None)
                self.tcp_client.sendto(m.encode("utf-8"),self.server)
                self.question_on = False

    def client_rcv_data(self):
        while True:
            try:
                data, addr = self.udp_client_socket.recvfrom(self.buffer_size)
                data = data.decode("utf-8")
                try:
                    if len(data.strip().split("+")) == 2:
                        self.question_on = True
                except Exception as e:
                    self.question_on = False
                if self.game_on:
                    if self.question_on:
                        print(data)
                        self.packets_q.put(0)
                    else:
                        print(data)
                else:
                    self.game_on = True
                    print(data)
            except Exception as e:
                self.packets_q.put(0)

    def client_rcv_data_tcp(self):
        while True:
            try:
                data, addr = self.tcp_client.recvfrom(self.buffer_size)
                data = data.decode("utf-8")
                try:
                    if len(data.strip().split("+")) == 2:
                        self.question_on = True
                        self.packets_q.put((data, addr))
                except Exception as e:
                    self.question_on = False
                if self.game_on:
                    if self.question_on:
                        print(data)
                        self.packets_q.put(0)
                    else:
                        print(data)
                else:
                    self.game_on = True
                    print(data)
            except Exception as e:
                self.packets_q.put(0)



if __name__ == '__main__':
    client = Client(sys.argv[1])
    client.run_client()
