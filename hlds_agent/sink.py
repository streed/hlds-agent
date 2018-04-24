import base64
import json
import time

import requests
import snappy

from .log import log

class Sink(object):
    
    def send(self, blobs):
        pass


class StdOutSink(Sink):

    def send(self, blobs):
        for blob in blobs:
            print(blob)


class HttpSink(Sink):

    def __init__(self, host, auth_token=None):
        self.host = host
        self.auth_token = auth_token


    def send(self, blobs):
        if blobs:
            log.info("Sending %d blobs to %s", len(blobs), self.host)
            headers = self._headers()
            compressed_blob = self._compress(blobs)

            response = requests.post(self.host, headers=headers, data=json.dumps({'blob': compressed_blob.decode('utf-8')}))

            if response.status_code == 200:
                return True
            else:
                response.raise_for_status()

    def _compress(self, blobs):
        json_blobs = json.dumps(blobs)
        json_blobs = json_blobs.encode('utf-8')
        compressed_blobs = snappy.compress(json_blobs)
        return base64.b64encode(compressed_blobs)


    def _headers(self):
        return {'X-HLDS-AUTH': self.auth_token,
                'Content-Type': 'application/json'}

