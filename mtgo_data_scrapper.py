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

        # Keep those line in this order
        self.records = defaultdict(dict)
        self.players = self._get_players()
        self._format_cards()
        self.records['match']['cards_played'] = self.cards_played
        self._format_lines()
        self.games = self._get_games()
        self.players_wins = {'player': 0,
                             'opponent': 0
                             }
        self.records['match']['match_ID'] = self._get_match_ID()

        for i, game in enumerate(self.games):
            self.records[f'game_{i+1}']['on_play'] = self._get_on_play(game)
            self.records[f'game_{i+1}']['starting_hands'] = self._get_starting_hands(game)
            self.records[f'game_{i+1}']['winner'] = self._get_winner(game)
            self.records[f'game_{i+1}']['last_turn'] = self._get_last_turn(game)

    def _get_players(self):
        # Find player names and set them as 'player' and 'opponent'.

        players = set(re.compile(
            '@P(\w+) rolled').findall(self.match_log))
        players.discard(self.player)
        self.opponent = list(players)[0]

        players = dict()
        players[self.opponent] = 'opponent'
        players[self.player] = 'player'

        return players

    def _format_cards(self):
        # Stores cards each player has played
        # The card names are formatted as @[Card Name@:numbers,numbers:@]
        # Game actions are @P(player_name) (casts|plays|discards|cycles|reveals) card_pattern

        card_pattern = re.compile('@\[([a-zA-Z\s,-]+)@:[0-9,]+:@\]')
        players_cards_pattern = re.compile(
            '@P(\w+) (casts|plays|discards|cycles|reveals) (@\[([a-zA-Z\s,-]+)@:[0-9,]+:@\])'
        )

        pattern_matches = players_cards_pattern.findall(self.match_log)
        self.cards_played = {'player': set(),
                             'opponent': set()
                             }
        for pattern_match in pattern_matches:
            self.cards_played[self.players[pattern_match[0]]].add(pattern_match[3])

        # set objects are not JSON serializable
        self.cards_played['player'] = list(self.cards_played['player'])
        self.cards_played['opponent'] = list(self.cards_played['opponent'])

        # Replace the weird card formatting with a simple Card Name
        self.match_log = re.sub(card_pattern, r"\g<1>", self.match_log)

    def _format_lines(self):
        # Remove non-relevant characters
        filtered_match = re.split(
            r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff\ufffd\.\{\}\|\\=#\^><$]',
            self.match_log)
        filtered_match = [re.sub('^.*@P', '', line) for line in filtered_match]
        filtered_match = [line for line in filtered_match if len(line) > 3]
        self.match_log = filtered_match

    def _get_match_ID(self):
        # Match_ID looks like it's the first line of the filtered log.

        return self.match_log[0]

    def _get_games(self):
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

    def _get_on_play(self, game):
        # Who is on the play in this game?
        # Returns 'player' or 'opponent'
        on_play = re.compile(
            '(\w+) chooses to play first'
            ).search(game[0]).group(1)
        return self.players[on_play]

    def _get_starting_hands(self, game):
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

    def _get_winner(self, game):
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
            # In those cases, query the user to check the game log
            print('\n'.join(game[-8:]))
            if yes_or_no('Did you win this game?'):
                return 'player'
            else:
                return 'opponent'

    def _get_last_turn(self, game):
        turn_pattern = re.compile('Turn (\d+)')
        # Iterating through finditer, only the last match is saved
        # This might save some memory
        for last_match in turn_pattern.finditer(' '.join(game)):
            pass

        return last_match.group(1)

    def get_json(self):
        return json.dumps(self.records)


def yes_or_no(question):
    # Copied from https://gist.github.com/garrettdreyfus/8153571
    answer = input(question + "(y/n): ").lower().strip()
    print("")
    while not(answer == "y" or answer == "yes" or
    answer == "n" or answer == "no"):
        print("Input yes or no")
        answer = input(question + "(y/n):").lower().strip()
        print("")
    if answer[0] == "y":
        return True
    else:
        return False


if __name__ == '__main__':
    match = MatchRecord('match5.dat', player='kley')
    print(match.get_json())
