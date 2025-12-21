class FareMachine:
  def __init__(self, fares: dict[str, int]):
    self._fares = fares
    self._shortage = 0
    self._settling = False

  def get_shortage(self) -> int:
    return self._shortage

  def is_settling(self) -> bool:
    return self._settling
  
  def start(self, card):
    fare = self._fares[card.entry_station]
    shortage = fare - card.balance

    if shortage <= 0:
      shortage = 0
      self._settling = False
      return False

    self._settling = True
    self._shortage = shortage

  def charge(self, amount: int) -> bool:
    if not self._settling:
      return False

    if amount < self._shortage:
      return False
