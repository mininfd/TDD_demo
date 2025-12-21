from fare_machine import FareMachine
from ic_card import ICCard

def test_start_reads_entry_and_balance_and_gets_fare():
  fares = {"A": 180, "B": 200}
  card = ICCard(entry_station="A", balance=100)
  m = FareMachine(fares)
  m.start(card)
  assert m.get_shortage() == 80
