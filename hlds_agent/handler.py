import asyncore
import re
import struct

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

        out['raw'] = logLine

        return self._next.parse(logLine, out)


class DateHandler(Handler):
    
    def __init__(self, _next):
        super().__init__(_next)


    def parse(self, data, out):
        date = data[:21]
        out['date'] = datetime.strptime(date, "%d/%m/%Y - %H:%M:%S")

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
            out = self.handle_log(data[8:], out)
        elif data.startswith("Rcon"):
            out = self.handle_rcon(data[5:], out)
        else:
            out = self.handle_game(data, out)

        return self._next(data, out)


    def handle_server(self, data, out):
        if data.startswith("cvar"):
            out['type'] = 'cvar'
        elif data.startswith("is empty"):
            out['type'] = 'cvar_empty'
        elif data.starswith("name"):
            out['type'] = 'server_name'
        elif data.startswith("say"):
            out['type'] = 'server_say'
        else:
            out['type'] = 'unknown'

        return out
        

    def handle_log(self, data, out):
        out['type'] = 'log'
        return out


    def handle_rcon(self, data, out):
        out['type'] = 'rcon'


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
            out = self.handle_player_interactions(data, out)

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
            map_name = vote.groups()

        return out

    def handle_kick(self, data, out):
        out['type'] = 'game_kick'

        return out

    def handle_world(self, data, out):
        out['type'] = 'game_world'

        return out

    def handle_team(self, data, out):
        out['type'] = 'game_team'

        return out

    def handle_player(self, data, out):
        out['type'] = 'game_player'

        return out

    def handle_player_interactions(self, data, out):
        out['type'] = 'game_player_interactions'

        return out

