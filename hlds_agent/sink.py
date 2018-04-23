import base64
import json
import time

import requests
import snappy

from elasticsearch import Elasticsearch

class Sink(object):
    
    def send(self, blobs):
        pass


class StdOutSink(Sink):

    def send(self, blobs):
        for blob in blobs:
            print(blob)


class ElasticSearchSink(Sink):

    def __init__(self, host='127.0.0.1:9300'):
        self.es = Elasticsearch()

    def send(self, blobs):
        for blob in blobs:
            todaysIndex = '%s-%s' % (blob['type'], self.get_index())
            res = self.es.index(index=todaysIndex, doc_type=blob['type'], body=blob)
            print(res['_id'] + ': ' + repr(blob))

        return True


    def get_index(self):
        day = time.strftime("%d-%m-%Y")

        return 'hlds-%s' % day


class HttpSink(Sink):

    def __init__(self, host, auth_token=None):
        self.host = host
        self.auth_token = auth_token


    def send(self, blobs):
        headers = self._headers()
        compressed_blob = self._compress(blobs)
        response = requests.post(self.host, headers=headers, data={'blob': compressed_blob})

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

