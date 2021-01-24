'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction, AssignAction
from skeleton.states import GameState, TerminalState, RoundState, BoardState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND, NUM_BOARDS
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot

import eval7
import random
from util import *

PF_CALL_RAISE = 0
PF_RAISE = 1
CALL_RAISE = 2
RAISE = 3


class Player(Bot):
    '''
    A pokerbot.
    '''

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        Nothing.

        Returns:
        Nothing.
        ''' 
        self.board_allocations = [[], [], []] #keep track of our allocations at round start
        self.equity = [0, 0, 0] #better representation of our hole strengths (win probability!)
        self.street_tracker = -1

        # self.opp_walks = [0, 0, 0] # SB folds
        # self.opp_vpip = [0, 0, 0] # times
        # self.opp_pfr = [0, 0, 0]
        # self.opp_vpip_round = [0, 0, 0] # 0 or 1 
        # self.opp_pfr_round = [0, 0, 0]

        # self.opp_walks_total = 0
        # self.opp_vpip_total = 0
        # self.opp_pfr_total = 0

        self.action_counter = [0, 0, 0, 0]
        self.action_probs = [0.0, 0.0, 0.0, 0.0]
        self.postflop_chances = 0

        self.stop_bluffing = False
        self.just_bluffed = False
        self.board_bluffed = -1
        self.times_called_bluff = 0
        self.times_bluff_succeeded = 0

        self.pf_tightness = 0.8
        self.tightness = 0.85

        self.total_times_all_in = 0
        self.times_all_in_this_rd = 0

        self.fold_rest = False

        self.initiate_destroy_hot_pott = False

        self.ranges = [eval7.HandRange("AA").hands] * 7
        for r in SLANSKY_KARLSON[1:]:
            c = eval7.HandRange(r).hands
            hr = self.ranges[-1] + c
            for i in range(len(c)):
                self.ranges.append(hr)


    def allocate_cards(self, my_cards):
        '''
        Method that allocates our cards at the beginning of a round. Method
        modifies self.board_allocations. The method attempts to make pairs
        by allocating hole cards that share a rank if possible. The exact
        stack these cards are allocated to is not defined.

        Arguments:
        my_cards: a list of the 6 cards given to us at round start
        '''
        my_cards_obj = {eval7.Card(c) for c in my_cards}
        opp_range = {hand for hand in ALL_HANDS.hands if hand[0][0] not in my_cards_obj and hand[0][1] not in my_cards_obj}
        self.opp_range = [opp_range.copy()] * 3

        opp_range_incl = set(ALL_HANDS.hands)
        self.opp_est_of_range = [opp_range_incl.copy()] * 3
        self.prev_opp_est_of_range = [{}] * 3

        equities = {}
        for i in range(5):
            for j in range(i + 1, 6):
                hand = (my_cards[i], my_cards[j])
                equities[hand] = eval7.py_hand_vs_range_monte_carlo(map(eval7.Card, hand), opp_range, [], 3000)

        dis = [(0, 1, 2, 3, 4, 5), (0, 1, 2, 4, 3, 5), (0, 1, 2, 5, 3, 4), 
                (0, 2, 1, 3, 4, 5), (0, 2, 1, 4, 3, 5), (0, 2, 1, 5, 3, 4), 
                (0, 3, 1, 2, 4, 5), (0, 3, 1, 4, 2, 5), (0, 3, 1, 5, 2, 4), 
                (0, 4, 1, 2, 3, 5), (0, 4, 1, 3, 2, 5), (0, 4, 1, 5, 2, 3), 
                (0, 5, 1, 2, 3, 4), (0, 5, 1, 3, 2, 4), (0, 5, 1, 4, 2, 3)]

        best_value = 0
        best_alloc = []
        best_eq = []
        for d in dis:
            eq = []
            for i in range(3):
                hand = (my_cards[d[2*i]], my_cards[d[2*i + 1]])
                eq.append((equities[hand], hand))
            eq.sort()
            value = 1 * eq[0][0] + 2 * eq[1][0] + 3 * eq[2][0]
            if value > best_value:
                best_value = value
                best_alloc = [eq[i][1] for i in range(3)]
                best_eq = [eq[i][0] for i in range(3)]

        ####
        if not self.initiate_destroy_hot_pott:
            self.strongest_board = 2
            if random.random() < 0.3:
                best_alloc[2], best_alloc[1] = best_alloc[1], best_alloc[2]
                best_eq[2], best_eq[1] = best_eq[1], best_eq[2]
                self.strongest_board = 1
                if random.random() < 0.35:
                    self.strongest_board = 0
                    best_alloc[0], best_alloc[1] = best_alloc[1], best_alloc[0]
                    best_eq[0], best_eq[1] = best_eq[1], best_eq[0]
        else:
            self.strongest_board = 2
            if random.random() < 0.5:
                best_alloc[2], best_alloc[1] = best_alloc[1], best_alloc[2]
                best_eq[2], best_eq[1] = best_eq[1], best_eq[2]
                self.strongest_board = 1
                if random.random() < 0.5:
                    self.strongest_board = 0
                    best_alloc[0], best_alloc[1] = best_alloc[1], best_alloc[0]
                    best_eq[0], best_eq[1] = best_eq[1], best_eq[0]
        ####

        self.my_cards_obj = [{eval7.Card(c) for c in hand} for hand in best_alloc]

        self.board_allocations = best_alloc
        self.equity = best_eq


    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        opp_bankroll = game_state.opp_bankroll # ^but for your opponent
        game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        my_cards = round_state.hands[active]  # your six cards at the start of the round
        big_blind = bool(active)  # True if you are the big blind

        rounds_left = NUM_ROUNDS - round_num + 1
        will_lose = rounds_left * 21 + (rounds_left % 2) * (3 if big_blind else -3)
        if my_bankroll - opp_bankroll > will_lose:
            self.fold_rest = True
            print("SEALED WIN ON RD", round_num)
        
        self.just_raised = [(False, -1)] * 3
        self.action_determined = [False, False, False]
        self.rd_board = [{}, {}, {}]
        self.my_cards_obj = [None, None, None]
        self.allocate_cards(my_cards)
        self.pf_call_raise_already = [False, False, False]


    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        opp_delta = terminal_state.deltas[1-active] # your opponent's bankroll change from this round 
        previous_state = terminal_state.previous_state  # RoundState before payoffs
        street = previous_state.street  # 0, 3, 4, or 5 representing when this round ended
        for i, terminal_board_state in enumerate(previous_state.board_states):
            previous_board_state = terminal_board_state.previous_state
            my_cards = previous_board_state.hands[active]  # your cards
            opp_cards = previous_board_state.hands[1-active]  # opponent's cards or [] if not revealed
            if self.just_bluffed and i == self.board_bluffed:
                self.just_bluffed = False
                if opp_cards[0] != '':
                    print("BLUFF CALLED")
                    self.times_called_bluff += 1
                else:
                    self.times_bluff_succeeded += 1
                    print("BLUFF SUCCEEDED")
        
        self.board_allocations = [[], [], []] #reset our variables at the end of every round!
        self.equity = [0, 0, 0]
        self.street_tracker = 0

        # for i in range(NUM_BOARDS):
        #     self.opp_vpip[i] += self.opp_vpip_round[i]
        #     self.opp_pfr[i] += self.opp_pfr_round[i]
        #     self.opp_vpip_total += self.opp_vpip_round[i]
        #     self.opp_pfr_total += self.opp_pfr_round[i]
        #     self.opp_vpip_round[i] = 0
        #     self.opp_pfr_round[i] = 0

        self.action_probs[PF_CALL_RAISE] = self.action_counter[PF_CALL_RAISE] / (3 * game_state.round_num)
        self.action_probs[PF_RAISE] = self.action_counter[PF_RAISE] / (3 * game_state.round_num)
        if self.postflop_chances > 0:
            self.action_probs[CALL_RAISE] = self.action_counter[CALL_RAISE] / self.postflop_chances
            self.action_probs[RAISE] = self.action_counter[RAISE] / self.postflop_chances
        # print(self.opp_vpip, self.opp_pfr)
        print("**", self.action_probs, "**")

        self.total_times_all_in += self.times_all_in_this_rd
        self.times_all_in_this_rd = 0

        game_clock = game_state.game_clock #check how much time we have remaining at the end of a game
        round_num = game_state.round_num #Monte Carlo takes a lot of time, we use this to adjust!

        if round_num == 50:
            self.bankrolls_at_50 = (game_state.bankroll, game_state.opp_bankroll)
            if not self.initiate_destroy_hot_pott:
                self.pf_tightness = 0.75
                self.tightness = 0.6

        # print(round_num, game_clock)
        if round_num == NUM_ROUNDS:
            print(game_clock)
            print("At rd 50:", self.bankrolls_at_50)
        

    def get_actions(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the engine needs a triplet of actions from your bot.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Your actions.
        '''
        legal_actions = round_state.legal_actions()  # the actions you are allowed to take
        street = round_state.street  # 0, 3, 4, or 5 representing pre-flop, flop, turn, or river respectively
        my_cards = round_state.hands[active]  # your cards across all boards
        board_cards = [board_state.deck if isinstance(board_state, BoardState) else board_state.previous_state.deck for board_state in round_state.board_states] #the board cards
        my_pips = [board_state.pips[active] if isinstance(board_state, BoardState) else 0 for board_state in round_state.board_states] # the number of chips you have contributed to the pot on each board this round of betting
        opp_pips = [board_state.pips[1-active] if isinstance(board_state, BoardState) else 0 for board_state in round_state.board_states] # the number of chips your opponent has contributed to the pot on each board this round of betting
        continue_cost = [opp_pips[i] - my_pips[i] for i in range(NUM_BOARDS)] #the number of chips needed to stay in each board's pot
        my_stack = round_state.stacks[active]  # the number of chips you have remaining
        opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
        stacks = [my_stack, opp_stack]
        net_upper_raise_bound = round_state.raise_bounds()[1] # max raise across 3 boards
        net_cost = 0 # keep track of the net additional amount you are spending across boards this round

        my_actions = [None] * NUM_BOARDS

        if street != self.street_tracker:
            self.action_determined = [False, False, False]

        for i in range(NUM_BOARDS):
            ###########################
            ### game is already won ###
            ###########################
            if self.fold_rest:
                if AssignAction in legal_actions[i]:
                    cards = self.board_allocations[i]
                    my_actions[i] = AssignAction(cards)
                elif CheckAction in legal_actions[i]:
                    my_actions[i] = CheckAction()
                else:
                    my_actions[i] = FoldAction()
                continue
            ###########################

            board_state = round_state.board_states[i]

            if AssignAction in legal_actions[i]:
                cards = self.board_allocations[i]
                my_actions[i] = AssignAction(cards)
            elif isinstance(board_state, TerminalState):
                my_actions[i] = CheckAction()
            else:
                cont_cost = continue_cost[i]
                init_pot = board_state.pot
                pot = my_pips[i] + opp_pips[i] + init_pot
                min_raise, max_raise = board_state.raise_bounds(active, round_state.stacks)

                ########################
                ### beating hot pott ###
                ########################
                if street < 3 and cont_cost > 120:
                    self.times_all_in_this_rd = 1
                    if game_state.round_num > 10 and self.total_times_all_in / game_state.round_num > 0.6:
                        print("HOT-POTT DETECTED")
                        self.initiate_destroy_hot_pott = True
                        self.pf_tightness = 0.7
                        self.tightness = 0.7
                    # else:
                    #     self.initiate_destroy_hot_pott = False
                    #     self.tightness = 0.8
                    #     print("False")

                if self.initiate_destroy_hot_pott:
                    strength = self.equity[i]
                    if street <= 3 and 60 < cont_cost < 70 and all(60<c<70 for c in continue_cost):
                        if strength > 0.57 and all(strength >= s for s in self.equity):
                            if CallAction in legal_actions[i] and cont_cost <= my_stack - net_cost:
                                my_actions[i] = CallAction()
                                net_cost += cont_cost
                                continue
                            else:
                                my_actions[i] = FoldAction()
                                continue
                    elif street == 0 and cont_cost > 100:
                        if strength > 0.75:
                            if CallAction in legal_actions[i] and cont_cost <= my_stack - net_cost:
                                my_actions[i] = CallAction()
                                net_cost += cont_cost
                                continue
                            else:
                                my_actions[i] = FoldAction()
                                continue
                    else:
                        if 0 < cont_cost <= 10:
                            if strength > 0.57:
                                if CallAction in legal_actions[i] and cont_cost <= my_stack - net_cost:
                                    my_actions[i] = CallAction()
                                    net_cost += cont_cost
                                    continue
                                else:
                                    my_actions[i] = FoldAction()
                                    continue
                        if cont_cost == 0:
                            if RaiseAction in legal_actions[i]:
                                if strength > 0.57 and all(strength >= s for s in self.equity):
                                    raise_amount = min_raise
                                    if raise_amount - my_pips[i] <= my_stack - net_cost:
                                        my_actions[i] = RaiseAction(raise_amount)
                                        net_cost += raise_amount - my_pips[i]
                                        continue
                # ########################

                # recalc = False
                # if street < 3:
                #     if active == 0: # the opp is bb
                #         if opp_pips[i] > 2: # opp has voluntarily put chips in (responding to our raise / raising after limp)
                #             if self.opp_vpip_round[i] == 0:
                #                 recalc = True
                #             self.opp_vpip_round[i] = 1
                #             if cont_cost > 0: # opp has raised in response to our raise / raised after limp
                #                 if self.opp_pfr_round[i] == 0:
                #                     recalc = True
                #                 self.opp_pfr_round[i] = 1
                #     else: # the opp is sb
                #         if opp_pips[i] > 1:
                #             if self.opp_vpip_round[i] == 0:
                #                 recalc = True
                #             self.opp_vpip_round[i] = 1
                #         if cont_cost > 0: # opp has raised
                #             if self.opp_pfr_round[i] == 0:
                #                 recalc = True
                #             self.opp_pfr_round[i] = 1
                            
                # if street == 3 and active == 0: # opp is bb, made it to the flop (neither of us folded)
                #     if cont_cost > 0 and my_pips[i] == 0: # opp has made a cbet
                #         self.opp_vpip_round[i] = 1

                ##################
                
                if street != self.street_tracker:
                    if street == 3:
                        self.rd_board[i] = {eval7.Card(c) for c in board_cards[i][:3]}
                        self.prev_opp_est_of_range[i] = self.opp_est_of_range[i]
                        self.opp_est_of_range[i] = {h for h in self.opp_est_of_range[i] if h[0][0] not in self.rd_board[i] and h[0][1] not in self.rd_board[i]}
                    elif street == 4:
                        added_card = eval7.Card(board_cards[i][3])
                        self.rd_board[i].add(added_card)
                        self.prev_opp_est_of_range[i] = self.opp_est_of_range[i]
                        self.opp_est_of_range[i] = {h for h in self.opp_est_of_range[i] if h[0][0] != added_card and h[0][1] != added_card}
                    else:
                        added_card = eval7.Card(board_cards[i][4])
                        self.rd_board[i].add(added_card)
                        self.prev_opp_est_of_range[i] = self.opp_est_of_range[i]
                        self.opp_est_of_range[i] = {h for h in self.opp_est_of_range[i] if h[0][0] != added_card and h[0][1] != added_card}

                if board_state.settled:
                    my_actions[i] = CheckAction()
                    continue

                if street != self.street_tracker and street > 0:
                    self.postflop_chances += 1

                if street == 3 and active == 0 and not self.pf_call_raise_already[i]:
                    if cont_cost > 0 and my_pips[i] == 0:
                        self.action_counter[PF_CALL_RAISE] += 1  # technically have to recompute range here
                        self.pf_call_raise_already[i] = True

                opp_action = None
                if not self.action_determined[i]:
                    if street == 0:  # preflop
                        if active == 0:  # opp is bb
                            if opp_pips[i] > 2:
                                # print("PF_CALL_RAISE")
                                self.pf_call_raise_already[i] = True
                                opp_action = PF_CALL_RAISE
                                self.action_counter[PF_CALL_RAISE] += 1
                                if cont_cost > 0:
                                    # print("PF_RAISE")
                                    opp_action = PF_RAISE
                                    self.action_counter[PF_RAISE] += 1
                        else:  # opp is sb
                            if opp_pips[i] > 1:
                                # print("PF_CALL_RAISE")
                                opp_action = PF_CALL_RAISE
                                self.pf_call_raise_already[i] = True
                                self.action_counter[PF_CALL_RAISE] += 1
                                if cont_cost > 0:
                                    # print("PF_RAISE")
                                    opp_action = PF_RAISE
                                    self.action_counter[PF_RAISE] += 1
                    else:  # flop/turn/river
                        if self.just_raised[i][0] and self.just_raised[i][1] != street:  # (raised, street raised on)
                            if street == 3 and not self.pf_call_raise_already[i]:
                                # print("PF_CALL_RAISE")
                                self.action_counter[PF_CALL_RAISE] += 1
                                top_percent = max(min(self.action_probs[PF_CALL_RAISE], 1), 0)
                                hand_to_equity = eval7.py_all_hands_vs_range(self.prev_opp_est_of_range[i], self.prev_opp_est_of_range[i], self.rd_board[i], 100)
                                sorted_hands = [(k,1.0) for k, v in sorted(hand_to_equity.items(), key=lambda item: item[1], reverse=True)]
                                est_range_this_action = set(sorted_hands[:round(top_percent * len(sorted_hands))])
                                self.opp_range[i] = self.opp_range[i] & est_range_this_action
                            elif street > 3:
                                # print("CALL_RAISE")
                                self.action_counter[CALL_RAISE] += 1
                                top_percent = max(min(self.action_probs[CALL_RAISE], 1), 0)
                                hand_to_equity = eval7.py_all_hands_vs_range(self.prev_opp_est_of_range[i], self.prev_opp_est_of_range[i], self.rd_board[i], 100)
                                sorted_hands = [(k,1.0) for k, v in sorted(hand_to_equity.items(), key=lambda item: item[1], reverse=True)]
                                est_range_this_action = set(sorted_hands[:round(top_percent * len(sorted_hands))])
                                self.opp_range[i] = self.opp_range[i] & est_range_this_action
                        if cont_cost > 0:
                            # print("RAISE")
                            opp_action = RAISE
                            self.action_counter[CALL_RAISE] += 1
                            self.action_counter[RAISE] += 1
                                
                if opp_action is not None:
                    self.action_determined[i] = True

                    if game_state.round_num > 50:  # narrow it using percentage
                        if street == 0:
                            if opp_action == PF_CALL_RAISE:
                                top_percent = max(min(self.action_probs[PF_CALL_RAISE], 1), 0)
                            else:  # raise
                                top_percent = max(min(self.action_probs[RAISE], 1), 0)
                            est_range_this_action = set(self.ranges[round(top_percent * 1326)])
                        else:  # has to be raise
                            top_percent = max(min(self.action_probs[RAISE], 1), 0)
                            hand_to_equity = eval7.py_all_hands_vs_range(self.opp_est_of_range[i], self.opp_est_of_range[i], self.rd_board[i], 100)
                            sorted_hands = [(k,1.0) for k, v in sorted(hand_to_equity.items(), key=lambda item: item[1], reverse=True)]
                            est_range_this_action = set(sorted_hands[:round(top_percent * len(sorted_hands))])

                        new_range = self.opp_range[i] & est_range_this_action
                        if len(new_range) > 10:
                            self.opp_range[i] = new_range
                        else:
                            self.opp_range[i] = self.opp_range[i] & self.opp_est_of_range[i]

                elif street != self.street_tracker:  # can also update this up top instead
                    self.opp_range[i] = self.opp_range[i] & self.opp_est_of_range[i]
                    
                self.equity[i] = eval7.py_hand_vs_range_monte_carlo(self.my_cards_obj[i], self.opp_range[i], self.rd_board[i], 1500)
                strength = self.equity[i]

                #######

                print(game_state.round_num, i+1, street, strength, len(self.opp_range[i]))


                if street < 3 and my_pips[i] == 1 and active == 0 and strength < self.pf_tightness:  # sb pre-flop 1st action, limp if s < 0.75
                    if CallAction in legal_actions[i] and cont_cost <= my_stack - net_cost:
                        my_actions[i] = CallAction()
                        net_cost += cont_cost
                        continue
                    else:
                        my_actions[i] = FoldAction()
                        continue

                if (self.times_called_bluff > 2 and self.times_bluff_succeeded / self.times_called_bluff < 7) or (self.times_called_bluff > 1 and self.times_bluff_succeeded / self.times_called_bluff < 4):
                    self.stop_bluffing = True

                raise_bluff = True
                if not self.stop_bluffing and not self.just_bluffed:
                    if active == 0 and legal_actions[i] == {CheckAction, RaiseAction} and all((self.equity[j] < 0.8 or isinstance(round_state.board_states[j], TerminalState)) for j in range(3)):
                        if street == 5 or random.random() < 0.1:
                            max_cost = min(max_raise - my_pips[i], my_stack - net_cost)
                            if max_cost + my_pips[i] > 100:
                                my_actions[i] = RaiseAction(max_cost + my_pips[i])
                                net_cost += max_cost
                                self.just_bluffed = True
                                self.board_bluffed = i
                                continue
                            else:
                                raise_bluff = False
                        elif raise_bluff: 
                            raise_amount = 2 * min_raise
                            if raise_amount - my_pips[i] <= my_stack - net_cost:
                                my_actions[i] = RaiseAction(raise_amount)
                                net_cost += raise_amount - my_pips[i]
                                continue
                
                if street == 0:
                    tightness = self.pf_tightness
                else:
                    tightness = self.tightness

                if self.stop_bluffing and active == 0 and legal_actions[i] == {CheckAction, RaiseAction}:
                    if strength > 0.85 and random.random() < 0.3:
                        max_cost = min(max_raise - my_pips[i], my_stack - net_cost)
                        if max_cost + my_pips[i] > 100:
                            print("BLUFF BAITED")
                            my_actions[i] = RaiseAction(max_cost + my_pips[i])
                            net_cost += max_cost
                            continue
                
                if strength > tightness + pot/2000:
                    raise_amount = int(my_pips[i] + cont_cost + (strength - 0.3) * (pot + cont_cost))
                    raise_amount = min(max(raise_amount, min_raise), max_raise)

                    if RaiseAction in legal_actions[i] and raise_amount - my_pips[i] <= my_stack - net_cost:
                        commit_action = RaiseAction(raise_amount)
                        commit_cost = raise_amount - my_pips[i]
                    elif CallAction in legal_actions[i] and cont_cost <= my_stack - net_cost:
                        commit_action = CallAction()
                        commit_cost = cont_cost
                    elif CheckAction in legal_actions[i]:
                        commit_action = CheckAction()
                        commit_cost = 0
                    else:
                        commit_action = FoldAction()
                        commit_cost = 0

                    my_actions[i] = commit_action
                    net_cost += commit_cost
                    continue

                if strength > tightness:
                    if CallAction in legal_actions[i] and cont_cost <= my_stack - net_cost:
                        commit_action = CallAction()
                        commit_cost = cont_cost
                    elif CheckAction in legal_actions[i]:
                        commit_action = CheckAction()
                        commit_cost = 0
                    else:
                        commit_action = FoldAction()
                        commit_cost = 0

                    my_actions[i] = commit_action
                    net_cost += commit_cost
                    continue

                if game_state.round_num > 50 and street > 0 and street != self.street_tracker and cont_cost == 0 and strength > max(self.action_probs[CALL_RAISE] + 0.05, 0.5):
                    print("TRIED PSEUDO-BLUFF")
                    raise_amount = min_raise
                    if RaiseAction in legal_actions[i] and raise_amount - my_pips[i] <= my_stack - net_cost:
                        commit_action = RaiseAction(raise_amount)
                        commit_cost = raise_amount - my_pips[i]
                    elif CheckAction in legal_actions[i]:
                        commit_action = CheckAction()
                        commit_cost = 0
                    else:
                        commit_action = FoldAction()
                        commit_cost = 0

                    my_actions[i] = commit_action
                    net_cost += commit_cost
                    continue

                if cont_cost > 0:
                    pot_odds = cont_cost / (pot + cont_cost)
                    if strength > max(pot_odds, pot/200):
                        if cont_cost >= 10:
                            if strength > tightness - 0.05:
                                if (cont_cost <= my_stack - net_cost):
                                    my_actions[i] = CallAction()
                                    net_cost += cont_cost
                                    continue
                                else:
                                    my_actions[i] = FoldAction()
                                    continue
                            else:
                                my_actions[i] = FoldAction()
                                continue
                        else:
                            my_actions[i] = CallAction()
                            net_cost += cont_cost
                            continue
                    else:
                        my_actions[i] = FoldAction()
                        continue
                else:
                    my_actions[i] = CheckAction()
                    continue

        for i, action in enumerate(my_actions):
            if not isinstance(round_state.board_states[i], TerminalState) and not round_state.board_states[i].settled and isinstance(action, RaiseAction):
                self.just_raised[i] = (True, street)
            else:
                self.just_raised[i] = (False, -1)
        self.street_tracker = street
        return my_actions


if __name__ == '__main__':
    run_bot(Player(), parse_args())
