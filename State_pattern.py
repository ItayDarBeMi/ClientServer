from __future__ import annotations
from abc import ABC, abstractmethod
import socket
import queue
import threading
import random

class Client:
    """
    The Context defines the interface of interest to clients. It also maintains
    a reference to an instance of a State subclass, which represents the current
    state of the Context.
    """

    _state = None
    """
    A reference to the current state of the Context.
    """
    def __init__(self, state: ClientState,server_ip, buffer_size=1024):
        self.transition_to(state)
        self.server_ip = server_ip
        self.server = (str(self.server_ip), 13117)
        self.buffer_size = buffer_size
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = random.randint(6000, 10000)
        self.packets_q = queue.Queue()

    def transition_to(self, state: ClientState):
        """
        The Context allows changing the State object at runtime.
        """

        print(f"Context: Transition to {type(state).__name__}")
        self._state = state
        self._state.context = self

    """
    The Context delegates part of its behavior to the current State object.
    """

    def run_client(self):
        self._state.handle1()



class ClientState(ABC):
    """
    The base State class declares methods that all Concrete State should
    implement and also provides a backreference to the Context object,
    associated with the State. This backreference can be used by States to
    transition the Context to another State.
    """

    @property
    def context(self) -> Client:
        return self._context

    @context.setter
    def context(self, context: Client) -> None:
        self._context = context

    @abstractmethod
    def handle(self, hmap) -> None:
        pass



"""
Concrete States implement various behaviors, associated with a state of the
Context.
"""


class ListenToServer(ClientState):
    def handle(self, hmap) -> None:





class ConnectServer(ClientState):
    def handle(self) -> None:
        print("ConcreteStateB handles request1.")


class GameMode(ClientState):
    def handle(self) -> None:
        print("user in game mode")


if __name__ == "__main__":
    # The client code.

    context = Client(ListenToServer())
