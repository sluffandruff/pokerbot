def pot_odds(pot, call_size):
    return call_size / (pot + call_size)
    # implied pot odds, etc.?


def equity(my_hand, range, board):
    # 0.0-1.0
    # Monte Carlo
    pass

def calculate_range():
    pass

class WeightedRange():
    
    def __init__(self):
        pass

class OpponentStats():

    def __init__(self):
        self.vpip = 0.0
        self.pfr = 0.0
        self.threeb = 0.0


# allocate based on initial equity, better hands on bigger blinds?, maximize return (calculation?)
# each round, calculate opp range based on stats and check if pot odds < equity to call 
# when to raise?