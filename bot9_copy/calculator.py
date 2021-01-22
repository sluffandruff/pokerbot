import eval7
import time

ALL_HANDS = eval7.HandRange("22+, A2+, K2+, Q2+, J2+, T2+, 92+, 82+, 72+, 62+, 52+, 42+, 32+")

# def generate_all_flops(){

# }

start = time.time()
board = {eval7.Card("7h"), eval7.Card("Js"), eval7.Card("Ad"), eval7.Card("As"), eval7.Card("2s")}
rnge = [h for h in ALL_HANDS if h[0][0] not in board and h[0][1] not in board]

hand_to_equity = eval7.py_all_hands_vs_range(rnge, rnge, board, 100)
sorted_hands = [(k,1.0) for k, v in sorted(hand_to_equity.items(), key=lambda item: item[1], reverse=True)]

PERCENT = 0.5
opp_range = sorted_hands[:round(PERCENT*len(sorted_hands))]

my_cards = [eval7.Card("Jh"), eval7.Card("Ah")]
print(eval7.py_hand_vs_range_monte_carlo(my_cards, opp_range, board, 100))
# print(opp_range)
print(time.time()-start)