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
