from enum import Enum

class TradingService:
  def __init__(self):
    self.financialBalance = {}
    self.energyAssets = {}
    self.nextEnergyAssetID = 0
    self.offers = {}
    self.nextOfferID = 0
  
  def test(self):
    address = 0
    self.addFinancialBalance(address, 1000)
    self.depositFinancial(500)
    self.addFinancialBalance(address, 2000)
    self.depositFinancial(1000)
    
    assetProd = self.addEnergyAsset(address, 100, 8, 10)
    assetCons = self.addEnergyAsset(address, -200, 9, 11)
    offer1 = postOffer(assetProd, 10)
    self.rescindOffer(offer1)
    offer2 = postOffer(assetProd, 5)
    self.acceptOffer(offer2, assetCons)
    self.depositEnergyAsset(assetProd)
    self.depositEnergyAsset(assetCons)
    
  # Financial Assets
  
  def FinancialAdded(self, prosumer, amount):
    print("FinancialAdded", prosumer, amount)
  def FinancialDeposited(self, prosumer, amount):
    print("FinancialAdded", prosumer, amount)
  
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
    print("FinancialAdded", address, assetID, power, start, end)
    
  def AssetDeposited(self, address, assetID, power, start, end):
    print("FinancialAdded", address, assetID, power, start, end)

  def depositEnergyAsset(self, sender, assetID):
    assert(assetID < nextEnergyAssetID)
    asset = self.energyAssets[assetID]
    assert(sender == asset.owner)
    asset.owner = None
    power = asset.power if asset.assetType == AssetType.Production else -asset.power
    self.AssetDeposited(sender, assetID, power, asset.start, asset.end)

  def createEnergyAsset(self, prosumer, assetType, power, start, end):
    self.energyAssets[self.nextEnergyAssetID] = EnergyAsset(
      assetType: assetType,
      power: power,
      start: start, 
      end: end, 
      owner: prosumer)
    if (assetType == AssetType.Production):
      self.AssetAdded(prosumer, nextEnergyAssetID, power, start, end)
    else:
      self.AssetAdded(prosumer, nextEnergyAssetID, -power, start, end)
    return self.nextEnergyAssetID++

  def addEnergyAsset(self, prosumer, power, start, end):
    return self.createEnergyAsset(
      prosumer, 
      (AssetType.Production if power > 0 else AssetType.Consumption), 
      (power if power > 0 else -power), 
      start, 
      end)
  
  def splitAssetByStart(self, assetID, newStart):
    asset = self.energyAssets[assetID]
    if (asset.start < newStart && asset.end >= newStart):
      self.createEnergyAsset(asset.owner, asset.assetType, asset.power, asset.start, newStart - 1)
      asset.start = newStart
  
  def splitAssetByEnd(self, assetID, newEnd):
    asset = self.energyAssets[assetID]
    if (asset.start <= newEnd && asset.end > newEnd):
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
      self.stat = state
  
  def OfferPosted(offerID, assetID, power, start, end, price):
    print("OfferPosted", offerID, assetID, power, start, end, price)

  def OfferRescinded(offerID):
    print("OfferRescinded", offerID)

  def OfferAccepted(offerID, assetID, transPower, transStart, transEnd, price):
    print("OfferAccepted", offerID, assetID, transPower, transStart, transEnd, price)
  
  def postOffer(self, sender, assetID, price) returns (offerID):
    asset = energyAssets[assetID]
    cost = price * asset.power * (asset.end + 1 - asset.start)
    # Checks
    assert(assetID < nextEnergyAssetID)
    assert(asset.owner == sender)
    if (asset.assetType == AssetType.Consumption) 
      assert(financialBalance[sender] >= cost)
    # Effects
    asset.owner = address(this)
    if (asset.assetType == AssetType.Consumption):
      financialBalance[sender] -= cost
      OfferType offerType = OfferType.Bid

    else:
      offerType = OfferType.Ask

    offers[nextOfferID] = Offer({
      poster: sender, 
      offerType: offerType,
      assetID: assetID, 
      price: price,
      state: OfferState.Open)
      
    power = asset.assetType == AssetType.Production ?(asset.power) : -int64(asset.power)
    OfferPosted(nextOfferID, assetID, power, asset.start, asset.end, price)
    return nextOfferID++

  
  def rescindOffer(self, sender, offerID):
    offer = offers[offerID]
    asset = energyAssets[offer.assetID]
    # Checks
    assert(offerID < nextOfferID)
    assert(offer.poster == sender)
    assert(offer.state == OfferState.Open)
    # Effects
    offer.state = OfferState.Rescinded
    asset.owner = sender
    if (offer.offerType == OfferType.Bid)
      financialBalance[sender] += offer.price * asset.power * (asset.end + 1 - asset.start)
    OfferRescinded(offerID)

  
  def acceptOffer(self, sender, offerID, assetID):
    offer = offers[offerID]
    offeredAsset = energyAssets[offer.assetID]
    providedAsset = energyAssets[assetID]
    transStart = offeredAsset.start > providedAsset.start ? offeredAsset.start : providedAsset.start
    transEnd = offeredAsset.end < providedAsset.end ? offeredAsset.end : providedAsset.end
    transPower = offeredAsset.power < providedAsset.power ? offeredAsset.power : providedAsset.power
    cost = offer.price * transPower * (transEnd + 1 - transStart)
    # Checks 
    assert(offerID < nextOfferID)
    assert(assetID < nextEnergyAssetID)
    assert(offer.state == OfferState.Open)
    assert(providedAsset.owner == sender)
    assert(!(offeredAsset.end < providedAsset.start && offeredAsset.start > providedAsset.end)) # assets overlap
    if (offer.offerType == OfferType.Ask):
      assert(providedAsset.assetType == AssetType.Consumption)
      assert(financialBalance[sender] >= cost)

    else:
      assert(offeredAsset.assetType == AssetType.Production)
    # Effects
    # split assets
    offeredAsset.owner = offer.poster  # assets inherit ownership
    splitAssetByStart(offer.assetID, transStart)
    splitAssetByStart(assetID, transStart)
    splitAssetByEnd(offer.assetID, transEnd)
    splitAssetByEnd(assetID, transEnd)
    splitAssetByPower(offer.assetID, transPower)
    splitAssetByPower(assetID, transPower)
    # transfer assets
    if (offer.offerType == OfferType.Ask):
      financialBalance[sender] -= cost
      financialBalance[offer.poster] += cost

    else:
      financialBalance[sender] += cost
    providedAsset.owner = offer.poster
    offeredAsset.owner = sender
    offer.state = OfferState.Closed
    OfferAccepted(
      offerID, 
      assetID,
      offeredAsset.assetType == AssetType.Production ?(transPower) : -int64(transPower), 
      transStart, 
      transEnd, 
      offer.price)


