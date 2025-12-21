# 乗り越し精算機

## 仕様

### 目的
電車を利用後、駅から出る際に交通系ICカードの残高が足りないとき、改札前でチャージが可能な乗り越し精算機を実装する

### 入力
- 交通系ICカードから取得できる情報
  - 乗車駅
  - 残高
- 運賃表
  - `駅名: 運賃`の対応を持つと辞書として受け取り
    
### 精算の要否判定
- 乗車駅に対応する運賃を運賃表から取得
- 不足額を次の式で計算
  - `不足額 = 運賃 - 残高`
  - 不足額が0以下の場合は0(不足額は常に0以上)
- 不足額が 0 のとき：精算は不要
- 不足額が 正 のとき：精算が必要（精算状態に入る）

### チャージ(精算状態のみ)
- チャージ操作は精算が必要なときだけ可能
- 投入金額が不足額以上のとき：チャージが成立し、カード残高が変化(増加)
- 投入金額が不足額未満のとき：チャージは成立しない(残高は変化しない)

### 精算機の初期化
- 「精算不要」と判定された場合、初期状態に戻る
- 「チャージ完了」した場合、初期状態に戻る

***
## テストシナリオ
1. カードから乗車駅と残高の情報を取得し、乗車駅から運賃の情報を取得、不足額を計算
2. 不足額が0以下の場合は不足額0として扱う
3. 精算不要時　初期状態に戻る
4. 不足額が0を超過する場合精算を開始
5. 非精算時、チャージ不可能
6. 投入金額が不足額未満ならチャージされない
7. 投入金額が不足額以上ならチャージされ残高が変化 初期状態に戻る

***
## TDDのサイクルを実践
#### 1. 乗車駅と残高の情報を取得し、乗車駅から運賃の情報を取得、不足額を計算

テスト

tests/test_fare_machine.py

```python
from fare_machine import FareMachine
from ic_card import ICCard

def test_start_reads_entry_and_balance_and_gets_fare():
  fares = {"A": 180, "B": 200}
  card = ICCard(entry_station="A", balance=100)
  m = FareMachine(fares)
  m.start(card)
  assert m.get_shortage() == 80
```

作成したコード

ic_card.py

```python
class ICCard:
  def __init__(self, entry_station: str, balance: int):
    self.entry_station = entry_station
    self.balance = balance
```

fare_machine.py

```python
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
```

#### 2. 不足額が0以下の場合は不足額0として扱う

テスト

tests/test_fare_machine.py

```python
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
```

作成したコード差分

fare_machine.py

```diff

  def start(self, card):
    fare = self._fares[card.entry_station]
    shortage = fare - card.balance

+   if shortage <= 0:
+     shortage = 0

    self._shortage = shortage
```

#### 3. 精算不要時　初期状態に戻る

テスト

tests/test_fare_machine.py

```python
def test_no_settlement_means_back_to_idle():
  fares = {"A": 180}
  card = ICCard(entry_station="A", balance=180)
  m = FareMachine(fares)

  m.start(card)
  assert m.get_shortage() == 0
  assert m.is_settling() is False
```

作成したコード差分

fare_machine.py

```diff
@@ def __init__(self, fares: dict[str, int]):

    self._shortage = 0
+   self._settling = False

+ def is_settling(self) -> bool:
+   return self._settling

@@ def start(self, card):

    if shortage <= 0:
      shortage = 0
+     self._settling = False
      
```

#### 4. 不足額が0を超過する場合精算を開始

テスト

tests/test_fare_machine.py

```python
def test_positive_shortage_requires_settlement():
  fares = {"A": 180}
  card = ICCard(entry_station="A", balance=100)
  m = FareMachine(fares)

  m.start(card)
  assert m.is_settling() is True
  assert m.get_shortage() == 80
```

作成したコード差分

fare_machine.py

```diff
@@ def start(self, card):

      self._settling = False
+     return False

+   self._settling = True
    self._shortage = shortage
```


#### 5. 非精算時チャージ不可能

テスト

tests/test_fare_machine.py

```python
def test_cannot_charge_when_settlement_not_needed():
  fares = {"A": 180}
  card = ICCard(entry_station="A", balance=300)  # shortage=0
  m = FareMachine(fares)

  m.start(card)  # idleに戻る
  canIcharge = m.charge(100)

  assert canIcharge is False
  assert card.balance == 300
  assert m.is_settling() is False
```

作成したコード差分

fare_machine.py

```diff
+ def charge(self, amount: int) -> bool:
+   if not self._settling:
+     return False
```

#### 6. 投入金額が不足額未満ならチャージされない

テスト

tests/test_fare_machine.py

```python
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
```

作成したコード差分

fare_machine.py

```diff
  def charge(self, amount: int) -> bool:
    if not self._settling:
      return False

+   if amount < self._shortage:
+     return False
```

#### 7. 投入金額が不足額以上ならチャージされ残高が変化 初期状態に戻る

テスト

tests/test_fare_machine.py

```python
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
```

作成したコード差分

fare_machine.py

```diff
@@ def __init__(self, fares: dict[str, int]):

    self._settling = False
+   self._card = None
+   self._reset()

+ def _reset(self):
+   self._settling = False
+   self._shortage = 0
+   self.card = None

@@ def start(self, card):

    self._settling = False
    return False

+   self._card = card
    self._settling = True

@@ def charge(self, amount: int) -> bool:

    if amount < self._shortage:
      return False
+   self._card.balance += amount
+   self._reset()
+   return True
```

#### リファクタリング

_reset()を精算不要時の初期化に利用

作成したコード差分

fare_machine.py

```diff
@@ def start(self, card):

    if shortage <= 0:
-     self._shortage = 0
-     self._settling = False
+     self._reset()
      return False
```
