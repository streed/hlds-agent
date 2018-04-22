import asyncore
import re
import struct
import time

from datetime import datetime

class Handler(object):
    def __init__(self, _next):
        self._next = _next

    def __call__(self, data, out):
        return self.parse(data, out)


class NoopHandler(Handler):

    def __init__(self):
        super().__init__( None)

    def parse(self, data, out):
        return out


class CleanHandler(Handler):

    def __init__(self, _next):
        super().__init__(_next)

    def parse(self, data, out):
        header = data[:8]
        headerValue, headerLog = struct.unpack('<L4s', header)
        logLine = data[10:-2].decode('utf-8')
        logLine = logLine.rstrip('\n')

        return self._next.parse(logLine, out)

class RawHandler(Handler):

    def __init__(self, _next):
        super().__init__(_next)

    def parse(self, data, out):
        out['raw'] = data

        return self._next.parse(data, out)



class DateHandler(Handler):
    
    def __init__(self, _next):
        super().__init__(_next)


    def parse(self, data, out):
        date = data[:21]
        try:
            out['date'] = datetime.strptime(date, "%d/%m/%Y - %H:%M:%S")
        except ValueError as e:
            out['date'] = datetime.strptime(date, "%m/%d/%Y - %H:%M:%S")

        out['date'] = int(time.mktime(out['date'].timetuple()))

        return self._next(data[23:], out)

class MessageHandler(Handler):
    def __init__(self, _next):
        super().__init__(_next)

    def parse(self, data, out):
        if data.startswith("Server"):
            out = self.handle_server(data[7:], out)
        elif data.startswith("Log"):
            out = self.handle_log(data[4:], out)
        elif data.startswith("Loading") or data.startswith("Started"):
            out = self.handle_map(data[8:], out)
        elif data.startswith("Rcon"):
            out = self.handle_rcon(data[5:], out)
        else:
            out = self.handle_game(data, out)

        return self._next(data, out)


    def handle_server(self, data, out):
        if data.startswith("cvar"):
            out['type'] = 'cvar'
        elif data.startswith("is empty"):
            out['type'] = 'server_status'
        elif data.startswith("name"):
            out['type'] = 'server_name'
        elif data.startswith("say"):
            out['type'] = 'server_say'
        else:
            out['type'] = 'unknown'

        return out
        

    def handle_log(self, data, out):
        out['type'] = 'log'

        log_data = re.search(r'file started \(file "([^"]+)"\) \(game "([^"]+)"\) \(version "([^"]+)"\)', data)

        if log_data:
            file_name, game, version = log_data.groups()

            out['log'] = {'file_name': file_name,
                          'game': game,
                          'version': version}

        return out


    def handle_rcon(self, data, out):
        out['type'] = 'rcon'

        return out


    def handle_map(self, data, out):
        out['type'] = 'map'

        map_name = re.search(r'map "([^"]+)"', data)

        if map_name:
            map_name = map_name.groups()

            out['map'] = {'map_name': map_name[0]}

        return out


    def handle_game(self, data, out):
        if data.startswith("Vote"):
            out = self.handle_vote(data[5:], out)
        elif data.startswith("Kick"):
            out = self.handle_kick(data[5:], out)
        elif data.startswith("World"):
            out = self.handle_world(data[6:], out)
        elif data.startswith('Team'):
            out = self.handle_team(data[5:], out)
        elif data.startswith('Player'):
            out = self.handle_player(data[7:], out)
        else:
            out = self.handle_interactions(data, out)

        return out

    def handle_vote(self, data, out):
        out['type'] = 'game_vote'

        vote = re.search(data, r'for map change to "([^"]+)" finished, succeeded. \(([\d\.]+)% reached, needed ([\d\.]+)%.\)/')

        if vote:
            map_name, vote_for, vote_required = vote.groups()

            out['vote'] = {'map_name': map_name,
                           'vote_for': vote_for,
                           'vote_required': vote_required}
        else:
            vote = re.search(data, r'for map change to "([^"]+)" has been passed, performing action.')
            if vote:
                map_name = vote.groups()
                out['vote'] = {'map_name': map_name}

        return out

    def handle_kick(self, data, out):
        out['type'] = 'game_kick'

        kick_data = re.search(r'"([^<]+)<([\d]+)><(STEAM_\d+:\d:\d+)><(.*)>" was kicked by "([^"]+)"', data)

        if kick_data:
            player_name, uid, steam_id, _, kicked_by = kick_data.groups()

            out['kick'] = {'player': {'name': player_name,
                                      'uid': int(uid),
                                      'steam_id': steam_id},
                           'kicked_by': kicked_by}

        return out

    def handle_world(self, data, out):
        out['type'] = 'game_world'

        world_parsed = re.search(r'triggered "([^"]+)"', data)

        if world_parsed:
            out['action'] = world_parsed.groups()[0]

        return out

    def handle_team(self, data, out):
        out['type'] = 'game_team'

        team_parsed = re.search(r'"([^"]+)" triggered "([^"]+)" \(\1 "([^"]+)"\) \(([\w_]+) "([^"]+)"\)', data)

        if team_parsed:
            team_a_name, did, team_a_score, team_b_name, team_b_score = team_parsed.groups()

            out['action'] = {'team_a': team_a_name,
                             'did': did,
                             'team_a_score': team_a_score,
                             'team_b': team_b_name,
                             'team_b_score': team_b_score}
        else:
            team_parsed = re.search(r'"([^"]+)" ([^ ]+) "([^"]+)" ([^ ]+) "([^"]+)" (.*)', data)

            if team_parsed:
                out['type'] = 'game_team_stats'
                team, did, x, adverb, y, z = team_parsed.groups()

                out['stats'] = {'team': team,
                                'did': did,
                                'x': x,
                                'adverb': adverb,
                                'y': y,
                                'z': z}
        return out

    def handle_player(self, data, out):
        out['type'] = 'game_player'

        return out

    def handle_interactions(self, data, out):
        out['type'] = 'game_interaction'

        interaction_data = re.search(r'"([^<]+)<([^>]+)><([^<]+)><([^>]*)>" (.*)', data)

        if interaction_data:
            name, _type, steam_id, team, action = interaction_data.groups()

            if action.startswith("stats:"):
                out['stats'] = {'who': name,
                                'entity_type': _type,
                                'steam_id': steam_id,
                                'team': team}
                out = self.handle_player_stats(action, out)
            else:
                out['interaction'] = {'who': name,
                                      'entity_type': _type,
                                      'steam_id': steam_id,
                                      'team': team,
                                      'action': self.handle_action(action)}
        return out

    def handle_action(self, action):
        action_parse = re.search(r'([\w]+) "([^<]+)<([^>]+)><([^<]+)><([^>]+)>" ([\w]+) "(.*)"', action)

        if action_parse:
            verb, name, _type, steam_id, team, adverb, noun = action_parse.groups()

            return {'verb': verb,
                    'name': name,
                    'type': _type,
                    'team': team,
                    'steam_id': steam_id,
                    'adverb': adverb,
                    'noun': noun}
        else:
            wordy_action = re.search(r'([\w\d, ]+) ?("([^"]+)")?', action)

            if wordy_action:
                verb, _, noun = wordy_action.groups()
                if verb:
                    verb = verb.rstrip(' ')

                if noun:
                    return {'verb': verb,
                            'noun': noun}
                else:
                    return {'verb': verb}

    def handle_player_stats(self, stats, out):
        stats_parsed = re.search(r'stats: frags="([^"]+)" deaths="([^"]+)" health="([^"]+)"', stats)

        if stats_parsed:
            frags, deaths, health = stats_parsed.groups()

            out['type'] = 'game_player_stats'
            out['stats']['frags'] = float(frags)
            out['stats']['health'] = float(health)
            out['stats']['deaths'] = float(deaths)

        return out

