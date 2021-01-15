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
        self.street_tracker = 0
        self.opp_range = [[], [], []]

        self.opp_walks = [0, 0, 0] # SB folds
        self.opp_vpip = [0, 0, 0] # times
        self.opp_pfr = [0, 0, 0]
        self.opp_vpip_round = [0, 0, 0] # 0 or 1 
        self.opp_pfr_round = [0, 0, 0]

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
        opp_range = [hand for hand in ALL_HANDS.hands if hand[0][0] not in my_cards_obj and hand[0][1] not in my_cards_obj]
        self.opp_range = [opp_range] * 3

        equities = {}
        for i in range(5):
            for j in range(i + 1, 6):
                hand = (my_cards[i], my_cards[j])
                equities[hand] = eval7.py_hand_vs_range_monte_carlo(map(eval7.Card, hand), opp_range, [], 3700)

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
        
        self.allocate_cards(my_cards)


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
        for terminal_board_state in previous_state.board_states:
            previous_board_state = terminal_board_state.previous_state
            my_cards = previous_board_state.hands[active]  # your cards
            opp_cards = previous_board_state.hands[1-active]  # opponent's cards or [] if not revealed
        
        self.board_allocations = [[], [], []] #reset our variables at the end of every round!
        self.equity = [0, 0, 0]
        self.street_tracker = 0
        self.opp_range = [[], [], []]
        
        for i in range(NUM_BOARDS):
            self.opp_vpip[i] += self.opp_vpip_round[i]
            self.opp_pfr[i] += self.opp_pfr_round[i]
            self.opp_vpip_round[i] = 0
            self.opp_pfr_round[i] = 0

        game_clock = game_state.game_clock #check how much time we have remaining at the end of a game
        round_num = game_state.round_num #Monte Carlo takes a lot of time, we use this to adjust!
        # print(round_num, game_clock)
        if round_num == NUM_ROUNDS:
            print(game_clock)
            print(self.opp_walks, self.opp_vpip, self.opp_pfr)
        

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
        
        for i in range(NUM_BOARDS):
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

                ######
                recalc = False
                if street < 3:
                    if active == 0: # the opp is bb
                        if opp_pips[i] > 2: # opp has voluntarily put chips in (responding to our raise / raising after limp)
                            if self.opp_vpip_round[i] == 0:
                                recalc = True
                            self.opp_vpip_round[i] = 1
                            if cont_cost > 0: # opp has raised in response to our raise / raised after limp
                                if self.opp_pfr_round[i] == 0:
                                    recalc = True
                                self.opp_pfr_round[i] = 1
                    else: # the opp is sb
                        if opp_pips[i] > 1:
                            if self.opp_vpip_round[i] == 0:
                                recalc = True
                            self.opp_vpip_round[i] = 1
                        if cont_cost > 0: # opp has raised
                            if self.opp_pfr_round[i] == 0:
                                recalc = True
                            self.opp_pfr_round[i] = 1
                            
                if street == 3 and active == 0: # opp is bb, made it to the flop (neither of us folded)
                    if cont_cost > 0 and my_pips[i] == 0: # opp has made a cbet
                        self.opp_vpip_round[i] = 1

                if street != self.street_tracker or recalc:           
                    if game_state.round_num > 50 and street <= 3:
                        if self.opp_pfr_round[i] == 1:
                            percentage = (self.opp_pfr[i] + 1) / (game_state.round_num - self.opp_walks[i]) 
                            self.opp_range[i] = self.ranges[round(percentage * 1326)]
                        elif self.opp_vpip_round[i] == 1:
                            percentage = (self.opp_vpip[i] + 1) / (game_state.round_num - self.opp_walks[i]) 
                            self.opp_range[i] = self.ranges[round(percentage * 1326)]
                            
                    my_cards_obj = {eval7.Card(c) for c in my_cards}
                    board = {eval7.Card(c) for c in board_cards[i] if c != ""}
                    self.opp_range[i] = [h for h in self.opp_range[i] if h[0][0] not in my_cards_obj and h[0][1] not in my_cards_obj
                                            and h[0][0] not in board and h[0][1] not in board]
                    self.equity[i] = eval7.py_hand_vs_range_monte_carlo(map(eval7.Card, self.board_allocations[i]), self.opp_range[i], board, 3700)
                
                strength = self.equity[i]
                #######

                if street < 3 and my_pips[i] == 1 and active == 0 and strength < 0.8:  # sb pre-flop 1st action, limp if s < 0.8
                    if CallAction in legal_actions[i] and cont_cost <= my_stack - net_cost:
                        my_actions[i] = CallAction()
                        net_cost += cont_cost
                    else:
                        my_actions[i] = FoldAction()
                elif strength < 0.5:
                    if CheckAction in legal_actions[i]:
                        my_actions[i] = CheckAction()
                    else:
                        my_actions[i] = FoldAction()
                else:
                    raise_amount = int(my_pips[i] + cont_cost + (strength - 0.5) * (pot + cont_cost))
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


                    if strength > 0.8:
                        my_actions[i] = commit_action
                        net_cost += commit_cost
                    else:
                        if cont_cost > 0:
                            pot_odds = cont_cost / (pot + cont_cost)
                            if strength > max(pot_odds, pot/200):
                                if cont_cost > 20:
                                    if strength > 0.7:
                                        if (cont_cost <= my_stack - net_cost):
                                            my_actions[i] = CallAction()
                                            net_cost += cont_cost
                                        else:
                                            my_actions[i] = FoldAction()
                                    else:
                                        my_actions[i] = FoldAction()
                                else:
                                    my_actions[i] = CallAction()
                                    net_cost += cont_cost
                            else:
                                my_actions[i] = FoldAction()
                                
                        else:
                            my_actions[i] = CheckAction()

            if isinstance(my_actions[i], FoldAction):
                if street < 3 and active == 0 and my_pips[i] == 1: # I have folded the sb
                    self.opp_walks[i] += 1

        self.street_tracker = street
        return my_actions


if __name__ == '__main__':
    run_bot(Player(), parse_args())
