from enum import Enum

class TradingService:
  def __init__(self):
    self.financialBalance = {}
    self.energyAssets = {}
    self.nextEnergyAssetID = 0
    self.offers = {}
    self.nextOfferID = 0
    
  # Financial Assets
  
  def FinancialAdded(self, address, amount):
    self.event("FinancialAdded", {'address': address, 'amount': amount})
  def FinancialDeposited(self, address, amount):
    self.event("FinancialDeposited", {'address': address, 'amount': amount})
  
  def addFinancialBalance(self, sender, amount):
    if sender in self.financialBalance:
      self.financialBalance[sender] += amount
    else:
      self.financialBalance[sender] = amount
    self.FinancialAdded(sender, amount)

  def depositFinancial(self, sender, amount):
    assert(self.financialBalance[sender] >= amount)
    self.financialBalance[sender] -= amount
    self.FinancialDeposited(sender, amount)

  # Energy Assets
  
  class AssetType(Enum):
    Production = 1
    Consumption = 2
  
  class EnergyAsset:
    def __init__(self, owner, assetType, power, start, end):
      self.owner = owner
      self.assetType = assetType
      self.power = power
      self.start = start
      self.end = end
    
  def AssetAdded(self, address, assetID, power, start, end):
    self.event("AssetAdded", {'address': address, 'assetID': assetID, 'power': power, 'start': start, 'end': end})
    
  def AssetDeposited(self, address, assetID, power, start, end):
    self.event("AssetDeposited", {'address': address, 'assetID': assetID, 'power': power, 'start': start, 'end': end})

  def depositEnergyAsset(self, sender, assetID):
    assert(assetID < self.nextEnergyAssetID)
    asset = self.energyAssets[assetID]
    assert(sender == asset.owner)
    asset.owner = None
    power = asset.power if asset.assetType == self.AssetType.Production else -asset.power
    self.AssetDeposited(sender, assetID, power, asset.start, asset.end)

  def createEnergyAsset(self, address, assetType, power, start, end):
    self.energyAssets[self.nextEnergyAssetID] = self.EnergyAsset(
      assetType=assetType,
      power=power,
      start=start, 
      end=end, 
      owner=address)
    if (assetType == self.AssetType.Production):
      self.AssetAdded(address, self.nextEnergyAssetID, power, start, end)
    else:
      self.AssetAdded(address, self.nextEnergyAssetID, -power, start, end)
    self.nextEnergyAssetID += 1
    return self.nextEnergyAssetID - 1

  def addEnergyAsset(self, address, power, start, end):
    return self.createEnergyAsset(
      address, 
      (self.AssetType.Production if power > 0 else self.AssetType.Consumption), 
      (power if power > 0 else -power), 
      start, 
      end)
  
  def splitAssetByStart(self, assetID, newStart):
    asset = self.energyAssets[assetID]
    if (asset.start < newStart) and (asset.end >= newStart):
      self.createEnergyAsset(asset.owner, asset.assetType, asset.power, asset.start, newStart - 1)
      asset.start = newStart
  
  def splitAssetByEnd(self, assetID, newEnd):
    asset = self.energyAssets[assetID]
    if (asset.start <= newEnd) and (asset.end > newEnd):
      self.createEnergyAsset(asset.owner, asset.assetType, asset.power, newEnd + 1, asset.end)
      asset.end = newEnd

  def splitAssetByPower(self, assetID, newPower):
    asset = self.energyAssets[assetID]
    if (asset.power > newPower):
      self.createEnergyAsset(asset.owner, asset.assetType, asset.power - newPower, asset.end, asset.end)
      asset.power = newPower
  
  # Energy Ask and Bid Offers
  
  class OfferType(Enum): 
    Ask = 1
    Bid = 2
    
  class OfferState(Enum):
    Open = 1
    Rescinded = 2
    Closed = 3

  class Offer:
    def __init__(self, poster, offerType, assetID, price, state):
      self.poster = poster
      self.offerType = offerType
      self.assetID = assetID
      self.price = price
      self.state = state
  
  def OfferPosted(self, offerID, assetID, power, start, end, price):
    self.event("OfferPosted", {'offerID': offerID, 'assetID': assetID, 'power': power, 'start': start, 'end': end, 'price': price})

  def OfferRescinded(self, offerID):
    self.event("OfferRescinded", {'offerID': offerID})

  def OfferAccepted(self, offerID, assetID, transPower, transStart, transEnd, price):
    self.event("OfferAccepted", {'offerID': offerID, 'assetID': assetID, 'transPower': transPower, 'transStart': transStart, 'transEnd': transEnd, 'price': price})
  
  def postOffer(self, sender, assetID, price):
    asset = self.energyAssets[assetID]
    cost = price * asset.power * (asset.end + 1 - asset.start)
    # Checks
    assert(assetID < self.nextEnergyAssetID)
    assert(asset.owner == sender)
    if (asset.assetType == self.AssetType.Consumption):
      assert(self.financialBalance[sender] >= cost)
    # Effects
    asset.owner = None
    if (asset.assetType == self.AssetType.Consumption):
      self.financialBalance[sender] -= cost
      offerType = self.OfferType.Bid
    else:
      offerType = self.OfferType.Ask

    self.offers[self.nextOfferID] = self.Offer(
      poster=sender, 
      offerType=offerType,
      assetID=assetID, 
      price=price,
      state=self.OfferState.Open)
      
    power = asset.power if asset.assetType == self.AssetType.Production else asset.power
    self.OfferPosted(self.nextOfferID, assetID, power, asset.start, asset.end, price)
    self.nextOfferID += 1
    return self.nextOfferID - 1
  
  def rescindOffer(self, sender, offerID):
    offer = self.offers[offerID]
    asset = self.energyAssets[offer.assetID]
    # Checks
    assert(offerID < self.nextOfferID)
    assert(offer.poster == sender)
    assert(offer.state == self.OfferState.Open)
    # Effects
    offer.state = self.OfferState.Rescinded
    asset.owner = sender
    if (offer.offerType == self.OfferType.Bid):
      self.financialBalance[sender] += offer.price * asset.power * (asset.end + 1 - asset.start)
    self.OfferRescinded(offerID)
  
  def acceptOffer(self, sender, offerID, assetID):
    offer = self.offers[offerID]
    offeredAsset = self.energyAssets[offer.assetID]
    providedAsset = self.energyAssets[assetID]
    transStart = offeredAsset.start if offeredAsset.start > providedAsset.start else providedAsset.start
    transEnd = offeredAsset.end if offeredAsset.end < providedAsset.end else providedAsset.end
    transPower = offeredAsset.power if offeredAsset.power < providedAsset.power else providedAsset.power
    cost = offer.price * transPower * (transEnd + 1 - transStart)
    # Checks 
    assert(offerID < self.nextOfferID)
    assert(assetID < self.nextEnergyAssetID)
    assert(offer.state == self.OfferState.Open)
    assert(providedAsset.owner == sender)
    assert(not ((offeredAsset.end < providedAsset.start) and (offeredAsset.start > providedAsset.end))) # assets overlap
    if (offer.offerType == self.OfferType.Ask):
      assert(providedAsset.assetType == self.AssetType.Consumption)
      assert(self.financialBalance[sender] >= cost)
    else:
      assert(offeredAsset.assetType == self.AssetType.Production)
    # Effects
    # split assets
    offeredAsset.owner = offer.poster  # assets inherit ownership
    self.splitAssetByStart(offer.assetID, transStart)
    self.splitAssetByStart(assetID, transStart)
    self.splitAssetByEnd(offer.assetID, transEnd)
    self.splitAssetByEnd(assetID, transEnd)
    self.splitAssetByPower(offer.assetID, transPower)
    self.splitAssetByPower(assetID, transPower)
    # transfer assets
    if (offer.offerType == self.OfferType.Ask):
      self.financialBalance[sender] -= cost
      self.financialBalance[offer.poster] += cost
    else:
      self.financialBalance[sender] += cost
    providedAsset.owner = offer.poster
    offeredAsset.owner = sender
    offer.state = self.OfferState.Closed
    self.OfferAccepted(
      offerID, 
      assetID,
      (transPower if offeredAsset.assetType == self.AssetType.Production else -transPower), 
      transStart, 
      transEnd, 
      offer.price)

  # for testing
  def event(self, name, params):
    print(name, params)
    
# tests
if __name__ == "__main__":
  address = 0
  service = TradingService()
  service.addFinancialBalance(address, 1000)
  service.depositFinancial(address, 500)
  service.addFinancialBalance(address, 2000)
  service.depositFinancial(address, 1000)
    
  assetProd = service.addEnergyAsset(address, 100, 8, 10)
  assetCons = service.addEnergyAsset(address, -200, 9, 11)
  offer1 = service.postOffer(address, assetProd, 10)
  service.rescindOffer(address, offer1)
  offer2 = service.postOffer(address, assetProd, 5)
  service.acceptOffer(address, offer2, assetCons)
  service.depositEnergyAsset(address, assetProd)
  service.depositEnergyAsset(address, assetCons)

