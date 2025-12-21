from fare_machine import FareMachine
from ic_card import ICCard

def test_start_reads_entry_and_balance_and_gets_fare():
  fares = {"A": 180, "B": 200}
  card = ICCard(entry_station="A", balance=100)
  m = FareMachine(fares)
  m.start(card)
  assert m.get_shortage() == 80

def test_shortage_below_zero_means_zero():
  fares = {"A": 180}
  card1 = ICCard(entry_station="A", balance=180)
  m1 = FareMachine(fares)
  m1.start(card1)
  assert m1.get_shortage() == 0

  card2 = ICCard(entry_station="A", balance=300)
  m2 = FareMachine(fares)
  m2.start(card2)
  assert m2.get_shortage() == 0

def test_no_settlement_means_back_to_idle():
  fares = {"A": 180}
  card = ICCard(entry_station="A", balance=180)
  m = FareMachine(fares)

  m.start(card)
  assert m.get_shortage() == 0
  assert m.is_settling() is False

def test_positive_shortage_requires_settlement():
  fares = {"A": 180}
  card = ICCard(entry_station="A", balance=100)
  m = FareMachine(fares)

  m.start(card)
  assert m.is_settling() is True
  assert m.get_shortage() == 80

def test_cannot_charge_when_settlement_not_needed():
  fares = {"A": 180}
  card = ICCard(entry_station="A", balance=300)  # shortage=0
  m = FareMachine(fares)

  m.start(card)  # idleに戻る
  canIcharge = m.charge(100)

  assert canIcharge is False
  assert card.balance == 300
  assert m.is_settling() is False

def test_insufficient_payment_does_not_charge_and_stays_settling():
  fares = {"A": 180}
  card = ICCard(entry_station="A", balance=100)  # shortage=80
  m = FareMachine(fares)
  m.start(card)

  canIcharge = m.charge(50)
  assert canIcharge is False
  assert card.balance == 100
  assert m.is_settling() is True
  assert m.get_shortage() == 80

def test_enough_payment_charges_and_back_to_idle_exact():
  fares = {"A": 180}
  card = ICCard(entry_station="A", balance=100)  # shortage=80
  m = FareMachine(fares)
  m.start(card)

  canIcharge= m.charge(80)
  assert canIcharge is True
  assert card.balance == 180  # 100+80
  assert m.is_settling() is False
  assert m.get_shortage() == 0


def test_enough_payment_charges_and_back_to_idle_overpay():
  fares = {"A": 180}
  card = ICCard(entry_station="A", balance=100)  # shortage=80
  m = FareMachine(fares)
  m.start(card)

  canIcharge= m.charge(100)
  assert canIcharge is True
  assert card.balance == 200  # 100+100
  assert m.is_settling() is False
  assert m.get_shortage() == 0
