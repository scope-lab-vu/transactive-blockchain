import logging

from LinearProgramCplex import LinearProgramCplex
import pprint
import json

class Offer:
  def __init__(self, ID, providing, prosumer, quantity=None, value=None):
      self.ID = ID
      self.providing = providing
      self.prosumer = prosumer
      if quantity is None:
          self.quantity = {}
      else:
          self.quantity = quantity
      if value is None:
          self.value = {}
      else:
          self.value = value

  def __repr__(self):
    return "<{}, {}, {}, {}, {}>".format(self.ID, self.providing, self.prosumer, self.quantity, self.value)

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
    export_vars = {}
    prov_vars = {}
    cons_vars = {}
    export_pos = {}
    export_cos = {}
    for po in providing_offers:
      export_pos["p_{}".format(po.ID)] = po.__repr__()
      for co in consuming_offers:
        export_cos["c_{}".format(co.ID)] = co.__repr__()
        for t in po.intersection(co):
          variable = {'po': po, 'co': co, 't': t}
          export_var = {'po': po.__repr__(), 'co': co.__repr__(), 't': t}
          varname = 'q_{}_{}_{}'.format(po.ID, co.ID, t)
          variables[varname] = variable
          export_vars[varname] = export_var
          if po in prov_vars:
            prov_vars[po][varname] = po.quantity[t]
          else:
            prov_vars[po] = {varname: po.quantity[t]}
          if co in cons_vars:
            cons_vars[co][varname] = co.quantity[t]
          else:
            cons_vars[co] = {varname: co.quantity[t]}
    with open('input.json', 'w') as fp:
        json.dump(export_vars, fp)
    with open("inputpo.json", 'w') as fp:
        json.dump(export_pos, fp)
    with open("inputco.json", 'w') as fp:
        json.dump(export_cos, fp)
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
    print("SOLUTION1")
    with open('solutions.json', 'w') as fp:
        json.dump(solution, fp)
    print("OBJECTIVE1")
    print(objective)
    export_out = {}
    for varname in variables:
      variables[varname]['q'] = solution[varname]
      if not solution[varname] == 0:
        #   print("SOLUTION VARIABLES")
        #   pprint.pprint(variables[varname])
          export_out[varname]=variables[varname]
    #pprint.pprint(variables)
    # with open('output.json', 'w') as fp:
    #     json.dump(variables, fp)
    return (variables.values(), -objective)

if __name__ == "__main__":
  solver = ResourceAllocationLP(1)
  (assignments, objective) = solver.solve()
  print("Success: objective = {}".format(objective))
