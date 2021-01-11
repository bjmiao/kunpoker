import random


class Participant(object):
    def __init__(self, _name, _chip):
        self.name = _name
        self.chip = _chip


class Desk(object):

    def __init__(self, participant_list):
        self.participant_list = participant_list
        self.position = None

    def newgame(self):
        player_list = [Player(p) for p in self.participant_list]
        self.current_game = SingleGame(player_list)
        return self.current_game


class Player(object):
    def __init__(self, participant):
        self.name = participant.name
        self.chip = participant.chip  # remain chip in hand


POINT = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
SUIT = ['S', 'H', 'D', 'C']
CARD = [s+p for s in SUIT for p in POINT]


class SingleGame(object):
    def __init__(self, player_info_list, dealer=0, bb=10):
        ''' Input: player_info_list [Player()]
                   dealer : dealer
                   bb : big blind
        '''
        self.player_list = []  # Name list with position
        self.player_info_list = {}  # Name and Chip
        for player in player_info_list:
            self.player_list.append(player.name)
            self.player_info_list[player.name] = player

        self.dealer = dealer  # who is the dealer
        self.bb = bb
        self.sb = bb // 2
        print(self.player_list)
        self.player_card, self.comm_card = self._deal(self.player_list)
        self.shown_card = 0  # 0:start, 3:flop, 4:turn, 5:river

        self.action = []  # [("player1", "call", None), ("player2", "folder", None), ("player3", "raise", 100)]

    def _deal(self, player_list):
        '''
        Output: player_card :[{"player1":["D3", "D4"]), "player2": ["D5, D6"]}] 
                comm_card: # ["D4", "D5", "D6","D7", "D8"]
        '''
        card = CARD.copy()
        random.shuffle(card)
        index = 0
        index += 1
        player_card = {player: [x for x in []] for player in player_list}
        comm_card = []
        # first round
        for player in player_list:
            player_card[player].append(card[index])
            index += 1
        # second round
        for player in player_list:
            player_card[player].append(card[index])
            index += 1
        index += 1
        for _ in range(3):
            comm_card.append(card[index])  # flop
            index += 1
        index += 1
        comm_card.append(card[index])  # turn
        index += 1
        index += 1
        comm_card.append(card[index])  # river

        return player_card, comm_card

    def get_player(self):
        ''' 
            Output: [('player0', '10000'), ('player1', '10000'), ...]
        ''' 
        ret = []
        for player in self.player_list:
            player_info = self.player_info_list[player]
            ret.append((player, player_info.chip))
        return ret

    def get_card(self, player="__GOD__"):
        ''' 
            Output:
            ({'player0': ['CQ', 'CK'], 
              'player1': ['HT', 'C2'], 
              ['ST', 'SJ', 'S8', 'DJ', 'DQ'])
        ''' 
        if (player == "__GOD__"):
            return self.player_card, self.comm_card
        else:
            shown_comm_card = self.comm_card[0:self.shown_card].copy()
            my_player_card = {player: self.player_card[player]} \
                if player in self.player_list else None
            return my_player_card, shown_comm_card



# if __name__ == "__main__":
player_list = []
for i in range(5):
    player = Participant("player" + str(i), "10000")
    player_list.append(player)
desk = Desk(player_list)

game = desk.newgame()
print(game)
game.get_player()