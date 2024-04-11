import socket
import json
import threading


class Client:

    def __init__(self, host: str = "localhost", port: int = 1234) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.listen_thread = threading.Thread(target=self.listen_for_messages)
        self.listen_thread.daemon = True
        self.listen_thread.start()

    def listen_for_messages(self):
        try:
            while True:
                data = self.sock.recv(1024)
                if not data:
                    print("connection closed by server")
                    break
                print("received:", data.decode())
        except Exception as e:
            print("exception", e)
        finally:
            self.sock.close()

    def send(self, message: str):
        try:
            self.sock.sendall(json.dumps({"m": message}).encode())
        except Exception as e:
            print("error occured in sending:", e)

    def start(self):
        try:
            while True:
                message = input('Send message: ')
                if message == 'q':
                    break
                self.send(message=message)
        except KeyboardInterrupt:
            pass
        finally:
            # server disconnect
            pass


client = Client()
client.start()
