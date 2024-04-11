import socket
import json
import threading
import queue
import random
from encryption import integer_to_aes_key, encrypt_message, decrypt_message
import typer


class Client:

    def __init__(self, host: str = "localhost", port: int = 1239) -> None:

        self.q = queue.Queue()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.listen_thread = threading.Thread(target=self.listen_for_messages)
        self.listen_thread.daemon = True
        self.listen_thread.start()

        # this is the keys to send messages
        self.p = None
        self.g = None
        self.A = None
        self.b = random.randint(2, 1000)
        self.s = None

    def listen_for_messages(self):
        try:
            while True:
                data = self.sock.recv(1024)
                if not data:
                    print("connection closed by server")
                    break
                if self.s is not None:
                    iv, message = data.split(b":sep:")
                    data = decrypt_message(iv, message, self.s)
                else:
                    data = data.decode()
                self.q.put(json.loads(data))
        except Exception as e:
            print("exception", e)
        finally:
            self.sock.close()

    def send(self, message: bytes):
        try:
            self.sock.sendall(message)
        except Exception as e:
            print("error occured in sending:", e)

    def start(self):
        self.send(json.dumps({"t": 'pg'}).encode())

        data = self.q.get()

        self.p = data['p']
        self.g = data['g']
        self.A = data['A']

        s = (self.A ** self.b) % self.p

        self.s = integer_to_aes_key(s)

        B = (self.g ** self.b) % self.p

        self.send(json.dumps({"t": "B", "B": B}).encode())

        data = self.q.get()

        assert data['chat'] == 'ready'

        try:
            while True:
                message = input('Send message: ')
                if message == 'q':
                    break
                e_message = encrypt_message(json.dumps(
                    {"m": message, "t": "chat"}), self.s)
                self.send(message=e_message)
        except KeyboardInterrupt:
            pass
        finally:
            # server disconnect
            pass


def main(host: str = 'localhost', port: int = 1239):
    client = Client(host, port)
    client.start()


if __name__ == '__main__':

    typer.run(main)
