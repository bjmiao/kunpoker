import random
from itertools import combinations
import functools
from pathlib import Path
import time
import pickle

COLOR = ['C', 'D', 'H', 'S']
NUM = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
def id2card(card_id):
    color = id2color(card_id)
    num = id2num(card_id)
    return (COLOR[color]+NUM[num])

def card2id(card):
    color = card[0]
    num = card[1]
    return NUM.index(num) * 4 + COLOR.index(color)

def aka_pair(cards_id):
    assert(len(cards_id)==2)
    colors = [id2color(card) for card in cards_id]
    nums = sorted([id2num(card) for card in cards_id],reverse=True)
    aka = f'{NUM[nums[0]]}{NUM[nums[1]]}'
    if nums[0] == nums[1]:
        return aka+'p'
    if colors[0] == colors[1]:    
        return aka+'s'
    else:
        return aka+'o'
    

# alter the card id into color
def id2color(card):
    return card % 4

# alter the card id into number
def id2num(card):
    return card // 4


def judge_exist(x):
    if x >= 1:
        return True
    return False

# poker hand of 7 card
# class Hand(object):
    # def __init__(self, cards):
    #     cards = cards[:]
    #     self.level = 0
    #     self.cnt_num = [0] * 13
    #     self.cnt_color = [0] * 4
    #     self.cnt_num_eachcolor = [[0 for col in range(13)] for row in range(4)]
    #     self.maxnum = -1
    #     self.single = []
    #     self.pair = []
    #     self.tripple = []
    #     self.nums = []
    #     for x in cards:
    #         self.cnt_num[id2num(x)] += 1
    #         self.cnt_color[id2color(x)] += 1
    #         self.cnt_num_eachcolor[id2color(x)][id2num(x)] += 1
    #         self.nums.append(id2num(x))

    #     self.judge_num_eachcolor = [[] for i in range(4)]

    #     for i in range(4):
    #         self.judge_num_eachcolor[i] = list(map(judge_exist, self.cnt_num_eachcolor[i]))


    #     self.nums.sort(reverse=True)
    #     for i in range(12, -1, -1):
    #         if self.cnt_num[i] == 1:
    #             self.single.append(i)
    #         elif self.cnt_num[i] == 2:
    #             self.pair.append(i)
    #         elif self.cnt_num[i] == 3:
    #             self.tripple.append(i)
    #     self.single.sort(reverse=True)
    #     self.pair.sort(reverse=True)
    #     self.tripple.sort(reverse=True)

def judge_card_level(card_list):
    # card_list = [card2id(card) for card in card_list]
    num_list = [id2num(c) for c in card_list]

    cnt_num = [0] * 13
    cnt_color = [0] * 4
    for card in card_list:
        cnt_num[id2num(card)] += 1
        cnt_color[id2color(card)] += 1

    max_num_cnt = max(cnt_num)
    max_color_cnt = max(cnt_color)
    is_flush = True if (max_color_cnt == 5) else False  # TongHua
    is_straight = False
    straight_max = -1
    if (cnt_num[12] == 1 and cnt_num[0] == 1 and cnt_num[1] == 1
            and cnt_num[2] == 1 and cnt_num[3] == 1):  # A2345
        is_straight = True
        straight_max = 3
    elif (max_num_cnt == 1 and (max(num_list) - min(num_list)) == 4):
        is_straight = True
        straight_max = max(num_list)
    # print("is_flush", is_flush)
    # print("is_straight", is_straight, straight_max)

    # print(cnt_num)
    num_count = {}
    for i in range(len(cnt_num)):
        if cnt_num[i] != 0:
            num_count[i] = cnt_num[i]
    # print(num_count)
    card_type = [(v, k) for k, v in num_count.items()]
    card_type = sorted(card_type, key=lambda x: x[0]*52+x[1], reverse=True)
    # print(card_type)
    # ['ST', 'DT', 'C9', 'S8', 'S9'] -> [(2, 8/"T"), (2, 7/"9"), (1, 6/"8")]

    level = -1
    if (is_flush and is_straight and straight_max == 12):
        level = (9, [12])   # royal flush straight
    elif (is_flush and is_straight):
        level = (8, [straight_max])   # flush straight
    elif (card_type[0][0] == 4):
        level = (7, [x[1] for x in card_type])  # 4 of one
    elif (card_type[0][0] == 3 and card_type[1][0] == 2):
        level = (6, [x[1] for x in card_type])   # full house
    elif (is_flush):
        level = (5, [x[1] for x in card_type])   # flush
    elif (is_straight):
        level = (4, [straight_max])  # straight
    elif (card_type[0][0] == 3 and card_type[1][0] == 1):
        level = (3, [x[1] for x in card_type])  # 3 of one
    elif (card_type[0][0] == 2 and card_type[1][0] == 2):
        level = (2, [x[1] for x in card_type])
    elif (card_type[0][0] == 2 and card_type[1][0] == 1):
        level = (1, [x[1] for x in card_type])
    elif (card_type[0][0] == 1):
        level = (0, [x[1] for x in card_type])

    # print(level)
    return level


def select_largest(all_cards, lookup_table):
    '''
    select the largest from 5, 6 or 7 cards
    
    '''
    if len(all_cards) < 5:
        raise ValueError("Cards number is less then 5")
    max_val = -1
    max_val_hand = None
    for hand in combinations(all_cards, 5):
        hand = sorted(hand)
        val = lookup_table[card_encoding_5(hand)]
        if val > max_val:
            max_val = val
            max_val_hand = hand
    return max_val_hand, max_val


def read_lookup_table(filename="lookup_table.pkl"):
    ''' read the look up table. That'''

    with open(Path(__file__).parent/filename, "rb") as f:
        lookup_table = pickle.load(f)
    return lookup_table


def compare_level(l1, l2):
    if (l1[0] < l2[0]):
        return -1
    if (l1[0] > l2[0]):
        return 1
    for c1, c2 in zip(l1[1], l2[1]):
        if (c1 < c2):
            return -1
        if (c1 > c2):
            return -1
    return 0

def card_encoding_2(card):
    a = (1 << card[0]) | (1 << card[1])
    return a

def card_encoding_5(card):
    # a = 0
    # for card in cards:
    a =  (1 << card[0]) | (1 << card[1]) | (1 << card[2]) | (1 << card[3]) | (1 << card[4])
    return a


def generate_hand_strength_lookup_table():
    index = 0
    level_table = [[] for _ in range(10)]
    for cards in combinations(range(52), 5):
        cards = sorted(cards)
        # print('===')
        # print(cards)
        # print([id2card(i) for i in cards])
        (level, desc) = judge_card_level(cards)
        # print('!!!')
        # print(level, desc)
        level_table[level].append((card_encoding_5(cards), (level, desc) ))
        index += 1
        if (index % 10000 == 0):
            print(index)
        # if index == 100000:
        #     break

    strength_table_in_level = []

    last_hand_strength = level_table[0][0]
    print(last_hand_strength)
    idx_cnt = 0
    level_cnt = 0
    for idx in range(len(level_table)):
        level_table[idx] = sorted(level_table[idx], key=functools.cmp_to_key(compare_level))
        print(idx, len(level_table[idx]))

        for (hand_id, hand) in level_table[idx]:
            if compare_level(hand, last_hand_strength) != 0:
                level_cnt = idx_cnt
                last_hand_strength = hand
            strength_table_in_level.append((hand_id, level_cnt))
            idx_cnt += 1
    total_len = len(strength_table_in_level)
    print(len(strength_table_in_level))
    print(strength_table_in_level[-1][-1]/total_len)

    lookup_table = {x[0]: x[1] for x in strength_table_in_level}

    with open("lookup_table.pkl", "wb") as f:
        pickle.dump(lookup_table, f)

def generate_2v2_table():
    ''' To generate a 2v2 table.
    It can show that at the beginning,
        the winning expctation of each two pairs (AA v.s. KK) 
    '''
    LOOKUP_TABLE = read_lookup_table()
    expectation_table = {}

    for _ in range(1):
        cards = random.sample(range(52), 4)
        my_card = [cards[0], cards[1]]
        other_card = [cards[2], cards[3]]

        my_card_idx = card_encoding_2(my_card)
        other_card_idx = card_encoding_2(other_card)

        print([id2card(x) for x in my_card], my_card_idx)
        print([id2card(x) for x in other_card], other_card_idx)

        if my_card_idx > other_card_idx:
            continue

        if (my_card_idx, other_card_idx) in expectation_table.keys():
            continue
   
        deck = list(range(52))
        for card in cards:
            deck.remove(card)
    
        winning, loss, tie = 0, 0, 0
        cnt = 0

        # for cnt in range(100000):
        for shared_card in combinations(deck, 5):
            # shared_card = random.sample(deck, 5)
            my_largest_hand, my_value = select_largest([*shared_card, *my_card], LOOKUP_TABLE)
            other_largest_hand, other_value = select_largest([*shared_card, *other_card], LOOKUP_TABLE)
            
            # print([id2card(x) for x in shared_card])
            if (my_value > other_value):
                winning += 1
            elif (my_value < other_value):
                loss += 1
            elif (my_value == other_value):
                tie += 1
            cnt += 1
            if (cnt % 100000 == 0):
                print(cnt)
            # if (cnt == 100000):
                # break

        expectation = (winning * 2 + tie) / (winning + loss + tie) / 2 
        # expectation \in [0, 1]. 1 means must win. 0 means must lose.
        # 0.5 means that it will win have of the pot
        print(winning, loss, tie)
        print(winning/cnt, loss/cnt, tie/cnt)
        expectation_table[(my_card_idx, other_card_idx)] = expectation

    print(expectation_table)
    with open("2v2_table.pkl", "wb"):
        pass

if __name__ == "__main__":
    # generate_hand_strength_lookup_table()

    generate_2v2_table()
