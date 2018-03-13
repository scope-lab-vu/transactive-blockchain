import logging

from Contract import Contract

class ResourceAllocationContract(Contract):
  def __init__(self, client, address):
    super(ResourceAllocationContract, self).__init__(client, address, [
      "OfferCreated(uint64 ID, bool providing, uint64 misc, uint64 prosumer)",
      "OfferUpdated(uint64 ID, uint64 resourceType, uint64 quantity, uint64 value)",
      "OfferPosted(uint64 ID)",
      "SolutionCreated(uint64 ID, uint64 misc)",
      "AssignmentAdded(uint64 ID, uint64 providingOfferID, uint64 consumingOfferID, uint64 resourceType, uint64 quantity, uint64 value, uint64 objective)",
      "AssignmentFinalized(uint64 providingOfferID, uint64 consumingOfferID, uint64 resourceType, uint64 quantity, uint64 value)"
    ])
    
  def setup(self, from_account, numTypes, precision, maxQuantity):
    self.call_func(from_account, "setup",
      "uint64", numTypes,
      "uint64", precision,
      "uint64", maxQuantity)      
    
  def createOffer(self, from_account, providing, misc, prosumer):
    self.call_func(from_account, "createOffer",
      "bool", providing,
      "uint64", misc,
      "uint64", prosumer)

  def updateOffer(self, from_account, ID, resourceType, quantity, value):
    self.call_func(from_account, "updateOffer", 
      "uint64", ID, 
      "uint64", resourceType, 
      "uint64", quantity, 
      "uint64", value)

  def postOffer(self, from_account, ID):
    self.call_func(from_account, "postSellingOffer", 
      "uint64", ID)
            
  def createSolution(self, from_account, misc):
    self.call_func(from_account, "createSolution",
      "uint64", misc)
    
  def addAssignment(self, from_account, ID, providingOfferID, consumingOfferID, resourceType, quantity, value):
    self.call_func(from_account, "addAssignment",
      "uint64", ID,
      "uint64", providingOfferID,
      "uint64", consumingOfferID,
      "uint64", resourceType,
      "uint64", quantity,
      "uint64", value)
      
  def finalize(self, from_account):
    self.call_func(from_account, "finalize")

