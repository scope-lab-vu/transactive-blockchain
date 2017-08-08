#from riaps.run.comp import Component

from random import Random

from const import *
from Account import Account
from EnergyAsset import EnergyAsset

BASE_PRICE = 1
NUM_ACCOUNTS = 10
PREDICTION_HORIZON = 6 

class SmartHomeTrader: #(Component):
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
    for timestep in range(PREDICTION_HORIZON):
      self.manage_assets(timestep)
    self.next_timestep = PREDICTION_HORIZON
      
  def predict_net_production(self, timestep):
    # TODO: use data (based on name and timestep)
    return int((CONSUMPTION_LIMIT + PRODUCTION_LIMIT) * self.random.random() - PRODUCTION_LIMIT)
    
  def manage_assets(self, timestep):
    # choose random address for trading
    address = self.random.choice(list(self.accounts.keys()))
    # request based on predicted net production
    asset = EnergyAsset(self.predict_net_production(timestep), timestep, timestep) 
    self.withdraw_assets(address, asset, 100)
    # TODO: verify success and retry on failure
    
  def add_asset(self, address, assetID, asset):
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
             
  # RIAPS message handlers

  def on_clock(self):
    msg = self.clock.recv_pyobj()
    # predict net production for one more timestep and withdraw assets
    self.manage_assets(self.next_timestep)
    self.next_timestep += 1

  # RIAPS message sender
  
  def withdraw_assets(self, address, asset, financial):
    # TODO: provide auth
    msg = { 
      'prosumer': self.name, 
      'auth': "password", 
      'asset': asset, 
      'address': address, 
      'financial': financial 
    }
    # TODO: remove testing code
    if "withdrawAssets" in dir(self):
      self.withdrawAssets.send_pyobj(msg)
    else:
      print("withdrawAssets", address, asset, financial)

  # Ethereum function calls
  
  def postOffer(self, address, assetID, price):
    # TODO: implement calling the function of TradingService contract
    print("postOffer", address, assetID, price)
    pass    
  
  def acceptOffer(self, address, offerID, assetID):
    # TODO: implement calling the function of TradingService contract
    print("acceptOffer", address, offerID, assetID)
    pass

  # Ethereum event handlers  
    
  def AssetAdded(self, address, assetID, power, start, end):
    # TODO: connect Ethereum listener
    self.add_asset(address, assetID, EnergyAsset(power, start, end))
        
  def OfferPosted(self, offerID, power, start, end, price):
    # TODO: connect Ethereum listener
    self.offer_posted(offerID, EnergyAsset(power, start, end), price)
    
  def OfferRescinded(offerID):
    # TODO: connect Ethereum listener
    self.offer_rescinded(offerID)
    
  def OfferAccepted(self, offerID, assetID, transPower, transStart, transEnd, price):
    # TODO: connect Ethereum listener
    self.offer_accepted(offerID, assetID, price)

if __name__ == "__main__":
  trader = SmartHomeTrader("home1")
  addresses = list(trader.accounts.keys())
  trader.AssetAdded(addresses[0], 0, 15, 0, 10)
  trader.AssetAdded(addresses[1], 1, -30, 0, 10)
  trader.OfferPosted(0, 10, 5, 15, 1)
  trader.OfferPosted(1, 10, 20, 25, 1)
  trader.AssetAdded(addresses[3], 2, -10, 20, 30)
    
  