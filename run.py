import asyncore

from hlds_agent.server import Server
from hlds_agent.collector import Collector 
from hlds_agent.sink import HttpSink as Sink


if __name__ == "__main__":
    collector = Collector(Sink("http://127.0.0.1:5000/", auth_token="test"))
    s = Server(collector)

    asyncore.loop()
