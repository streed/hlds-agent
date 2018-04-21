import asyncore

from hlds_agent.server import Server
from hlds_agent.collector import Collector 
from hlds_agent.sink import ElasticSearchSink as Sink


if __name__ == "__main__":
    print("Starting!")
    collector = Collector(Sink())
    s = Server(collector)

    asyncore.loop()
