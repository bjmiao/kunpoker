'''
Author: zgong
Date: 2021-01-15 15:19:34
LastEditors: zgong
LastEditTime: 2021-01-23 23:02:13
'''
import random
import pickle

import numpy as np
import pandas as pd
import copy

from lib.card_value import aka_pair, card_encoding_5
from lib.client_lib import Decision, Hand, Player, State
from lib.read_lookup_table import (MonteCarlo, MonteCarlo_compare,
                                   read_pair_level,
                                   PAIR_LEVEL_DICT)


class AI_Client():
    def __init__(self):
        pass


def ai(id, state):
    print(state._decision_so_far)
    
    for player in state.player:
        if player.active:
            print(player.cards)
            print(player.money)
    print(state)

    if state.turnNum == 2:
        state.dump('state.pkl')
        raise Exception
    remain_card = list(range(0, 52))
    cards = state.player[id].cards + state.sharedcards
    num = len(cards)  # 当前状态

    pot = state.moneypot  # 当前底池
    decision = Decision()
    # judge call cost
    totalbet = state.player[state.currpos].bet
    delta = state.minbet - totalbet
    if delta >= state.player[state.currpos].money:
        delta = state.player[state.currpos].money

    if num == 2:
        level = read_pair_level(cards)
        if level in [1, 2]:
            alpha = random.randint(1, 3)*state.bigBlind
            decision.raisebet = 1
            decision.amount = int(alpha+delta+totalbet)
        elif level in [3, 4, 5]:
            decision.callbet = 1
        elif level in [6]:
            if delta == 0:
                decision.callbet = 1
            else:
                decision.giveup = 1
    else:
        oppsite_card_range = PAIR_LEVEL_DICT[1] + \
            PAIR_LEVEL_DICT[2]+PAIR_LEVEL_DICT[3]+PAIR_LEVEL_DICT[4]
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
            alpha = min((1-win_rate)/(2*win_rate-1),2)*(pot+delta)  # 打弃牌率？
            alpha = (alpha//state.bigBlind) * state.bigBlind
            decision.raisebet = 1
            decision.amount = int(alpha+delta+totalbet)

    if decision.callbet == 1 and delta == state.player[state.currpos].money:
        decision.callbet = 0
        decision.allin = 1

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
