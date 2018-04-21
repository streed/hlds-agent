import time

import pytest

from hlds_agent.collector import Collector

@pytest.fixture
def collector():
    class Sink:
        def __init__(self):
            self.blobs = []

        def send(self, blobs):
            self.blobs = blobs

    return Collector(Sink(), collect_time=1)


def test_Collector_single_blob(collector):
    collector.start()

    collector.put(1)

    time.sleep(1)

    assert([1] == collector.sink.blobs)

    
def test_Collector_multiple_blobs(collector):
    collector.start()

    collector.put(1)
    collector.put(2)
    collector.put(3)

    time.sleep(2)

    assert([1,2,3] == collector.sink.blobs)
