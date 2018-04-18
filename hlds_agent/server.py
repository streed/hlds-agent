import asyncore
import json
import socket

from .handler import CleanHandler, DateHandler, NoopHandler, MessageHandler, RawHandler

class Server(asyncore.dispatcher):
    def __init__(self, host='0.0.0.0', port=27115):
        asyncore.dispatcher.__init__(self)

        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.set_reuse_addr()
        self.bind((host, port,))


    def handle_connected(self):
        print("Started!")

    def handle_read(self):
        data = self.recv(2048)
        handler = CleanHandler(
                    RawHandler(
                        DateHandler(
                            MessageHandler(
                                NoopHandler()))))

        cleanedData = handler(data, {})

        print(json.dumps(cleanedData))


    def handle_write(self):
        pass
