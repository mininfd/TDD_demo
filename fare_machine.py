class FareMachine:
  def __init__(self, fares: dict[str, int]):
    self._fares = fares
    self._shortage = 0

  def get_shortage(self) -> int:
    return self._shortage
  
  def start(self, card):
    fare = self._fares[card.entry_station]
    shortage = fare - card.balance

    self._shortage = shortage
