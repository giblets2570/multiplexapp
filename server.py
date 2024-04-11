import selectors
import socket


class Server:

    def __init__(self, host: str = 'localhost', port: int = 1234, backlog: int = 100) -> None:

        self.sel = selectors.DefaultSelector()
        self.sock = socket.socket()
        self.sock.bind((host, port))
        self.sock.listen(100)
        self.sock.setblocking(False)
        self.sel.register(self.sock, selectors.EVENT_READ, self.accept)

    def accept(self, sock, mask):
        conn, addr = self.sock.accept()  # Should be ready
        print('accepted', conn, 'from', addr)
        conn.setblocking(False)
        self.sel.register(conn, selectors.EVENT_READ, self.read)

    def read(self, conn, mask):
        data = conn.recv(1000)  # Should be ready
        if data:
            print('echoing', repr(data), 'to', conn)
            conn.send(data)  # Hope it won't block
        else:
            print('closing', conn)
            self.sel.unregister(conn)
            conn.close()

    def start(self):

        while True:
            events = self.sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)


server = Server()


server.start()
