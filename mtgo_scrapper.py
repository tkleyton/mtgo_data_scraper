from match_record import MatchRecord


if __name__ == '__main__':
    print('Running...')
    match = MatchRecord('match5.dat', player='kley')
    print(match.get_json())
