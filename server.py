from __future__ import annotations

import time
from abc import ABC
import socket
import queue
import threading
import random


def create_questions():
    while True:
        x = random.randint(0, 10)
        y = random.randint(0, 10)
        if x + y < 9:
            tup = (f"{x} + {y}", x + y)
            yield tup


class Server:
    """
    The Context defines the interface of interest to clients. It also maintains
    a reference to an instance of a State subclass, which represents the current
    state of the Context.
    """

    _state = None

    def __init__(self, state: ServerState, buffer_size=1024):
        self.transition_to(state)
        self.host = "0.0.0.0"
        self.buffer_size = buffer_size
        self.port = 13117
        self.clients = {}
        self.players = {}
        self.questions = create_questions()
        self.game_on = False
        self.question_on = False
        self.tcp_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.tcp_sock.bind((self.host, self.port))
        self.tcp_sock.listen(2)

    def transition_to(self, state: ServerState):
        """
        The Context allows changing the State object at runtime.
        """

        print(f"Context: Transition to {type(state).__name__}")
        self._state = state
        self._state.context = self

    """
    The Context delegates part of its behavior to the current State object.
    """

    def run_server(self):
        while True:
            self.players = self._state.wait_for_offers(self.host, self.port)
            self.transition_to(GameMode(self.players, self.host, self.port, self.tcp_sock))
            self._state.play_game(next(self.questions))
            self.players = {}
            self.transition_to(SendOffers(self.clients, self.players))


class ServerState(ABC):
    """
    The base State class declares methods that all Concrete State should
    implement and also provides a backreference to the Context object,
    associated with the State. This backreference can be used by States to
    transition the Context to another State.
    """

    @property
    def context(self) -> Server:
        return self._context

    @context.setter
    def context(self, context: Server) -> None:
        self._context = context

    def init_connection(self, con_type: str) -> socket.socket:
        if con_type == "TCP":
            s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        elif con_type == "UDP":
            s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        else:
            raise Exception("Type entered must be TCP or UDP")
        return s

    def send_all_players(self, m, players, con):
        for player in players:
            con.sendto(m.encode("utf-8"), player)


class SendOffers(ServerState):

    def __init__(self, clients, players):
        self.con = self.init_connection("UDP")
        self.clients = clients
        self.players = players

    def wait_for_offers(self, host, port):
        print('Server hosting on IP-> ' + str(host))
        self.con.bind((host, port))
        rcv_packet = queue.Queue()
        print('Server Running...')

        t = threading.Thread(target=self.rcv_data)

        t.start()

        while len(self.clients) < 2:
            self.send_offers()
            time.sleep(1)

        time.sleep(10)
        self.send_all_players(self.opening_message(), self.players, self.con)
        time.sleep(1)
        self.con.close()
        return self.players

    def send_offers(self):
        for client in self.clients:
            if client not in self.players:
                m = "Send Offer To Connect"
                self.con.sendto(m.encode("utf-8"), client)

    def rcv_data(self):
        while True:
            try:
                data, address = self.con.recvfrom(2048)
                if address not in self.clients:
                    self.clients[address] = True
                if len(self.players) == 0:
                    print("first client in")
                    self.players[address] = True
                    m = f"Server Accept Request from {address}"
                    m += "\nWaiting For Another User To Join..."
                    self.con.sendto(m.encode('utf-8'), address)
                elif len(self.players) == 1:
                    print("second client in")
                    m = f"Server Accept Request from {address}"
                    m += "\nThe Game Will Start Soon"
                    self.players[address] = True
                    self.send_all_players(m, self.players, self.con)
                    return
                else:
                    self.con.sendto(" -- Server Full, Return Later -- ".encode("utf-8"), address)
            except Exception as e:
                pass

    def opening_message(self):
        return f'''Welcome to Quick Maths.\nPlayer 1: Instinct \nPlayer 2: Rocket\n==\nPlease answer the following question as fast as you can:'''


class GameMode(ServerState):

    def __init__(self, players, host, port, sock):
        self.players = players
        self.host = host
        self.port = port
        self.game_on = True
        self.con = sock

    def play_game(self, question):
        rcv_packet = queue.Queue()
        socket_dic = {}
        connection_socket, address = self.con.accept()
        connection_socket_2, address_2 = self.con.accept()
        socket_dic[address] = connection_socket
        socket_dic[address_2] = connection_socket_2
        for addr in socket_dic:
            socket_dic[addr].sendto(question[0].encode("utf-8"), addr)
        threads = []
        for addr in socket_dic:
            t = threading.Thread(
                target=self.rcv_data,
                args=[rcv_packet, socket_dic[addr]]
            )
            threads.append(t)
        for t in threads:
            t.start()
        while self.game_on:
            while not rcv_packet.empty():
                data, address = rcv_packet.get()
                other = [add for add in socket_dic if add != address][0]
                win = "You Won The Game"
                lose = "You Lose The Game"
                try:
                    if int(data) == question[1]:
                        socket_dic[address].send(win.encode("utf-8"))
                        socket_dic[other].send(lose.encode("utf-8"))
                        self.game_on = False
                    else:
                        socket_dic[other].send(win.encode("utf-8"))
                        socket_dic[address].send(lose.encode("utf-8"))
                        self.game_on = False
                except Exception as e:
                    pass
        return

    def rcv_data(self, rcv_packet, sock):
        while True:
            data, address = sock.recvfrom(2048)
            data = data.decode('utf-8')
            rcv_packet.put((data, sock.getpeername()))


if __name__ == "__main__":
    server = Server(SendOffers({}, {}))
    server.run_server()
