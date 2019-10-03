import argparse
import re
from os.path import basename

parser = argparse.ArgumentParser(description='Process a Solidity source file and generate a Python class for Contract.py.')
parser.add_argument('src', metavar='src', type=str,
                   help='path to Solidity source file')

args = parser.parse_args()

events = []
functions = []
with open(args.src, 'rt') as fin:
  for part in fin.read().split(';'):
    event = re.search(r'event\s+(\w+)\(([^\)]*)\)', part)
    if event is not None:
      events.append(f"{event.group(1)}({event.group(2)})")
    function = re.search(r'function\s+(\w+)\(([^\)]*)\)', part)
    if function is not None:
      params = []
      for param in function.group(2).split(","):
        if param != "":
          type_name = param.strip().split(" ")
          params.append((type_name[0], type_name[-1]))
      functions.append((function.group(1), params))
      
classname = basename(args.src).split('.')[0] + "Contract"
  
with open(classname + ".py", 'wt') as fout:
  fout.write(f"""from Contract import Contract

class {classname}(Contract):
  def __init__(self, client, address):
    super({classname}, self).__init__(client, address, [
""")
  for event in events:
    fout.write(f'      "{event}",\n')
  fout.write("""    ])

""")
  for (name, params) in functions:
    paramnames = ", ".join([pname for (ptype, pname) in params])
    fout.write(f"""  def {name}(self, from_account, {paramnames}):
    self.call_func(from_account, "{name}" """)
    for (ptype, pname) in params:
      fout.write(f',\n      "{ptype}", {pname}')
    fout.write(")\n\n")
    
