import logging

from collections import defaultdict
from typing import Dict, Tuple, List, Iterable

from LinearProgram import LinearProgram
from LinearProgramCplex import LinearProgramCplex

class ArchitectureJob:
  def __init__(self, reqCPU: int, reqRAM: int, reqStorage: int, imageHash: str):
    self.reqCPU = reqCPU
    self.reqRAM = reqRAM
    self.reqStorage = reqStorage
    self.imageHash = imageHash

  def __repr__(self):
    return f"<{self.reqCPU}, {self.reqRAM}, {self.reqStorage}, {self.imageHash}>"

class JobOffer:
  def __init__(self, offerID: int, actorID: int, timeLimit: int, price: int):
    self.offerID = offerID
    self.actorID = actorID
    self.timeLimit = timeLimit
    self.price = price
    self.desc = {}

  def __repr__(self):
    return f"<{self.offerID}, {self.actorID}, {self.timeLimit}, {self.price}, {self.desc}>"

  def update(self, architecture: int, archJob: ArchitectureJob):
    self.desc[architecture] = archJob

class ResourceOffer:
  def __init__(self, offerID: int, actorID: int, architecture: int, capCPU: int, capRAM: int, capStorage: int, price: int):
    self.offerID = offerID
    self.actorID = actorID
    self.architecture = architecture
    self.capCPU = capCPU
    self.capRAM = capRAM
    self.capStorage = capStorage
    self.price = price

  def __repr__(self):
    return f"<{self.offerID}, {self.actorID}, {self.architecture}, {self.capCPU}, {self.capRAM}, {self.capStorage}, {self.price}>"

  def supports(self, jobOffer: JobOffer) -> bool:
    print(f"jobOffer: {jobOffer}")
    print(f"jobOffer.desc: {jobOffer.desc}")
    print(self.architecture)
    if self.architecture not in jobOffer.desc:
      return False
    archJob = jobOffer.desc[self.architecture]
    print(f"capCPU:{self.capCPU} >= reqCPU:{archJob.reqCPU}")
    print(f"capRAM:{self.capRAM} >= reqRAM:{archJob.reqRAM}")
    print(f"capStorage: {self.capStorage} >= reqStorage:{archJob.reqStorage}")
    print(f"jobOffer.price: {jobOffer.price} >= resourcePrice:{self.price * archJob.reqCPU * jobOffer.timeLimit}")

    return ((self.capCPU >= archJob.reqCPU)
        and (self.capRAM >= archJob.reqRAM)
        and (self.capStorage >= archJob.reqStorage)
        and (jobOffer.price >= self.price * archJob.reqCPU * jobOffer.timeLimit))

class ResourceAllocationLP:
  def solve(self, job_offers: Iterable[JobOffer], resource_offers: Iterable[ResourceOffer], lp_solver: LinearProgram=LinearProgramCplex) -> Tuple[List[Dict],float]:
    program = lp_solver()
    variables = []
    resource_vars = defaultdict(lambda : [])
    job_vars = defaultdict(lambda : [])
    for ro in resource_offers:
      for jo in job_offers:
        if ro.supports(jo):
          varname = 'a_{ro.offerID}_{jo.offerID}'
          var = {'name': varname, 'ro': ro, 'jo': jo}
          variables.append(var)
          resource_vars[ro].append(var)
          job_vars[jo].append(var)
    if not len(variables):
      logging.info("No matchable offers, skipping solver.")
      return ([], 0)

    program.set_objective({v['name']: -v['jo'].price for v in variables})
    for jo in job_offers:
      program.add_constraint({v['name']: 1 for v in job_vars[jo]}, 1) # each job may be assigned to only one resource offer
    for ro in resource_offers:
      program.add_constraint({v['name']: v['jo'].desc[ro.architecture].reqCPU for v in resource_vars[ro]}, ro.capCPU)
      program.add_constraint({v['name']: v['jo'].desc[ro.architecture].reqRAM for v in resource_vars[ro]}, ro.capRAM)
      program.add_constraint({v['name']: v['jo'].desc[ro.architecture].reqStorage for v in resource_vars[ro]}, ro.capStorage)

    (solution, objective) = program.solve()

    for v in variables:
      v['a'] = solution[v['name']]
    return (variables, -objective)
