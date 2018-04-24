import asyncore
import json
import socket

from .handler import CleanHandler, DateHandler, NoopHandler, MessageHandler, RawHandler
from .log import log

class Server(asyncore.dispatcher):
    def __init__(self, collector, host='0.0.0.0', port=27115):
        asyncore.dispatcher.__init__(self)

        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.set_reuse_addr()
        self.bind((host, port,))

        self.collector = collector
        self.collector.start()


    def handle_read(self):
        data = self.recv(2048)
        handler = CleanHandler(
                    RawHandler(
                        DateHandler(
                            MessageHandler(
                                NoopHandler()))))


        log.debug('Received packet')
        cleanedData = handler(data, {})

        self.collector.put(cleanedData)

    def handle_write(self):
        pass
