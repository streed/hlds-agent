import time
import datetime

import pytest

from hlds_agent.handler import NoopHandler, DateHandler, MessageHandler

@pytest.fixture
def messageHandler():
    return DateHandler(MessageHandler(NoopHandler()))


@pytest.fixture
def dateHandler():
    class DateHandlerTest(DateHandler):
        def get_time(self):
            return 1

    return DateHandlerTest(NoopHandler())

def test_DateHandler(dateHandler):
    line = '15/04/2018 - 23:56:25: Server cvar "mp_consistency" = "0"'

    out = dateHandler.parse(line, {})

    assert(out['date'] == 1)

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
                                  'action': {'verb': 'has been killed by',
                                             'noun': 'invalid_ent'}})

    out = messageHandler.parse(line, {})

def test_MessageHandler_player_stats(messageHandler):
    line = '17/04/2018 - 03:07:12: "ltkitty<9><STEAM_0:1:813><players>" stats: frags="0.00" deaths="1" health="82"'
    out = messageHandler.parse(line, {})

    assert(out['type'] == 'game_player_stats')
    assert(out['stats'] == {'who': 'ltkitty',
                            'entity_type': '9',
                            'steam_id': 'STEAM_0:1:813',
                            'team': 'players',
                            'frags': 0.0,
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


def test_MessageHandler_cs_joined_team(messageHandler):
    line = '04/19/2018 - 01:37:59: "Player<1><STEAM_0:0:12345><>" joined team "TERRORIST"'

    out = messageHandler.parse(line, {})

    assert(out['type'] == 'game_interaction')
    assert(out['interaction'] == {'who': 'Player',
                                  'entity_type': '1',
                                  'steam_id': 'STEAM_0:0:12345',
                                  'team': '',
                                  'action': {'verb': 'joined team',
                                             'noun': 'TERRORIST'}})

def test_MessageHandler_cs_Spawned_With_Bomb(messageHandler):
    line = '04/19/2018 - 01:37:59: "Player<1><STEAM_0:0:123><TERRORIST>" triggered "Spawned_With_The_Bomb"'

    out = messageHandler.parse(line, {})

    assert(out['type'] == 'game_interaction')
    assert(out['interaction'] == {'who': 'Player',
                                  'entity_type': '1',
                                  'steam_id': 'STEAM_0:0:123',
                                  'team': 'TERRORIST',
                                  'action': {'verb': 'triggered',
                                             'noun': 'Spawned_With_The_Bomb'}})


def test_MessageHandler_cs_committed_suicide(messageHandler):
    line = '04/19/2018 - 01:38:29: "Player<1><STEAM_0:0:123><TERRORIST>" committed suicide with "world"'

    out = messageHandler.parse(line, {})

    assert(out['type'] == 'game_interaction')
    assert(out['interaction'] == {'who': 'Player',
                                  'entity_type': '1',
                                  'steam_id': 'STEAM_0:0:123',
                                  'team': 'TERRORIST',
                                  'action': {'verb': 'committed suicide with',
                                             'noun': 'world'}})


def test_MessageHandler_cs_disconnected(messageHandler):
    line = '04/19/2018 - 01:38:43: "Player<1><STEAM_0:0:123><TERRORIST>" disconnected'

    out = messageHandler.parse(line, {})

    assert(out['type'] == 'game_interaction')
    assert(out['interaction'] == {'who': 'Player',
                                  'entity_type': '1',
                                  'steam_id': 'STEAM_0:0:123',
                                  'team': 'TERRORIST',
                                  'action': {'verb': 'disconnected'}})

def test_MessageHandler_cs_entered_the_game(messageHandler):
    line = '04/19/2018 - 01:38:43: "Player<1><STEAM_0:0:123><TERRORIST>" entered the game'

    out = messageHandler.parse(line, {})

    assert(out['type'] == 'game_interaction')
    assert(out['interaction'] == {'who': 'Player',
                                  'entity_type': '1',
                                  'steam_id': 'STEAM_0:0:123',
                                  'team': 'TERRORIST',
                                  'action': {'verb': 'entered the game'}})

def test_MessageHandler_cs_connected(messageHandler):
    line = '04/19/2018 - 01:37:50: "Player<1><STEAM_0:0:123><>" connected, address "127.0.0.1:27005"'

    out = messageHandler.parse(line, {})

    assert(out['type'] == 'game_interaction')
    assert(out['interaction'] == {'who': 'Player',
                                  'entity_type': '1',
                                  'steam_id': 'STEAM_0:0:123',
                                  'team': '',
                                  'action': {'verb': 'connected, address',
                                             'noun': '127.0.0.1:27005'}})

def test_MessageHandler_cs_steam_validated(messageHandler):
    line = '04/19/2018 - 01:37:50: "Player<1><STEAM_0:0:123><>" STEAM USERID validated'
    out = messageHandler.parse(line, {})

    assert(out['type'] == 'game_interaction')
    assert(out['interaction'] == {'who': 'Player',
                                  'entity_type': '1',
                                  'steam_id': 'STEAM_0:0:123',
                                  'team': '',
                                  'action': {'verb': 'STEAM USERID validated'}})
