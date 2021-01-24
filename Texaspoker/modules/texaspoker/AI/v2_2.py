'''
Author: zgong
Date: 2021-01-15 15:19:34
LastEditors: zgong
LastEditTime: 2021-01-24 13:42:50
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
                                   MonteCarlo_compare, read_pair_level, get_card_range)

FRESH_LEVEL = PAIR_LEVEL_DICT[1] + \
    PAIR_LEVEL_DICT[2]+PAIR_LEVEL_DICT[3]+PAIR_LEVEL_DICT[4]+PAIR_LEVEL_DICT[5]


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
        self.global_info = {} #style
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
        self.pair_range = FRESH_LEVEL

    def update(self, player,first=False):
        if first:
            self.username = player.username     # username, 'unknown' is unknown
            self.init_money = player.init_money  # init money
            self.inited = player.inited
        self.money = player.money      # money player remains
        self.active = player.active
        self.bet = player.bet            # the bet in this round
        self.cards = player.cards         # private cards
        self.totalbet = player.totalbet       # the bet in total(all round)
        self.allin = player.allin          # if the player has all in

    def update_action(self, pos, nowturn_actions, player_actions, turnnum, shared_card=[]):
        self.pos = pos
        self.game_actions = nowturn_actions
        self.actions = player_actions
        self.update_pair_range(turnnum, shared_card)  # need 全局信息

    def update_pair_range(self, turnnum, shared_card):
        # TODO
        
        if self.active:
            raise_dic = {0: 0, 1: 0, 2: 0}
            allin_dic = {0: 0, 1: 0, 2: 0}
            raise_num = 0
            allin_num = 0
            for action in self.game_actions:
                action_pos = action[1]
                if action[0] == 'raisebet':
                    raise_num += 1
                    raise_dic[action_pos] = raise_num
                elif action[0] == 'allin':
                    allin_num += 1
                    allin_dic[action_pos] = allin_num

            if turnnum == 0:
                if allin_dic[self.pos] == 1:
                    self.pair_range = PAIR_LEVEL_DICT[1]
                elif raise_dic[self.pos] == 3:
                    self.pair_range = PAIR_LEVEL_DICT[1] + \
                        PAIR_LEVEL_DICT[2]+PAIR_LEVEL_DICT[3]
                elif raise_dic[self.pos] == 4:
                    self.pair_range = PAIR_LEVEL_DICT[1] + PAIR_LEVEL_DICT[2]

            else:
                threshold = 0
                pair_length = len(self.pair_range)
                if allin_dic[self.pos] == 1:
                    threshold = 0.1
                elif raise_dic[self.pos] == 1:
                    threshold = 0.3
                elif raise_dic[self.pos] == 2:
                    threshold = 0.1
                if threshold > 0:
                    print(f'update card_range:{threshold}')
                    card_list = get_card_range(
                        shared_card, remain_card_range=self.pair_range, threshold=threshold, nsamples=50)
                    self.pair_range = [value_cards[1]
                                       for value_cards in card_list]
                    print(len(self.pair_range))


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
            player_actions[_pos][turn].append(
                [action, _pos, _amount, _actionNum])

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
        actions.append([action, _pos, _amount, _actionNum])
    return actions


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
            if pos == mypos:
                continue
            username = player.username

            play_info = getattr(global_player_info, username, -1)
            if play_info == -1:
                print(f'init:{username}')
                play_info = PlayerInfo(player)
                setattr(global_player_info, username, play_info)
                play_info = getattr(global_player_info, username)
            play_info.update(player,first=True)
            play_info.refresh()
            play_info.update_action(
                pos, nowturn_actions, player_actions[pos], 0)
            if play_info.active:

                nowturn_play_info_name.append(username)
    else:
        for pos, player in enumerate(state.player):
            if pos == mypos:
                continue
            username = player.username
            play_info = getattr(global_player_info, username)
            play_info.update_action(
                pos, nowturn_actions, player_actions[pos], nowturn, state.sharedcards)
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
        delta = state.player[state.currpos].money  # allin

    if nowturn == 0:
        last_raised = state.last_raised

        raise_num = 0
        allin_num = 0

        for action in nowturn_actions:
            if action[0] == 'raisebet':
                raise_num += 1
            elif action[0] == 'allin':
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
            decision.giveup = 1

    else:
        last_raised = state.last_raised

        raise_num = 0
        allin_num = 0

        for action in nowturn_actions:
            if action[0] == 'raisebet':
                raise_num += 1
            elif action[0] == 'allin':
                allin_num += 1

        oppsite_card_range = [getattr(
            global_player_info, username).pair_range for username in nowturn_play_info_name]
        oppsite_card_range = reduce(list.__add__, oppsite_card_range)
        print(f'oppsite_card:{len(oppsite_card_range)}')
        win_rate = calculate_win_rate(state.sharedcards, state.player[id].cards, oppsite_card_range)
        
        if allin_num == 1:
            raise_threshold = 1

        elif raise_num == 0:
            raise_threshold = 0.6
        elif raise_num == 1:
            raise_threshold = 0.8
        elif raise_num >= 2:
            raise_threshold = 0.9

        if win_rate <= raise_threshold:
            expect_call = win_rate*(pot)+(1-win_rate)*(-delta)
            if expect_call > 0:
                decision.callbet = 1
            else:
                decision.giveup = 1

        raise_smooth = np.array([0.33, 0.5, 0.7, 1, 1.5, 2])
        if win_rate > raise_threshold:
            ratio = (1-win_rate)/(2*win_rate-1)
            ratio = raise_smooth[(ratio > raise_smooth).sum()]
            alpha = ratio*(pot+delta)  # 打弃牌率？
            alpha = max((alpha//state.bigBlind) * state.bigBlind, last_raised)
            decision.raisebet = 1
            decision.amount = int(alpha+delta+totalbet)

    if decision.giveup == 1 and (delta == 0):  # 不需要筹码，肯定进
        decision.callbet = 1
        decision.giveup = 0
    if decision.callbet == 1 and delta == state.player[state.currpos].money:
        decision.callbet = 0
        decision.allin = 1

    # global_player_info.pickle('infos.pkl')
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
