import numpy
import binascii

class Account:
  def __init__(self):
    # TODO: generate Ethereum account
    self.address = numpy.random.bytes(20)
    
  def __repr__(self):
    return str(binascii.hexlify(self.address))
    

