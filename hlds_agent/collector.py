import queue
import time
import threading

class Collector(threading.Thread):

    def __init__(self, sink, collect_time=5):
        super().__init__()
        self.daemon = True
        self.name = 'CollectorThread'

        self.collect_time = collect_time
        self.sink = sink

        self.queue = queue.Queue()
        self.lock = threading.Lock()


    def run(self):
        while True:
            time.sleep(self.collect_time)  

            batch = []

            with self.lock:
                while not self.queue.empty():
                    blob = self.queue.get()
                    batch.append(blob)

            self.sink.send(batch)


    def put(self, blob):
        with self.lock:
            self.queue.put(blob)
