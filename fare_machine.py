class FareMachine:
  def __init__(self, fares: dict[str, int]):
    self._fares = fares
    self._shortage = 0
    self._settling = False
    self._card = None
    self._reset()

  def _reset(self):
    self._settling = False
    self._shortage = 0
    self._card = None
  
  def get_shortage(self) -> int:
    return self._shortage

  def is_settling(self) -> bool:
    return self._settling
  
  def start(self, card):

    if self._card is not None:
      return False

    if not card.entry_station:
      self._reset()
      return False

    if card.entry_station not in self._fares:
      self._reset()
      return False
    
    fare = self._fares[card.entry_station]
    shortage = fare - card.balance

    if shortage <= 0:
      self._reset()
      return False

    self._card = card
    self._settling = True
    self._shortage = shortage
    return True

  def charge(self, amount: int) -> bool:
    if not self._settling:
      return False

    if amount < self._shortage:
      return False

    self._card.balance += amount
    self._reset()
    return True
