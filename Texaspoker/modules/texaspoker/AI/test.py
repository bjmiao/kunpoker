'''
Author: zgong
Date: 2021-01-11 21:54:45
LastEditors: zgong
LastEditTime: 2021-01-12 19:44:08
'''

from modules.texaspoker.lib.client_lib import State
from modules.texaspoker.lib.client_lib import Player
from modules.texaspoker.lib.client_lib import Hand
from modules.texaspoker.lib.client_lib import Decision
import random

import matplotlib.pyplot as plt
import numpy as np

def sigmoid(inx):
    if inx>=0:
        return 1.0/(1+np.exp(-inx))
    else:
        return np.exp(inx)/(1+np.exp(inx))

win_rate = 0.7

totalbet = 1000
call = 200 

expect_call = win_rate*(totalbet+call)+(1-win_rate)*(-call)

# x = []
# y = []
# break_point = (1-win_rate)/(2*win_rate-1)*(totalbet+2*call)

# for alpha in range(200):
#     alpha = 20*alpha
#     fold_rate = sigmoid((alpha-break_point)/20)
#     expect_raise = fold_rate*(totalbet+call)+(1-fold_rate)*(win_rate*(totalbet+call+alpha)+(1-win_rate)*(-call-alpha))
#     x.append(alpha)
#     y.append(expect_raise)


cards = list(range(0, 52))
cnt = [0 for col in range(11)]
# 模拟发牌100000次, TODO:模拟胜率
for i in range(100000):
    heap = cards[:]
    mycards = []
    random.shuffle(heap)
    while len(mycards) != 7:
        mycards.append(heap.pop())
    hand = Hand(mycards)
    level = hand.level
    cnt[level] += 1
