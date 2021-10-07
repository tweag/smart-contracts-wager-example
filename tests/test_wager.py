import brownie
from brownie.test import strategy


class StateMachine:

    value = strategy("uint256", max_value="1 ether")
    wagerID = strategy("uint256", min_value="1", max_value="15")
    address = strategy("address")

    def __init__(cls, accounts, GameWager):
        # deploy the contract at the start of the test
        cls.accounts = accounts
        cls.contract = GameWager.deploy({"from": accounts[0]})
        cls.ids = []

    def setup(self):
        self.ids = []

    def rule_create(self, wagerID, value, address):
        if value == 0:
            with brownie.reverts():
                self.contract.createWager(wagerID, {"from": address, "value": value})
                self.ids.append(wagerID)
        else:
            self.contract.createWager(wagerID, {"from": address, "value": value})
            self.ids.append(wagerID)

    def rule_accept(self, wagerID, value, address):
        if wagerID not in self.ids or value == 0:
            with brownie.reverts():
                self.contract.AcceptWager(wagerID, {"from": address, "value": value})
        else:
            self.contract.AcceptWager(wagerID, {"from": address, "value": value})

    def rule_payout(self, wagerID, address):
        _, owner, owner_wager_amount, _, _, state = self.contract.wagers(wagerID)
        if wagerID in self.ids and state == 1:
            wager = self.contract.wagers(wagerID)
            self.contract.PayoutWager(wagerID, address, {"from": address})
        else:
            with brownie.reverts():
                self.contract.PayoutWager(wagerID, address, {"from": address})

    def invariant_all_states(self):
        for id in self.ids:
            _, owner, owner_wager_amount, _, _, _ = self.contract.wagers(id)
            assert owner != "0x0000000000000000000000000000000000000000"
            assert owner_wager_amount > 0

    def invariant_accepted_state(self):
        for id in self.ids:
            (
                _,
                owner,
                owner_wager_amount,
                player2,
                player2_wager_amount,
                state,
            ) = self.contract.wagers(id)
            if state == 1:
                assert owner != "0x0000000000000000000000000000000000000000"
                assert owner_wager_amount > 0
                assert player2 != "0x0000000000000000000000000000000000000000"
                assert player2_wager_amount > 0


def test_stateful(GameWager, accounts, state_machine):
    state_machine(StateMachine, accounts, GameWager)
