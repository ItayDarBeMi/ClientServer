import socket
import threading
import queue
import sys

class Server:

    def __init__(self, host,buffer_size=1024):
        self.host = host
        self.buffer_size = buffer_size
        self.port = 5000


    def run_server(self):
        print('Server hosting on IP-> ' + str(self.host))
        udp_server_socket = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_DGRAM
        )
        udp_server_socket.bind((self.host, self.port))
        rcv_packet = queue.Queue()

        print('Server Running...')

        threading.Thread(
            target=self.rcv_data,
            args=(udp_server_socket, rcv_packet)
        ).start()

        while True:
            while not rcv_packet.empty():
                data, addr = rcv_packet.get()
                data = data.decode('utf-8')
                print(data)
                massege = "SERVER: Done"
                udp_server_socket.sendto(massege.encode('utf-8'), addr)

    def rcv_data(self,sock,rcv_packet):
        while True:
            data, addr = sock.recvfrom(self.buffer_size)
            rcv_packet.put((data, addr))

if __name__ == '__main__':
    host = sys.argv[1]
    server = Server(host=host)
    server.run_server()

