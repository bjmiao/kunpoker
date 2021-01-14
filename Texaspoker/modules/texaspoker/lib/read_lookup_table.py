import pickle
import random
from itertools import combinations
from card_value import encoding, card2id, id2card

LENGTH = 2598960

def read_lookup_table():
    with open("lookup_table.pkl", "rb") as f:
        lookup_table = pickle.load(f)
    return lookup_table

def select_largest(all_cards, lookup_table):
    if len(all_cards) < 5:
        raise ValueError("Cards number is less then 5")
    max_val = -1
    max_val_hand = None
    for hand in combinations(all_cards, 5):
        val = lookup_table[encoding(hand)]
        if val > max_val:
            max_val = val
            max_val_hand = hand
    return max_val_hand, max_val / LENGTH

if __name__ == "__main__":
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