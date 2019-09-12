from Contract import Contract

class ResourceAllocationContract(Contract):
  def __init__(self, client, address):
    super(ResourceAllocationContract, self).__init__(client, address, [
      "Closed()",
      "ResourceOfferPosted(uint64 offerID, uint64 actorID, uint64 architecture, uint64 capCPU, uint64 capRAM, uint64 capStorage, uint64 price)",
      "ResourceOfferCanceled(uint64 offerID)",
      "JobOfferCreated(uint64 offerID, uint64 actorID, uint64 timeLimit, uint64 price, uint64 ioid)",
      "JobOfferUpdated(uint64 offerID, uint64 architecture, uint64 reqCPU, uint64 reqRAM, uint64 reqStorage, uint256 imageHash)",
      "JobOfferPosted(uint64 offerID)",
      "JobOfferCanceled(uint64 offerID)",
      "SolutionCreated(uint64 solutionID, uint64 actorID)",
      "AssignmentAdded(uint64 solutionID, uint64 jobOfferID, uint64 resourceOfferID)",
      "AssignmentFinalized(uint64 jobOfferID, uint64 resourceOfferID)",
      "Debug(string Description, uint64 value, bool boolean, uint64 state, uint256 e256)",
    ])

  def postResourceOffer(self, from_account, actorID, architecture, capCPU, capRAM, capStorage, price):
    self.call_func(from_account, "postResourceOffer" ,
      "uint64", actorID,
      "uint64", architecture,
      "uint64", capCPU,
      "uint64", capRAM,
      "uint64", capStorage,
      "uint64", price)

  def cancelResourceOffer(self, from_account, offerID):
    self.call_func(from_account, "cancelResourceOffer" ,
      "uint64", offerID)

  def createJobOffer(self, from_account, actorID, timeLimit, price, ioid):
      self.call_func(from_account, "createJobOffer" ,
                                   "uint64", actorID,
                                   "uint64", timeLimit,
                                   "uint64", price,
                                   "uint64", ioid)

  def updateJobOffer(self, from_account, offerID, architecture, reqCPU, reqRAM, reqStorage, imageHash):
    self.call_func(from_account, "updateJobOffer" ,
      "uint64", offerID,
      "uint64", architecture,
      "uint64", reqCPU,
      "uint64", reqRAM,
      "uint64", reqStorage,
      "uint256", imageHash)

  def postJobOffer(self, from_account, offerID):
    self.call_func(from_account, "postJobOffer" ,
      "uint64", offerID)

  def postJobCanceled(self, from_account, offerID):
    self.call_func(from_account, "postJobCanceled" ,
      "uint64", offerID)

  def close(self, from_account, ):
    self.call_func(from_account, "close" )

  def createSolution(self, from_account, actorID):
    self.call_func(from_account, "createSolution" ,
      "uint64", actorID)

  def addAssignment(self, from_account, solutionID, jobOfferID, resourceOfferID):
    self.call_func(from_account, "addAssignment" ,
      "uint64", solutionID,
      "uint64", jobOfferID,
      "uint64", resourceOfferID)

  def finalize(self, from_account, ):
    self.call_func(from_account, "finalize" )
