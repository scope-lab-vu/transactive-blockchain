class EnergyAsset:
  def __init__(self, power, start, end):
    self.power = power
    self.start = start
    self.end = end
    
  def tradeable(self, otherAsset):
    return (self.power * otherAsset.power < 0) and (self.start <= otherAsset.end) and (self.end >= otherAsset.start)
    

