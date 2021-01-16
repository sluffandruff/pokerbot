import eval7

SLANSKY_KARLSON = ['AA', 'KK', 'AKs', 'QQ', 'AKo', 'JJ', 'AQs', 'TT', 'AQo', '99', 'AJs', '88', 'ATs', 'AJo', 
                    '77', '66', 'ATo', 'A9s', '55', 'A8s', 'KQs', '44', 'A9o', 'A7s', 'KJs', 'A5s', 'A8o', 
                    'A6s', 'A4s', '33', 'KTs', 'A7o', 'A3s', 'KQo', 'A2s', 'A5o', 'A6o', 'A4o', 'KJo', 'QJs', 
                    'A3o', '22', 'K9s', 'A2o', 'KTo', 'QTs', 'K8s', 'K7s', 'JTs', 'K9o', 'K6s', 'QJo', 'Q9s', 
                    'K5s', 'K8o', 'K4s', 'QTo', 'K7o', 'K3s', 'K2s', 'Q8s', 'K6o', 'J9s', 'K5o', 'Q9o', 'JTo', 
                    'K4o', 'Q7s', 'T9s', 'Q6s', 'K3o', 'J8s', 'Q5s', 'K2o', 'Q8o', 'Q4s', 'J9o', 'Q3s', 'T8s', 
                    'J7s', 'Q7o', 'Q2s', 'Q6o', '98s', 'Q5o', 'J8o', 'T9o', 'J6s', 'T7s', 'J5s', 'Q4o', 'J4s', 
                    'J7o', 'Q3o', '97s', 'T8o', 'J3s', 'T6s', 'Q2o', 'J2s', '87s', 'J6o', '98o', 'T7o', '96s', 
                    'J5o', 'T5s', 'T4s', '86s', 'J4o', 'T6o', '97o', 'T3s', '76s', '95s', 'J3o', 'T2s', '87o', 
                    '85s', '96o', 'T5o', 'J2o', '75s', '94s', 'T4o', '65s', '86o', '93s', '84s', '95o', 'T3o', 
                    '76o', '92s', '74s', '54s', 'T2o', '85o', '64s', '83s', '94o', '75o', '82s', '73s', '93o', 
                    '65o', '53s', '63s', '84o', '92o', '43s', '74o', '72s', '54o', '64o', '52s', '62s', '83o', 
                    '42s', '82o', '73o', '53o', '63o', '32s', '43o', '72o', '52o', '62o', '42o', '32o']

# NUM_SK = [(6, 'AA'), (12, 'KK'), (16, 'AKs'), (22, 'QQ'), (34, 'AKo'), (40, 'JJ'), (44, 'AQs'), (50, 'TT'), (62, 'AQo'), 
#             (68, '99'), (72, 'AJs'), (78, '88'), (82, 'ATs'), (94, 'AJo'), (100, '77'), (106, '66'), (118, 'ATo'), 
#             (122, 'A9s'), (128, '55'), (132, 'A8s'), (136, 'KQs'), (142, '44'), (154, 'A9o'), (158, 'A7s'), (162, 'KJs'), 
#             (166, 'A5s'), (178, 'A8o'), (182, 'A6s'), (186, 'A4s'), (192, '33'), (196, 'KTs'), (208, 'A7o'), (212, 'A3s'), 
#             (224, 'KQo'), (228, 'A2s'), (240, 'A5o'), (252, 'A6o'), (264, 'A4o'), (276, 'KJo'), (280, 'QJs'), (292, 'A3o'), 
#             (298, '22'), (302, 'K9s'), (314, 'A2o'), (326, 'KTo'), (330, 'QTs'), (334, 'K8s'), (338, 'K7s'), (342, 'JTs'), 
#             (354, 'K9o'), (358, 'K6s'), (370, 'QJo'), (374, 'Q9s'), (378, 'K5s'), (390, 'K8o'), (394, 'K4s'), (406, 'QTo'), 
#             (418, 'K7o'), (422, 'K3s'), (426, 'K2s'), (430, 'Q8s'), (442, 'K6o'), (446, 'J9s'), (458, 'K5o'), (470, 'Q9o'), 
#             (482, 'JTo'), (494, 'K4o'), (498, 'Q7s'), (502, 'T9s'), (506, 'Q6s'), (518, 'K3o'), (522, 'J8s'), (526, 'Q5s'), 
#             (538, 'K2o'), (550, 'Q8o'), (554, 'Q4s'), (566, 'J9o'), (570, 'Q3s'), (574, 'T8s'), (578, 'J7s'), (590, 'Q7o'), 
#             (594, 'Q2s'), (606, 'Q6o'), (610, '98s'), (622, 'Q5o'), (634, 'J8o'), (646, 'T9o'), (650, 'J6s'), (654, 'T7s'), 
#             (658, 'J5s'), (670, 'Q4o'), (674, 'J4s'), (686, 'J7o'), (698, 'Q3o'), (702, '97s'), (714, 'T8o'), (718, 'J3s'), 
#             (722, 'T6s'), (734, 'Q2o'), (738, 'J2s'), (742, '87s'), (754, 'J6o'), (766, '98o'), (778, 'T7o'), (782, '96s'), 
#             (794, 'J5o'), (798, 'T5s'), (802, 'T4s'), (806, '86s'), (818, 'J4o'), (830, 'T6o'), (842, '97o'), (846, 'T3s'), 
#             (850, '76s'), (854, '95s'), (866, 'J3o'), (870, 'T2s'), (882, '87o'), (886, '85s'), (898, '96o'), (910, 'T5o'), 
#             (922, 'J2o'), (926, '75s'), (930, '94s'), (942, 'T4o'), (946, '65s'), (958, '86o'), (962, '93s'), (966, '84s'), 
#             (978, '95o'), (990, 'T3o'), (1002, '76o'), (1006, '92s'), (1010, '74s'), (1014, '54s'), (1026, 'T2o'), 
#             (1038, '85o'), (1042, '64s'), (1046, '83s'), (1058, '94o'), (1070, '75o'), (1074, '82s'), (1078, '73s'), 
#             (1090, '93o'), (1102, '65o'), (1106, '53s'), (1110, '63s'), (1122, '84o'), (1134, '92o'), (1138, '43s'), 
#             (1150, '74o'), (1154, '72s'), (1166, '54o'), (1178, '64o'), (1182, '52s'), (1186, '62s'), (1198, '83o'), 
#             (1202, '42s'), (1214, '82o'), (1226, '73o'), (1238, '53o'), (1250, '63o'), (1254, '32s'), (1266, '43o'), 
#             (1278, '72o'), (1290, '52o'), (1302, '62o'), (1314, '42o'), (1326, '32o')]


ALL_HANDS = eval7.HandRange("22+, A2+, K2+, Q2+, J2+, T2+, 92+, 82+, 72+, 62+, 52+, 42+, 32+")


# def percent_to_range(n):
#     num_hands = round(n * 1326)
#     i = 0
#     range_text = "AA"
#     while num_hands > NUM_SK[i][0]:
#         range_text += "," + NUM_SK[i + 1][1]
#         i += 1
#     # print(range_text)
#     return eval7.HandRange(range_text)

# import pickle
# import time

# start = time.perf_counter()
# ranges = [eval7.HandRange("AA")]
# range_text = "AA"
# for r in SLANSKY_KARLSON:
#     num = len(eval7.HandRange(r))
#     if r != "AA":
#         range_text += "," + r
#     hr = eval7.HandRange(range_text)
#     for i in range(num):
#         ranges.append(hr)
# stop = time.perf_counter()
# print(stop - start)

# start = time.perf_counter()
# ranges = [eval7.HandRange("AA").hands] * 7
# # print(ranges)
# for r in SLANSKY_KARLSON[1:]:
#     # print(r)
#     c = eval7.HandRange(r).hands
#     hr = ranges[-1] + c
#     for i in range(len(c)):
#         ranges.append(hr)
# stop = time.perf_counter()
# print(ranges[1316])
# print(len(ranges))
# print(stop - start)

# with open("ranges.pkl", "wb") as f:
#     pickle.dump(ranges, f)

# print(ranges[1326])


# my_cards = ["As", "Ac", "Ks", "Qs", "Kc", "Js"]

# my_cards_obj = [eval7.Card(c) for c in my_cards]
# opp_range = ALL_HANDS.hands
# opp_range = [hand for hand in opp_range if hand[0][0] not in my_cards_obj and hand[0][1] not in my_cards_obj]
# print(len(opp_range))

# equities = {}
# for i in range(5):
#     for j in range(i + 1, 6):
#         hand = (my_cards[i], my_cards[j])
#         equities[hand] = eval7.py_hand_vs_range_monte_carlo(map(eval7.Card, hand), opp_range, [], 10000)

# dis = [(0, 1, 2, 3, 4, 5), (0, 1, 2, 4, 3, 5), (0, 1, 2, 5, 3, 4), 
#         (0, 2, 1, 3, 4, 5), (0, 2, 1, 4, 3, 5), (0, 2, 1, 5, 3, 4), 
#         (0, 3, 1, 2, 4, 5), (0, 3, 1, 4, 2, 5), (0, 3, 1, 5, 2, 4), 
#         (0, 4, 1, 2, 3, 5), (0, 4, 1, 3, 2, 5), (0, 4, 1, 5, 2, 3), 
#         (0, 5, 1, 2, 3, 4), (0, 5, 1, 3, 2, 4), (0, 5, 1, 4, 2, 3)]

# best_value = 0
# best_alloc = []
# best_eq = []
# for d in dis:
#     eq = []
#     for i in range(3):
#         hand = (my_cards[d[2*i]], my_cards[d[2*i + 1]])
#         eq.append((equities[hand], hand))
#     eq.sort()
#     value = 1 * eq[0][0] + 2 * eq[1][0] + 3 * eq[2][0]
#     if value > best_value:
#         best_value = value
#         best_alloc = [eq[i][1] for i in range(3)]
#         best_eq = [eq[i][0] for i in range(3)]

# print(best_value, best_alloc, best_eq)



# hole = ("As","Ac")
# hole_cards = [eval7.Card(card) for card in hole] 

# all_hands = "22+, A2+, K2+, Q2+, J2+, T2+, 92+, 82+, 72+, 62+, 52+, 42+, 32+"
# print(len(eval7.HandRange(all_hands)))

# print(eval7.py_hand_vs_range_exact(hole_cards, eval7.HandRange(all_hands), []))

# test = [((eval7.Card("Ac"), eval7.Card("Qc")), 1.0),
#         ((eval7.Card("Ad"), eval7.Card("Qd")), 1.0),
#         ((eval7.Card("Ah"), eval7.Card("Qh")), 1.0),
#         ((eval7.Card("As"), eval7.Card("Qs")), 1.0),
#         ((eval7.Card("Ac"), eval7.Card("Kc")), 1.0),
#         ((eval7.Card("Ad"), eval7.Card("Kd")), 1.0),
#         ((eval7.Card("Ah"), eval7.Card("Kh")), 1.0),
#         ((eval7.Card("As"), eval7.Card("Ks")), 1.0),
#         ((eval7.Card("As"), eval7.Card("Ks")), 0.4)]

# def pot_odds(pot, call_size):
#     return call_size / (pot + call_size)
#     # implied pot odds, etc.?


# def equity(my_hand, range, board):
#     # 0.0-1.0
#     # Monte Carlo
#     pass

# def calculate_range():
#     pass

# class WeightedRange():
    
#     def __init__(self):
#         pass

# class OpponentStats():

#     def __init__(self):
#         self.vpip = 0.0
#         self.pfr = 0.0
#         self.threeb = 0.0


# allocate based on initial equity, better hands on bigger blinds?, maximize return (calculation?)
# each round, calculate opp range based on stats and check if pot odds < equity to call 
# when to raise?