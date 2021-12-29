import socket
import threading
import queue
import sys
import random
import math


def create_questions():
    while True:
        x = random.randint(0,10)
        y = random.randint(0, 10)
        if x+y < 9:
            tup = (f"{x} + {y}",x+y)
            yield tup



class Server:

    def __init__(self, host, buffer_size=1024):
        self.host = host
        self.buffer_size = buffer_size
        self.port = 13117
        self.clients = {}
        self.udp_server_socket = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_DGRAM
        )
        self.questions = create_questions()
        self.game_on = False
        self.question_on = False

    def run_server(self):
        print('Server hosting on IP-> ' + str(self.host))
        self.udp_server_socket.bind((self.host, self.port))
        rcv_packet = queue.Queue()

        print('Server Running...')

        threading.Thread(
            target=self.rcv_data,
            args=[rcv_packet]
        ).start()

        while True:
            while not rcv_packet.empty():
                data, addr = rcv_packet.get()
                data = data.decode('utf-8')
                print(data)
                if not self.game_on:
                    m = f"Server Accept Request from {addr}"
                    m += "\nWaiting For Another User To Join..."
                    self.udp_server_socket.sendto(m.encode('utf-8'), addr)
                else:
                    if self.question_on:
                        try:
                            other = [address for address in self.clients if address != addr][0]
                            win = "You Won The Game"
                            lose = "You Lose The Game"
                            if int(data) == self.q[1]:
                                self.udp_server_socket.sendto(win.encode("utf-8"),addr)
                                self.udp_server_socket.sendto(lose.encode("utf-8"),other)
                                self.question_on = False
                            else:
                                self.udp_server_socket.sendto(win.encode("utf-8"),other)
                                self.udp_server_socket.sendto(lose.encode("utf-8"),addr)
                                self.question_on = False
                        except ValueError:
                            m = "Please Answer with integers numbers only!".capitalize()
                            self.udp_server_socket.sendto(m.encode('utf-8'), addr)
                    self.q = next(self.questions)
                    self.send_to_all_client(self.q[0])
                    self.question_on = True

    def rcv_data(self, rcv_packet):
        while True:
            data, addr = self.udp_server_socket.recvfrom(self.buffer_size)
            if addr in self.clients:
                rcv_packet.put((data, addr))
            elif len(self.clients) < 2:
                self.clients[addr] = True
                if len(self.clients) == 2:
                    self.game_on = True
                    self.play_game()
                rcv_packet.put((data, addr))
            else:
                self.udp_server_socket.sendto(" -- Server Full, Return Later -- ".encode("utf-8"), addr)
                continue

    def play_game(self):
        m = '''Welcome to Quick Maths.\nPlayer 1: Instinct Player\n2: Rocket\nPlease answer the following question as fast as you can:'''
        self.send_to_all_client(m)

    def send_to_all_client(self,m):
        for client in self.clients:
            self.udp_server_socket.sendto(m.encode("utf-8"), client)



if __name__ == '__main__':
    host = sys.argv[1]
    server = Server(host=host)
    server.run_server()
