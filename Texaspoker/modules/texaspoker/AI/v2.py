'''
Author: zgong
Date: 2021-01-15 15:19:34
LastEditors: zgong
LastEditTime: 2021-01-15 20:19:26
'''
import random

import pandas as pd
import numpy as np

from lib.card_value import aka_pair, encoding
from lib.client_lib import Decision, Hand, Player, State
from lib.read_lookup_table import MonteCarlo, read_lookup_table, select_largest, read_pair_level, MonteCarlo_compare


def ai(id, state):
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
        elif level in [3, 4]:
            decision.callbet = 1
        elif level in [5, 6]:
            decision.giveup = 1

    else:
        remain_card = list(range(0, 52))
        for x in cards:
            remain_card.pop(remain_card.index(x))
        # 模拟发牌1000次

        win_rate = np.mean([MonteCarlo_compare(remain_card.copy(), cards.copy())
                            for i in range(1000)])

        if win_rate < 0.5:
            expect_call = win_rate*(pot)+(1-win_rate)*(-delta)
            if expect_call > 0:
                decision.callbet = 1
            else:
                decision.giveup = 1

        if win_rate > 0.5:
            alpha = (1-win_rate)/(2*win_rate-1)*(pot+delta)  # 打弃牌率？
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
