from scipy.optimize import linprog

class LinearProgram:
  def __init__(self):
    self.variables = {} # maps variable names to numbers (variable name may actually be any object)
    self.num_variables = 0 # counts the number of variables
    self.constraints = []
    
  def get_variable(self, name):
    if name not in self.variables:
      self.variables[name] = self.num_variables
      self.num_variables += 1
    return self.variables[name]

  def get_coeffs(self, expr):
    coeffs = {}
    for (name, coeff) in expr.items():
      var = self.get_variable(name)
      coeffs[var] = coeff
    return coeffs
   
  def add_constraint(self, expr, const):
    self.constraints.append((self.get_coeffs(expr), const))
    
  def set_objective(self, expr):
    self.objective = self.get_coeffs(expr)
    
  def get_vector(self, coeffs):
    vect = [0.0] * self.num_variables
    for (var, coeff) in coeffs.items():
      vect[var] = coeff
    return vect
    
  def solve(self):
    logging.debug("Solving linear program with {} variables and {} contraints...".format(len(self.variables), len(self.constraints)))
    c = self.get_vector(self.objective)
    A = []
    b = []
    for (coeffs, const) in self.constraints:
      A.append(self.get_vector(coeffs))
      b.append(const)
    result = linprog(c=c, A_ub=A, b_ub=b)
    logging.debug("Solver output: message = '{}', fun = {}, status = {}".format(result.message, result.fun, result.status))
    return {name: result.x[var] for (name, var) in self.variables.items()}

