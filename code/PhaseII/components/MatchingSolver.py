from Microgrid import Microgrid
from LinearProgram import LinearProgram

class Offer:
  def __init__(self, prosumer, startTime, endTime, energy):
    self.prosumer = prosumer 
    self.startTime = startTime
    self.endTime = endTime
    self.energy = energy
    
  def matchable(self, offer):
    return (self.endTime >= offer.startTime) and (self.startTime <= offer.endTime)
    
  def intersection(self, offer):
    if not self.matchable(offer):
      return []
    start = max(self.startTime, offer.startTime)
    end = min(self.endTime, offer.endTime)
    return list(range(start, end + 1))  

class MatchingSolver:
  def __init__(self, microgrid):
    self.microgrid = microgrid
    
  def solve(self, buying_offers, selling_offers):
    program = LinearProgram()
    variables = []
    prosumer_prod = {}
    prosumer_cons = {}
    feeder_prod = {f: {} for f in self.microgrid.feeders}
    feeder_cons = {f: {} for f in self.microgrid.feeders}
    for b in range(len(buying_offers)):
      for s in range(len(selling_offers)):
        b_offer = buying_offers[b]
        s_offer = selling_offers[s]
        for t in b_offer.intersection(s_offer):
          varname = "p_{},{},{}".format(s, b, t)
          variables.append(varname)
          # prosumer production
          try:
            prosumer_prod[s_offer].append(varname)
          except KeyError:
            prosumer_prod[s_offer] = [varname]
          # prosumer consumption
          try:
            prosumer_cons[b_offer].append(varname)
          except KeyError:
            prosumer_cons[b_offer] = [varname]
          # feeder production
          s_feeder = self.microgrid.prosumer_feeder[s_offer.prosumer]
          if t not in feeder_prod[s_feeder]:
            feeder_prod[s_feeder][t] = [varname]
          else:
            feeder_prod[s_feeder][t].append(varname)
          # feeder consumption
          b_feeder = self.microgrid.prosumer_feeder[b_offer.prosumer]
          if t not in feeder_cons[b_feeder]:
            feeder_cons[b_feeder][t] = [varname]
          else:
            feeder_cons[b_feeder][t].append(varname)
    program.set_objective({varname: -1.0 for varname in variables})
    # eq:constrEnergyProd   
    for s_offer in selling_offers:
      program.add_constraint(
        {varname: 1.0 for varname in prosumer_prod[s_offer]},
        s_offer.energy / float(microgrid.interval_length))    
    # eq:constrEnergyCons       
    for b_offer in buying_offers:
      program.add_constraint(
        {varname: 1.0 for varname in prosumer_cons[b_offer]},
        b_offer.energy / float(microgrid.interval_length)) 
    for f in self.microgrid.feeders:
      for t in feeder_prod[f]:
        # eq:constrIntProd
        program.add_constraint({varname: 1.0 for varname in feeder_prod[f][t]}, 
          microgrid.C_int)
        # eq:constrExtProd
        if t in feeder_cons[f]:
          expr = {varname: 1.0 for varname in feeder_prod[f][t]}
          for varname in feeder_cons[f][t]:
            expr[varname] = -1.0
          program.add_constraint(expr, microgrid.C_ext)
      for t in feeder_cons[f]:
        # eq:constrIntCons
        program.add_constraint({varname: 1.0 for varname in feeder_cons[f][t]}, 
          microgrid.C_int)
        # eq:constrExtCons
        if t in feeder_prod[f]:
          expr = {varname: 1.0 for varname in feeder_cons[f][t]}
          for varname in feeder_prod[f][t]:
            expr[varname] = -1.0
          program.add_constraint(expr, microgrid.C_ext)
    print(program.solve())
    

if __name__ == "__main__":
  microgrid = Microgrid(interval_length=1.0, C_ext=20.0, C_int=25.0, feeders=[0, 1], prosumer_feeder={
    0: 0,
    1: 0,
    2: 0,
    3: 1,
    4: 1,
    5: 1
  }) 
  solver = MatchingSolver(microgrid)
  buying_offers = [
    Offer(0, 1, 10, 5),
    Offer(1, 6, 15, 5),
    Offer(3, 1, 10, 5),
    Offer(4, 6, 15, 5),
  ]
  selling_offers = [
    Offer(2, 1, 15, 15),
    Offer(5, 1, 15, 5),
  ]
  solver.solve(buying_offers=buying_offers, selling_offers=selling_offers)
  print("Success.")
