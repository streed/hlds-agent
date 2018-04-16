import datetime

from hlds_agent.handler import NoopHandler, DateHandler, MessageHandler

def test_DateHandler():
    line = '15/04/2018 - 23:56:25: Server cvar "mp_consistency" = "0"'
    dateHandler = DateHandler(NoopHandler())

    out = dateHandler.parse(line, {})

    assert(out['date'] == datetime.datetime(2018, 4, 15, 23, 56, 25))

def test_MessageHandler():
    line = '15/04/2018 - 23:56:25: Server cvar "mp_consistency" = "0"'
    messageHandler = DateHandler(MessageHandler(NoopHandler()))
    out = messageHandler.parse(line, {})

    assert(out['type'] == 'cvar')


