import datetime

import pytest

from hlds_agent.handler import NoopHandler, DateHandler, MessageHandler

@pytest.fixture
def messageHandler():
    return DateHandler(MessageHandler(NoopHandler()))


def test_DateHandler():
    line = '15/04/2018 - 23:56:25: Server cvar "mp_consistency" = "0"'
    dateHandler = DateHandler(NoopHandler())

    out = dateHandler.parse(line, {})

    assert(out['date'] == datetime.datetime(2018, 4, 15, 23, 56, 25))

def test_MessageHandler_cvar(messageHandler):
    line = '15/04/2018 - 23:56:25: Server cvar "mp_consistency" = "0"'
    out = messageHandler.parse(line, {})

    assert(out['type'] == 'cvar')

def test_MessageHandler_log_simple(messageHandler):
    line = '15/04/2018 - 23:56:25: Log file closed'
    out = messageHandler.parse(line, {})

    assert(out['type'] == 'log')

def test_MessageHandler_log_complex(messageHandler):
    line = '15/04/2018 - 23:56:25: Log file started (file "logs/2018-04-15.log") (game "svencoop") (version "48/5.0.0.0/7744")'
    out = messageHandler.parse(line, {})

    assert(out['type'] == 'log')
    assert(out['log'] == {'file_name': 'logs/2018-04-15.log',
                          'game': 'svencoop',
                          'version': '48/5.0.0.0/7744'})

def test_MessageHandler_map(messageHandler):
    line = '15/04/2018 - 23:56:25: Started map "svencoop1" (CRC "530877971")'
    out = messageHandler.parse(line, {})

    assert(out['type'] == 'map')
    assert(out['map'] == {'map_name': 'svencoop1'})

def test_MessageHandler_kick(messageHandler):
    line = '15/04/2018 - 20:25:48: Kick: "reivaj9916<95><STEAM_0:0:435113400><>" was kicked by "Console"'

    out = messageHandler.parse(line, {})

    assert(out['type'] == 'game_kick')
    assert(out['kick'] == {'player': {'name': 'reivaj9916',
                                      'uid': 95,
                                      'steam_id': 'STEAM_0:0:435113400'},
                            'kicked_by': 'Console'})

def test_MessageHandler_interaction(messageHandler):
    line = '15/04/2018 - 08:02:46: "trigger_hurt<generic_ent><NoAuthID><neutral>" killed "New Playerd<25><STEAM_0:1:29713080><players>" with "trigger_hurt"'

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

def test_MessageHandler_killed_by(messageHandler):
    line = '17/04/2018 - 03:06:44: "monster_shockroach<monster><NoAuthID><enemy>" has been killed by "invalid_ent"'

    out = messageHandler.parse(line, {})

    assert(out['type'] == 'game_interaction')
    assert(out['interaction'] == {'who': 'monster_shockroach',
                                  'entity_type': 'monster',
                                  'steam_id': 'NoAuthID',
                                  'team': 'enemy',
                                  'action': {'verb': 'killed by',
                                             'noun': 'invalid_ent'}})

    out = messageHandler.parse(line, {})

def test_MessageHandler_player_stats(messageHandler):
    line = '17/04/2018 - 03:07:12: "ltkitty<9><STEAM_0:1:8134911><players>" stats: frags="0.00" deaths="1" health="82"'
    out = messageHandler.parse(line, {})

    assert(out['type'] == 'game_player_stats')
    assert(out['stats'] == {'frags': 0.0,
                            'deaths': 1,
                            'health': 82})

def test_MessageHandler_world(messageHandler):
    line = '04/17/2018 - 21:30:08: World triggered "Round_Start"'
    out = messageHandler.parse(line, {})

    assert(out['type'] == 'game_world')
    assert(out['action'] == 'Round_Start')


def test_MessageHandler_team(messageHandler):
    line = '04/18/2018 - 04:36:46: Team "CT" triggered "Target_Saved" (CT "1") (T "0")'
    out = messageHandler.parse(line, {})

    assert(out['type'] == 'game_team')
    assert(out['action'] == {'team_a': 'CT',
                             'team_a_score': '1',
                             'team_b': 'T',
                             'team_b_score': '0',
                             'did': 'Target_Saved'})

def test_MessageHandler_team_stats(messageHandler):
    line = '04/18/2018 - 04:52:15: Team "TERRORIST" scored "0" with "0" players'
    out = messageHandler.parse(line, {})

    assert(out['type'] == 'game_team_stats')
    assert(out['stats'] == {'team': 'TERRORIST',
                            'did': 'scored',
                            'x': '0',
                            'adverb': 'with',
                            'y': '0',
                            'z': 'players'})

