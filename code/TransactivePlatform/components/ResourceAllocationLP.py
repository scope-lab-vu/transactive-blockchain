import logging

from LinearProgramCplex import LinearProgramCplex

class Offer:
  def __init__(self, ID, providing, prosumer, quantity={}, value={}):
    self.ID = ID
    self.providing = providing
    self.prosumer = prosumer
    self.quantity = quantity
    self.value = value

  def matchable(self, offer):
    for res_type in self.quantity:
      if res_type in offer.quantity:
        if (self.providing and (not offer.providing) and (self.value[res_type] <= offer.value[res_type])) or ((not self.providing) and offer.providing and (self.value[res_type] >= offer.value[res_type])):
          return True
    return False

  def intersection(self, offer):
    res_types = []
    for res_type in self.quantity:
      if res_type in offer.quantity:
        if (self.providing and (not offer.providing) and (self.value[res_type] <= offer.value[res_type])) or ((not self.providing) and offer.providing and (self.value[res_type] >= offer.value[res_type])):
          res_types.append(res_type)
    return res_types

class ResourceAllocationLP:
  def __init__(self, precision):
    self.precision = precision

  def solve(self, providing_offers, consuming_offers, lp_solver=LinearProgramCplex):
    program = lp_solver()
    variables = {}
    prov_vars = {}
    cons_vars = {}
    for po in providing_offers:
      for co in consuming_offers:
        for t in po.intersection(co):
          variable = {'po': po, 'co': co, 't': t}
          varname = 'q_{}_{}_{}'.format(po.ID, co.ID, t)
          variables[varname] = variable
          if po in prov_vars:
            prov_vars[po][varname] = po.quantity[t]
          else:
            prov_vars[po] = {varname: po.quantity[t]}
          if co in cons_vars:
            cons_vars[co][varname] = co.quantity[t]
          else:
            cons_vars[co] = {varname: co.quantity[t]}
    if not len(variables):
      logging.info("No matchable offers, skipping solver.")
      return ([], 0)

    # TODO: add integer constraints based on precision
    program.set_objective({varname: -1.0 for varname in variables})
    for po in prov_vars:
      program.add_constraint(
        {varname: 1.0 / float(prov_vars[po][varname]) for varname in prov_vars[po]}, 1.0)
    for co in cons_vars:
      program.add_constraint(
        {varname: 1.0 / float(cons_vars[co][varname]) for varname in cons_vars[co]}, 1.0)

    (solution, objective) = program.solve()
    for varname in variables:
      variables[varname]['q'] = solution[varname]
    return (variables.values(), -objective)

if __name__ == "__main__":
  solver = ResourceAllocationLP(1)
  (assignments, objective) = solver.solve()
  print("Success: objective = {}".format(objective))
