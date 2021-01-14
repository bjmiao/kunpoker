from lib.client_lib import Decision

def final_decision(action, amount, remain_chip, bb=40):
    decision = Decision()
    if (action == "fold"):
        decision.giveup = 1
    elif (action == "check"):
        decision.callbet = 1
    elif (action == "call"):
        if ()
    elif (action == )

def add_bet(state, total):
    # amount: 本局需要下的总注
    amount = total - state.player[state.currpos].totalbet
    assert(amount > state.player[state.currpos].bet)
    # Obey the rule of last_raised
    minamount = state.last_raised + state.minbet
    real_amount = max(amount, minamount)
    # money_needed = real_amount - state.player[state.currpos].bet
    decision = Decision()
    decision.raisebet = 1
    decision.amount = real_amount
    return decision