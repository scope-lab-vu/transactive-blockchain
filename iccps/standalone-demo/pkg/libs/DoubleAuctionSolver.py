import logging

# from Microgrid import Microgrid
# from LinearProgramCplex import LinearProgramCplex

class Offer:
  def __init__(self, ID, prosumer, startTime, endTime, energy, price):
    self.ID = ID
    self.prosumer = prosumer
    self.startTime = startTime
    self.endTime = endTime
    self.energy = energy
    self.price = price

  def contains(self, interval):
    return self.startTime <= interval <= self.endTime

  def __repr__(self):
    return f'{{id: {self.ID}, prosumer: {self.prosumer}, startTime: {self.startTime}, endTime: {self.endTime}, energy: {self.energy}, price: {self.price}}}'

class DoubleAuctionSolver:
  def __init__(self):
    pass

  def solve(self, buying_offers, selling_offers, interval):
    selling = sorted([o for o in selling_offers if o.contains(interval)], key=lambda s: s.price)
    buying = sorted([o for o in buying_offers if o.contains(interval)], key=lambda s: -s.price)

    bi = 0 #index
    si = 0

    bq = 0 #quantity
    sq = 0

    bp = buying[0].price
    sp = selling[0].price

    while bp > sp:
      if bq > sq:
        sq += selling[si].energy
        sp = selling[si].price
        si += 1
      else:
        bq += buying[bi].energy
        bp = buying[bi].price
        bi += 1

    return {
      'buyers': buying[0:bi],
      'sellers': selling[0:si],
      'price': bp
    }


if __name__ == "__main__":
  solver = DoubleAuctionSolver()
  buying_offers = [
    Offer(0, 0, 1, 10, 5, 1),
    Offer(1, 1, 6, 15, 5, 2),
    Offer(2, 3, 1, 10, 5, 3),
    Offer(3, 4, 6, 15, 5, 4),
  ]
  selling_offers = [
    Offer(4, 2, 1, 15, 15, 2),
    Offer(5, 5, 1, 15, 5, 6),
  ]
  da = solver.solve(buying_offers=buying_offers, selling_offers=selling_offers, interval=8)
  print(f'{da["sellers"]} are selling to {da["buyers"]} at price {da["price"]}')
