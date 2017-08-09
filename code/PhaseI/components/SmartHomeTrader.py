from random import Random

from const import *
from Account import Account
from EnergyAsset import EnergyAsset

BASE_PRICE = 1
NUM_ACCOUNTS = 1
PREDICTION_HORIZON = 1

class SmartHomeTrader: 
  def __init__(self, name):
    super(SmartHomeTrader, self).__init__()
    self.name = name
    self.random = Random(name)
    # track own consumption assets
    self.cons_assets = {}
    # track all offers
    self.offers = {}
    # create anonymous accounts
    self.accounts = {}
    for _ in range(NUM_ACCOUNTS):
      account = Account()
      self.accounts[account.address] = Account()
    # predict net production and request assets for trading 
    self.next_interval = 0
    for timestep in range(PREDICTION_HORIZON):
      self.predict()
      
  def net_production_predictor(self, timestep):
    # TODO: use data (based on name and timestep)
    return int((CONSUMPTION_LIMIT + PRODUCTION_LIMIT) * self.random.random() - CONSUMPTION_LIMIT)
    
  def predict(self):
    # choose random address for trading
    address = self.random.choice(list(self.accounts.keys()))
    # request based on predicted net production
    asset = EnergyAsset(self.net_production_predictor(self.next_interval), self.next_interval, self.next_interval) 
    self.next_interval += 1
    self.withdraw_assets(address, asset, 100)
    # TODO: verify success and retry on failure
    
  def asset_added(self, address, assetID, asset):
    # check if asset belongs to the prosumer
    if address not in self.accounts:
      return
    # production or consumption 
    if asset.power > 0:
      # offer production asset for trade
      self.postOffer(address, assetID, BASE_PRICE)
    else:
      # track consumption asset
      self.cons_assets[assetID] = (self.accounts[address], asset)  
      # check if there is an open offer
      for offerID, (offered_asset, price) in self.offers.items():
        if offered_asset.tradeable(asset):
          self.acceptOffer(address, offerID, assetID)
      
  def offer_posted(self, offerID, offered_asset, price):
    # pass on offers that are overpriced
    if price > BASE_PRICE:
      return
    # check if prosumer has tradeable asset
    for assetID, (account, asset) in self.cons_assets.items():
      if asset.tradeable(offered_asset):
        self.acceptOffer(account.address, offerID, assetID)
        return
    # remember offer
    self.offers[offerID] = (offered_asset, price)
        
  def offer_rescinded(self, offerID):
    if offerID in self.offers:
      del self.offers[offerID]
        
  def offer_accepted(self, offerID, assetID, price):
    if offerID in self.offers:
      del self.offers[offerID]
    if assetID in self.cons_assets:
      del self.cons_assets[assetID]           

  # DSO message sender for testing
  def withdraw_assets(self, address, asset, financial):
    print("withdrawAssets", address, asset, financial)

  # contract function calls for testing
  def postOffer(self, address, assetID, price):
    print("postOffer", address, assetID, price)  
  def acceptOffer(self, address, offerID, assetID):
    print("acceptOffer", address, offerID, assetID)

  # contract event handlers for testing     
  def AssetAdded(self, address, assetID, power, start, end):
    self.asset_added(address, assetID, EnergyAsset(power, start, end))        
  def FinancialAdded(self, address, amount):
    pass      
  def OfferPosted(self, offerID, power, start, end, price):
    self.offer_posted(offerID, EnergyAsset(power, start, end), price)    
  def OfferRescinded(offerID):
    self.offer_rescinded(offerID)    
  def OfferAccepted(self, offerID, assetID, transPower, transStart, transEnd, price):
    self.offer_accepted(offerID, assetID, price)

# tests
if __name__ == "__main__":
  NUM_ACCOUNTS = 3
  trader = SmartHomeTrader("home1")
  addresses = list(trader.accounts.keys())
  trader.AssetAdded(addresses[0], 0, 15, 0, 10)
  trader.AssetAdded(addresses[1], 1, -30, 0, 10)
  trader.OfferPosted(0, 10, 5, 15, 1)
  trader.OfferPosted(1, 10, 20, 25, 1)
  trader.AssetAdded(addresses[2], 2, -10, 20, 30)
    
  
