import logging

from Contract import Contract

class ResourceAllocationContract(Contract):
  def __init__(self, client, address):
    super(ResourceAllocationContract, self).__init__(client, address, [
      "OfferCreated(uint64 ID, bool providing, uint64 misc, uint64 prosumer)",
      "OfferUpdated(uint64 ID, uint64 resourceType, uint64 quantity, uint64 value)",
      "OfferPosted(uint64 ID)",
      "OfferCanceled(uint64 ID)",
      "SolutionCreated(uint64 ID, uint64 misc)",
      "AssignmentAdded(uint64 ID, uint64 providingOfferID, uint64 consumingOfferID, uint64 resourceType, uint64 quantity, uint64 value, uint64 objective)",
      "AssignmentFinalized(uint64 providingOfferID, uint64 consumingOfferID, uint64 resourceType, uint64 quantity, uint64 value)",
      "Debug(string Description, uint64 value, bool boolean, uint64 state)",
      "FinalizeRequested(string Description, uint64 state)",
      "FinalizeComplete(string Description, uint64 state)"
    ])

  def setup(self, from_account, numTypes, precision, maxQuantity):
    print("numTypes %s : %s" %(numTypes, Contract.encode_uint(numTypes)))
    print("precision %s : %s" %(precision, Contract.encode_uint(precision)))
    print("max %s : %s" %(maxQuantity, Contract.encode_uint(maxQuantity)))
    self.call_func(from_account, "setup",
      "uint64", numTypes,
      "uint64", precision,
      "uint64", maxQuantity)

  def createOffer(self, from_account, providing, misc, prosumer):
    print("providing %s : %s" %(providing, Contract.encode_bool(providing)))
    print("misc %s : %s" %(misc, Contract.encode_uint(misc)))
    print("prosumer %s : %s" %(prosumer, Contract.encode_uint(prosumer)))
    self.call_func(from_account, "createOffer",
      "bool", providing,
      "uint64", misc,
      "uint64", prosumer)

  def updateOffer(self, from_account, ID, resourceType, quantity, value):
    print("ID %s : %s" %(ID, Contract.encode_uint(ID)))
    print("RT %s : %s" %(resourceType, Contract.encode_uint(resourceType)))
    print("Q %s : %s" %(quantity, Contract.encode_uint(quantity)))
    print("V %s : %s" %(value, Contract.encode_uint(value)))
    print("UPDATE OFFER")
    self.call_func(from_account, "updateOffer",
      "uint64", ID,
      "uint64", resourceType,
      "uint64", quantity,
      "uint64", value)

  def postOffer(self, from_account, ID):
    print("ID %s : %s" %(ID, Contract.encode_uint(ID)))
    print("POST OFFER")
    self.call_func(from_account, "postOffer",
      "uint64", ID)

  def cancelOffer(self, from_account, ID):
    self.call_func(from_account, "cancelOffer",
      "uint64", ID)

  def check(self, from_account):
    self.call_func(from_account, "check")

  def checkcreateSolution(self, from_account):
    self.call_func(from_account, "checkcreateSolution")

  def createSolution(self, from_account, misc):
    self.call_func(from_account, "createSolution",
      "uint64", misc)
  def close(self, from_account):
    self.call_func(from_account, "close")

  def addAssignment(self, from_account, ID, providingOfferID, consumingOfferID, resourceType, quantity, value):
    # print("ID %s : %s" %(ID, Contract.encode_uint(ID)))
    # print("POID %s : %s" %(providingOfferID, Contract.encode_uint(providingOfferID)))
    # print("COID %s : %s" %(consumingOfferID, Contract.encode_uint(consumingOfferID)))
    # print("RT %s : %s" %(resourceType, Contract.encode_uint(resourceType)))
    # print("Q %s : %s" %(quantity, Contract.encode_uint(quantity)))
    # print("V %s : %s" %(value, Contract.encode_uint(value)))
    print("addAssignment function")
    self.call_func(from_account, "addAssignment",
      "uint64", ID,
      "uint64", providingOfferID,
      "uint64", consumingOfferID,
      "uint64", resourceType,
      "uint64", quantity,
      "uint64", value)

  def finalize(self, from_account):
    self.call_func(from_account, "finalize")
