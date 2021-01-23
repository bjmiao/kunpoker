'''
Author: zgong
Date: 2021-01-15 15:19:34
LastEditors: zgong
LastEditTime: 2021-01-24 01:48:35
'''
import copy
import pickle
import random
from functools import reduce

import numpy as np
import pandas as pd
from lib.card_value import aka_pair, card_encoding_5
from lib.client_lib import Decision, Hand, Player, State
from lib.read_lookup_table import (PAIR_LEVEL_DICT, MonteCarlo,
                                   MonteCarlo_compare, read_pair_level)


class PLAYER_INFO:
    def __init__(self):
        pass

    def pickle(self, f):
        with open(f, 'wb') as hander:
            pickle.dump(self, hander)


global_player_info = PLAYER_INFO()


class PlayerInfo():
    def __init__(self, player):
        self.update(player)
        self.global_info = {}
        self.action_history = []
        self.actions = {0: [], 1: [], 2: [], 3: []}
        self.pair_power = 0
        self.pair_range = []
        self.style = None
        self.refresh()

    def refresh(self):  # now_game_state 在 pre-flop 启动
        self.pos = -1
        self.action_history.append(self.actions.copy())
        self.actions = {0: [], 1: [], 2: [], 3: []}
        self.pair_power = 0
        self.pair_range = []

    def update(self, player):
        self.username = player.username     # username, 'unknown' is unknown
        self.init_money = player.init_money  # init money
        self.inited = player.inited
        self.money = player.money      # money player remains
        # if the player is active(haven't giveups)
        self.active = player.active
        self.bet = player.bet            # the bet in this round
        self.cards = player.cards         # private cards
        self.totalbet = player.totalbet       # the bet in total(all round)
        self.allin = player.allin          # if the player has all in

    def update_action(self, pos, game_actions, action_list):
        self.pos = pos
        self.game_actions = game_actions
        self.actions = action_list
        self.update_pair_range()  # need 全局信息

    def update_pair_range(self):
        # TODO
        if self.active:
            self.pair_range = PAIR_LEVEL_DICT[1] + \
                PAIR_LEVEL_DICT[2]+PAIR_LEVEL_DICT[3]+PAIR_LEVEL_DICT[4]


def gen_play_actions(state):
    player_actions = {i: {0: [], 1: [], 2: [], 3: []}
                      for i in range(state.totalPlayer)}
    for turn in state.decision_history:
        for decision in state.decision_history[turn]:
            _actionNum = int(decision.actionNum)
            _pos = int(decision.pos)
            _amount = int(decision.amount)
            _type = int(decision.type)
            action = ""
            if int(decision.raisebet) == 1:
                action = 'raisebet'
            elif int(decision.callbet) == 1:
                action = 'callbet'
            elif int(decision.check) == 1:
                action = 'check'
            elif int(decision.giveup) == 1:
                action = 'fold'
            elif int(decision.allin) == 1:
                action = 'allin'
            player_actions[_pos][turn].append([action, _amount, _actionNum])

    return player_actions


def gen_nowturn_actions(nowturn, state):
    actions = []
    for decision in state.decision_history[nowturn]:
        _actionNum = int(decision.actionNum)
        _pos = int(decision.pos)
        _amount = int(decision.amount)
        _type = int(decision.type)
        action = ""
        if int(decision.raisebet) == 1:
            action = 'raisebet'
        elif int(decision.callbet) == 1:
            action = 'callbet'
        elif int(decision.check) == 1:
            action = 'check'
        elif int(decision.giveup) == 1:
            action = 'fold'
        elif int(decision.allin) == 1:
            action = 'allin'
        actions.append([action, _amount, _actionNum])
    return actions


def calculate_win_rate(cards, oppsite_card_range):

    remain_card = list(range(0, 52))
    for x in cards:
        remain_card.pop(remain_card.index(x))

    valid_ls = []

    for i, oppsite_cards in enumerate(oppsite_card_range):
        valid = True
        for card in oppsite_cards:
            if card in cards:
                valid = False
                break
        valid_ls.append(valid)

    oppsite_card_range = [oppsite_card_range[i]
                          for i in range(len(oppsite_card_range)) if valid_ls[i]]
    # 模拟发牌10000次

    win_rate = np.mean([MonteCarlo_compare(remain_card[:], cards[:], oppsite_card_range)
                        for i in range(10000)])
    return win_rate


'''
rule:

pre-flop:
1. 3bet  -- 强牌力

flop:
raise -- 中牌：牌力为前30%的牌力范围 + 翻牌前牌力
call -- 不变
call - raise : 超强牌力:

turn:
raise -- 强牌 
call -- 

river:
raise -- 
call --

'''


def ai(id, state):
    mypos = state.currpos
    nowturn = state.turnNum
    active_players = np.sum([player.active for player in state.player])

    nowturn_actions = gen_nowturn_actions(nowturn, state)
    player_actions = gen_play_actions(state)

    nowturn_play_info_name = []
    if nowturn == 0:
        for pos, player in enumerate(state.player):
            username = player.username

            play_info = getattr(global_player_info, username, -1)
            if play_info == -1:
                print(f'init:{username}')
                play_info = PlayerInfo(player)
                setattr(global_player_info, username, play_info)
                play_info = getattr(global_player_info, username)
            play_info.update(player)
            play_info.refresh()
            play_info.update_action(pos, nowturn_actions, player_actions[pos])
            if play_info.active:
                nowturn_play_info_name.append(username)
    else:
        for pos, player in enumerate(state.player):
            username = player.username
            play_info = getattr(global_player_info, username, -1)
            play_info.update_action(pos, nowturn_actions, player_actions[pos])
            if play_info.active:
                nowturn_play_info_name.append(username)

    # print(player_actions)
    cards = state.player[id].cards + state.sharedcards

    pot = state.moneypot  # 当前底池
    decision = Decision()
    # judge call cost
    totalbet = state.player[state.currpos].bet
    delta = state.minbet - totalbet
    if delta >= state.player[state.currpos].money:
        delta = state.player[state.currpos].money

    if nowturn == 0:
        last_raised = state.last_raised

        raise_num = 0
        allin_num = 0

        for action in nowturn_actions:
            if action[0] == 'raisebet':
                raise_num += 1
            elif action[1] == 'allin':
                allin_num += 1

        if allin_num >= 1:
            raise_pairs = []
            call_pairs = [1, 2]
            fold_pairs = [3, 4, 5, 6]

        elif raise_num == 2:
            raise_pairs = [1, 2]
            call_pairs = [3, 4, 5]
            fold_pairs = [6]

        elif raise_num == 3:
            raise_pairs = [1]
            call_pairs = [2, 3, 4]
            fold_pairs = [5, 6]

        elif raise_num >= 4:
            raise_pairs = []
            call_pairs = [1]
            fold_pairs = [2, 3, 4, 5, 6]

        level = read_pair_level(cards)
        if level in raise_pairs:
            alpha = random.randint(1, 3)*last_raised
            decision.raisebet = 1
            decision.amount = int(alpha+delta+totalbet)
        elif level in call_pairs:
            decision.callbet = 1
        elif level in fold_pairs:
            if delta == 0:
                decision.callbet = 1
            else:
                decision.giveup = 1
    else:
        last_raised = state.last_raised

        raise_num = 0
        allin_num = 0

        for action in nowturn_actions:
            if action[0] == 'raisebet':
                raise_num += 1
            elif action[1] == 'allin':
                allin_num += 1

        oppsite_card_range = [getattr(
            global_player_info, username).pair_range for username in nowturn_play_info_name]
        oppsite_card_range = reduce(list.__add__, oppsite_card_range)
        print(f'oppsite_card:{len(oppsite_card_range)}')

        win_rate = calculate_win_rate(cards, oppsite_card_range)

        if win_rate < 0.5:
            expect_call = win_rate*(pot)+(1-win_rate)*(-delta)
            if expect_call > 0:
                decision.callbet = 1
            else:
                if delta == 0:
                    decision.callbet = 1
                else:
                    decision.giveup = 1

        if win_rate > 0.5:
            # ratio = (1-win_rate)/(2*win_rate-1)
            # if ratio >
            alpha = min((1-win_rate)/(2*win_rate-1), 2)*(pot+delta)  # 打弃牌率？
            alpha = (alpha//state.bigBlind) * state.bigBlind
            decision.raisebet = 1
            decision.amount = int(alpha+delta+totalbet)

    if decision.callbet == 1 and delta == state.player[state.currpos].money:
        decision.callbet = 0
        decision.allin = 1

    global_player_info.pickle('infos.pkl')
    return decision


# add_bet: 将本局总注额加到total
def add_bet(state, total):
    # amount: 本局需要下的总注
    amount = total - state.player[state.currpos].totalbet
    assert(amount > state.player[state.currpos].bet)
    # Obey the rule of last_raised
    minamount = state.last_raised + state.minbet
    real_amount = max(amount, minamount)
    # money_needed = real_amount - state.player[state.currpos].bet
    decision = Decision()
    decision.raisebet = 1
    decision.amount = real_amount
    return decision
