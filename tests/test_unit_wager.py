import pytest


@pytest.fixture
def game_wager(GameWager, accounts):
    return GameWager.deploy({"from": accounts[0]})


@pytest.fixture
def alice(accounts):
    return accounts[1]


@pytest.fixture
def bob(accounts):
    return accounts[2]


def test_happy_path(game_wager, alice, bob):
    wager_amount = "1 ether"
    wager_id = 1
    winner = alice

    tx1 = game_wager.createWager(wager_id, {"from": alice, "value": wager_amount})
    assert game_wager.balance() == "1 ether"
    assert "WagerCreated" in tx1.events

    tx2 = game_wager.AcceptWager(wager_id, {"from": bob, "value": wager_amount})
    assert game_wager.balance() == "2 ether"
    assert "WagerAccepted" in tx2.events

    winner_balance = winner.balance()
    tx3 = game_wager.PayoutWager(wager_id, winner, {"from": bob})
    assert "WagerFinished" in tx3.events

    assert game_wager.balance() == "0 ether"
    assert winner_balance + "2 ether" == winner.balance()
