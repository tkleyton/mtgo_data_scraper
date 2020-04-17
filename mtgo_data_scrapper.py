#!/usr/bin/env python3
# coding: utf-8
import re
from collections import defaultdict
import json


player = 'kley'
numbers_dict = {'one': 1,
                'two': 2,
                'three': 3,
                'four': 4,
                'five': 5,
                'six': 6,
                'seven': 7
                }


class MatchRecord:
    def __init__(self, filename, player):
        self.player = player
        with open(filename, 'rb') as f:
            self.match_log = f.read().decode(
                encoding='utf-8', errors='replace')
            # Unknown characters are replaced by \ufffd (those question marks)

        self.format_cards()
        self.format_lines()
        self.match_ID = self.get_match_ID()
        self.players = self.get_players()
        self.games = self.get_games()
        self.players_wins = {'player': 0,
                             'opponent': 0
                             }
        self.records = defaultdict(dict)
        for i, game in enumerate(self.games):
            self.records[f'game_{i+1}']['on_play'] = self.get_on_play(game)
            self.records[f'game_{i+1}']['starting_hands'] = self.get_starting_hands(game)
            self.records[f'game_{i+1}']['winner'] = self.get_winner(game)

    def format_cards(self):
        # The card names are formatted as @[Card Name@:numbers,numbers:@]
        card_pattern = re.compile('@\[([a-zA-Z\s,-]+)@:[0-9,]+:@\]')
        self._cards_played = set(card_pattern.findall(self.match_log))
        self.match_log = re.sub(card_pattern, r"\g<1>", self.match_log)

    def get_cards_played(self):
        # Replace the weird card formatting with a simple Card Name
        return self._cards_played

    def format_lines(self):
        # Remove non-relevant characters
        filtered_match = re.split(
            r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff\ufffd\.\{\}\|\\=#\^><$]',
            self.match_log)
        filtered_match = [re.sub('^.*@P', '', line) for line in filtered_match]
        filtered_match = [line for line in filtered_match if len(line) > 3]
        self.match_log = filtered_match

    def get_match_ID(self):
        # Match_ID looks like it's the first line of the filtered log.

        return self.match_log[0]

    def get_players(self):
        # Then it's followed by lines 2 and 3 with the players' rolls

        players = set(re.compile(
            '(\w+) rolled').findall(' '.join(self.match_log[2:4])))
        players.discard(self.player)
        self.opponent = list(players)[0]

        players = dict()
        players[self.opponent] = 'opponent'
        players[self.player] = 'player'

        return players

    def get_games(self):
        # Breakdown the match into different games.
        # Game 1 is games[0] and so on
        games = list()
        game_i = 0
        for i, line in enumerate(self.match_log):
            if "chooses to play" in line:
                games.append(self.match_log[game_i:i])
                game_i = i
        games.append(self.match_log[game_i:-1])
        games.pop(0)

        return games

    def get_on_play(self, game):
        # Who is on the play in this game?
        # Returns 'player' or 'opponent'
        on_play = re.compile(
            '(\w+) chooses to play first'
            ).search(game[0]).group(1)
        return self.players[on_play]

    def get_starting_hands(self, game):
        # Returns a dict containing the number of
        # cards in each player's starting hand
        # at a given game
        starting_hands = [(self.players[match_obj.group(1).split()[0]],
            match_obj.group(2)) for match_obj in
            [re.compile('(.+) begins the game with (\w+) cards').
            search(line) for line in game] if match_obj]

        starting_hands = dict(starting_hands)
        for k, v in starting_hands.items():
            starting_hands[k] = numbers_dict[v]

        return starting_hands

    def get_winner(self, game):
        conceded_pattern = re.compile('(\w+) has conceded')
        wins_pattern = re.compile('(\w+) wins the game')
        loses_pattern = re.compile('(\w+) loses the game')

        conceded = conceded_pattern.search(' '.join(game))
        wins = wins_pattern.search(' '.join(game))
        loses = loses_pattern.search(' '.join(game))

        if wins:
            return self.players[wins.group(1)]
        elif conceded:
            if self.players[conceded.group(1)] == 'player':
                return 'opponent'
            else:
                return 'player'
        elif loses:
            if self.players[loses.group(1)] == 'player':
                return 'opponent'
            else:
                return 'player'
        else:
            # Sometimes players just leave the match
            # instead of properly conceding.
            # In those cases, maybe query the user to check the game log?
            # raise AmbiguousResultError
            return 'player'

    def get_json(self):
        return json.dumps(self.records)


class IncompleteMatchError(Exception):
    pass


class AmbiguousResultError(Exception):
    pass


if __name__ == '__main__':
    match1 = MatchRecord('match1.dat', player='kley')
    print(match1.get_json())

    match2 = MatchRecord('match2.dat', player='kley')
    print(match2.get_json())
    print(match2.get_cards_played())
