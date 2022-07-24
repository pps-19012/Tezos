import smartpy as sp

class Lottery(sp.Contract):
    def __init__(self):
        # storage
        self.init(
            players = sp.map(l = {}, tkey = sp.TNat, tvalue = sp.TAddress),
            ticket_cost = sp.tez(1),
            tickets_available = sp.nat(5),
            max_tickets = sp.nat(5),
            operator = sp.test_account("admin").address,
        )
    
    @sp.entry_point
    def buy_ticket(self):
        # assertions
        sp.verify(self.data.tickets_available > 0, "No Tickets Available")
        sp.verify(sp.amount >= self.data.ticket_cost, "Invalid Amount") 

        #storage changes
        self.data.players[sp.len(self.data.players)] = sp.sender
        self.data.tickets_available = sp.as_nat(self.data.tickets_available - 1)

        # return extra
        extra_amount = sp.amount - self.data.ticket_cost
        sp.if extra_amount > sp.tez(0):
            sp.send(sp.sender, extra_amount)

    @sp.entry_point
    def end_game(self, random_number):

        sp.set_type(random_number, sp.TNat)

        # assertions
        sp.verify(self.data.tickets_available == 0, "Game is still ON")
        sp.verify(sp.sender == self.data.operator, "Not Authorised")

        # generate winner
        # winner_index = sp.as_nat(sp.now - sp.timestamp(0)) % self.data.max_tickets
        winner_index = random_number % self.data.max_tickets
        winner_address = self.data.players[winner_index]

        # send reward to winner
        sp.send(winner_address, sp.balance)

        # reset game
        self.data.players = {}
        self.data.tickets_available = self.data.max_tickets

@sp.add_test(name="main")
def test():
    scenario = sp.test_scenario()

    # test accounts
    admin = sp.test_account("admin")
    alice = sp.test_account("alice")
    bob = sp.test_account("bob")
    charles = sp.test_account("charles")
    david = sp.test_account("david")
    eve = sp.test_account("eve")

    # contract instance
    lottery = Lottery()
    scenario += lottery

    # buy_ticket
    scenario += lottery.buy_ticket().run(amount=sp.tez(1), sender=alice)
    scenario += lottery.buy_ticket().run(amount=sp.tez(1), sender=bob)
    scenario += lottery.buy_ticket().run(amount=sp.tez(1), sender=charles)
    scenario += lottery.buy_ticket().run(amount=sp.tez(1), sender=david)
    scenario += lottery.buy_ticket().run(amount=sp.tez(4), sender=eve)

    # result
    scenario += lottery.end_game(25).run(sender = admin)
