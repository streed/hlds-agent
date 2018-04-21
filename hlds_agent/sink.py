import time

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
        todaysIndex = self.get_index() 

        for blob in blobs:
            print(blob['type'])
            res = self.es.index(index=todaysIndex, doc_type=blob['type'], body=blob)
            print(res)


    def get_index(self):
        day = time.strftime("%d-%m-%Y")

        return 'hlds-%s' % day
