#from riaps.run.comp import Component

from const import *

class AuthenticationException(Exception):
  def __init__(self, msg):
    super(AuthenticationException, self).__init__(msg)

class SafetyException(Exception):
  def __init__(self):
    super(SafetyException, self).__init__("Withdrawal would violate safety constraints!")
  
class DSO: #(Component):
  def __init__(self):
    super(DSO, self).__init__()
    # track amount of assets withdrawn by each prosumer for each timestep
    self.prod_withdrawn = {}
    self.cons_withdrawn = {}
    # track which address belongs to which prosumer
    self.addresses = {}
   
  def withdraw_assets(self, prosumer, auth, asset, financial, address):
    try:
      # TODO: verify auth
      if auth != "password":
        raise AuthenticationException("Authentication failed!")
      # check if address has already been taken by another prosumer
      if address in self.addresses and self.addresses[address] != prosumer:
        raise AuthenticationException("Address already taken!")
      self.addresses[address] = prosumer
      # check if withdrawal would violate safety constraints
      for t in range(asset.start, asset.end + 1):
        if asset.power > 0:
          if (prosumer, t) in self.prod_withdrawn and self.prod_withdrawn[(prosumer, t)] + asset.power > PRODUCTION_LIMIT:
            raise SafetyException()          
        elif (prosumer, t) in self.cons_withdrawn and self.cons_withdrawn[(prosumer, t)] - asset.power > CONSUMPTION_LIMIT:
          raise SafetyException()
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
      self.addFinancialBalance(address, financial)
      self.addEnergyAsset(address, asset.power, asset.start, asset.end)
      self.sendEther(address)
    except (AuthenticationException, SafetyException) as e:
      # TODO: notify prosumer
      print(repr(e))    
      pass
      
  # RIAPS message handlers
  
  def on_withdrawAssets(self):
    msg = self.withdrawAsset.recv_pyobj()
    self.withdraw_asset(msg['prosumer'], msg['auth'], msg['asset'], msg['financial'], msg['address'])
    
  # Ethereum function calls
  
  def sendEther(self, address):
    # TODO: implement sending some Ether to address
    print("sendEther", address)
    pass
  
  def addFinancialBalance(self, address, amount):
    # TODO: implement calling the function of TradingService contract
    print("addFinancialBalance", address, amount)
    pass
  
  def addEnergyAsset(self, address, power, start, end):
    # TODO: implement calling the function of TradingService contract
    print("addEnergyAsset", address, power, start, end)
    pass
    
if __name__ == "__main__":
  dso = DSO()
  from EnergyAsset import EnergyAsset
  from Account import Account
  address = Account().address
  dso.withdraw_assets("home1", "password", EnergyAsset(PRODUCTION_LIMIT/2, 0, 10), 10, address) 
  dso.withdraw_assets("home1", "password", EnergyAsset(-(CONSUMPTION_LIMIT/2), 0, 10), 10, address) 
  dso.withdraw_assets("home1", "password", EnergyAsset(PRODUCTION_LIMIT, 5, 15), 10, address) 
  dso.withdraw_assets("home1", "password", EnergyAsset(-CONSUMPTION_LIMIT, 5, 15), 10, address) 
  dso.withdraw_assets("home1", "ohno", EnergyAsset(15, 0, 5), 10, address) 
  dso.withdraw_assets("home2", "password", EnergyAsset(15, 0, 5), 10, address) 
  print("Success.")

