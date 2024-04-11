import json
import selectors
import socket
import typing
from diffie_hellman import find_PG
import random
from encryption import integer_to_aes_key, encrypt_message, decrypt_message
import typer


class Server:

    def __init__(self, host: str = 'localhost', port: int = 1239, backlog: int = 100) -> None:

        self.sel = selectors.DefaultSelector()
        self.sock = socket.socket()
        self.sock.bind((host, port))
        self.sock.listen(backlog)
        self.sock.setblocking(False)
        self.sel.register(self.sock, selectors.EVENT_READ, self.accept)

        self.addrs = {}

    def accept(self, sock, mask):
        conn, addr = self.sock.accept()  # Should be ready
        print('accepted', conn, 'from', addr)
        self.addrs[addr] = {}
        conn.setblocking(False)
        self.sel.register(conn, selectors.EVENT_READ, self.read)

    def read(self, conn, mask):
        data = conn.recv(1000)  # Should be ready\

        addr = conn.getpeername()
        if addr not in self.addrs:
            self.addrs[addr] = {}
        if data:
            message = json.loads(data.decode())
            return_message = self.process_message(addr, message)
            if return_message:
                bytes_message = json.dumps(return_message).encode()
                s = self.addrs[addr].get('s')
                if s is not None:
                    iv, encrypted = encrypt_message(
                        bytes_message.decode(), s)
                    bytes_message = iv + b":sep:" + encrypted
                conn.send(bytes_message)
        else:
            print('closing', conn)
            self.sel.unregister(conn)
            conn.close()

    def process_message(self, addr: typing.Tuple[str, int], message: typing.Dict):
        if 't' not in message.keys():
            message['t'] = 'chat'
        if message['t'] == 'pg':
            p, g = find_PG()
            self.addrs[addr]['a'] = random.randint(2, 1000)
            A = (g ** self.addrs[addr]['a']) % p
            self.addrs[addr]['p'] = p
            self.addrs[addr]['g'] = g
            return {'p': p, 'g': g, 'A': A}
        elif message['t'] == 'B':
            a = self.addrs[addr]['a']
            p = self.addrs[addr]['p']
            s = (message['B'] ** a) % p
            self.addrs[addr]['s'] = integer_to_aes_key(s)
            return {'chat': 'ready'}

    def start(self):

        while True:
            events = self.sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)


def main(host: str = 'localhost', port: int = 1239, backlog: int = 100):
    server = Server(host, port, backlog)
    server.start()


if __name__ == '__main__':

    typer.run(main)
