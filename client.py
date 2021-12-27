import queue
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
        self.packets_q = queue.Queue()
        self.game_on = False
        self.question_on = False
        self.udp_client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def run_client(self):
        print('Client IP->' + str(self.host) + ' Port->' + str(self.port))

        self.udp_client_socket.bind((self.host, self.port))

        name = f"Client Hosted by {self.host}:{self.port} Request for connection"
        self.udp_client_socket.sendto(name.encode('utf-8'), self.server)

        threading.Thread(
            target=self.client_rcv_data
        ).start()

        print("Connected successfully")

        while True:
            while not self.packets_q.empty():
                self.packets_q.get()
                m = input()
                self.udp_client_socket.sendto(m.encode("utf-8"), self.server)
                self.question_on = False

    def client_rcv_data(self,):
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
                        # response = data.split("(")[1].split(")")
                        # port = response[0].split(",")[1]
                        # is_win = True if "Win" in response[1] else False
                        # if is_win:
                        #     print("Congratulations! You Won The Game")
                        # else:
                        #     print("Loser! You lose The Game")
                else:
                    self.game_on = True
                    print(data)
            except Exception as e:
                self.packets_q.put(0)


if __name__ == '__main__':
    server_ip = sys.argv[1]
    client = Client(server_ip)
    client.run_client()

# check git