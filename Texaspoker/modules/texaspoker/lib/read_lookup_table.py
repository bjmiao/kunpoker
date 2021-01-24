'''
Author: bmiao
Date: 2021-01-15 15:12:59
LastEditors: zgong
LastEditTime: 2021-01-24 13:24:43
'''
import pickle
import random
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

# from card_value import (aka_pair, card2id, card_encoding_5, id2card,
from .card_value import (aka_pair, card2id, card_encoding_5, id2card,
                         read_lookup_table, select_largest, card_encoding_2)

PAIR_LEVEL = pd.read_csv(Path(__file__).parent/'pair_level.csv', index_col=0)


LOOKUPTABLE = read_lookup_table()

def read_pair_level(pairs):
    aka = aka_pair(pairs)
    z = aka[2]
    if z == 's':
        x, y = aka[0], aka[1]
    else:
        x, y = aka[1], aka[0]
    return PAIR_LEVEL.loc[x, y]


def gen_level_dict():
    level_dict = {i: [] for i in range(1, 7)}
    for cards in combinations(range(52), 2):
        cards = sorted(cards)
        level = read_pair_level(cards)
        level_dict[level].append(cards)
    return level_dict


PAIR_LEVEL_DICT = gen_level_dict()


def get_card_range(shared_card, remain_card_range=None, threshold=0.3, nsamples=1000):
    ''' given shared card, return the strongests hands'''
    deck = list(range(52))
    for card in shared_card:
        deck.remove(card)

    hand_value_pair = []
    # for hand in [(12,16)]:
    if (remain_card_range):
        card_iter = combinations(deck, 2)
    else:
        card_iter = remain_card_range
    for hand in card_iter:
        deck.remove(hand[0])
        deck.remove(hand[1])
        value_list = []
        for _ in range(nsamples):
            value = MonteCarlo(deck, list(shared_card)+list(hand))
            value_list.append(value)
        # if (hand == (12, 16)):
        #     print(value_list)
        hand_value = np.median(value_list)
        hand_value_pair.append((hand_value, hand))
        deck.append(hand[0])
        deck.append(hand[1])

    # print(hand_value_pair[:10])
    hand_value_pair = sorted(hand_value_pair, reverse=True)
    # print(hand_value_pair)
    return hand_value_pair[:int(threshold*len(hand_value_pair))]


def MonteCarlo(heap, mycards):
    ''' Monte Carlo single time'''
    need_card = 7 - len(mycards)
    new_card = random.sample(heap, need_card)

    max_val_hand, max_val = select_largest(new_card + list(mycards), LOOKUPTABLE)
    return max_val


def MonteCarlo_compare(heap, shared_card, mycards, oppsite_cards):
    ''' 
    heap: remaining deck
        shared_card: shared card
        mycard: my card
        oppsite_card_range: the pool to select oppsite card
    '''
    need_card = 5 - len(shared_card)
    new_card = random.sample(heap, need_card)

    max_val_hand, max_val = select_largest(shared_card + new_card + mycards, LOOKUPTABLE)
    oppsite_val_hand, oppsite_max_val = select_largest(shared_card + new_card + oppsite_cards, LOOKUPTABLE)
    return max_val > oppsite_max_val


def calculate_win_rate(shared_cards, my_cards, oppsite_card_range=None,
                        nsamples=1000): 
    ''' 
        shared_card :
        my_car
        oppsite_card_range

    '''
    deck = list(range(0, 52))
    for card in shared_cards:
        deck.remove(card)
    for card in my_cards:
        deck.remove(card)

    # for i, oppsite_cards in enumerate(oppsite_card_range):
    #     valid = True
    #     for card in oppsite_cards:
    #         if card in cards:
    #             valid = False
    #             break
    #     valid_ls.append(valid)
    # if nsamples > len(oppsite_card_range):
        # nsamples = len(oppsite_card_range)
    win_list = []
    for _ in range(nsamples):
        if oppsite_card_range:
            oppsite_cards = random.choice(oppsite_card_range)
        else:
            oppsite_cards = random.sample(deck, 2)
        if (oppsite_cards[0] in shared_cards or oppsite_cards[0] in my_cards
            or oppsite_cards[1] in shared_cards or oppsite_cards[1] in my_cards):
            continue

        need_append = []
        if oppsite_cards[0] in deck:
            deck.remove(oppsite_cards[0])
            need_append.append(oppsite_cards[0])
        if oppsite_cards[1] in deck:
            deck.remove(oppsite_cards[1])
            need_append.append(oppsite_cards[1])
    
        win_list.append(MonteCarlo_compare(deck, shared_cards, my_cards, oppsite_cards))
        for card in need_append:
            deck.append(card)
    if len(win_list) == 0:
        return 0.5
    win_rate = np.mean(win_list)
    return win_rate



def test():
    cards = ['C2', 'S3', 'S2', 'S4', 'H3']
    hand = [card2id(card) for card in cards]
    lookup_table = read_lookup_table()
    print(lookup_table[card_encoding_5(hand)])
    cnt = 0
    while (True):
        cnt += 1
        hand = random.sample(range(52), 7)
        print([id2card(x) for x in hand])
        # value = lookup_table[card_encoding_5(hand)] / LENGTH
        max_val_hand, max_val = select_largest(hand, lookup_table)

        print("Level:", max_val, " hand:", [id2card(x) for x in max_val_hand])
        if (max_val > 0.99):
            print("Count = ", cnt)
            input()


if __name__ == "__main__":
    total_result = {}
    for cards in combinations(list(range(0, 52)), 2):
        cards = list(cards)
        aka = aka_pair(cards)
        if aka in total_result:
            continue
        print(aka)
        remain_card = list(range(52))
        # num = len(cards) ## 当前状态
        for x in cards:
            remain_card.pop(remain_card.index(x))
        # 模拟发牌10000次
        raw_win_rate = np.mean(
            [MonteCarlo(remain_card.copy(), cards.copy()) for i in range(100000)])
        total_result[aka] = raw_win_rate

        NUM = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        result_matrix = np.zeros((13, 13))
        df = pd.DataFrame(6, index=NUM[::-1], columns=NUM[::-1])
        for key in total_result:
            z = key[2]
            if z == 's':
                x, y = key[0], key[1]
            else:
                x, y = key[1], key[0]
            df.loc[x, y] = total_result[key]

        df.to_csv('pair_result.csv')
