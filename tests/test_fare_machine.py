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

def test_cannot_handle_two_cards_at_once_but_after_settlement_second_card_can_start():
  fares = {"A": 180, "B": 200}

  card1 = ICCard(entry_station="A", balance=100)  # shortage=80
  card2 = ICCard(entry_station="B", balance=150)  # shortage=50

  m = FareMachine(fares)

  # 1枚目精算可
  assert m.start(card1) is True
  assert m.is_settling() is True
  assert m.get_shortage() == 80

  # 2枚目精算不可
  assert m.start(card2) is False
  assert m.is_settling() is True
  assert m.get_shortage() == 80

  # 1枚目を精算完了 -> 初期状態
  assert m.charge(80) is True
  assert card1.balance == 180
  assert m.is_settling() is False
  assert m.get_shortage() == 0

def test_missing_entry_station_means_cannot_settle_and_back_to_idle():
  fares = {"A": 180}
  m = FareMachine(fares)

  # entry_station が空（情報なし）
  card = ICCard(entry_station="", balance=100)

  assert m.start(card) is False
  assert m.is_settling() is False
  assert m.get_shortage() == 0
  assert m.charge(100) is False
  assert card.balance == 100

def test_unknown_entry_station_means_cannot_settle_and_back_to_idle():
  fares = {"A": 180}
  m = FareMachine(fares)

  # 運賃表に存在しない駅
  card = ICCard(entry_station="Z", balance=100)

  assert m.start(card) is False
  assert m.is_settling() is False
  assert m.get_shortage() == 0
  assert m.charge(100) is False
  assert card.balance == 100

def test_negative_balance_means_cannot_settle_and_back_to_idle():
  fares = {"A": 180}
  m = FareMachine(fares)

  card = ICCard(entry_station="A", balance=-1)

  assert m.start(card) is False
  assert m.is_settling() is False
  assert m.get_shortage() == 0
  assert m.charge(100) is False
  assert card.balance == -1  

def test_negative_charge_amount_is_rejected_and_stays_settling():
  fares = {"A": 180}
  m = FareMachine(fares)

  card = ICCard(entry_station="A", balance=100)  
  assert m.start(card) is True
  assert m.is_settling() is True
  assert m.get_shortage() == 80

  assert m.charge(-10) is False
  assert card.balance == 100
  assert m.is_settling() is True
  assert m.get_shortage() == 80
