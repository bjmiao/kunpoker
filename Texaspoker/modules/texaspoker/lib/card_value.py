import random
from itertools import combinations
import time

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
        level = (9, 12)   # royal flush straight
    elif (is_flush and is_straight):
        level = (8, [straight_max])   # flush straight
    elif (card_type[0][0] == 4):
        level = (7, [card_type[0][1], ])  # 4 of one
    elif (card_type[0][0] == 3 and card_type[1][0] == 2):
        level = (6, [card_type[0][1], ])   # full house
    elif (is_flush):
        level = (5, [x[1] for x in card_type])   # flush
    elif (is_straight):
        level = (4, straight_max)  # straight
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

def encoding(card):
    # for card in cards:
    a = 0 ^ (1 << card[0]) ^ (1 << card[1]) ^ (1 << card[2]) ^ (1 << card[3]) ^ (1 << card[4])
    # print(type(a))
    return a

if __name__ == "__main__":
    # card_list = [0, 3, 6, 10, 20, 30, 40]
    # hand = Hand(card_list)
    # print(hand)

    cards = ['S2', 'S3', 'S4', 'S5', 'SA']
    card_list = [card2id(card) for card in cards]
    # print(card_list)
    # start = time.time()
    e = encoding(card_list)
    # print(e)
    # for _ in range(1000):
    #     encoding(card_list)
    # end = time.time()
    # print(end - start,'s')

    cards = ['C2', 'S3', 'S2', 'S4', 'H3']
    card_list = [card2id(card) for card in cards]
    # print(card_list)
    # e = encoding(card_list)
    # print(e)
    # start = time.time()
    # for _ in range(1000):
    #     encoding(card_list)
    # end = time.time()
    # print(end - start,'s')

    index = 0
    lookup_table = {}
    level_table = [[] for _ in range(9)]
    for cards in combinations(range(52), 5):
        # print('===')
        # print(cards)
        # print([id2card(i) for i in cards])
        # print(encoding(cards), judge_card_level(cards))

        (level, desc) = judge_card_level(cards)
        # print('!!!')
        # print(level, desc)

        level_table[level].append((encoding(cards), (level,desc) ))
        index += 1
        if (index % 10000 == 0):
            print(index)
        #     break
    for idx in range(len(level_table)):
        print(len(level_table[idx]))
    # print(level_table)
    # print(lookup_table)
    # l1 = judge_card_level(cards)
    # cards = ['S9', 'S7', 'ST', 'S8', 'S6']
    # l2 = judge_card_level(cards)
    # print(compare_level(l1, l2))
    # # cards = ['SQ', 'SK', 'SJ', 'S9', 'ST']
    # # judge_card_level(cards)
    # # cards = ['HA', 'H3', 'H8', 'H5', 'H4']
    # # judge_card_level(cards)
    # # cards = ['S5', 'D3', 'C4', 'S6', 'D2']
    # # judge_card_level(cards)
    # # cards = ['ST', 'DT', 'C9', 'S8', 'S9']
    # # judge_card_level(cards)
    # # cards = ['ST', 'DT', 'C9', 'ST', 'S9']
    # # judge_card_level(cards)
    # # cards = ['ST', 'DT', 'CA', 'S8', 'S9']
    # # judge_card_level(cards)
    # # cards = ['ST', 'DT', 'CT', 'S8', 'S9']
    # # judge_card_level(cards)
    # # cards = ['ST', 'DT', 'CT', 'ST', 'S9']
    # # judge_card_level(cards)
    # # cards = ['SA', 'D3', 'C6', 'S8', 'S9']
    # # judge_card_level(cards)
