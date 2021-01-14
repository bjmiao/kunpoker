import pickle
import random
from card_value import encoding, card2id, id2card
with open("lookup_table.pkl", "rb") as f:
    lookup_table = pickle.load(f)

cards = ['C2', 'S3', 'S2', 'S4', 'H3']
hand = [card2id(card) for card in cards]
 
print(lookup_table[encoding(hand)])

LENGTH = 2598960
cnt = 0
while (True):
    cnt += 1
    hand = random.sample(range(52), 5)
    print([id2card(x) for x in hand])
    value = lookup_table[encoding(hand)] / LENGTH
    print("Level:", lookup_table[encoding(hand)] / LENGTH)
    if (value > 0.99):
        print("Count = ", cnt)
        input()
