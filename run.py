import asyncore

from hlds_agent.server import Server


if __name__ == "__main__":
    s = Server()

    asyncore.loop()
