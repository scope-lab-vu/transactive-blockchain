class Contract:
  def __init__(self, client, address):
    self.client = client
    self.address = address
    self.func_hash = {}
    self.event_hash = {}
    
  def call_func(self, from_account, name, *args):
    # generate signature
    arg_types = []
    arg_values = []
    for i in range(len(args) >> 1):
      arg_types.append(args[i * 2])
      arg_values.append(args[i * 2 + 1])
    signature = "{}({})".format(name, ",".join(arg_types))
    if signature not in self.func_hash:
      keccak256 = client.keccak256(signature)
      if not (keccak256.startswith("0x") and len(keccak256) == 66):
        raise Exception("Incorrect hash {} computed for signature {}!".format(keccak256, signature))
      self.func_hash[signature] = keccak256
    data = self.func_hash[signature]
    # encode arguments
    for i in range(len(arg_types)):
      if arg_types[i] == "uint64":
        data += client.encode_uint(arg_values[i])
      elif arg_types[i] == "int64":
        data += client.encode_int(arg_values[i])
      elif arg_types[i] == "address":
        data += client.encode_address(arg_values[i])
      else:
        raise Exception("Unknown type {}!".format(arg_types[i]))
    # send transaction
    self.client.transaction(from_account, data, self.address)

if __name__ == "__main__":
  c = Contract(None, None)
  c.call_func("createSolution")
  c.call_func("addTrade", "uint64", 0, "uint64", 7, "uint64", 2774, "uint64", 29, "uint64", 400)  
