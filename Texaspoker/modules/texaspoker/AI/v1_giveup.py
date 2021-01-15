'''
    AI: v1_1版本
    详见AI-v1.1_interpretation.txt
'''
from lib.client_lib import State
from lib.client_lib import Player
from lib.client_lib import Hand
from lib.client_lib import Decision
import random

def ai(id, state):
    decision = Decision()
    print(state)
    print(id)
    cards = state.sharedcards + state.player[id].cards
    remain_cards = list(range(0, 52))
    for x in cards:
        remain_cards.remove(x)
    
    decision.giveup = 1
    return decision
