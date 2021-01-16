'''
Author: bmiao
Date: 2021-01-15 15:12:59
LastEditors: zgong
LastEditTime: 2021-01-16 20:30:18
'''
import pickle
import random
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

from .card_value import aka_pair, card2id, encoding, id2card

LENGTH = 2598960

PAIR_LEVEL = pd.read_csv(Path(__file__).parent/'pair_level.csv', index_col=0)

def read_lookup_table():
    with open(Path(__file__).parent/"lookup_table.pkl", "rb") as f:
        lookup_table = pickle.load(f)
    return lookup_table

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
    level_dict = {i:[] for i in range(1,7)}
    for cards in combinations(range(52),2):
        cards = sorted(cards)
        level = read_pair_level(cards)    
        level_dict[level].append(cards)
    return level_dict

PAIR_LEVEL_DICT = gen_level_dict()


def select_largest(all_cards, lookup_table):
    if len(all_cards) < 5:
        raise ValueError("Cards number is less then 5")
    max_val = -1
    max_val_hand = None
    for hand in combinations(all_cards, 5):
        hand = sorted(hand)
        val = lookup_table[encoding(hand)]
        if val > max_val:
            max_val = val
            max_val_hand = hand
    return max_val_hand, max_val / LENGTH

def MonteCarlo(heap, mycards):
    random.shuffle(heap)
    while len(mycards) != 7:
        mycards.append(heap.pop())
    max_val_hand, max_val = select_largest(mycards, LOOKUPTABLE)
    return max_val

def MonteCarlo_compare(heap, mycards,oppsite_card_range=[]):
    random.shuffle(heap)
    oppsite_hand = [-1,-1]
    if len(oppsite_card_range)==0:
        oppsite_hand[0] = heap.pop()
        oppsite_hand[1] = heap.pop()
    else:
        while True:
            oppsite_hand = random.choice(oppsite_card_range)
            if (oppsite_hand[0] in heap) and (oppsite_hand[1] in heap):
                heap.remove(oppsite_hand[0])
                heap.remove(oppsite_hand[1])
                random.shuffle(heap)
                break

    oppsite = mycards.copy()
    oppsite[0] = oppsite_hand[0]
    oppsite[1] = oppsite_hand[1]
    
    while len(mycards) != 7:
        share_card = heap.pop()
        mycards.append(share_card)
        oppsite.append(share_card)

    max_val_hand, max_val = select_largest(mycards, LOOKUPTABLE)
    oppsite_val_hand,oppsite_max_val = select_largest(oppsite,LOOKUPTABLE)
    return max_val>oppsite_max_val

def test():
    cards = ['C2', 'S3', 'S2', 'S4', 'H3']
    hand = [card2id(card) for card in cards]
    lookup_table = read_lookup_table()
    print(lookup_table[encoding(hand)])
    cnt = 0
    while (True):
        cnt += 1
        hand = random.sample(range(52), 7)
        print([id2card(x) for x in hand])
        # value = lookup_table[encoding(hand)] / LENGTH
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
