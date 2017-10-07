import logging
from time import time
from sys import argv

from config import *
from MatchingSolver import MatchingSolver, Offer
from LinearProgram import LinearProgram
from LinearProgramCplex import LinearProgramCplex

DATA_PATH = "../data/{}/".format(argv[1])

def read_data(prosumer_id):
  logging.info("Reading net production values...")
  feeder = int(prosumer_id / 100)
  prosumer = prosumer_id % 100
  with open(DATA_PATH + "prosumer_{}.csv".format(prosumer_id), "rt") as fin:
    line = next(fin)
    offers = []
    for line in fin:
      try:
        fields = line.split(',')
        offers.append({
          'start': int(fields[0]), 
          'end': int(fields[1]),
          'energy': int(1000 * float(fields[2]))
        })
      except Exception:
        pass
    if not len(offers):
      raise Exception("No values found in data file!") 
    logging.info("Read {} values.".format(len(offers)))
    return offers
    
def filter_offers(time_interval, offers):
  filtered_offers = []
  for offer in offers:
    if (offer.startTime <= time_interval + PREDICTION_WINDOW) and (offer.endTime >= time_interval) and (offer.energy > 0):
      filtered_offers.append(offer)
  return filtered_offers
     
def match(solver, interval, selling_offers, buying_offers):
  #for (name, lp_solver) in [("CPLEX", LinearProgramCplex)]: #, ("SciPy", LinearProgram)]:
  name = "CPLEX"
  lp_solver = LinearProgramCplex
  tick = time()
  (solution, objective) = solver.solve(buying_offers, selling_offers, finalized=interval-1, lp_solver=lp_solver)
  print("{}: objective = {}, running time = {}".format(name, objective, time() - tick))
  finalized_amount = sum((trade['p'] for trade in solution if trade['t'] == interval))
  print("Finalized energy trades: {}".format(finalized_amount))
  for trade in solution:
    if trade['t'] == interval:
      trade['b'].energy -= trade['p']
      if trade['b'].energy < 0:
        raise Exception()
      trade['s'].energy -= trade['p']
      if trade['s'].energy < 0:
        raise Exception()
  return finalized_amount

if __name__ == "__main__":
  solver = MatchingSolver(MICROGRID)
  interval = 0
  selling_offers = []
  buying_offers = []
  for prosumer in PROSUMERS:
    for offer in read_data(prosumer):
      if offer['energy'] > 0:
        selling_offers.append(Offer(0, prosumer, offer['start'], offer['end'], offer['energy']))
      elif offer['energy'] < 0:
        buying_offers.append(Offer(0, prosumer, offer['start'], offer['end'], -offer['energy']))
  print("Total offered: {}".format(sum((offer.energy for offer in selling_offers)) / 1000))
  print("Total requested: {}".format(sum((offer.energy for offer in buying_offers)) / 1000))
  total_traded = 0
  experiment_start_time = time()
  for interval in range(0, 97):
    print("Time interval: {} (finalized: {})".format(interval, interval - 1))
    filtered_selling = filter_offers(interval, selling_offers)
    filtered_buying = filter_offers(interval, buying_offers)
    finalized_amount = match(solver, interval, filtered_selling, filtered_buying)
    total_traded += finalized_amount
  print("Dataset: {}".format(argv[1]))
  print("Total traded: {}".format(total_traded / 1000))
  print("Total running time: {}".format(time() - experiment_start_time))


