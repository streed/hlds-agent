import datetime

from hlds_agent.handler import NoopHandler, DateHandler, MessageHandler

def test_DateHandler():
    line = '15/04/2018 - 23:56:25: Server cvar "mp_consistency" = "0"'
    dateHandler = DateHandler(NoopHandler())

    out = dateHandler.parse(line, {})

    assert(out['date'] == datetime.datetime(2018, 4, 15, 23, 56, 25))

def test_MessageHandler_cvar():
    line = '15/04/2018 - 23:56:25: Server cvar "mp_consistency" = "0"'
    messageHandler = DateHandler(MessageHandler(NoopHandler()))
    out = messageHandler.parse(line, {})

    assert(out['type'] == 'cvar')

def test_MessageHandler_log_simple():
    line = '15/04/2018 - 23:56:25: Log file closed'
    messageHandler = DateHandler(MessageHandler(NoopHandler()))
    out = messageHandler.parse(line, {})

    assert(out['type'] == 'log')

def test_MessageHandler_log_complex():
    line = '15/04/2018 - 23:56:25: Log file started (file "logs/2018-04-15.log") (game "svencoop") (version "48/5.0.0.0/7744")'
    messageHandler = DateHandler(MessageHandler(NoopHandler()))
    out = messageHandler.parse(line, {})

    assert(out['type'] == 'log')
    assert(out['log'] == {'file_name': 'logs/2018-04-15.log',
                          'game': 'svencoop',
                          'version': '48/5.0.0.0/7744'})

def test_MessageHandler_map():
    line = '15/04/2018 - 23:56:25: Started map "svencoop1" (CRC "530877971")'
    messageHandler = DateHandler(MessageHandler(NoopHandler()))
    out = messageHandler.parse(line, {})

    assert(out['type'] == 'map')
    assert(out['map'] == {'map_name': 'svencoop1'})

def test_MessageHandler_kick():
    line = '15/04/2018 - 20:25:48: Kick: "reivaj9916<95><STEAM_0:0:435113400><>" was kicked by "Console"'
    messageHandler = DateHandler(MessageHandler(NoopHandler()))

    out = messageHandler.parse(line, {})

    assert(out['type'] == 'game_kick')
    assert(out['kick'] == {'player': {'name': 'reivaj9916',
                                      'uid': 95,
                                      'steam_id': 'STEAM_0:0:435113400'},
                            'kicked_by': 'Console'})

def test_MessageHandler_interaction():
    line = '15/04/2018 - 08:02:46: "trigger_hurt<generic_ent><NoAuthID><neutral>" killed "New Playerd<25><STEAM_0:1:29713080><players>" with "trigger_hurt"'

    messageHandler = DateHandler(MessageHandler(NoopHandler()))

    out = messageHandler.parse(line, {})

    assert(out['type'] == 'game_interaction')
    assert(out['interaction'] == {'who': 'trigger_hurt',
                                  'entity_type': 'generic_ent',
                                  'steam_id': 'NoAuthID',
                                  'team': 'neutral',
                                  'action': {'verb': 'killed',
                                      'name': 'New Playerd',
                                      'type': '25',
                                      'steam_id': 'STEAM_0:1:29713080',
                                      'team': 'players',
                                      'adverb': 'with',
                                      'noun': 'trigger_hurt'}})

def test_MessageHandler_killed_by():
    line = '17/04/2018 - 03:06:44: "monster_shockroach<monster><NoAuthID><enemy>" has been killed by "invalid_ent"'
    messageHandler = DateHandler(MessageHandler(NoopHandler()))

    out = messageHandler.parse(line, {})

    assert(out['type'] == 'game_interaction')
    assert(out['interaction'] == {'who': 'monster_shockroach',
                                  'entity_type': 'monster',
                                  'steam_id': 'NoAuthID',
                                  'team': 'enemy',
                                  'action': {'verb': 'killed by',
                                             'noun': 'invalid_ent'}})

    out = messageHandler.parse(line, {})
