from const import *
  
class DSO: 
  def __init__(self):
    super(DSO, self).__init__()
    # track amount of assets withdrawn by each prosumer for each timestep
    self.prod_withdrawn = {}
    self.cons_withdrawn = {}
    # track which address belongs to which prosumer
    self.addresses = {}
   
  def withdraw_assets(self, prosumer, auth, asset, financial, address):
    # TODO: verify auth
    if auth != "password":
      return "Authentication failed!"
    # check if address has already been taken by another prosumer
    if address in self.addresses and self.addresses[address] != prosumer:
      return "Address already taken!"
    self.addresses[address] = prosumer
    if asset is not None:
      # check if withdrawal would violate safety constraints
      for t in range(asset.start, asset.end + 1):
        if asset.power > 0:
          if (prosumer, t) in self.prod_withdrawn and self.prod_withdrawn[(prosumer, t)] + asset.power > PRODUCTION_LIMIT:
            return "Withdrawal would violate safety constraints!"    
        elif (prosumer, t) in self.cons_withdrawn and self.cons_withdrawn[(prosumer, t)] - asset.power > CONSUMPTION_LIMIT:
          return "Withdrawal would violate safety constraints!"
      # update amount of assets withdrawn
      for t in range (asset.start, asset.end + 1):
        if asset.power > 0:
          if (prosumer, t) not in self.prod_withdrawn:
            self.prod_withdrawn[(prosumer, t)] = 0
          self.prod_withdrawn[(prosumer, t)] = self.prod_withdrawn[(prosumer, t)] + asset.power
        else:
          if (prosumer, t) not in self.cons_withdrawn:
            self.cons_withdrawn[(prosumer, t)] = 0
          self.cons_withdrawn[(prosumer, t)] = self.cons_withdrawn[(prosumer, t)] - asset.power
      # create and transfer assets to address 
      self.addEnergyAsset(address, asset.power, asset.start, asset.end)
    if financial > 0:     
      # send Ether and add financial balance
      self.addFinancialBalance(address, financial)
      self.sendEther(address)
    return "Success."

  # contract function calls for testing
  def sendEther(self, address):
    print("sendEther", address)
  def addFinancialBalance(self, address, amount):
    print("addFinancialBalance", address, amount)
  def addEnergyAsset(self, address, power, start, end):
    print("addEnergyAsset", address, power, start, end)

# tests
if __name__ == "__main__":
  dso = DSO()
  from EnergyAsset import EnergyAsset
  from Account import Account
  address = "0x407d73d8a49eeb85d32cf465507dd71d507100c1"
  dso.withdraw_assets("home1", "password", EnergyAsset(PRODUCTION_LIMIT/2, 0, 10), 10, address) 
  dso.withdraw_assets("home1", "password", EnergyAsset(-(CONSUMPTION_LIMIT/2), 0, 10), 10, address) 
  dso.withdraw_assets("home1", "password", EnergyAsset(PRODUCTION_LIMIT, 5, 15), 10, address) 
  dso.withdraw_assets("home1", "password", EnergyAsset(-CONSUMPTION_LIMIT, 5, 15), 10, address) 
  dso.withdraw_assets("home1", "ohno", EnergyAsset(15, 0, 5), 10, address) 
  dso.withdraw_assets("home2", "password", EnergyAsset(15, 0, 5), 10, address) 
  print("Success.")

