import logging

class MatchingContract(Contract):
  def __init__(self, client, address):
    super(MatchingContract, self).__init__(client, address, [
      "BuyingOfferPosted(uint64 ID, uint64 prosumer, uint64 startTime, uint64 endTime, uint64 energy, uint64 price)",
      "SellingOfferPosted(uint64 ID, uint64 prosumer, uint64 startTime, uint64 endTime, uint64 energy, uint64 price)",
      "SolutionCreated(uint64 ID)",
      "TradeAdded(uint64 solutionID, uint64 sellerID, uint64 buyerID, uint64 time, uint64 power, uint64 price, uint64 objective)"
    ])

  def postBuyingOffer(self, from_account, prosumer_id, start_time, end_time, energy):
    self.call_func(from_account, "postBuyingOffer", 
      "uint64", prosumer_id, 
      "uint64", start_time, 
      "uint64", end_time, 
      "uint64", energy, 
      "uint64", 0) # default price

  def postSellingOffer(self, from_account, prosumer_id, start_time, end_time, energy):
    self.call_func(from_account, "postSellingOffer", 
      "uint64", prosumer_id, 
      "uint64", start_time, 
      "uint64", end_time, 
      "uint64", energy, 
      "uint64", 0) # default price
            
  def createSolution(self, from_account):
    self.call_func(from_account, "createSolution")
    
  def addTrade(uint64 solutionID, uint64 sellerID, uint64 buyerID, uint64 time, uint64 power)
    self.call_func(from_account, "addTrade",
      "uint64", solutionID,
      "uint64", sellerID,
      "uint64", buyerID,
      "uint64", time,
      "uint64", power,
      "uint64", 0) # default price

